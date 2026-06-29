"""Document indexing, semantic retrieval, and context formatting."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from langsmith import traceable

from core.config import Config
from rag.chunker import Chunker
from rag.document_processor import DocumentProcessor
from rag.providers import create_embedding_manager, create_vector_store
from rag.retrieval_config import RetrievalConfig


logger = logging.getLogger(__name__)


class RAGEngine:
    """Handle document loading, indexing, and semantic retrieval."""

    def __init__(self):
        self.embedding_manager = create_embedding_manager()
        self.vector_store = create_vector_store()
        self.doc_processor = DocumentProcessor()
        self.collection = None

    def initialize(self):
        """Load an existing vector store or build it from documents."""
        logger.info("Initializing vector database...")
        try:
            self.collection = self.vector_store.get_collection()
            existing_count = self.collection.count()
            if existing_count == 0:
                logger.info("Vector database is empty. Building index from documents...")
                self.load_documents()
                return

            logger.info(f"Loaded existing vector database with {existing_count} chunks")
        except Exception:
            logger.info("No existing database found. Building from documents...")
            self.load_documents()

    @traceable(name="load_and_index_documents")
    def load_documents(self) -> Tuple[bool, str]:
        """Load all markdown/text files from the docs folder and index them."""
        try:
            logger.info(f"Loading documents from {Config.DOCS_FOLDER}...")
            self.collection = self.vector_store.create_collection(reset=True)

            docs_path = Path(Config.DOCS_FOLDER)
            doc_files = list(docs_path.glob("*.md")) + list(docs_path.glob("*.txt"))
            if not doc_files:
                return False, f"No documents found in {Config.DOCS_FOLDER}"

            logger.info(f"Found {len(doc_files)} document(s)")
            all_chunks: List[str] = []
            all_metadatas: List[Dict] = []
            skipped_docs: List[str] = []

            for doc_file in doc_files:
                logger.info(f"Processing: {doc_file.name}")
                content = doc_file.read_text(encoding="utf-8")

                validation = self.doc_processor.chunker.validate_document_format(content)
                logger.info(f"Validation: {validation['message']}")

                if not validation["valid"]:
                    logger.error(f"Skipping {doc_file.name}: {validation['message']}")
                    skipped_docs.append(doc_file.name)
                    continue

                sections = self.doc_processor.extract_sections(content)
                logger.info(f"Found {len(sections)} section(s)")

                for section in sections:
                    if not section["content"].strip():
                        continue

                    chunks = self.doc_processor.chunk_text(section["content"])
                    if not chunks:
                        logger.error(f"No chunks created for section '{section['title']}'")
                        continue

                    for index, chunk in enumerate(chunks):
                        if not chunk.strip():
                            continue
                        all_chunks.append(chunk)
                        all_metadatas.append(
                            Chunker.extract_metadata_from_chunk(
                                chunk,
                                doc_file.stem,
                                section["title"],
                                index,
                            )
                        )

            if not all_chunks:
                message = (
                    f"No chunks created. Processed {len(doc_files)} files, "
                    f"skipped {len(skipped_docs)}."
                )
                logger.error(message)
                return False, message

            logger.info(f"Created {len(all_chunks)} chunks. Generating embeddings...")
            embeddings = self.embedding_manager.encode_batch(all_chunks)
            self.vector_store.add_documents(all_chunks, all_metadatas, embeddings)

            final_count = self.collection.count()
            message = f"Indexed {final_count} chunks from {len(doc_files)} documents."
            logger.info(message)
            return True, message
        except Exception as exc:
            message = f"Error loading documents: {exc}"
            logger.error(message, exc_info=True)
            return False, message

    @traceable(name="retrieve_semantic", run_type="retriever")
    def retrieve_semantic(self, query: str, config: Optional[RetrievalConfig] = None) -> Dict:
        """Run semantic retrieval with threshold filtering and min/max chunk bounds."""
        config = config or RetrievalConfig()

        logger.info(
            f"Semantic retrieval: threshold={config.distance_threshold}, "
            f"min={config.min_chunks}, max={config.max_chunks}"
        )

        query_embedding = self.embedding_manager.encode(query)
        semantic_results = self.vector_store.query(query_embedding, config.top_k_semantic)

        ranked = []
        if semantic_results["documents"] and semantic_results["documents"][0]:
            distances = semantic_results.get("distances", [[]])[0]
            for doc, metadata, distance in zip(
                semantic_results["documents"][0],
                semantic_results["metadatas"][0],
                distances if distances else [None] * len(semantic_results["documents"][0]),
            ):
                ranked.append({
                    "document_text": doc,
                    "distance": distance,
                    "metadata": metadata,
                })

        filtered = [
            item for item in ranked
            if item["distance"] is None or item["distance"] <= config.distance_threshold
        ]
        logger.info(f"Before filtering: {len(ranked)} chunks, After: {len(filtered)}")

        if len(filtered) < config.min_chunks and len(ranked) >= config.min_chunks:
            logger.info(
                f"Below min_chunks ({len(filtered)} < {config.min_chunks}), relaxing threshold..."
            )
            filtered = ranked[: config.min_chunks]

        filtered = filtered[: config.max_chunks]
        logger.info(f"Final retrieval: {len(filtered)} chunks")

        return {
            "documents": [[item["document_text"] for item in filtered]],
            "metadatas": [[item["metadata"] for item in filtered]],
            "distances": [item["distance"] for item in filtered],
            "ids": [None] * len(filtered),
        }

    def format_context(self, results: Dict) -> str:
        """Convert retrieval results into a formatted context string for the LLM."""
        if not results["documents"] or not results["documents"][0]:
            return ""

        parts = []
        for index, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            section = metadata.get("section", "Unknown")
            document = metadata.get("document", "Unknown")
            parts.append(f"[Source {index + 1} - Document: {document}, Section: {section}]\n{doc}")

        return "\n\n---\n\n".join(parts)
