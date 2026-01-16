from openai import OpenAI
from typing import List
import logging
import os

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Handles text embeddings using OpenAI embeddings API"""
    
    def __init__(self, model_name: str):
        """Initialize OpenAI embedding model"""
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model_name = model_name
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("✅ OpenAI embedding model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    def encode(self, text: str) -> List[float]:
        """Encode single text to embedding"""
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            raise
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Encode multiple texts to embeddings"""
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            # Sort by index to maintain order
            embeddings = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in embeddings]
        except Exception as e:
            logger.error(f"Failed to encode batch: {e}")
            raise
