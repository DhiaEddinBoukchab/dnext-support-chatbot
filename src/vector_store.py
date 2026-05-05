import chromadb
from pathlib import Path
from typing import List, Dict, Tuple
import logging
import shutil
from langsmith import traceable

logger = logging.getLogger(__name__)

class VectorStore:
    """Manages ChromaDB vector database operations"""
    
    def __init__(self, db_path: str):
        """Initialize ChromaDB client"""
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = None
    
    def create_collection(self, name: str = "support_docs", collection_name: str = None, reset: bool = False):
        """
        Create or get collection
        
        Args:
            name: Collection name (legacy parameter for compatibility)
            collection_name: Collection name (new parameter)
            reset: Whether to delete existing collection
        """
        # Use collection_name if provided, otherwise use name
        collection_name = collection_name or name
        
        try:
            if reset:
                try:
                    self.client.delete_collection(collection_name)
                    logger.info(f"Deleted existing collection: {collection_name}")
                except:
                    pass
            
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Dnext customer support documentation"}
            )
            logger.info(f"✅ Collection '{collection_name}' created")
        except Exception as e:
            try:
                self.collection = self.client.get_collection(collection_name)
                logger.info(f"✅ Loaded existing collection: {collection_name}")
            except Exception as collection_error:
                logger.warning(f"Could not load collection: {collection_error}. Attempting to reset database...")
                self._reset_database()
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": "Dnext customer support documentation"}
                )
                logger.info(f"✅ Collection '{collection_name}' created after reset")
        
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
    
    @traceable(name="add_documents_to_vectorstore")
    def add_documents(self, chunks: List[str], metadatas: List[Dict], 
                     embeddings: List[List[float]], collection_name: str = None):
        """
        Add documents to collection
        
        Args:
            chunks: List of text chunks to add
            metadatas: List of metadata dicts for each chunk
            embeddings: List of embedding vectors
            collection_name: Optional collection name to use (if different from current)
        """
        # If collection_name is provided, switch to that collection
        if collection_name:
            self.get_collection(collection_name)
        
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(chunks)} documents to vector store")
    
    @traceable(
        name="query_vectorstore",
        run_type="retriever",
        metadata={"retriever_type": "chromadb"}
    )
    def query(self, query_embedding: List[float], top_k: int = 3, n_results: int = None):
        """
        Query similar documents with detailed tracing
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return (legacy parameter)
            n_results: Number of results to return (new parameter)
        """
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        # Use n_results if provided, otherwise use top_k
        num_results = n_results if n_results is not None else top_k
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=num_results
            )
            
            # Log retrieval details
            logger.info(f"Retrieved {len(results['documents'][0])} chunks")
            
            return results
        except Exception as e:
            if "expecting embedding with dimension" in str(e).lower():
                logger.error(f"Embedding dimension mismatch detected: {e}")
                logger.info("This usually happens when switching embedding models. Please reload documents.")
                raise ValueError(
                    "Embedding dimension mismatch. Please reload your documents through the admin dashboard. "
                    "This occurs when changing embedding models (the old database is incompatible)."
                )
            raise