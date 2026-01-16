import chromadb
from pathlib import Path
from typing import List, Dict, Tuple
import logging
import shutil

logger = logging.getLogger(__name__)

class VectorStore:
    """Manages ChromaDB vector database operations"""
    
    def __init__(self, db_path: str):
        """Initialize ChromaDB client"""
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = None
    
    def create_collection(self, name: str = "support_docs", reset: bool = False):
        """Create or get collection"""
        try:
            if reset:
                try:
                    self.client.delete_collection(name)
                    logger.info(f"Deleted existing collection: {name}")
                except:
                    pass
            
            self.collection = self.client.create_collection(
                name=name,
                metadata={"description": "Dnext customer support documentation"}
            )
            logger.info(f"✅ Collection '{name}' created")
        except Exception as e:
            try:
                self.collection = self.client.get_collection(name)
                logger.info(f"✅ Loaded existing collection: {name}")
            except Exception as collection_error:
                logger.warning(f"Could not load collection: {collection_error}. Attempting to reset database...")
                self._reset_database()
                self.collection = self.client.create_collection(
                    name=name,
                    metadata={"description": "Dnext customer support documentation"}
                )
                logger.info(f"✅ Collection '{name}' created after reset")
        
        return self.collection
    
    def _reset_database(self):
        """Reset the entire database (useful for embedding dimension changes)"""
        try:
            if Path(self.db_path).exists():
                shutil.rmtree(self.db_path)
                logger.info(f"✅ Cleared database at {self.db_path}")
            self.client = chromadb.PersistentClient(path=self.db_path)
            logger.info("✅ Database reinitialized")
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            raise
    
    def get_collection(self, name: str = "support_docs"):
        """Get existing collection or create if not found"""
        try:
            self.collection = self.client.get_collection(name)
            logger.info(f"✅ Retrieved existing collection: {name}")
            return self.collection
        except Exception as e:
            logger.warning(f"Collection not found or error retrieving: {e}")
            logger.info(f"Creating new collection: {name}")
            return self.create_collection(name)
    
    def add_documents(self, chunks: List[str], metadatas: List[Dict], 
                     embeddings: List[List[float]]):
        """Add documents to collection"""
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
    
    def query(self, query_embedding: List[float], top_k: int = 3):
        """Query similar documents"""
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        try:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
        except Exception as e:
            # If embedding dimension mismatch, reset and raise informative error
            if "expecting embedding with dimension" in str(e).lower():
                logger.error(f"Embedding dimension mismatch detected: {e}")
                logger.info("This usually happens when switching embedding models. Please reload documents.")
                raise ValueError(
                    "Embedding dimension mismatch. Please reload your documents through the admin dashboard. "
                    "This occurs when changing embedding models (the old database is incompatible)."
                )
            raise