import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Paths
    BASE_DIR = Path(__file__).parent
    DOCS_FOLDER = os.getenv("DOCS_FOLDER", "docs_md")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    
    # Models
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    
    # Server
    SERVER_PORT = int(os.getenv("SERVER_PORT", "7860"))
    SERVER_NAME = "localhost"
    
    # Chunking
    CHUNK_SIZE = 400
    CHUNK_OVERLAP = 50
    TOP_K_RESULTS = 3
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GROQ_API_KEY:
            raise ValueError(
                "❌ GROQ_API_KEY not found!\n"
                "Please set it in .env file or environment variables.\n"
                "Get your key from: https://console.groq.com/keys"
            )
        
        docs_path = Path(cls.DOCS_FOLDER)
        if not docs_path.exists():
            docs_path.mkdir(parents=True)
            print(f"✅ Created {cls.DOCS_FOLDER} folder")