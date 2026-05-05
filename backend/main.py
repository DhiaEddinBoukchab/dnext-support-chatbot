"""
FastAPI backend for DNEXT Support Chatbot V2
Provides REST API for chat functionality with streaming support
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Set paths relative to the repository root so the API and UI share one data store.
import os
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent
os.environ.setdefault("CHROMA_DB_PATH", str(project_root / "data" / "chroma_db"))
os.environ.setdefault("DATABASE_PATH", str(project_root / "data" / "chatbot.db"))

# Load environment variables
load_dotenv(project_root / ".env")
load_dotenv(backend_dir / ".env")

# Import routes
from routes.chat import router as chat_router
from routes.health import router as health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown handler"""
    logger.info("🚀 Starting FastAPI backend")
    yield
    logger.info("🛑 Shutting down FastAPI backend")


# Create FastAPI app
app = FastAPI(
    title="DNEXT Support Chatbot API",
    description="REST API for the DNEXT Support Chatbot",
    version="2.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(chat_router, prefix="/api", tags=["chat"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DNEXT Support Chatbot API v2.0",
        "docs": "/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
