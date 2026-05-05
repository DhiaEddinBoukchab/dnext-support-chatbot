# DNEXT MCP Server Setup & Usage Guide

## Overview

The **Model Context Protocol (MCP) Server** enables your online colleagues to access chatbot tools remotely through a secure API. Three main tools are exposed:

1. **send_message** - Send chat messages and get responses
2. **upload_and_process_file** - Upload PDFs/images for knowledge base indexing
3. **search_knowledge_base** - Semantic search across documents

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Server Setup](#server-setup)
3. [API Key Management](#api-key-management)
4. [Authentication](#authentication)
5. [Using the Tools](#using-the-tools)
6. [Client Examples](#client-examples)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Python 3.8+
- Backend FastAPI server running on `http://localhost:8000`

### 1. Install Dependencies
```bash
cd backend/mcp
pip install -r requirements.txt
```

### 2. Generate API Key for Colleague
```bash
python manage_keys.py generate --name "john@example.com" --expires 30
```

You'll get a key like: `dnext_xxxxxxxxxxxxx`

### 3. Start the MCP Server
```bash
python server_secure.py
```

Server will start on `http://localhost:8001`

### 4. Share with Colleague
Colleague uses:
```
Server URL: http://your-domain:8001
API Key: dnext_xxxxxxxxxxxxx
```

---

## Server Setup

### Step 1: Configure Environment

Create `.env` file in `backend/mcp/`:

```env
# Backend URL for API calls
BACKEND_URL=http://localhost:8000

# MCP Server port
MCP_PORT=8001

# API keys storage location
MCP_KEYS_FILE=./keys.json
```

### Step 2: Install Dependencies
```bash
cd backend/mcp
pip install -r requirements.txt
```

### Step 3: Choose Server Implementation

#### Option A: Secured Server (Recommended)
Uses FastAPI with built-in authentication:
```bash
python server_secure.py
```

**Endpoints:**
- `POST /tools/send-message` - Send chat messages
- `POST /tools/upload-file` - Upload files
- `POST /tools/search` - Search knowledge base
- `GET /health` - Health check
- `GET /tools/info` - Tool information

#### Option B: FastMCP Standard Server
```bash
python server.py
```

Requires MCP-compatible client (Claude Desktop, MCP Inspector).

### Step 4: Verify Server

Check if server is running:
```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "dnext-mcp-server",
  "version": "1.0.0"
}
```

---

## API Key Management

### Generate API Keys

```bash
# Generate key for a colleague (expires in 30 days)
python manage_keys.py generate --name "alice@company.com" --expires 30

# Generate key without expiration
python manage_keys.py generate --name "bob@company.com"
```

Output:
```
============================================================
API Key Generated Successfully!
============================================================
Colleague: alice@company.com
API Key:   dnext_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Share this key with your colleague. They will use it as:
  Authorization: Bearer dnext_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Expiration: 30 days
============================================================
```

### List All Keys

```bash
python manage_keys.py list
```

Shows all active keys with usage stats:
```
============================================================
Active API Keys
============================================================

1. alice@company.com
   Created: 2024-01-15T10:30:45.123456
   Expires: 2024-02-14T10:30:45.123456
   Last Used: 2024-01-15T11:05:12.654321
   Usage Count: 42
   Status: Active

2. bob@company.com
   Created: 2024-01-10T09:15:30.654321
   Expires: Never
   Last Used: 2024-01-15T14:20:33.987654
   Usage Count: 128
   Status: Active

============================================================
```

### Revoke API Keys

```bash
python manage_keys.py revoke --key "dnext_xxxxxxxxxxxxx"
```

Once revoked, the key cannot be used to authenticate.

---

## Authentication

### Request Format

All API requests must include the API key in the `Authorization` header:

```
Authorization: Bearer dnext_xxxxxxxxxxxxx
```

### Example cURL Request

```bash
curl -X POST http://localhost:8001/tools/send-message \
  -H "Authorization: Bearer dnext_xxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello chatbot!",
    "session_id": "my_session"
  }'
```

### Error Responses

**Missing API Key:**
```json
{
  "detail": "Invalid or missing API key. Use: Authorization: Bearer <key>"
}
```
Status: 401

**Expired API Key:**
```json
{
  "detail": "Invalid or missing API key. Use: Authorization: Bearer <key>"
}
```
Status: 401

**Revoked API Key:**
```json
{
  "detail": "Invalid or missing API key. Use: Authorization: Bearer <key>"
}
```
Status: 401

---

## Using the Tools

### Tool 1: Send Message

**Endpoint:** `POST /tools/send-message`

**Request:**
```json
{
  "message": "What is DNEXT?",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "status": "success",
  "response": "DNEXT is a comprehensive platform for...",
  "session_id": "optional_session_id",
  "metadata": {
    "chunks_retrieved": 3,
    "response_time_ms": 1250
  }
}
```

**Parameters:**
- `message` (required): The user message to send
- `session_id` (optional): Session identifier for multi-turn conversations

---

### Tool 2: Upload File

**Endpoint:** `POST /tools/upload-file`

**Request:**
```
Content-Type: multipart/form-data

file: <binary file content>
session_id: optional_session_id
```

**Supported File Types:**
- `.pdf` - PDF documents
- `.jpg`, `.jpeg` - JPEG images
- `.png` - PNG images

**Response:**
```json
{
  "status": "success",
  "file_name": "guide.pdf",
  "message": "File 'guide.pdf' uploaded and processed successfully",
  "details": {
    "chunks_created": 15,
    "processing_time_ms": 3200
  }
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8001/tools/upload-file \
  -H "Authorization: Bearer dnext_xxxxxxxxxxxxx" \
  -F "file=@/path/to/document.pdf" \
  -F "session_id=my_session"
```

---

### Tool 3: Search Knowledge Base

**Endpoint:** `POST /tools/search`

**Request:**
```json
{
  "query": "How to reset password?",
  "limit": 5
}
```

**Response:**
```json
{
  "status": "success",
  "query": "How to reset password?",
  "results": [
    {
      "chunk": "To reset your password, go to Settings > Account Security...",
      "source": "user_guide.pdf",
      "relevance_score": 0.96,
      "metadata": {}
    }
  ],
  "total_results": 1
}
```

**Parameters:**
- `query` (required): Search query
- `limit` (optional): Max results to return (1-20, default: 5)

---

## Client Examples

### Python

```python
from examples.client_python import DNEXTMCPClient
import asyncio

async def main():
    client = DNEXTMCPClient(
        server_url="http://localhost:8001",
        api_key="dnext_xxxxxxxxxxxxx"
    )
    
    # Send message
    result = await client.send_message("What is DNEXT?")
    print(result['response'])
    
    # Search knowledge base
    results = await client.search("password reset", limit=5)
    for item in results['results']:
        print(f"Score: {item['relevance_score']}")
        print(f"Text: {item['chunk']}")

asyncio.run(main())
```

**Run Example:**
```bash
cd examples
python client_python.py
```

### TypeScript/JavaScript

```typescript
import DNEXTMCPClient from './client_typescript'

const client = new DNEXTMCPClient(
  'http://localhost:8001',
  'dnext_xxxxxxxxxxxxx'
)

// Send message
const result = await client.sendMessage('What is DNEXT?')
console.log(result.response)

// Search knowledge base
const searchResults = await client.search('password reset', 5)
searchResults.results.forEach(item => {
  console.log(`Score: ${item.relevance_score}`)
  console.log(`Text: ${item.chunk}`)
})
```

**In Browser:**
```html
<script src="client_typescript.js"></script>
<script>
  const client = new DNEXTMCPClient(
    'http://your-domain:8001',
    'dnext_xxxxxxxxxxxxx'
  )
  
  // Use in your app
  client.sendMessage('Hello!')
    .then(result => console.log(result))
</script>
```

---

## Deployment

### Local Development

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: MCP Server
cd backend/mcp
python server_secure.py
```

### Docker Deployment

**Build:**
```bash
docker build -f backend/mcp/Dockerfile -t dnext-mcp:latest .
```

**Run:**
```bash
docker run -p 8001:8001 \
  -e BACKEND_URL=http://backend:8000 \
  -e MCP_PORT=8001 \
  -v mcp-keys:/app/keys \
  dnext-mcp:latest
```

### VPS/Server Deployment

1. Clone repository
2. Install Python 3.8+
3. Install dependencies: `pip install -r backend/mcp/requirements.txt`
4. Configure `.env` file
5. Generate API keys for colleagues
6. Start server: `python backend/mcp/server_secure.py`
7. Expose port 8001 (firewall rules)
8. Use reverse proxy (nginx) for HTTPS

**Nginx Configuration Example:**
```nginx
server {
    listen 443 ssl;
    server_name mcp.your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Authorization $http_authorization;
        proxy_set_header Content-Type $http_content_type;
    }
}
```

---

## Troubleshooting

### "Connection refused"
- Check if backend is running on `http://localhost:8000`
- Check if MCP server is running on `http://localhost:8001`
- Verify `BACKEND_URL` in `.env` file

### "Invalid API Key"
- Verify key format: should start with `dnext_`
- Check Authorization header format: `Bearer dnext_xxxxx`
- Generate new key if needed: `python manage_keys.py generate --name "user@email.com"`
- Check if key has expired

### "File upload failed"
- Verify file format: only `.pdf`, `.jpg`, `.jpeg`, `.png`
- Check file size (should be < 10MB)
- Verify backend `/api/chat/with-files` endpoint is working

### "Search returns no results"
- Check if documents have been uploaded to knowledge base
- Try different search queries
- Verify backend `/api/search` endpoint exists

### CORS Issues (Browser)

If using from browser, add CORS headers to nginx:
```nginx
add_header 'Access-Control-Allow-Origin' '*';
add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type';
```

---

## API Rate Limiting

Currently not implemented, but planned for Phase 2.

---

## Support

For issues or questions, contact your DNEXT administrator or check:
- Server logs: `python server_secure.py` output
- Health check: `curl http://localhost:8001/health`
- Tool info: `curl -H "Authorization: Bearer <key>" http://localhost:8001/tools/info`

