# MCP Server Simple Setup Checklist

## Files You Need (5 Total)

Copy these 5 files from the repo to your local VSCode project:

```
✓ backend/mcp/server_simple.py           (Main server - 334 lines)
✓ backend/mcp/requirements.txt            (Dependencies)
✓ backend/mcp/SIMPLE_START.md             (Setup guide)
✓ backend/mcp/examples/client_simple_python.py  (Python client)
✓ backend/mcp/examples/curl_examples.sh         (cURL examples)
```

## Setup Steps

### Step 1: Copy Files
- [ ] Copy the 5 files above to your `backend/mcp/` directory
- [ ] Make sure directory structure matches above

### Step 2: Install Dependencies
```bash
cd backend/mcp
pip install -r requirements.txt
```
- [ ] `pip install` completes without errors
- [ ] Check: `pip show fastapi uvicorn httpx`

### Step 3: Start Server
```bash
python server_simple.py
```
- [ ] See: `Application startup complete`
- [ ] See: `[MCP] Server starting on port 8001`

### Step 4: Test Health
```bash
curl http://localhost:8001/health
```
- [ ] Returns: `{"status":"ok","service":"dnext-mcp-server",...}`

### Step 5: Test Send Message
```bash
curl -X POST http://localhost:8001/tools/send-message \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```
- [ ] Returns JSON response with `"status":"success"`

## Done!

You now have MCP server running with:
- ✓ No authentication required
- ✓ 3 tools available
- ✓ Ready for colleagues to use

## Share with Colleagues

Send them:
1. **Server URL**: `http://your-domain:8001`
2. **Documentation**: `backend/mcp/SIMPLE_START.md`
3. **Client example**: `backend/mcp/examples/client_simple_python.py`

## Quick Usage

### Python Client
```python
from examples.client_simple_python import SimpleMCPClientSync

client = SimpleMCPClientSync("http://localhost:8001")
response = client.send_message("What is DNEXT?")
print(response['response'])
```

### cURL
```bash
curl -X POST http://localhost:8001/tools/send-message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### JavaScript
```javascript
const res = await fetch('http://localhost:8001/tools/send-message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello!' })
});
console.log(await res.json());
```

## Tools Available

1. **Send Message** - `POST /tools/send-message`
2. **Upload File** - `POST /tools/upload-file`
3. **Search KB** - `POST /tools/search`
4. **Get Info** - `GET /tools/info`
5. **Health** - `GET /health`

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 8001 in use | `export MCP_PORT=8002` then start |
| Backend not found | Make sure FastAPI backend is running |
| Import errors | `pip install -r requirements.txt` |
| cURL not found | Use Python client instead |

## Environment Variables (Optional)

```bash
# Default backend URL
export BACKEND_URL=http://localhost:8000

# Change port (default 8001)
export MCP_PORT=8001

# Then start:
python server_simple.py
```

## That's All!

You have everything needed. No keys, no auth, just works!
