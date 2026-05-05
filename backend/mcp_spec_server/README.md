# DNEXT MCP Server

An MCP (Model Context Protocol) server exposing the `query_platform_supporting` tool for answering DNEXT platform documentation questions.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env
```bash
cat > .env << EOF
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
BACKEND_URL=http://localhost:8000
EOF
```

### 3. Start Server
```bash
python http_server.py
```

### 4. Test
```bash
curl http://localhost:8001/health
```

---

## Files

| File | Purpose |
|------|---------|
| `http_server.py` | FastAPI HTTP server with Streamable HTTP transport |
| `server.py` | MCP protocol handler (alternative stdio transport) |
| `tools.py` | `query_platform_supporting` tool implementation |
| `config.py` | Configuration management |
| `test_mcp.py` | Test script for manual testing |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Docker container definition |

## Documentation

- **YOUR_SETUP.md** - Setup instructions for you (server owner)
- **HAOTIAN_INTEGRATION.md** - Complete integration guide for Haotian
- **DEPLOYMENT.md** - Production deployment options (Docker, VPS, AWS)

---

## Tool Definition

**Name**: `query_platform_supporting`

**Purpose**: Answer questions about DNEXT platform documentation, features, and how-to guides.

**Scope**:
- **Answers**: Platform modules, features, how-to guides, troubleshooting, documentation
- **Rejects**: Data-specific questions, SQL queries, metadata, catalogue entries

**Input**: String query

**Output**: JSON with `{"answer": "..."}` format

---

## Server Endpoints

### Health Check
```bash
GET /health
```

### MCP Endpoint (Streamable HTTP)
```bash
POST /mcp
```

---

## Integration with Haotian

1. Start the server with `python http_server.py`
2. Share endpoint URL with Haotian
3. Haotian registers the tool in his agent config
4. Tool is discovered via `tools/list` call
5. Haotian's agent can call `query_platform_supporting` with queries

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_HOST` | `0.0.0.0` | Server bind address |
| `MCP_SERVER_PORT` | `8001` | Server port |
| `BACKEND_URL` | `http://localhost:8000` | DNEXT backend URL |

---

## Logging

All operations are logged with `[MCP HTTP]` and `[MCP Tool]` prefixes for easy debugging.

---

## Performance

- **Response Time**: Typically 2-10 seconds
- **Max Timeout**: 60 seconds
- **Concurrent Requests**: Supported
- **Streaming**: Full support via Server-Sent Events

---

## Troubleshooting

See DEPLOYMENT.md for troubleshooting guide.

---

## Support

For issues or questions, contact Dhia at the DNEXT platform team.
