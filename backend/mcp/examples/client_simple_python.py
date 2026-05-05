"""
Simple Python MCP Client (No Authentication)
Usage examples for connecting to DNEXT MCP Server without API keys
"""

import httpx
import asyncio
import json
from typing import Optional


class SimpleMCPClient:
    """Simple client for MCP Server without authentication"""
    
    def __init__(self, server_url: str = "http://localhost:8001"):
        """
        Initialize client
        
        Args:
            server_url: URL of the MCP server (e.g., http://localhost:8001)
        """
        self.server_url = server_url.rstrip('/')
        self.client = httpx.AsyncClient(base_url=self.server_url)
    
    async def send_message(self, message: str, session_id: Optional[str] = None) -> dict:
        """
        Send a message to the chatbot
        
        Args:
            message: The message to send
            session_id: Optional session ID for conversation continuity
            
        Returns:
            Response with chatbot's reply
        """
        try:
            payload = {
                "message": message,
                "session_id": session_id or "default-session"
            }
            
            response = await self.client.post(
                "/tools/send-message",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Server error: {response.text}")
            
            return response.json()
        
        except Exception as e:
            print(f"Error sending message: {e}")
            raise
    
    async def upload_file(self, file_path: str, session_id: Optional[str] = None) -> dict:
        """
        Upload a file to the knowledge base
        
        Args:
            file_path: Path to file (PDF, JPG, PNG)
            session_id: Optional session ID
            
        Returns:
            Upload response
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f)}
                data = {'session_id': session_id or 'default-session'}
                
                response = await self.client.post(
                    "/tools/upload-file",
                    files=files,
                    data=data
                )
            
            if response.status_code != 200:
                raise Exception(f"Server error: {response.text}")
            
            return response.json()
        
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            raise
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise
    
    async def search_knowledge_base(self, query: str, limit: int = 5) -> dict:
        """
        Search the knowledge base
        
        Args:
            query: Search query
            limit: Maximum number of results (default 5)
            
        Returns:
            Search results
        """
        try:
            payload = {
                "query": query,
                "limit": limit
            }
            
            response = await self.client.post(
                "/tools/search",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Server error: {response.text}")
            
            return response.json()
        
        except Exception as e:
            print(f"Error searching: {e}")
            raise
    
    async def get_tools_info(self) -> dict:
        """Get available tools information"""
        try:
            response = await self.client.get("/tools/info")
            return response.json()
        except Exception as e:
            print(f"Error getting tools info: {e}")
            raise
    
    async def health_check(self) -> dict:
        """Check if server is running"""
        try:
            response = await self.client.get("/health")
            return response.json()
        except Exception as e:
            print(f"Server health check failed: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Example usage
async def main():
    """Example usage of SimpleMCPClient"""
    
    # Initialize client
    client = SimpleMCPClient("http://localhost:8001")
    
    try:
        # Check server health
        print("1. Checking server health...")
        health = await client.health_check()
        print(f"   Status: {health['status']}")
        
        # Get available tools
        print("\n2. Getting available tools...")
        tools = await client.get_tools_info()
        print(f"   Available tools: {[t['name'] for t in tools['tools']]}")
        
        # Send a message
        print("\n3. Sending message...")
        response = await client.send_message("What is DNEXT?")
        print(f"   Response: {response['response'][:100]}...")
        
        # Search knowledge base
        print("\n4. Searching knowledge base...")
        results = await client.search_knowledge_base("DNEXT features", limit=3)
        print(f"   Found {results['total_results']} results")
        for i, result in enumerate(results['results'], 1):
            print(f"   {i}. {result.get('chunk', 'N/A')[:80]}...")
        
        # Example: Upload a file (if you have one)
        # print("\n5. Uploading file...")
        # upload_response = await client.upload_file("path/to/your/document.pdf")
        # print(f"   File uploaded: {upload_response['file_name']}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await client.close()


# Synchronous wrapper for easier use
class SimpleMCPClientSync:
    """Synchronous wrapper for SimpleMCPClient"""
    
    def __init__(self, server_url: str = "http://localhost:8001"):
        self._client = SimpleMCPClient(server_url)
    
    def send_message(self, message: str, session_id: Optional[str] = None) -> dict:
        """Send a message (synchronous)"""
        return asyncio.run(self._client.send_message(message, session_id))
    
    def upload_file(self, file_path: str, session_id: Optional[str] = None) -> dict:
        """Upload a file (synchronous)"""
        return asyncio.run(self._client.upload_file(file_path, session_id))
    
    def search_knowledge_base(self, query: str, limit: int = 5) -> dict:
        """Search knowledge base (synchronous)"""
        return asyncio.run(self._client.search_knowledge_base(query, limit))
    
    def health_check(self) -> dict:
        """Health check (synchronous)"""
        return asyncio.run(self._client.health_check())


# Example sync usage
def example_sync():
    """Example using synchronous client"""
    client = SimpleMCPClientSync("http://localhost:8001")
    
    # Send message
    response = client.send_message("Hello! What can you help me with?")
    print(f"Bot: {response['response']}")
    
    # Search
    results = client.search_knowledge_base("help")
    print(f"Found {results['total_results']} results")


if __name__ == "__main__":
    # Run async examples
    print("=== DNEXT MCP Client Examples ===\n")
    asyncio.run(main())
