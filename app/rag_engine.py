"""
RAG engine: document indexing, vector retrieval, and context formatting.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

from langsmith import traceable

from app.document_processor import DocumentProcessor
from config import Config
from src.chunker import Chunker
from src.embeddings import EmbeddingManager
from src.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGEngine:
    """Handles document loading, indexing, and semantic retrieval."""

    def __init__(self):
        self.embedding_manager = EmbeddingManager(Config.EMBEDDING_MODEL)
        self.vector_store = VectorStore(Config.CHROMA_DB_PATH)
        self.doc_processor = DocumentProcessor()
        self.collection = None

    def initialize(self):
        """Load an existing vector DB or rebuild it from the docs folder."""
        logger.info("Initializing vector database...")
        try:
            self.collection = self.vector_store.get_collection()
            count = self.collection.count()
            if count > 0:
                logger.info("Loaded existing vector database with %s chunks", count)
                return

            logger.info("Existing collection is empty, rebuilding from documents...")
        except Exception as exc:
            logger.warning(
                "Could not load existing database (%s), rebuilding from documents...",
                exc,
            )

        success, message = self.load_documents()
        if not success:
            logger.error(message)

    @traceable(name="load_and_index_documents")
    def load_documents(self) -> Tuple[bool, str]:
        """Load all .md / .txt files from DOCS_FOLDER and index them."""
        try:
            docs_path = Path(Config.DOCS_FOLDER)
            if not docs_path.is_absolute():
                docs_path = Path(Config.BASE_DIR) / docs_path
            docs_path = docs_path.resolve()

            logger.info("Loading documents from %s...", docs_path)

            if not docs_path.exists():
                return False, f"Docs folder not found: {docs_path}"

            self.collection = self.vector_store.create_collection(reset=True)
            md_files = list(docs_path.glob("*.md")) + list(docs_path.glob("*.txt"))

            if not md_files:
                return False, f"No documents found in {docs_path}"

            logger.info("Found %s document(s)", len(md_files))
            total_chunks = 0
            all_chunks: List[str] = []
            all_metadatas: List[Dict] = []
            skipped_docs: List[str] = []

            for doc_file in md_files:
                logger.info("\n%s\nProcessing: %s\n%s", "=" * 60, doc_file.name, "=" * 60)

                with open(doc_file, "r", encoding="utf-8") as file_handle:
                    content = file_handle.read()

                validation = self.doc_processor.chunker.validate_document_format(content)
                logger.info("Validation: %s", validation["message"])

                if not validation["valid"]:
                    logger.error("Skipping %s: %s", doc_file.name, validation["message"])
                    skipped_docs.append(doc_file.name)
                    continue

                sections = self.doc_processor.extract_sections(content)
                logger.info("Found %s section(s)", len(sections))

                for section in sections:
                    section_title = section["title"]
                    section_content = section["content"]

                    if not section_content.strip():
                        continue

                    chunks = self.doc_processor.chunk_text(section_content)
                    if not chunks:
                        logger.error("No chunks created for section '%s'", section_title)
                        continue

                    for index, chunk in enumerate(chunks):
                        if not chunk.strip():
                            continue

                        all_chunks.append(chunk)
                        all_metadatas.append(
                            Chunker.extract_metadata_from_chunk(
                                chunk,
                                doc_file.stem,
                                section_title,
                                index,
                            )
                        )
                        total_chunks += 1

            if not all_chunks:
                message = (
                    f"No chunks created. Processed {len(md_files)} files, "
                    f"skipped {len(skipped_docs)}."
                )
                logger.error(message)
                return False, message

            logger.info("Created %s chunks, generating embeddings...", total_chunks)
            embeddings = self.embedding_manager.encode_batch(all_chunks)
            self.vector_store.add_documents(all_chunks, all_metadatas, embeddings)

            final_count = self.collection.count()
            message = f"Indexed {final_count} chunks from {len(md_files)} documents."
            logger.info(message)
            return True, message

        except Exception as exc:
            message = f"Error loading documents: {exc}"
            logger.error(message, exc_info=True)
            return False, message

    @traceable(name="retrieve_relevant_chunks", run_type="retriever")
    def retrieve(self, query: str, top_k: int = None) -> Dict:
        """Embed a query and return the top matching chunks."""
        if top_k is None:
            top_k = Config.TOP_K_RESULTS

        query_embedding = self.embedding_manager.encode(query)
        results = self.vector_store.query(query_embedding, top_k)

        if results["documents"] and results["documents"][0]:
            distances = results["distances"][0] if "distances" in results else [None] * len(
                results["documents"][0]
            )
            for index, (document, metadata, distance) in enumerate(
                zip(results["documents"][0], results["metadatas"][0], distances)
            ):
                logger.info(
                    "  Rank %s: %s / %s (dist: %s)",
                    index + 1,
                    metadata.get("document", "?"),
                    metadata.get("section", "?"),
                    distance,
                )
        return results

    def format_context(self, results: Dict) -> str:
        """Convert retrieval results into a formatted context string for the LLM."""
        if not results["documents"] or not results["documents"][0]:
            return ""

        parts = []
        for index, (document, metadata) in enumerate(
            zip(results["documents"][0], results["metadatas"][0])
        ):
            section = metadata.get("section", "Unknown")
            source_document = metadata.get("document", "Unknown")
            parts.append(
                f"[Source {index + 1} - Document: {source_document}, Section: {section}]\n"
                f"{document}"
            )

        return "\n\n---\n\n".join(parts)
