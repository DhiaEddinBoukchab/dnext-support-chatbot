# MCP Server - Files to Add (No Authentication)

Here are the ONLY files you need to add to your repository for the simplified MCP server.

## File Structure

Add these files to your `backend/mcp/` directory:

```
backend/mcp/
├── server_simple.py                    # Main MCP server (NO AUTH)
├── requirements.txt                    # Python dependencies
├── SIMPLE_START.md                     # Setup & usage guide
└── examples/
    ├── client_simple_python.py         # Python client
    └── curl_examples.sh                # cURL examples
```

## Files to Add (Copy These)

### 1. `backend/mcp/server_simple.py`
- **What it does**: Main FastAPI server exposing 3 tools
- **Size**: ~334 lines
- **No authentication required**
- **Port**: 8001 (configurable)

### 2. `backend/mcp/requirements.txt`
Already created. Contains:
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6
```

### 3. `backend/mcp/SIMPLE_START.md`
- Quick start guide
- Usage examples (Python, cURL, JavaScript)
- Troubleshooting

### 4. `backend/mcp/examples/client_simple_python.py`
- Python async client
- Synchronous wrapper included
- Ready to use examples

### 5. `backend/mcp/examples/curl_examples.sh`
- cURL command examples
- Copy-paste ready
- Demonstrates all 3 tools

## Which Files to IGNORE

❌ **DO NOT** add these (they require authentication):
- `auth.py` - API key validation
- `manage_keys.py` - Key management CLI
- `server_secure.py` - Secured version
- `COLLEAGUE_QUICK_START.md` - For auth version

## Quick Copy Instructions

### From this repo to yours:

```bash
# Copy server
cp backend/mcp/server_simple.py your-repo/backend/mcp/

# Copy requirements (already has MCP deps)
cp backend/mcp/requirements.txt your-repo/backend/mcp/

# Copy documentation
cp backend/mcp/SIMPLE_START.md your-repo/backend/mcp/

# Copy examples
cp -r backend/mcp/examples/ your-repo/backend/mcp/
```

Or manually copy the 5 files above.

## What You Get

✅ **No authentication** - Just start and use
✅ **3 tools**:
   - Send message to chatbot (streaming)
   - Upload PDF/images for knowledge base
   - Search knowledge base

✅ **Multiple client options**:
   - Python (async & sync)
   - cURL
   - JavaScript/Node.js

✅ **Easy sharing** - Just give colleagues the server URL

## Setup Instructions

### 1. Copy the 5 files above

### 2. Install dependencies
```bash
cd backend/mcp
pip install -r requirements.txt
```

### 3. Start server
```bash
python server_simple.py
```

### 4. Test it
```bash
curl http://localhost:8001/health
```

### 5. Use it
See `SIMPLE_START.md` for Python, cURL, and JavaScript examples

## That's It!

No API keys, no authentication, no configuration.

Just:
1. Add 5 files
2. Install dependencies
3. Start server
4. Use the tools

Done!

## Questions?

- **How to use?** → See `SIMPLE_START.md`
- **Client examples?** → See `examples/client_simple_python.py`
- **cURL usage?** → Run `bash examples/curl_examples.sh`
- **Configuration?** → Set `BACKEND_URL` and `MCP_PORT` env vars

## Security Note

This version has **NO authentication**. Use only if:
- ✓ All users on trusted network
- ✓ Server behind firewall
- ✓ No sensitive data exposed
- ✓ Testing/development only

For production with remote users, use the authenticated version instead.
