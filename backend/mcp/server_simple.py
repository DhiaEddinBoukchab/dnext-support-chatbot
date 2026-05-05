"""
Simple MCP Server without Authentication
This is a lightweight implementation of the MCP server for local/trusted networks
"""

import os
import json
import logging
from typing import Optional, List
import httpx

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
MCP_PORT = int(os.getenv("MCP_PORT", "8001"))

# HTTP client
async_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def get_client():
    """Get or create async HTTP client"""
    global async_client
    if async_client is None:
        async_client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=30.0)
    yield async_client


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


class ChatResponse(BaseModel):
    status: str
    response: str
    session_id: str
    metadata: dict = {}


class SearchResponse(BaseModel):
    status: str
    query: str
    results: list
    total_results: int


class FileUploadResponse(BaseModel):
    status: str
    file_name: str
    message: str
    details: dict = {}


# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    logger.info(f"[MCP] Server starting on port {MCP_PORT}")
    logger.info(f"[MCP] Backend URL: {BACKEND_URL}")
    logger.info("[MCP] No authentication enabled - use on trusted networks only")
    yield
    logger.info("[MCP] Shutting down")
    global async_client
    if async_client:
        await async_client.aclose()


app = FastAPI(
    title="DNEXT MCP Server",
    description="Model Context Protocol server for DNEXT Support Chatbot",
    version="1.0.0",
    lifespan=lifespan
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "dnext-mcp-server",
        "version": "1.0.0"
    }


# Tool 1: Send Message
@app.post("/tools/send-message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message to the chatbot"""
    try:
        logger.info(f"[MCP] Sending message: {request.message[:50]}...")
        
        async with get_client() as client:
            payload = {
                "message": request.message,
                "session_id": request.session_id or "mcp-session"
            }
            
            response_text = ""
            metadata = {}
            
            async with client.stream(
                "POST",
                "/api/chat",
                json=payload
            ) as response:
                if response.status_code != 200:
                    error_content = await response.aread()
                    logger.error(f"Backend error: {error_content}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Backend processing error"
                    )
                
                # Parse streaming SSE response - backend yields cumulative responses
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        try:
                            data = json.loads(line[5:].strip())
                            if data.get("type") == "response":
                                response_text = data.get("content", "")  # Take latest cumulative response
                            elif data.get("type") == "metadata":
                                metadata = data
                        except json.JSONDecodeError:
                            pass
            
            logger.info(f"[MCP] Response generated")
            
            return ChatResponse(
                status="success",
                response=response_text,
                session_id=request.session_id or "mcp-session",
                metadata=metadata
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing error: {str(e)}"
        )


# Info endpoint
@app.get("/tools/info")
async def tools_info():
    """Get information about available tools"""
    return {
        "tools": [
            {
                "name": "send_message",
                "description": "Send a message to the chatbot and get a streamed response",
                "endpoint": "POST /tools/send-message",
                "parameters": {
                    "message": {"type": "string", "required": True},
                    "session_id": {"type": "string", "required": False}
                }
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("[MCP] Starting simple MCP server (no authentication)")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=MCP_PORT,
        log_level="info"
    )
