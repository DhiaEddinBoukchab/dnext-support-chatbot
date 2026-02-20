"""
RAG engine: document indexing, vector retrieval, and context formatting.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

from langsmith import traceable

from config import Config
from src.embeddings import EmbeddingManager
from src.vector_store import VectorStore
from src.chunker import Chunker
from app.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class RAGEngine:
    """Handles document loading/indexing and semantic retrieval."""

    def __init__(self):
        self.embedding_manager = EmbeddingManager(Config.EMBEDDING_MODEL)
        self.vector_store = VectorStore(Config.CHROMA_DB_PATH)
        self.doc_processor = DocumentProcessor()
        self.collection = None

    def initialize(self):
        """Load existing vector DB or build it from documents."""
        logger.info("Initializing vector database...")
        try:
            self.collection = self.vector_store.get_collection()
            logger.info("✅ Loaded existing vector database")
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