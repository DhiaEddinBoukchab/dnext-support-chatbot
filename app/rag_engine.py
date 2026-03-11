"""
RAG engine: document indexing, vector retrieval, and context formatting.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from langsmith import traceable

from config import Config
from src.embeddings import EmbeddingManager
from src.vector_store import VectorStore
from src.chunker import Chunker
from src.bm25_search import get_bm25_indexer
from src.retrieval_config import RetrievalConfig, get_config_for_conversation_type
from app.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class RAGEngine:
    """Handles document loading/indexing and semantic retrieval."""

    def __init__(self):
        self.embedding_manager = EmbeddingManager(Config.EMBEDDING_MODEL)
        self.vector_store = VectorStore(Config.CHROMA_DB_PATH)
        self.doc_processor = DocumentProcessor()
        self.collection = None
        self.bm25_indexer = get_bm25_indexer()  # Initialize BM25 indexer

    def initialize(self):
        """Load existing vector DB or build it from documents."""
        logger.info("Initializing vector database...")
        try:
            self.collection = self.vector_store.get_collection()
            logger.info("✅ Loaded existing vector database")
            # Index all existing chunks with BM25
            self._index_collection_with_bm25()
        except Exception:
            logger.info("No existing database found — building from documents...")
            self.load_documents()

    @traceable(name="load_and_index_documents")
    def load_documents(self) -> Tuple[bool, str]:
        """Load all .md / .txt files from DOCS_FOLDER and index them."""
        try:
            logger.info(f"Loading documents from {Config.DOCS_FOLDER}...")
            self.collection = self.vector_store.create_collection(reset=True)

            docs_path = Path(Config.DOCS_FOLDER)
            md_files = list(docs_path.glob("*.md")) + list(docs_path.glob("*.txt"))

            if not md_files:
                return False, f"❌ No documents found in {Config.DOCS_FOLDER}"

            logger.info(f"Found {len(md_files)} document(s)")
            total_chunks = 0
            all_chunks: List[str] = []
            all_metadatas: List[Dict] = []
            skipped_docs: List[str] = []

            for doc_file in md_files:
                logger.info(f"\n{'='*60}\nProcessing: {doc_file.name}\n{'='*60}")

                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                validation = self.doc_processor.chunker.validate_document_format(content)
                logger.info(f"Validation: {validation['message']}")

                if not validation['valid']:
                    logger.error(f"❌ Skipping {doc_file.name}: {validation['message']}")
                    skipped_docs.append(doc_file.name)
                    continue

                sections = self.doc_processor.extract_sections(content)
                logger.info(f"Found {len(sections)} section(s)")

                for section in sections:
                    section_title = section["title"]
                    section_content = section["content"]

                    if not section_content.strip():
                        continue

                    chunks = self.doc_processor.chunk_text(section_content)
                    if not chunks:
                        logger.error(f"❌ No chunks created for section '{section_title}'")
                        continue

                    for i, chunk in enumerate(chunks):
                        if not chunk.strip():
                            continue
                        all_chunks.append(chunk)
                        metadata = Chunker.extract_metadata_from_chunk(
                            chunk, doc_file.stem, section_title, i
                        )
                        all_metadatas.append(metadata)
                        total_chunks += 1

            if not all_chunks:
                msg = f"❌ No chunks created! Processed {len(md_files)} files, skipped {len(skipped_docs)}."
                logger.error(msg)
                return False, msg

            logger.info(f"✅ Created {total_chunks} chunks — generating embeddings...")
            embeddings = self.embedding_manager.encode_batch(all_chunks)
            self.vector_store.add_documents(all_chunks, all_metadatas, embeddings)

            # Index chunks with BM25 for hybrid search
            logger.info("Indexing chunks with BM25 for keyword search...")
            self.bm25_indexer.index_chunks(all_chunks)

            final_count = self.collection.count()
            msg = f"✅ Indexed {final_count} chunks from {len(md_files)} documents!"
            logger.info(msg)
            return True, msg

        except Exception as e:
            msg = f"❌ Error loading documents: {str(e)}"
            logger.error(msg, exc_info=True)
            return False, msg

    @traceable(name="retrieve_relevant_chunks", run_type="retriever")
    def retrieve(self, query: str, top_k: int = None) -> Dict:
        """Embed query and return top-k matching chunks from the vector store."""
        if top_k is None:
            top_k = Config.TOP_K_RESULTS

        query_embedding = self.embedding_manager.encode(query)
        results = self.vector_store.query(query_embedding, top_k)

        if results['documents'] and results['documents'][0]:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0] if 'distances' in results
                else [None] * len(results['documents'][0])
            )):
                logger.info(
                    f"  Rank {i+1}: {metadata.get('document','?')} / "
                    f"{metadata.get('section','?')} (dist: {distance})"
                )
        return results

    def _index_collection_with_bm25(self) -> None:
        """Index all chunks in the collection with BM25 for hybrid search."""
        try:
            if self.collection is None:
                logger.warning("Collection not initialized. Skipping BM25 indexing.")
                return
            
            # Retrieve all chunks from the collection
            all_results = self.collection.get()
            if all_results and all_results['documents']:
                logger.info(f"Indexing {len(all_results['documents'])} chunks with BM25...")
                self.bm25_indexer.index_chunks(all_results['documents'])
            else:
                logger.warning("No documents found in collection for BM25 indexing.")
        except Exception as e:
            logger.error(f"Error indexing collection with BM25: {e}")

    @traceable(name="retrieve_hybrid", run_type="retriever")
    def retrieve_hybrid(self, query: str, config: Optional[RetrievalConfig] = None) -> Dict:
        """
        Hybrid retrieval combining semantic (vector) search + BM25 keyword search.
        
        Args:
            query: Search query
            config: RetrievalConfig with thresholds and weights
            
        Returns:
            Dict with filtered and merged documents, metadatas, and distances
        """
        if config is None:
            config = RetrievalConfig()
        
        logger.info(f"Hybrid retrieval: threshold={config.distance_threshold}, "
                   f"min={config.min_chunks}, max={config.max_chunks}")
        
        # 1. Semantic search
        query_embedding = self.embedding_manager.encode(query)
        semantic_results = self.vector_store.query(query_embedding, config.top_k_semantic)
        
        # Build semantic results dict: {text -> (distance, metadata)}
        semantic_dict = {}
        if semantic_results['documents'] and semantic_results['documents'][0]:
            for doc, metadata, distance in zip(
                semantic_results['documents'][0],
                semantic_results['metadatas'][0],
                semantic_results['distances'][0] if 'distances' in semantic_results else [None] * len(semantic_results['documents'][0])
            ):
                semantic_dict[doc] = {
                    'distance': distance,
                    'metadata': metadata,
                    'semantic_score': 1.0 - distance if distance is not None else 0.5,
                }
        
        # 2. BM25 keyword search
        bm25_results = self.bm25_indexer.search(query, config.top_k_keyword) if config.use_hybrid_search else []
        
        # Build BM25 results dict: {text -> bm25_score}
        bm25_scores = {}
        max_bm25_score = 1.0
        if bm25_results:
            max_bm25_score = max([score for _, score, _ in bm25_results]) or 1.0
        
        for idx, bm25_score, text in bm25_results:
            normalized_score = bm25_score / max_bm25_score if max_bm25_score > 0 else 0
            bm25_scores[text] = normalized_score
        
        # 3. Merge results with weighted scoring
        merged = {}
        
        # Add all semantic results
        for text, sem_data in semantic_dict.items():
            bm25_score = bm25_scores.get(text, 0.0)
            combined_score = (
                config.semantic_weight * sem_data['semantic_score'] +
                config.keyword_weight * bm25_score
            )
            merged[text] = {
                'distance': sem_data['distance'],
                'metadata': sem_data['metadata'],
                'semantic_score': sem_data['semantic_score'],
                'bm25_score': bm25_score,
                'combined_score': combined_score,
            }
        
        # Add BM25-only results (not in semantic results)
        for text in bm25_scores:
            if text not in merged:
                # Estimate distance based on BM25 score (inverse relationship)
                estimated_distance = 1.0 - bm25_scores[text]
                merged[text] = {
                    'distance': estimated_distance,
                    'metadata': {'document': 'Unknown', 'section': 'Unknown'},
                    'semantic_score': 0.0,
                    'bm25_score': bm25_scores[text],
                    'combined_score': config.keyword_weight * bm25_scores[text],
                }
        
        # 4. Filter by distance threshold
        filtered = {
            text: data for text, data in merged.items()
            if data['distance'] <= config.distance_threshold
        }
        
        logger.info(f"Before filtering: {len(merged)} chunks, After: {len(filtered)}")
        
        # 5. Apply min/max chunk bounds
        sorted_results = sorted(
            filtered.items(),
            key=lambda x: x[1]['combined_score'],
            reverse=True
        )
        
        # Enforce min_chunks
        if len(sorted_results) < config.min_chunks and len(merged) >= config.min_chunks:
            # If we have fewer chunks than min_chunks after filtering, relax threshold
            logger.info(f"Below min_chunks ({len(sorted_results)} < {config.min_chunks}), relaxing threshold...")
            sorted_all = sorted(merged.items(), key=lambda x: x[1]['combined_score'], reverse=True)
            sorted_results = sorted_all[:config.min_chunks]
        
        # Enforce max_chunks
        if len(sorted_results) > config.max_chunks:
            sorted_results = sorted_results[:config.max_chunks]
        
        logger.info(f"Final retrieval: {len(sorted_results)} chunks")
        
        # 6. Format results in the same structure as original retrieve()
        documents = [text for text, _ in sorted_results]
        metadatas = [data['metadata'] for _, data in sorted_results]
        distances = [data['distance'] for _, data in sorted_results]
        
        return {
            'documents': [documents],
            'metadatas': [metadatas],
            'distances': distances,
            'ids': [None] * len(documents),  # Placeholder
        }

    def format_context(self, results: Dict) -> str:
        """Convert retrieval results into a formatted context string for the LLM."""
        if not results['documents'] or not results['documents'][0]:
            return ""

        parts = []
        for i, (doc, metadata) in enumerate(
            zip(results['documents'][0], results['metadatas'][0])
        ):
            section = metadata.get('section', 'Unknown')
            document = metadata.get('document', 'Unknown')
            parts.append(f"[Source {i+1} - Document: {document}, Section: {section}]\n{doc}")

        return "\n\n---\n\n".join(parts)
