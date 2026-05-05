# MCP Server Integration Guide for Haotian

## Server Overview

The DNEXT MCP Server provides a single tool: `query_platform_supporting` that answers questions about the DNEXT platform.

**Server Details:**
- **Endpoint**: `http://<dhia-server>:8001/mcp`
- **Protocol**: MCP 2.0 with Streamable HTTP
- **Authentication**: None (direct access)
- **Response Time**: < 60 seconds typical

---

## Tool Definition

Use this exact definition in your agent configuration:

```json
{
  "name": "query_platform_supporting",
  "description": "This agent answers platform-related questions about the DNEXT platform: module definitions, feature explanations, how-to guides, general troubleshooting, user documentation, and support email knowledge. It does NOT answer questions about specific datasets, data values, metadata, catalogue entries, or anything requiring SQL execution. Call this tool when the user asks how something works, what something means, or how to fix a general platform issue.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string" }
    },
    "required": ["query"]
  }
}
```

---

## Tool Behavior

### What This Tool Answers

- **Platform Documentation**: Module definitions, features, capabilities
- **How-to Guides**: Step-by-step instructions for using DNEXT
- **Troubleshooting**: General platform issues and fixes
- **Configuration**: Platform setup and configuration guidance
- **Support Resources**: References to support documentation

### What This Tool Rejects (Redirects to data-catalog/query_data tools)

- **Dataset Questions**: "What are the sales figures for Q3 2024?"
- **Metadata Questions**: "Show me the schema for the customers table"
- **SQL Questions**: "How do I write a query for..."
- **Data Values**: Any specific data point from datasets
- **Catalogue Entries**: Information about specific data tables/catalogs

---

## Example Requests

### Example 1: Platform Documentation (ANSWERED)

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "query_platform_supporting",
    "arguments": {
      "query": "How do I set up user authentication in DNEXT?"
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"answer\": \"To set up user authentication in DNEXT, follow these steps: 1. Navigate to the Security Settings... [detailed guide]\"}"
      }
    ]
  }
}
```

### Example 2: Dataset Question (REDIRECTED)

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "query_platform_supporting",
    "arguments": {
      "query": "What are the total sales for Q3 2024?"
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"answer\": \"That's a data-specific question about actual datasets. Please use the data-catalog tool or query_data tool instead.\"}"
      }
    ]
  }
}
```

### Example 3: Metadata Question (REDIRECTED)

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "query_platform_supporting",
    "arguments": {
      "query": "Show me the columns in the transactions table"
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"answer\": \"That's a metadata/SQL question about catalogue entries. Please use the data-catalog tool instead.\"}"
      }
    ]
  }
}
```

---

## Tool Discovery

### List Available Tools

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "query_platform_supporting",
        "description": "This agent answers platform-related questions...",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": { "type": "string" }
          },
          "required": ["query"]
        }
      }
    ]
  }
}
```

---

## Integration Checklist

- [ ] Server URL: `http://<dhia-server>:8001/mcp` (replace `<dhia-server>` with actual hostname)
- [ ] Network connectivity: Verify you can reach the endpoint from your agent
- [ ] Tool definition: Copy exact JSON definition above into your agent config
- [ ] Test call: Make a test request with a platform documentation question
- [ ] Verify scope boundaries: Confirm redirects work for data/SQL questions

---

## Troubleshooting

### Server Not Responding
- Check if server is running: `curl http://<server>:8001/health`
- Check firewall rules allow port 8001
- Verify correct hostname/IP in endpoint URL

### Tool Returns Error
- Check query syntax (should be a string)
- Verify tool name matches exactly: `query_platform_supporting`
- Check backend service is running

### Tool Returns "I couldn't find..."
- The question might be out of scope - rephrase focusing on platform features
- Try asking about documentation or how-to guides instead

### Unexpected Redirects
- If you're being redirected to data-catalog tool, your question is about specific data
- This is intentional behavior - switch to the appropriate data tool

---

## Performance Notes

- **Typical Response Time**: 2-10 seconds
- **Max Response Time**: 60 seconds
- **Timeout**: Requests exceeding 60s will be terminated
- **Concurrent Requests**: Supported (requests processed in parallel)

---

## Support

For issues or questions about this MCP server, contact Dhia at the DNEXT platform team.
