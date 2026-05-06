from openai import OpenAI, APIConnectionError, AuthenticationError
from typing import List
import logging
import os
from langsmith import traceable


logger = logging.getLogger(__name__)


def _build_openai_error_message(error: Exception) -> str:
    """Convert OpenAI client failures into actionable setup guidance."""
    if isinstance(error, AuthenticationError):
        return "OpenAI authentication failed. Check that OPENAI_API_KEY is set to a valid key."

    if isinstance(error, APIConnectionError):
        return (
            "OpenAI connection failed. Check your internet access and any "
            "HTTP_PROXY/HTTPS_PROXY/ALL_PROXY settings."
        )

    return f"OpenAI request failed: {error}"

class EmbeddingManager:
    """Handles text embeddings using OpenAI embeddings API"""
    
    def __init__(self, model_name: str):
        """Initialize OpenAI embedding model"""
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model_name = model_name
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("✅ OpenAI embedding model initialized with LangSmith tracing")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    @traceable(name="encode_single_text")
    def encode(self, text: str) -> List[float]:
        """Encode single text to embedding"""
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            message = _build_openai_error_message(e)
            logger.error(f"Failed to encode text: {message}")
            raise RuntimeError(message) from e
    @traceable(name="encode_batch_texts")
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
            message = _build_openai_error_message(e)
            logger.error(f"Failed to encode batch: {message}")
            raise RuntimeError(message) from e
