"""
Tool definitions and implementations for MCP Server
Each tool is wrapped with detailed documentation and type hints
"""

import logging
from typing import Optional, List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ToolType(str, Enum):
    """Supported tool types"""
    SEND_MESSAGE = "send_message"
    UPLOAD_FILE = "upload_and_process_file"
    SEARCH_KB = "search_knowledge_base"


class MessageResponse:
    """Response model for send_message tool"""
    
    def __init__(
        self,
        status: str,
        response: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.status = status
        self.response = response
        self.session_id = session_id
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "response": self.response,
            "session_id": self.session_id,
            "metadata": self.metadata
        }


class FileUploadResponse:
    """Response model for upload_and_process_file tool"""
    
    def __init__(
        self,
        status: str,
        file_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status = status
        self.file_name = file_name
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "file_name": self.file_name,
            "message": self.message,
            "details": self.details
        }


class SearchResult:
    """Single search result"""
    
    def __init__(
        self,
        chunk: str,
        source: str,
        relevance_score: float,
        metadata: Optional[Dict] = None
    ):
        self.chunk = chunk
        self.source = source
        self.relevance_score = relevance_score
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        return {
            "chunk": self.chunk,
            "source": self.source,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata
        }


class SearchResponse:
    """Response model for search_knowledge_base tool"""
    
    def __init__(
        self,
        status: str,
        query: str,
        results: List[SearchResult],
        total_results: int
    ):
        self.status = status
        self.query = query
        self.results = results
        self.total_results = total_results
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_results": self.total_results
        }


class ToolRegistry:
    """Registry of all available tools"""
    
    TOOLS = {
        "send_message": {
            "name": "send_message",
            "description": "Send a message to the DNEXT Support Chatbot and receive a streamed response",
            "parameters": {
                "message": {
                    "type": "string",
                    "description": "The user message to send to the chatbot",
                    "required": True
                },
                "session_id": {
                    "type": "string",
                    "description": "Optional session ID for multi-turn conversations. If not provided, a default session is used.",
                    "required": False
                }
            },
            "example": {
                "message": "What are the main features of DNEXT?",
                "session_id": "session_abc123"
            }
        },
        "upload_and_process_file": {
            "name": "upload_and_process_file",
            "description": "Upload a document file (PDF, JPEG, PNG) to the knowledge base for processing and indexing",
            "parameters": {
                "file_name": {
                    "type": "string",
                    "description": "Name of the file with extension (.pdf, .jpg, .jpeg, .png)",
                    "required": True
                },
                "file_content": {
                    "type": "string",
                    "description": "Base64 encoded file content",
                    "required": True
                },
                "session_id": {
                    "type": "string",
                    "description": "Optional session ID to associate with the upload",
                    "required": False
                }
            },
            "example": {
                "file_name": "DNEXT_User_Guide.pdf",
                "file_content": "JVBERi0xLjQK...",  # Base64 encoded
                "session_id": "session_abc123"
            }
        },
        "search_knowledge_base": {
            "name": "search_knowledge_base",
            "description": "Search the knowledge base using semantic search to find relevant documents and chunks",
            "parameters": {
                "query": {
                    "type": "string",
                    "description": "Search query to find relevant information",
                    "required": True
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (1-20, default: 5)",
                    "required": False
                }
            },
            "example": {
                "query": "How to configure dashboard settings?",
                "limit": 5
            }
        }
    }
    
    @classmethod
    def get_tool(cls, tool_name: str) -> Optional[Dict]:
        """Get tool definition by name"""
        return cls.TOOLS.get(tool_name)
    
    @classmethod
    def list_tools(cls) -> List[Dict]:
        """List all available tools"""
        return list(cls.TOOLS.values())


# Tool documentation for API clients
TOOL_DOCUMENTATION = """
# DNEXT MCP Server Tools

## Overview
The MCP (Model Context Protocol) server exposes three powerful tools for interacting with the DNEXT Support Chatbot:

### 1. send_message
Send messages to the chatbot and get real-time streamed responses.

**Parameters:**
- `message` (string, required): The user message
- `session_id` (string, optional): Session identifier for multi-turn conversations

**Returns:**
```json
{
  "status": "success",
  "response": "The chatbot's response...",
  "session_id": "session_id",
  "metadata": {
    "chunks_retrieved": 3,
    "response_time_ms": 1200
  }
}
```

**Example:**
```python
result = await send_message(
    message="What is DNEXT?",
    session_id="my_session"
)
```

---

### 2. upload_and_process_file
Upload documents (PDF, images) to the knowledge base for indexing and retrieval.

**Parameters:**
- `file_name` (string, required): Filename with extension (.pdf, .jpg, .png)
- `file_content` (string, required): Base64 encoded file content
- `session_id` (string, optional): Associated session ID

**Returns:**
```json
{
  "status": "success",
  "file_name": "document.pdf",
  "message": "File uploaded and processed successfully",
  "details": {
    "chunks_created": 10,
    "processing_time_ms": 2500
  }
}
```

**Example:**
```python
import base64

with open("guide.pdf", "rb") as f:
    file_content = base64.b64encode(f.read()).decode()

result = await upload_and_process_file(
    file_name="guide.pdf",
    file_content=file_content
)
```

---

### 3. search_knowledge_base
Search the knowledge base using semantic search to find relevant information.

**Parameters:**
- `query` (string, required): Search query
- `limit` (integer, optional): Max results (1-20, default: 5)

**Returns:**
```json
{
  "status": "success",
  "query": "How to reset password?",
  "results": [
    {
      "chunk": "To reset your password, go to Settings > Account...",
      "source": "user_guide.pdf",
      "relevance_score": 0.95,
      "metadata": {}
    }
  ],
  "total_results": 1
}
```

**Example:**
```python
result = await search_knowledge_base(
    query="password reset",
    limit=5
)
```

---

## Error Handling

All tools return a response with a `status` field:
- `"success"`: Operation completed successfully
- `"error"`: Operation failed

When status is "error", check the `message` field for details:
```json
{
  "status": "error",
  "message": "File type .docx not supported. Allowed: .pdf, .jpg, .jpeg, .png"
}
```

---

## Authentication

All requests must include an API key in the Authorization header:
```
Authorization: Bearer dnext_xxxxx
```

Contact your DNEXT administrator for an API key.
"""
