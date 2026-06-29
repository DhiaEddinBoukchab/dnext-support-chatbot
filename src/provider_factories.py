"""Factory helpers for the FastAPI runtime stack."""

from config import Config
from src.embeddings import EmbeddingManager
from src.llm_handler import LLMHandler
from src.vector_store import VectorStore


def create_embedding_manager():
    """Create the OpenAI embedding manager used by the API."""
    return EmbeddingManager(Config.EMBEDDING_MODEL)


def create_llm_handler():
    """Create the OpenAI LLM handler used by the API."""
    return LLMHandler(Config.OPENAI_API_KEY, Config.OPENAI_MODEL)


def create_vector_store():
    """Create the Chroma vector store used by the API."""
    return VectorStore(Config.CHROMA_DB_PATH)
