"""MCP Server for query_platform_supporting tool."""
import logging
import json
from typing import Any

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ToolResult,
)
import mcp.server.stdio

from tools import query_tool
from config import TOOL_NAME, TOOL_DESCRIPTION

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# Create MCP Server
server = Server("dnext-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    Handle list_tools request.
    Returns the query_platform_supporting tool definition.
    """
    logger.info("[MCP] list_tools called")

    return [
        Tool(
            name=TOOL_NAME,
            description=TOOL_DESCRIPTION,
            inputSchema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle call_tool request.
    Processes the query_platform_supporting tool.
    """
    logger.info(f"[MCP] call_tool: {name}")

    if name != TOOL_NAME:
        logger.error(f"[MCP] Unknown tool: {name}")
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"answer": f"Unknown tool: {name}. Available tool: {TOOL_NAME}"}
                ),
            )
        ]

    # Extract query from arguments
    if "query" not in arguments:
        logger.error("[MCP] Missing 'query' argument")
        return [
            TextContent(
                type="text",
                text=json.dumps({"answer": "Missing 'query' parameter"}),
            )
        ]

    query = arguments["query"]
    logger.info(f"[MCP] Query: {query[:100]}...")

    # Execute the tool
    try:
        result = await query_tool.execute(query)
        logger.info(f"[MCP] Tool executed successfully")

        # Return result in exact format
        return [TextContent(type="text", text=json.dumps(result))]

    except Exception as e:
        logger.error(f"[MCP] Tool execution error: {str(e)}")
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"answer": "An error occurred while processing your query."}
                ),
            )
        ]


async def main():
    """Run the MCP server."""
    logger.info("[MCP] Starting DNEXT Platform Support MCP Server")
    logger.info(f"[MCP] Tool available: {TOOL_NAME}")

    # For Streamable HTTP transport, use stdio by default
    # For HTTP transport, would use transport.http below
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("[MCP] Connected via stdio transport")
        await server.run(read_stream, write_stream, mcp.server.stdio.StdioServerParameters())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
