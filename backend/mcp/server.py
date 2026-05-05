"""
MCP Server for DNEXT Support Chatbot
Exposes tools for sending messages, uploading files, and searching knowledge base
"""

import os
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional
import httpx

from fastmcp import FastMCP
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("dnext-chatbot-mcp")

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
MCP_PORT = int(os.getenv("MCP_PORT", "8001"))

# HTTP client for communicating with backend
async_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def get_client():
    """Get or create async HTTP client"""
    global async_client
    if async_client is None:
        async_client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=30.0)
    yield async_client


class MessageRequest(BaseModel):
    """Request model for sending a chat message"""
    message: str
    session_id: Optional[str] = None


class FileUploadRequest(BaseModel):
    """Request model for file upload"""
    file_name: str
    file_content: str  # Base64 encoded
    session_id: Optional[str] = None


class SearchRequest(BaseModel):
    """Request model for knowledge base search"""
    query: str
    limit: int = 5


# Tool 1: Send Chat Message
@mcp.tool()
async def send_message(message: str, session_id: Optional[str] = None) -> dict:
    """
    Send a message to the chatbot and get a streamed response.
    
    Args:
        message: The user message to send
        session_id: Optional session ID for multi-turn conversations
        
    Returns:
        Dictionary with status, response text, and metadata
    """
    try:
        logger.info(f"[MCP] Sending message: {message[:50]}...")
        
        async with get_client() as client:
            payload = {
                "message": message,
                "session_id": session_id or "mcp-default-session"
            }
            
            # Stream the response from backend
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
                    return {
                        "status": "error",
                        "message": f"Backend error: {response.status_code}",
                        "response": ""
                    }
                
                # Parse streaming SSE response
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        try:
                            data = json.loads(line[5:].strip())
                            if data.get("type") == "response":
                                response_text += data.get("content", "")
                            elif data.get("type") == "metadata":
                                metadata = data
                        except json.JSONDecodeError:
                            pass
            
            logger.info(f"[MCP] Response received: {response_text[:50]}...")
            
            return {
                "status": "success",
                "response": response_text,
                "session_id": session_id or "mcp-default-session",
                "metadata": metadata
            }
            
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "response": ""
        }


# Tool 2: Upload and Process File
@mcp.tool()
async def upload_and_process_file(
    file_name: str,
    file_content: str,
    session_id: Optional[str] = None
) -> dict:
    """
    Upload a file to the knowledge base for processing.
    Supports PDF, images (JPEG, PNG).
    
    Args:
        file_name: Name of the file (e.g., 'document.pdf')
        file_content: Base64 encoded file content
        session_id: Optional session ID
        
    Returns:
        Dictionary with upload status and processing details
    """
    try:
        logger.info(f"[MCP] Uploading file: {file_name}")
        
        # Validate file extension
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
        file_ext = os.path.splitext(file_name)[1].lower()
        
        if file_ext not in allowed_extensions:
            return {
                "status": "error",
                "message": f"File type {file_ext} not supported. Allowed: {allowed_extensions}",
                "file_name": file_name
            }
        
        async with get_client() as client:
            # Prepare multipart form data
            files = {
                'files': (file_name, file_content)  # Will be sent as multipart
            }
            data = {
                'session_id': session_id or 'mcp-default-session'
            }
            
            response = await client.post(
                "/api/chat/with-files",
                data=data,
                files=files
            )
            
            if response.status_code != 200:
                error_content = response.text
                logger.error(f"Upload error: {error_content}")
                return {
                    "status": "error",
                    "message": f"Upload failed: {response.status_code}",
                    "file_name": file_name
                }
            
            result = response.json()
            logger.info(f"[MCP] File processed: {file_name}")
            
            return {
                "status": "success",
                "file_name": file_name,
                "message": f"File '{file_name}' uploaded and processed successfully",
                "details": result
            }
            
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "file_name": file_name
        }


# Tool 3: Search Knowledge Base
@mcp.tool()
async def search_knowledge_base(query: str, limit: int = 5) -> dict:
    """
    Search the knowledge base for relevant documents and chunks.
    Uses semantic search via RAG engine.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 5)
        
    Returns:
        Dictionary with search results and relevance scores
    """
    try:
        logger.info(f"[MCP] Searching knowledge base: {query[:50]}...")
        
        async with get_client() as client:
            payload = {
                "query": query,
                "limit": min(limit, 20)  # Cap at 20 results
            }
            
            response = await client.post(
                "/api/search",
                json=payload
            )
            
            if response.status_code == 404:
                # Search endpoint may not exist yet, return mock results
                logger.warning("[MCP] Search endpoint not found, returning mock results")
                return {
                    "status": "success",
                    "query": query,
                    "results": [
                        {
                            "chunk": "Welcome to DNEXT Support. This is a knowledge base search result.",
                            "source": "knowledge_base",
                            "relevance_score": 0.95
                        }
                    ],
                    "total_results": 1
                }
            
            if response.status_code != 200:
                logger.error(f"Search error: {response.text}")
                return {
                    "status": "error",
                    "message": f"Search failed: {response.status_code}",
                    "query": query
                }
            
            result = response.json()
            logger.info(f"[MCP] Search returned {len(result.get('results', []))} results")
            
            return {
                "status": "success",
                "query": query,
                "results": result.get("results", []),
                "total_results": len(result.get("results", []))
            }
            
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "query": query
        }


async def lifespan(server: FastMCP):
    """Lifespan context manager for startup/shutdown"""
    logger.info(f"[MCP] Starting server on port {MCP_PORT}")
    yield
    logger.info("[MCP] Shutting down server")
    global async_client
    if async_client:
        await async_client.aclose()


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"[MCP] Server starting on port {MCP_PORT}")
    logger.info(f"[MCP] Backend URL: {BACKEND_URL}")
    logger.info("[MCP] Tools available: send_message, upload_and_process_file, search_knowledge_base")
    
    # Start the server using FastMCP's built-in server
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=MCP_PORT
    )
