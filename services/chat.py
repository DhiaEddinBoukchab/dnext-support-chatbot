"""Chat orchestration service for the FastAPI API."""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from core.config import Config
from domain.models import Conversation, RetrievalTrace
from infrastructure.database import DatabaseRepository
from rag.engine import RAGEngine
from rag.providers import create_llm_handler
from rag.retrieval_config import get_config_for_conversation_type
from rag.session_manager import SessionManager
from services.auth import AuthenticationService


logger = logging.getLogger(__name__)

NO_CONTEXT_REPLY = (
    "I couldn't find relevant information about this. "
    "For specific assistance, please contact our support team at support@dnext.io"
)


class ChatService:
    """Reusable text-chat service for the REST API."""

    def __init__(self, db: DatabaseRepository, auth: AuthenticationService):
        Config.validate()
        self.db = db
        self.auth = auth
        self.rag = RAGEngine()
        self.rag.initialize()
        self.llm = create_llm_handler()
        self.sessions = SessionManager(db)

    def process_query(self, user_id: int, query: str, session_id: Optional[str] = None) -> Dict:
        """Run the current RAG pipeline for a text query and persist the result."""
        if not self.auth.verify_user_access(user_id):
            raise PermissionError("User is not allowed to access the chatbot")

        session = self._load_session(user_id, session_id)
        start_time = time.time()

        conversation_type = self.llm.classify_conversation(query)
        retrieved_chunks = []
        chunks_retrieved = 0

        if conversation_type == "CASUAL":
            answer = self.llm.generate_response(
                "",
                query,
                conversation_history=session.messages,
                conversation_type=conversation_type,
            )
        else:
            retrieval_config = get_config_for_conversation_type(conversation_type)
            results = self.rag.retrieve_semantic(query, retrieval_config)
            context = self.rag.format_context(results)
            retrieved_chunks = self._build_retrieved_chunks(results)
            chunks_retrieved = len(retrieved_chunks)

            if not context:
                answer = NO_CONTEXT_REPLY
            else:
                answer = self.llm.generate_response(
                    context,
                    query,
                    conversation_history=session.messages,
                    conversation_type=conversation_type,
                )

        session.add_message("user", query)
        session.add_message("assistant", answer)

        elapsed_ms = int((time.time() - start_time) * 1000)
        conversation_id = self.db.save_conversation(
            Conversation(
                user_id=user_id,
                session_id=session.session_id,
                message=query,
                response=answer,
                timestamp=datetime.now(),
                conversation_type=conversation_type,
                response_time_ms=elapsed_ms,
            )
        )

        if conversation_type == "TECHNICAL" and conversation_id:
            self.db.save_retrieval_trace(
                RetrievalTrace(
                    conversation_id=conversation_id,
                    query_input=query,
                    retrieved_chunks=json.dumps(retrieved_chunks),
                    final_answer=answer,
                    num_chunks_retrieved=chunks_retrieved,
                    timestamp=datetime.now(),
                )
            )

        return {
            "session_id": session.session_id,
            "conversation_type": conversation_type,
            "answer": answer,
            "chunks_retrieved": chunks_retrieved,
            "retrieved_chunks": retrieved_chunks,
            "response_time_ms": elapsed_ms,
        }

    def list_sessions(self, user_id: int) -> List[Dict]:
        """Return session summaries for the authenticated user."""
        rows = self.db.get_session_summaries(user_id)
        return [
            {
                "session_id": row["session_id"],
                "title": row["first_message"][:50] + "..." if len(row["first_message"]) > 50 else row["first_message"],
                "last_updated": row["last_updated"],
            }
            for row in rows
        ]

    def get_session_history(self, user_id: int, session_id: str) -> Dict:
        """Return all messages for one session."""
        session = self.sessions.restore_from_db(user_id, session_id)
        return {
            "session_id": session.session_id,
            "messages": session.get_chat_history(),
        }

    def reindex_documents(self) -> Dict:
        """Rebuild the local document index."""
        success, message = self.rag.load_documents()
        return {"success": success, "message": message}

    def _load_session(self, user_id: int, session_id: Optional[str]):
        if not session_id:
            return self.sessions.get_or_create(user_id)

        existing = self.db.get_conversations_by_session(user_id, session_id)
        if existing:
            return self.sessions.restore_from_db(user_id, session_id)
        return self.sessions.get_or_create(user_id, session_id)

    @staticmethod
    def _build_retrieved_chunks(results: Dict) -> List[Dict]:
        if not results.get("documents") or not results["documents"][0]:
            return []

        distances = results.get("distances")
        if not distances:
            distances = [None] * len(results["documents"][0])
        elif isinstance(distances[0], list):
            distances = distances[0]

        chunks = []
        for doc, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            distances,
        ):
            chunks.append({
                "document": metadata.get("document", "Unknown"),
                "section": metadata.get("section", "Unknown"),
                "distance": distance,
                "text": doc,
            })
        return chunks
