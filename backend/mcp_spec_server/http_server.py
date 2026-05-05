"""HTTP Streamable Server for MCP."""
import json
import logging
from typing import Any
import asyncio

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn

from tools import query_tool
from config import MCP_SERVER_HOST, MCP_SERVER_PORT, TOOL_NAME, TOOL_DESCRIPTION

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="DNEXT MCP Server", version="1.0.0")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "dnext-mcp-server"}


@app.post("/mcp")
async def mcp_streamable_endpoint(request: Request):
    """
    Streamable HTTP endpoint for MCP protocol.
    Accepts JSON-RPC 2.0 requests and returns streaming responses.
    """
    try:
        # Log incoming request details
        content_type = request.headers.get("content-type", "unknown")
        logger.info(f"[MCP HTTP] Incoming request - Content-Type: {content_type}")
        
        # Read and parse JSON body
        try:
            body = await request.json()
        except json.JSONDecodeError as e:
            logger.error(f"[MCP HTTP] JSON decode error: {str(e)}")
            # Try reading raw body to debug
            raw_body = await request.body()
            logger.error(f"[MCP HTTP] Raw body: {raw_body[:200]}")
            raise
        
        logger.info(f"[MCP HTTP] Request: {body.get('method', 'unknown')}")

        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")

        # Handle list_tools
        if method == "tools/list":
            logger.info("[MCP HTTP] list_tools requested")
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": TOOL_NAME,
                            "description": TOOL_DESCRIPTION,
                            "inputSchema": {
                                "type": "object",
                                "properties": {"query": {"type": "string"}},
                                "required": ["query"],
                            },
                        }
                    ]
                },
            }
            return StreamingResponse(
                _generate_sse(json.dumps(response)), media_type="text/event-stream"
            )

        # Handle call_tool
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            logger.info(f"[MCP HTTP] tool called: {tool_name}")

            if tool_name != TOOL_NAME:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                }
                return StreamingResponse(
                    _generate_sse(json.dumps(error_response)), media_type="text/event-stream"
                )

            # Get query
            query = arguments.get("query")
            if not query:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32600, "message": "Missing 'query' parameter"},
                }
                return StreamingResponse(
                    _generate_sse(json.dumps(error_response)), media_type="text/event-stream"
                )

            # Execute tool and stream response
            async def stream_tool_response():
                try:
                    result = await query_tool.execute(query)
                    logger.info(f"[MCP HTTP] Tool executed successfully")

                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
                    }
                    yield f"data: {json.dumps(response)}\n\n"

                except Exception as e:
                    logger.error(f"[MCP HTTP] Tool error: {str(e)}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32603, "message": str(e)},
                    }
                    yield f"data: {json.dumps(error_response)}\n\n"

            return StreamingResponse(stream_tool_response(), media_type="text/event-stream")

        else:
            logger.warning(f"[MCP HTTP] Unknown method: {method}")
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"},
            }
            return StreamingResponse(
                _generate_sse(json.dumps(error_response)), media_type="text/event-stream"
            )

    except json.JSONDecodeError:
        logger.error("[MCP HTTP] Invalid JSON")
        error_response = {
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
        }
        return StreamingResponse(
            _generate_sse(json.dumps(error_response)), media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"[MCP HTTP] Unexpected error: {str(e)}")
        error_response = {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": "Internal error"},
        }
        return StreamingResponse(
            _generate_sse(json.dumps(error_response)), media_type="text/event-stream"
        )


async def _generate_sse(message: str):
    """Generate Server-Sent Event format."""
    yield f"data: {message}\n\n"
    await asyncio.sleep(0)


def run_server():
    """Run the HTTP server."""
    logger.info(f"[MCP HTTP] Starting server on {MCP_SERVER_HOST}:{MCP_SERVER_PORT}")
    logger.info(f"[MCP HTTP] Endpoint: http://{MCP_SERVER_HOST}:{MCP_SERVER_PORT}/mcp")

    uvicorn.run(
        app,
        host=MCP_SERVER_HOST,
        port=MCP_SERVER_PORT,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()
