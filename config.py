import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Config:
    """Application configuration."""

    # API keys / cloud settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")

    # Paths
    BASE_DIR = Path(__file__).parent
    DOCS_FOLDER = os.getenv("DOCS_FOLDER", "docs_md")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    API_DB_PATH = os.getenv("API_DB_PATH", "./runtime_data/chatbot_api.db")

    # Provider selection
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
    VECTOR_STORE_PROVIDER = os.getenv("VECTOR_STORE_PROVIDER", "chroma").lower()

    # Models
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
    GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
    BEDROCK_EMBEDDING_MODEL = os.getenv("BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0")
    BEDROCK_LLM_MODEL = os.getenv("BEDROCK_LLM_MODEL", "")
    OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "")

    # Servers
    SERVER_PORT = int(os.getenv("SERVER_PORT", "7860"))
    SERVER_NAME = "0.0.0.0"
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Local JWT auth for localhost API testing
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "local-dev-secret-change-me-1234567890")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

    # Chunking
    CHUNK_SIZE = 400
    CHUNK_OVERLAP = 50
    TOP_K_RESULTS = 5

    # LangSmith
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "dnext-support-chatbot")

    @classmethod
    def validate(cls):
        """Validate required configuration for the currently selected providers."""
        if (cls.LLM_PROVIDER == "openai" or cls.EMBEDDING_PROVIDER == "openai") and not cls.OPENAI_API_KEY:
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
        """Return a small summary of the configured stack for diagnostics."""
        return {
            "embedding_provider": cls.EMBEDDING_PROVIDER,
            "embedding_model": cls.EMBEDDING_MODEL if cls.EMBEDDING_PROVIDER == "openai" else cls.BEDROCK_EMBEDDING_MODEL,
            "llm_provider": cls.LLM_PROVIDER,
            "llm_model": cls.OPENAI_MODEL if cls.LLM_PROVIDER == "openai" else cls.BEDROCK_LLM_MODEL,
            "vector_store_provider": cls.VECTOR_STORE_PROVIDER,
        }
