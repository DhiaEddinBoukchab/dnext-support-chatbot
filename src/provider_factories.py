"""
Provider factories for the local REST API.

The current stack is OpenAI + Chroma. These factories keep the API layer
provider-agnostic so Bedrock + OpenSearch can be added later by configuration.
"""

from config import Config
from src.embeddings import EmbeddingManager
from src.llm_handler import LLMHandler
from src.vector_store import VectorStore


def create_embedding_manager():
    """Return the configured embedding provider implementation."""
    if Config.EMBEDDING_PROVIDER == "openai":
        return EmbeddingManager(Config.EMBEDDING_MODEL)
    if Config.EMBEDDING_PROVIDER == "bedrock":
        raise NotImplementedError(
            "Bedrock embeddings are not implemented in this local version yet. "
            "Use EMBEDDING_PROVIDER=openai for localhost testing."
        )
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {Config.EMBEDDING_PROVIDER}")


def create_llm_handler():
    """Return the configured LLM provider implementation."""
    if Config.LLM_PROVIDER == "openai":
        return LLMHandler(Config.OPENAI_API_KEY, Config.OPENAI_MODEL)
    if Config.LLM_PROVIDER == "bedrock":
        raise NotImplementedError(
            "Bedrock LLM integration is not implemented in this local version yet. "
            "Use LLM_PROVIDER=openai for localhost testing."
        )
    raise ValueError(f"Unsupported LLM_PROVIDER: {Config.LLM_PROVIDER}")


def create_vector_store():
    """Return the configured vector store implementation."""
    if Config.VECTOR_STORE_PROVIDER == "chroma":
        return VectorStore(Config.CHROMA_DB_PATH)
    if Config.VECTOR_STORE_PROVIDER == "opensearch":
        raise NotImplementedError(
            "OpenSearch integration is not implemented in this local version yet. "
            "Use VECTOR_STORE_PROVIDER=chroma for localhost testing."
        )
    raise ValueError(f"Unsupported VECTOR_STORE_PROVIDER: {Config.VECTOR_STORE_PROVIDER}")
