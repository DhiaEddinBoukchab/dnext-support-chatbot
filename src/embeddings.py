from sentence_transformers import SentenceTransformer
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Handles text embeddings using sentence transformers"""
    
    def __init__(self, model_name: str):
        """Initialize embedding model"""
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            logger.info("✅ Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def encode(self, text: str) -> List[float]:
        """Encode single text to embedding"""
        return self.model.encode(text).tolist()
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Encode multiple texts to embeddings"""
        return self.model.encode(texts).tolist()
