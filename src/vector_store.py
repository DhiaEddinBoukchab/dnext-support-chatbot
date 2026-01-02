import chromadb
from pathlib import Path
from typing import List, Dict, Tuple
import logging

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
        except:
            self.collection = self.client.get_collection(name)
            logger.info(f"✅ Loaded existing collection: {name}")
        
        return self.collection
    
    def get_collection(self, name: str = "support_docs"):
        """Get existing collection"""
        try:
            self.collection = self.client.get_collection(name)
            return self.collection
        except:
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
        
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )