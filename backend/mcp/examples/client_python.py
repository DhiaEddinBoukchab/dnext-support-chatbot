"""
Python client example for connecting to DNEXT MCP Server
This example shows how to use the three tools: send_message, upload_file, search
"""

import asyncio
import base64
import httpx
from typing import Optional


class DNEXTMCPClient:
    """Python client for DNEXT MCP Server"""
    
    def __init__(self, server_url: str, api_key: str):
        """
        Initialize the client
        
        Args:
            server_url: URL of the MCP server (e.g., http://localhost:8001)
            api_key: API key provided by DNEXT admin
        """
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def send_message(self, message: str, session_id: Optional[str] = None) -> dict:
        """
        Send a message to the chatbot
        
        Args:
            message: The user message
            session_id: Optional session ID for multi-turn conversations
            
        Returns:
            Response dict with status, response text, and metadata
            
        Example:
            result = await client.send_message("What is DNEXT?")
            print(result['response'])
        """
        payload = {
            "message": message,
            "session_id": session_id or "default"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/tools/send-message",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Server error: {response.status_code}",
                    "response": ""
                }
            
            return response.json()
    
    async def upload_file(
        self,
        file_path: str,
        session_id: Optional[str] = None
    ) -> dict:
        """
        Upload a file to the knowledge base
        
        Args:
            file_path: Path to the file (PDF, JPG, PNG)
            session_id: Optional session ID
            
        Returns:
            Response dict with upload status and details
            
        Example:
            result = await client.upload_file("document.pdf")
            print(f"Uploaded: {result['file_name']}")
        """
        # Read and encode file
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        file_name = file_path.split('/')[-1]
        
        # Prepare multipart form
        files = {
            'file': (file_name, file_content)
        }
        data = {
            'session_id': session_id or 'default'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/tools/upload-file",
                files=files,
                data=data,
                headers={"Authorization": self.headers["Authorization"]}
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Server error: {response.status_code}",
                    "file_name": file_name
                }
            
            return response.json()
    
    async def search(self, query: str, limit: int = 5) -> dict:
        """
        Search the knowledge base
        
        Args:
            query: Search query
            limit: Max number of results (1-20)
            
        Returns:
            Response dict with search results and relevance scores
            
        Example:
            result = await client.search("password reset")
            for item in result['results']:
                print(f"Score: {item['relevance_score']}")
                print(f"Text: {item['chunk']}")
        """
        payload = {
            "query": query,
            "limit": min(limit, 20)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/tools/search",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Server error: {response.status_code}",
                    "query": query,
                    "results": []
                }
            
            return response.json()
    
    async def get_tools_info(self) -> dict:
        """Get information about available tools"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.server_url}/tools/info",
                headers=self.headers
            )
            return response.json() if response.status_code == 200 else {}


# Example usage
async def main():
    # Initialize client
    client = DNEXTMCPClient(
        server_url="http://localhost:8001",
        api_key="dnext_xxxxx"  # Replace with your actual API key
    )
    
    # Example 1: Send a message
    print("=" * 60)
    print("Example 1: Sending a message")
    print("=" * 60)
    
    result = await client.send_message(
        message="What are the main features of DNEXT?",
        session_id="my_session_1"
    )
    
    print(f"Status: {result['status']}")
    print(f"Response: {result['response'][:200]}...")
    print()
    
    # Example 2: Search knowledge base
    print("=" * 60)
    print("Example 2: Searching knowledge base")
    print("=" * 60)
    
    result = await client.search(
        query="How to configure dashboard?",
        limit=3
    )
    
    print(f"Status: {result['status']}")
    print(f"Found {result['total_results']} results")
    
    for i, item in enumerate(result['results'], 1):
        print(f"\nResult {i}:")
        print(f"  Score: {item['relevance_score']:.2f}")
        print(f"  Source: {item['source']}")
        print(f"  Text: {item['chunk'][:100]}...")
    
    print()
    
    # Example 3: Get tools info
    print("=" * 60)
    print("Example 3: Available tools")
    print("=" * 60)
    
    info = await client.get_tools_info()
    
    for tool in info.get('tools', []):
        print(f"\nTool: {tool['name']}")
        print(f"  Endpoint: {tool['endpoint']}")
        print(f"  Description: {tool['description']}")


if __name__ == "__main__":
    asyncio.run(main())
