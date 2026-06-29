"""ChromaDB vector store adapter."""

import logging
from pathlib import Path
import shutil
from typing import Dict, List

import chromadb
from langsmith import traceable


logger = logging.getLogger(__name__)


class VectorStore:
    """Manage ChromaDB vector store operations."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = None

    def create_collection(self, name: str = "support_docs", reset: bool = False):
        """Create or load the default collection."""
        try:
            if reset:
                try:
                    self.client.delete_collection(name)
                    logger.info(f"Deleted existing collection: {name}")
                except Exception:
                    pass

            self.collection = self.client.create_collection(
                name=name,
                metadata={"description": "Dnext customer support documentation"},
            )
            logger.info(f"Collection '{name}' created")
        except Exception:
            try:
                self.collection = self.client.get_collection(name)
                logger.info(f"Loaded existing collection: {name}")
            except Exception as collection_error:
                logger.warning(f"Could not load collection: {collection_error}. Resetting database.")
                self._reset_database()
                self.collection = self.client.create_collection(
                    name=name,
                    metadata={"description": "Dnext customer support documentation"},
                )
                logger.info(f"Collection '{name}' created after reset")

        return self.collection

    def _reset_database(self):
        """Reset the entire database after embedding incompatibilities."""
        if Path(self.db_path).exists():
            shutil.rmtree(self.db_path)
            logger.info(f"Cleared database at {self.db_path}")
        self.client = chromadb.PersistentClient(path=self.db_path)
        logger.info("Database reinitialized")

    def get_collection(self, name: str = "support_docs"):
        """Get the existing collection or create it if missing."""
        try:
            self.collection = self.client.get_collection(name)
            logger.info(f"Retrieved existing collection: {name}")
            return self.collection
        except Exception as exc:
            logger.warning(f"Collection not found or retrieval failed: {exc}")
            return self.create_collection(name)

    @traceable(name="add_documents_to_vectorstore")
    def add_documents(self, chunks: List[str], metadatas: List[Dict], embeddings: List[List[float]]):
        """Add documents to the active collection."""
        if not self.collection:
            raise ValueError("Collection not initialized")

        ids = [f"chunk_{index}" for index in range(len(chunks))]
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
        logger.info(f"Added {len(chunks)} documents to vector store")

    @traceable(name="query_vectorstore", run_type="retriever", metadata={"retriever_type": "chromadb"})
    def query(self, query_embedding: List[float], top_k: int = 3):
        """Query similar documents from the active collection."""
        if not self.collection:
            raise ValueError("Collection not initialized")

        try:
            results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
            logger.info(f"Retrieved {len(results['documents'][0])} chunks")
            return results
        except Exception as exc:
            if "expecting embedding with dimension" in str(exc).lower():
                raise ValueError(
                    "Embedding dimension mismatch. Please reload the indexed documents."
                ) from exc
            raise
