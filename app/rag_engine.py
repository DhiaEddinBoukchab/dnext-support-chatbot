"""
RAG engine: document indexing, vector retrieval, and context formatting.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from langsmith import traceable

from app.document_processor import DocumentProcessor
from config import Config
from src.bm25_search import get_bm25_indexer
from src.chunker import Chunker
from src.provider_factories import create_embedding_manager, create_vector_store
from src.retrieval_config import RetrievalConfig

logger = logging.getLogger(__name__)


class RAGEngine:
    """Handles document loading/indexing and semantic retrieval."""

    def __init__(self):
        self.embedding_manager = create_embedding_manager()
        self.vector_store = create_vector_store()
        self.doc_processor = DocumentProcessor()
        self.collection = None
        self.bm25_indexer = get_bm25_indexer()

    def initialize(self):
        """Load an existing vector DB or build it from documents."""
        logger.info("Initializing vector database...")
        try:
            self.collection = self.vector_store.get_collection()
            existing_count = self.collection.count()
            if existing_count == 0:
                logger.info("Vector database is empty. Building index from documents...")
                self.load_documents()
                return

            logger.info(f"Loaded existing vector database with {existing_count} chunks")
            self._index_collection_with_bm25()
        except Exception:
            logger.info("No existing database found. Building from documents...")
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
                return False, f"No documents found in {Config.DOCS_FOLDER}"

            logger.info(f"Found {len(md_files)} document(s)")
            total_chunks = 0
            all_chunks: List[str] = []
            all_metadatas: List[Dict] = []
            skipped_docs: List[str] = []

            for doc_file in md_files:
                logger.info(f"\n{'=' * 60}\nProcessing: {doc_file.name}\n{'=' * 60}")

                with open(doc_file, "r", encoding="utf-8") as f:
                    content = f.read()

                validation = self.doc_processor.chunker.validate_document_format(content)
                logger.info(f"Validation: {validation['message']}")

                if not validation["valid"]:
                    logger.error(f"Skipping {doc_file.name}: {validation['message']}")
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
                        logger.error(f"No chunks created for section '{section_title}'")
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
                msg = (
                    f"No chunks created. Processed {len(md_files)} files, "
                    f"skipped {len(skipped_docs)}."
                )
                logger.error(msg)
                return False, msg

            logger.info(f"Created {total_chunks} chunks. Generating embeddings...")
            embeddings = self.embedding_manager.encode_batch(all_chunks)
            self.vector_store.add_documents(all_chunks, all_metadatas, embeddings)

            logger.info("Indexing chunks with BM25 for keyword search...")
            self.bm25_indexer.index_chunks(all_chunks)

            final_count = self.collection.count()
            msg = f"Indexed {final_count} chunks from {len(md_files)} documents."
            logger.info(msg)
            return True, msg

        except Exception as exc:
            msg = f"Error loading documents: {exc}"
            logger.error(msg, exc_info=True)
            return False, msg

    @traceable(name="retrieve_relevant_chunks", run_type="retriever")
    def retrieve(self, query: str, top_k: int = None) -> Dict:
        """Embed the query and return top-k matching chunks from the vector store."""
        if top_k is None:
            top_k = Config.TOP_K_RESULTS

        query_embedding = self.embedding_manager.encode(query)
        results = self.vector_store.query(query_embedding, top_k)

        if results["documents"] and results["documents"][0]:
            for i, (doc, metadata, distance) in enumerate(
                zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                    if "distances" in results
                    else [None] * len(results["documents"][0]),
                )
            ):
                logger.info(
                    f"  Rank {i + 1}: {metadata.get('document', '?')} / "
                    f"{metadata.get('section', '?')} (dist: {distance})"
                )
        return results

    def _index_collection_with_bm25(self) -> None:
        """Index all chunks in the collection with BM25 for compatibility."""
        try:
            if self.collection is None:
                logger.warning("Collection not initialized. Skipping BM25 indexing.")
                return

            all_results = self.collection.get()
            if all_results and all_results["documents"]:
                logger.info(f"Indexing {len(all_results['documents'])} chunks with BM25...")
                self.bm25_indexer.index_chunks(all_results["documents"])
            else:
                logger.warning("No documents found in collection for BM25 indexing.")
        except Exception as exc:
            logger.error(f"Error indexing collection with BM25: {exc}")

    @traceable(name="retrieve_semantic", run_type="retriever")
    def retrieve_hybrid(self, query: str, config: Optional[RetrievalConfig] = None) -> Dict:
        """
        Semantic retrieval with threshold-based filtering and min/max chunk bounds.
        """
        if config is None:
            config = RetrievalConfig()

        logger.info(
            f"Semantic retrieval: threshold={config.distance_threshold}, "
            f"min={config.min_chunks}, max={config.max_chunks}"
        )

        query_embedding = self.embedding_manager.encode(query)
        semantic_results = self.vector_store.query(query_embedding, config.top_k_semantic)

        merged = {}
        if semantic_results["documents"] and semantic_results["documents"][0]:
            for doc, metadata, distance in zip(
                semantic_results["documents"][0],
                semantic_results["metadatas"][0],
                semantic_results["distances"][0]
                if "distances" in semantic_results
                else [None] * len(semantic_results["documents"][0]),
            ):
                score = 1.0 - distance if distance is not None else 0.5
                merged[doc] = {
                    "distance": distance,
                    "metadata": metadata,
                    "semantic_score": score,
                    "combined_score": score,
                }

        filtered = {
            text: data for text, data in merged.items()
            if data["distance"] is None or data["distance"] <= config.distance_threshold
        }

        logger.info(f"Before filtering: {len(merged)} chunks, After: {len(filtered)}")

        sorted_results = sorted(
            filtered.items(),
            key=lambda item: item[1]["combined_score"],
            reverse=True,
        )

        if len(sorted_results) < config.min_chunks and len(merged) >= config.min_chunks:
            logger.info(
                f"Below min_chunks ({len(sorted_results)} < {config.min_chunks}), relaxing threshold..."
            )
            sorted_results = sorted(
                merged.items(),
                key=lambda item: item[1]["combined_score"],
                reverse=True,
            )[: config.min_chunks]

        if len(sorted_results) > config.max_chunks:
            sorted_results = sorted_results[: config.max_chunks]

        logger.info(f"Final retrieval: {len(sorted_results)} chunks")

        documents = [text for text, _ in sorted_results]
        metadatas = [data["metadata"] for _, data in sorted_results]
        distances = [data["distance"] for _, data in sorted_results]

        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": distances,
            "ids": [None] * len(documents),
        }

    def format_context(self, results: Dict) -> str:
        """Convert retrieval results into a formatted context string for the LLM."""
        if not results["documents"] or not results["documents"][0]:
            return ""

        parts = []
        for i, (doc, metadata) in enumerate(
            zip(results["documents"][0], results["metadatas"][0])
        ):
            section = metadata.get("section", "Unknown")
            document = metadata.get("document", "Unknown")
            parts.append(f"[Source {i + 1} - Document: {document}, Section: {section}]\n{doc}")

        return "\n\n---\n\n".join(parts)
