"""
ChatbotApp: top-level application object.
Wires together RAGEngine, SessionManager, and MessageHandler.
"""

import logging

from config import Config
from src.llm_handler import LLMHandler
from src.vlm_handler import VLMHandler
from database import DatabaseRepository
from auth_service import AuthenticationService

from app.rag_engine import RAGEngine
from app.session_manager import SessionManager
from app.message_handler import MessageHandler
from app.ui_builder import build_interface

logger = logging.getLogger(__name__)


class ChatbotApp:
    """
    Top-level application object.

    Responsibilities:
      - Validate config
      - Instantiate all components
      - Expose create_interface() for the entry-point (main.py)
    """

    def __init__(self, db: DatabaseRepository, auth: AuthenticationService):
        Config.validate()

        self.db   = db
        self.auth = auth

        # Core ML components
        llm_handler = LLMHandler(Config.OPENAI_API_KEY, Config.OPENAI_MODEL)
        vlm_handler = (
            VLMHandler(Config.GROQ_API_KEY, Config.GROQ_VISION_MODEL)
            if Config.GROQ_API_KEY else None
        )

        if not vlm_handler:
            logger.warning("⚠️  Groq API key not configured — image analysis disabled.")

        # RAG engine (vector DB + embeddings)
        self.rag_engine = RAGEngine()
        self.rag_engine.initialize()

        # Session management
        self.session_mgr = SessionManager(db)

        # Message processing (streaming)
        self.msg_handler = MessageHandler(
            rag_engine=self.rag_engine,
            llm_handler=llm_handler,
            vlm_handler=vlm_handler,
            db=db,
            auth=auth,
        )

    def create_interface(self):
        """Build and return the Gradio Blocks demo."""
        return build_interface(self)