"""Test script for MCP server."""
import asyncio
import json
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_server(base_url: str = "http://localhost:8001"):
    """Test the MCP server endpoints."""
    
    logger.info(f"Testing MCP server at {base_url}")
    
    async with httpx.AsyncClient(timeout=30) as client:
        # Test 1: Health check
        logger.info("\n[TEST 1] Health Check")
        try:
            response = await client.get(f"{base_url}/health")
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Response: {response.json()}")
        except Exception as e:
            logger.error(f"Failed: {e}")
            return
        
        # Test 2: List tools
        logger.info("\n[TEST 2] List Tools")
        try:
            response = await client.post(
                f"{base_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list"
                }
            )
            logger.info(f"Status: {response.status_code}")
            # Read streaming response
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    logger.info(f"Tools: {json.dumps(data, indent=2)}")
        except Exception as e:
            logger.error(f"Failed: {e}")
        
        # Test 3: Call tool with platform question
        logger.info("\n[TEST 3] Call Tool - Platform Question")
        try:
            response = await client.post(
                f"{base_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "query_platform_supporting",
                        "arguments": {
                            "query": "What is the DNEXT platform?"
                        }
                    }
                }
            )
            logger.info(f"Status: {response.status_code}")
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    if "result" in data:
                        content = data["result"]["content"][0]["text"]
                        answer = json.loads(content)
                        logger.info(f"Answer: {answer['answer'][:200]}...")
        except Exception as e:
            logger.error(f"Failed: {e}")
        
        # Test 4: Call tool with data question (should redirect)
        logger.info("\n[TEST 4] Call Tool - Data Question (Should Redirect)")
        try:
            response = await client.post(
                f"{base_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "query_platform_supporting",
                        "arguments": {
                            "query": "how to download a data set from the platform?"
                        }
                    }
                }
            )
            logger.info(f"Status: {response.status_code}")
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    if "result" in data:
                        content = data["result"]["content"][0]["text"]
                        answer = json.loads(content)
                        logger.info(f"Answer: {answer['answer']}")
        except Exception as e:
            logger.error(f"Failed: {e}")
        
        # Test 5: Invalid tool (should error)
        logger.info("\n[TEST 5] Invalid Tool (Should Error)")
        try:
            response = await client.post(
                f"{base_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "invalid_tool",
                        "arguments": {}
                    }
                }
            )
            logger.info(f"Status: {response.status_code}")
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    logger.info(f"Response: {json.dumps(data, indent=2)}")
        except Exception as e:
            logger.error(f"Failed: {e}")
        
        logger.info("\n[TESTS COMPLETE]")


if __name__ == "__main__":
    import sys
    
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
    asyncio.run(test_mcp_server(url))
