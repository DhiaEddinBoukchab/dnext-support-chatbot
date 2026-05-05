"""Integration tests for chat endpoint"""

import pytest
import json
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


class TestChatEndpoint:
    """Tests for the chat endpoint"""
    
    def test_chat_missing_message(self):
        """Test chat endpoint without message"""
        response = client.post("/api/chat", json={})
        # Pydantic validation should catch this
        assert response.status_code == 422
    
    def test_chat_empty_message(self):
        """Test chat endpoint with empty message"""
        response = client.post("/api/chat", json={"message": ""})
        # Pydantic min_length validation should catch this
        assert response.status_code == 422
    
    def test_chat_basic_request(self):
        """Test basic chat request with streaming response"""
        response = client.post(
            "/api/chat",
            json={"message": "Hello, how are you?", "session_id": "test_session_123"}
        )
        
        # Should return 200 with streaming content
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        
        # Check that response contains SSE data
        content = response.text
        assert "data:" in content
        
        # Parse SSE messages
        lines = content.strip().split("\n")
        sse_lines = [line for line in lines if line.startswith("data:")]
        assert len(sse_lines) > 0
        
        # Parse first message
        first_message = json.loads(sse_lines[0][6:])  # Remove "data: " prefix
        assert first_message["type"] in ["response", "metadata", "error"]
    
    def test_chat_with_session_id(self):
        """Test chat endpoint preserves session ID"""
        session_id = "test_session_abc123"
        response = client.post(
            "/api/chat",
            json={"message": "Test message", "session_id": session_id}
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check that metadata contains the session ID
        lines = content.strip().split("\n")
        sse_lines = [line for line in lines if line.startswith("data:")]
        
        for sse_line in sse_lines:
            try:
                message = json.loads(sse_line[6:])
                if message.get("type") == "metadata":
                    assert message["data"]["session_id"] == session_id
                    break
            except json.JSONDecodeError:
                continue


class TestSessionManagement:
    """Tests for session management endpoints"""
    
    def test_get_nonexistent_session(self):
        """Test getting a non-existent session"""
        response = client.get("/api/sessions/nonexistent_session")
        assert response.status_code == 404
    
    def test_delete_nonexistent_session(self):
        """Test deleting a non-existent session"""
        response = client.delete("/api/sessions/nonexistent_session")
        assert response.status_code == 404


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_invalid_json(self):
        """Test endpoint with invalid JSON"""
        response = client.post(
            "/api/chat",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_chat_content_type(self):
        """Test proper content-type for streaming response"""
        response = client.post(
            "/api/chat",
            json={"message": "Test"}
        )
        assert response.headers["content-type"] == "text/event-stream"
        assert "no-cache" in response.headers.get("cache-control", "").lower()
        assert "no" in response.headers.get("x-accel-buffering", "").lower()
