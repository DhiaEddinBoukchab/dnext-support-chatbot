import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Config:
    """Application configuration."""

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    DOCS_FOLDER = os.getenv("DOCS_FOLDER", "docs_md")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    API_DB_PATH = os.getenv("API_DB_PATH", "./runtime_data/chatbot_api.db")

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

    API_PORT = int(os.getenv("API_PORT", "8000"))

    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "dnext-support-chatbot")

    @classmethod
    def validate(cls):
        """Validate required runtime configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found.\n"
                "Please set it in .env or environment variables."
            )

        docs_path = Path(cls.DOCS_FOLDER)
        if not docs_path.exists():
            docs_path.mkdir(parents=True)
            print(f"Created {cls.DOCS_FOLDER} folder")

    @classmethod
    def provider_summary(cls) -> dict:
        """Return a small summary of the current runtime stack."""
        return {
            "embedding_provider": "openai",
            "embedding_model": cls.EMBEDDING_MODEL,
            "llm_provider": "openai",
            "llm_model": cls.OPENAI_MODEL,
            "vector_store_provider": "chroma",
        }
