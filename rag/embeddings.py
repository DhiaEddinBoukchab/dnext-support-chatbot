"""OpenAI embedding helpers."""

import logging
from typing import List

from langsmith import traceable
from openai import OpenAI


logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Handle text embeddings using the OpenAI embeddings API."""

    def __init__(self, api_key: str, model_name: str):
        logger.info(f"Loading embedding model: {model_name}")
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key)
        logger.info("OpenAI embedding model initialized")

    @traceable(name="encode_single_text")
    def encode(self, text: str) -> List[float]:
        """Encode a single text to an embedding."""
        response = self.client.embeddings.create(model=self.model_name, input=text)
        return response.data[0].embedding

    @traceable(name="encode_batch_texts")
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Encode multiple texts while preserving order."""
        response = self.client.embeddings.create(model=self.model_name, input=texts)
        embeddings = sorted(response.data, key=lambda item: item.index)
        return [item.embedding for item in embeddings]
