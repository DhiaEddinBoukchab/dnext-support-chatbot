from datetime import datetime
import logging

from fastapi import Depends, FastAPI, HTTPException, status

from api.dependencies import get_chat_service, get_current_user
from api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ReindexResponse,
    SessionHistoryResponse,
    SessionSummary,
    UserResponse,
)
from core.config import Config


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dnext Support Chatbot API",
    version="0.1.0",
    description="Local REST API for testing the current chatbot logic before AWS migration.",
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health endpoint for local testing and containers."""
    return HealthResponse(
        status="ok",
        providers=Config.provider_summary(),
        docs_folder=Config.DOCS_FOLDER,
        timestamp=datetime.utcnow(),
    )


@app.post("/api/v1/chat/query", response_model=ChatResponse)
def chat_query(payload: ChatRequest, current_user: UserResponse = Depends(get_current_user)):
    """Process a text query through the current RAG pipeline."""
    try:
        result = get_chat_service().process_query(
            user_id=current_user.user_id,
            query=payload.query,
            session_id=payload.session_id,
        )
        return ChatResponse(**result)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Chat query failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@app.get("/api/v1/chat/sessions", response_model=list[SessionSummary])
def list_sessions(current_user: UserResponse = Depends(get_current_user)):
    """List the current user's sessions."""
    return get_chat_service().list_sessions(current_user.user_id)


@app.get("/api/v1/chat/sessions/{session_id}", response_model=SessionHistoryResponse)
def get_session(session_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Load one session history."""
    return get_chat_service().get_session_history(current_user.user_id, session_id)


@app.post("/api/v1/knowledge/reindex", response_model=ReindexResponse)
def reindex_knowledge(current_user: UserResponse = Depends(get_current_user)):
    """Rebuild the local docs index after changing files under docs_md/."""
    return get_chat_service().reindex_documents()
