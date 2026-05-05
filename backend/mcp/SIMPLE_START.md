# MCP Server - Simple Setup (No Authentication)

This is the simplified version of the MCP Server that doesn't require API keys. Perfect for local testing or trusted networks.

## Quick Start (2 minutes)

### Step 1: Install Dependencies
```bash
cd backend/mcp
pip install -r requirements.txt
```

### Step 2: Start the Server
```bash
python server_simple.py
```

You should see:
```
[MCP] Server starting on port 8001
[MCP] Backend URL: http://localhost:8000
[MCP] No authentication enabled - use on trusted networks only
Application startup complete
```

### Step 3: Test It Works
```bash
curl http://localhost:8001/health
```

Should return:
```json
{"status":"ok","service":"dnext-mcp-server","version":"1.0.0"}
```

## Usage

### Option 1: Using Python Client
```python
from examples.client_simple_python import SimpleMCPClient
import asyncio

async def main():
    client = SimpleMCPClient("http://localhost:8001")
    
    # Send message
    response = await client.send_message("What is DNEXT?")
    print(response['response'])
    
    # Search
    results = await client.search_knowledge_base("help")
    print(f"Found {results['total_results']} results")
    
    await client.close()

asyncio.run(main())
```

Or synchronous version:
```python
from examples.client_simple_python import SimpleMCPClientSync

client = SimpleMCPClientSync("http://localhost:8001")
response = client.send_message("Hello!")
print(response['response'])
```

### Option 2: Using cURL
```bash
# Send message
curl -X POST http://localhost:8001/tools/send-message \
  -H "Content-Type: application/json" \
  -d '{"message": "What is DNEXT?"}'

# Search
curl -X POST http://localhost:8001/tools/search \
  -H "Content-Type: application/json" \
  -d '{"query": "DNEXT features", "limit": 5}'

# Upload file
curl -X POST http://localhost:8001/tools/upload-file \
  -F "file=@document.pdf"
```

### Option 3: Using JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:8001/tools/send-message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello!' })
});

const data = await response.json();
console.log(data.response);
```

## Available Tools

### 1. Send Message
- **Endpoint**: `POST /tools/send-message`
- **No auth needed**
- **Parameters**:
  - `message` (string, required): The message to send
  - `session_id` (string, optional): For conversation continuity

**Example**:
```bash
curl -X POST http://localhost:8001/tools/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What can you help me with?",
    "session_id": "user-123"
  }'
```

### 2. Upload File
- **Endpoint**: `POST /tools/upload-file`
- **No auth needed**
- **Supported formats**: PDF, JPG, PNG
- **Parameters**:
  - `file` (file, required): PDF or image file
  - `session_id` (string, optional): Session ID

**Example**:
```bash
curl -X POST http://localhost:8001/tools/upload-file \
  -F "file=@document.pdf" \
  -F "session_id=user-123"
```

### 3. Search Knowledge Base
- **Endpoint**: `POST /tools/search`
- **No auth needed**
- **Parameters**:
  - `query` (string, required): What to search for
  - `limit` (integer, optional, default=5): Max results

**Example**:
```bash
curl -X POST http://localhost:8001/tools/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "DNEXT features",
    "limit": 10
  }'
```

### 4. Get Tools Info
- **Endpoint**: `GET /tools/info`
- **Returns**: List of available tools and their parameters

### 5. Health Check
- **Endpoint**: `GET /health`
- **Returns**: Server status

## Run Examples

### Python Examples
```bash
# Async example
python examples/client_simple_python.py

# Or use the synchronous wrapper
python -c "
from examples.client_simple_python import SimpleMCPClientSync
client = SimpleMCPClientSync()
print(client.health_check())
"
```

### cURL Examples
```bash
# Run all examples
bash examples/curl_examples.sh
```

## Configuration

Set environment variables to customize:

```bash
# Change backend URL (if not at localhost:8000)
export BACKEND_URL=http://your-backend:8000

# Change MCP server port (default 8001)
export MCP_PORT=8001

# Then start server
python server_simple.py
```

## Testing

### Test Send Message
```bash
curl -X POST http://localhost:8001/tools/send-message \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

Response:
```json
{
  "status": "success",
  "response": "...",
  "session_id": "mcp-session",
  "metadata": {...}
}
```

### Test Search
```bash
curl -X POST http://localhost:8001/tools/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

Response:
```json
{
  "status": "success",
  "query": "test",
  "results": [...],
  "total_results": 0
}
```

## Sharing with Colleagues

Since there's no authentication, just share:
1. **Server URL**: `http://your-domain:8001`
2. **Simple Python example**: Send them `examples/client_simple_python.py`
3. **cURL example**: Show them `examples/curl_examples.sh`

They can start using it immediately!

## Limitations (No Auth)

This version has no authentication. Use it only if:
- ✓ All colleagues are on same trusted network
- ✓ Server is behind firewall
- ✓ No sensitive data exposed via API
- ✓ Testing/development only

For production with remote access, use `server_secure.py` with API keys.

## Troubleshooting

### Server won't start
```bash
# Make sure backend is running
curl http://localhost:8000/api/health

# Check port isn't in use
lsof -i :8001

# Kill existing process if needed
kill -9 $(lsof -t -i:8001)
```

### Backend connection error
- Verify `BACKEND_URL` is correct
- Check backend is running: `curl http://localhost:8000/api/health`
- Default is `http://localhost:8000`

### File upload fails
- Only PDF, JPG, PNG supported
- Check file exists and is readable
- Verify content type is correct

## Files Included

- `server_simple.py` - Main MCP server (no auth)
- `requirements.txt` - Python dependencies
- `examples/client_simple_python.py` - Python client library
- `examples/curl_examples.sh` - cURL examples
- `SIMPLE_START.md` - This file

## Next Steps

1. ✓ Start server: `python server_simple.py`
2. ✓ Test: `curl http://localhost:8001/health`
3. ✓ Use: Pick Python, cURL, or JavaScript client
4. ✓ Share: Give colleagues the server URL

That's it! No keys to manage, simple and straightforward.
