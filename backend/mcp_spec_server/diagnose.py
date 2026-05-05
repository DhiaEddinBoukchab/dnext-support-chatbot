"""Diagnostic script to test MCP server and backend integration."""
import asyncio
import json
import httpx
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def diagnose():
    """Run diagnostics on MCP server and backend."""
    print("\n" + "="*70)
    print("MCP SERVER DIAGNOSTIC TEST")
    print("="*70)
    
    async with httpx.AsyncClient(timeout=10) as client:
        # Test 1: Backend health
        print("\n[TEST 1] Backend Health Check")
        print("-" * 70)
        try:
            response = await client.get("http://localhost:8000/api/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"ERROR: Backend not responding at localhost:8000")
            print(f"Details: {e}")
            return
        
        # Test 2: MCP health
        print("\n[TEST 2] MCP Server Health Check")
        print("-" * 70)
        try:
            response = await client.get("http://localhost:8001/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"ERROR: MCP server not responding at localhost:8001")
            print(f"Details: {e}")
            return
        
        # Test 3: Backend /api/chat endpoint
        print("\n[TEST 3] Backend /api/chat Endpoint")
        print("-" * 70)
        try:
            response = await client.post(
                "http://localhost:8000/api/chat",
                json={"message": "Hello", "session_id": "test_session"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response type: {response.headers.get('content-type')}")
            print(f"Response text (first 300 chars): {response.text[:300]}")
            
            # Try to parse response
            try:
                data = response.json()
                print(f"Parsed JSON: {json.dumps(data, indent=2)[:300]}")
            except:
                print("Response is streaming (SSE), not JSON")
                
        except Exception as e:
            print(f"ERROR: Backend /api/chat failed")
            print(f"Details: {e}")
        
        # Test 4: MCP list_tools
        print("\n[TEST 4] MCP list_tools (Check JSON parsing)")
        print("-" * 70)
        try:
            request_body = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            print(f"Request body: {json.dumps(request_body)}")
            
            response = await client.post(
                "http://localhost:8001/mcp",
                json=request_body,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response type: {response.headers.get('content-type')}")
            
            # Parse SSE response
            print("\nParsing SSE response:")
            for line in response.text.split("\n"):
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    print(f"Parsed: {json.dumps(data, indent=2)[:300]}")
                    
        except Exception as e:
            print(f"ERROR: MCP list_tools failed")
            print(f"Details: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 5: MCP call_tool
        print("\n[TEST 5] MCP call_tool (Check query execution)")
        print("-" * 70)
        try:
            request_body = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "query_platform_supporting",
                    "arguments": {
                        "query": "What is DNEXT?"
                    }
                }
            }
            print(f"Request body: {json.dumps(request_body, indent=2)[:300]}")
            
            response = await client.post(
                "http://localhost:8001/mcp",
                json=request_body,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response type: {response.headers.get('content-type')}")
            
            # Parse SSE response
            print("\nParsing SSE response:")
            for line in response.text.split("\n"):
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:].strip())
                        if "result" in data:
                            content = data["result"]["content"][0]["text"]
                            answer = json.loads(content)
                            print(f"Answer: {answer['answer'][:200]}")
                        elif "error" in data:
                            print(f"Error: {data['error']}")
                    except Exception as parse_e:
                        print(f"Parse error: {parse_e}")
                        print(f"Line: {line[:100]}")
                    
        except Exception as e:
            print(f"ERROR: MCP call_tool failed")
            print(f"Details: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(diagnose())
