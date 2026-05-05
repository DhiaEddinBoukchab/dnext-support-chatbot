# MCP Server Setup - For You (Server Owner)

## What You Need to Do

You need to run the MCP server so that Haotian can connect to it remotely.

---

## Prerequisites

- Backend is running: `cd backend && python main.py`
- You have Python 3.8+
- Port 8001 is available

---

## Step 1: Install Dependencies

```bash
cd backend/mcp_spec_server
pip install -r requirements.txt
```

**Expected output**: Dependencies installed without errors

---

## Step 2: Create .env File

Create `.env` in `backend/mcp_spec_server/`:

```
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
BACKEND_URL=http://localhost:8000
```

---

## Step 3: Start the MCP Server

```bash
python http_server.py
```

**Expected output**:
```
[MCP HTTP] Starting server on 0.0.0.0:8001
[MCP HTTP] Endpoint: http://0.0.0.0:8001/mcp
INFO:     Uvicorn running on http://0.0.0.0:8001
```

Keep this terminal open while Haotian uses the server.

---

## Step 4: Test It Works

In a new terminal:

```bash
curl http://localhost:8001/health
```

**Expected response**:
```json
{"status":"ok","service":"dnext-mcp-server"}
```

---

## Step 5: Get Your Server URL

For **Haotian** to connect, provide him with your server URL.

**Local Network** (if you're on same WiFi):
- Get your machine's IP: `ipconfig getifaddr en0` (macOS) or `hostname -I` (Linux)
- URL: `http://<YOUR_IP>:8001/mcp` (e.g., `http://192.168.1.100:8001/mcp`)

**Remote** (Internet):
- Use your public IP or domain
- URL: `http://<YOUR_DOMAIN>:8001/mcp`
- May need firewall/NAT configuration

**Docker/VPS**:
- Use VPS hostname
- URL: `http://<your-vps.com>:8001/mcp`

---

## Step 6: Share with Haotian

Send Haotian:
1. **Server URL**: `http://<YOUR_ADDRESS>:8001/mcp`
2. **File**: `HAOTIAN_INTEGRATION.md` (in this directory)
3. Tell him the tool name: `query_platform_supporting`

---

## Step 7: Keep Running

Just keep the server running in the terminal. When Haotian needs to use it, the server must be active.

---

## Testing the Tool

You can test the tool manually:

```bash
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "query_platform_supporting",
      "arguments": {
        "query": "What is DNEXT platform?"
      }
    }
  }'
```

**Expected response**: JSON with `{"answer": "..."}`

---

## Monitoring

Check logs in the terminal:
- `[MCP HTTP]` logs show what requests are coming in
- `[MCP Tool]` logs show tool execution details
- `[MCP]` general logs

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Port 8001 already in use | Change `MCP_SERVER_PORT` in .env |
| Backend not responding | Check backend is running on port 8000 |
| Dependencies error | Run `pip install --upgrade pip` first |
| Connection timeout | Check firewall allows port 8001 |

---

## Stopping the Server

Press `Ctrl+C` in the terminal running the server.

---

## File Structure

```
backend/mcp_spec_server/
├── http_server.py          ← Run this
├── server.py               ← MCP protocol handler
├── tools.py                ← Tool implementation
├── config.py               ← Configuration
├── requirements.txt        ← Dependencies
├── __init__.py
├── YOUR_SETUP.md           ← This file
└── HAOTIAN_INTEGRATION.md  ← For Haotian
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_HOST` | `0.0.0.0` | Listen on all interfaces |
| `MCP_SERVER_PORT` | `8001` | Server port |
| `BACKEND_URL` | `http://localhost:8000` | DNEXT backend URL |

---

**You're all set! Keep the server running and share the URL with Haotian.**
