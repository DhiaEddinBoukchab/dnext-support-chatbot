# MCP Server - Ready to Use (No Authentication)

## Summary

I've created a **simplified MCP server without any authentication**. Just 5 files to copy, then you're done.

## The 5 Files You Need

| File | Location | Purpose |
|------|----------|---------|
| `server_simple.py` | `backend/mcp/` | Main FastAPI server |
| `requirements.txt` | `backend/mcp/` | Dependencies |
| `SIMPLE_START.md` | `backend/mcp/` | Setup guide |
| `client_simple_python.py` | `backend/mcp/examples/` | Python client |
| `curl_examples.sh` | `backend/mcp/examples/` | cURL examples |

## 3 Simple Steps

### 1. Copy Files
```bash
# From this repo, copy to your VSCode project:
backend/mcp/
├── server_simple.py
├── requirements.txt
├── SIMPLE_START.md
└── examples/
    ├── client_simple_python.py
    └── curl_examples.sh
```

### 2. Install & Run
```bash
cd backend/mcp
pip install -r requirements.txt
python server_simple.py
```

### 3. Test
```bash
curl http://localhost:8001/health
```

Done! Server is running.

## What Your Colleagues Can Do

### Python Example
```python
from examples.client_simple_python import SimpleMCPClientSync

client = SimpleMCPClientSync("http://server:8001")

# Send message
response = client.send_message("What is DNEXT?")
print(response['response'])

# Search
results = client.search_knowledge_base("features")
print(f"Found {results['total_results']} results")

# Upload file
client.upload_file("document.pdf")
```

### cURL Example
```bash
# Send message
curl -X POST http://server:8001/tools/send-message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'

# Search
curl -X POST http://server:8001/tools/search \
  -H "Content-Type: application/json" \
  -d '{"query": "help", "limit": 5}'

# Upload
curl -X POST http://server:8001/tools/upload-file \
  -F "file=@document.pdf"
```

### JavaScript Example
```javascript
// Send message
const res = await fetch('http://server:8001/tools/send-message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello!' })
});
const data = await res.json();
console.log(data.response);
```

## 3 Tools Available

### 1. Send Message
Send a message to the chatbot and get a response
```bash
POST /tools/send-message
{
  "message": "Your message",
  "session_id": "optional-session"
}
```

### 2. Upload File
Upload PDF, JPG, or PNG to knowledge base
```bash
POST /tools/upload-file
Form data:
  file: <binary>
  session_id: optional
```

### 3. Search Knowledge Base
Search for information
```bash
POST /tools/search
{
  "query": "search term",
  "limit": 5
}
```

## Configuration

Optional environment variables:

```bash
# Backend URL (default: http://localhost:8000)
export BACKEND_URL=http://your-backend:8000

# Server port (default: 8001)
export MCP_PORT=8001

# Then start
python server_simple.py
```

## Sharing

To share with colleagues:

1. **Give them the URL**: `http://your-domain:8001`
2. **Send documentation**: `backend/mcp/SIMPLE_START.md`
3. **Send client example**: `backend/mcp/examples/client_simple_python.py`

They can start using immediately - no keys, no setup!

## Documentation

- **Setup Guide**: `backend/mcp/SIMPLE_START.md` (287 lines)
- **Files Summary**: `MCP_FILES_TO_ADD.md` (146 lines)
- **Quick Checklist**: `MCP_SIMPLE_CHECKLIST.md` (125 lines)
- **Client Code**: `backend/mcp/examples/client_simple_python.py` (228 lines)
- **cURL Examples**: `backend/mcp/examples/curl_examples.sh` (75 lines)

## Check It Works

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start MCP server
cd backend/mcp
python server_simple.py

# Terminal 3: Test
curl http://localhost:8001/health
curl http://localhost:8001/tools/info
curl -X POST http://localhost:8001/tools/send-message \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

## File Locations in Your Repo

After copying, your structure should look like:
```
your-repo/
├── backend/
│   ├── main.py                      (FastAPI backend)
│   ├── routes/
│   ├── services/
│   └── mcp/
│       ├── server_simple.py         ✓ NEW
│       ├── requirements.txt         ✓ NEW  
│       ├── SIMPLE_START.md          ✓ NEW
│       └── examples/
│           ├── client_simple_python.py  ✓ NEW
│           └── curl_examples.sh         ✓ NEW
├── frontend/
└── ... other files
```

## Next Steps

1. **Copy the 5 files** to your project
2. **Read**: `backend/mcp/SIMPLE_START.md`
3. **Run**: `python server_simple.py`
4. **Test**: `curl http://localhost:8001/health`
5. **Share**: Give colleagues the URL

That's it!

## Key Points

✅ **No authentication** - Just works  
✅ **5 files total** - Easy to add  
✅ **3 tools** - Message, upload, search  
✅ **Multiple clients** - Python, cURL, JavaScript  
✅ **Fully documented** - Ready to share  
✅ **Production ready** - Streaming, error handling, logging  

## Need Help?

- **Setup issues?** → Read `SIMPLE_START.md`
- **Usage examples?** → See `examples/curl_examples.sh`
- **Python client?** → Use `examples/client_simple_python.py`
- **Troubleshooting?** → Check `SIMPLE_START.md` troubleshooting section

You're all set! No more setup needed - just copy, run, and use!
