# What YOU Need to Do (Server Owner)

## Overview
You own the DNEXT chatbot with the MCP server. Your job is to:
1. Set up the MCP server on your machine/server
2. Share the server URL with colleagues
3. Maintain the server

---

## Step 1: Copy Files to Your Project

From the repo, you already have these files:
```
backend/mcp/
├── server_simple.py
├── requirements.txt
├── SIMPLE_START.md
├── examples/
│   ├── client_simple_python.py
│   └── curl_examples.sh
```

These are already in your VSCode. **No action needed** - they're already there.

---

## Step 2: Make Sure Backend is Running

Before starting MCP server, ensure your main chatbot backend is running:

```bash
# Terminal 1 - Backend (runs on port 8000)
cd backend
python main.py
```

Wait until you see: `Application startup complete`

---

## Step 3: Start the MCP Server

```bash
# Terminal 2 - MCP Server (runs on port 8001)
cd backend/mcp
pip install -r requirements.txt  # Only first time
python server_simple.py
```

You should see:
```
[MCP] Initializing tools...
[MCP] Starting simple MCP server
[MCP] Server running on http://0.0.0.0:8001
[MCP] Available tools: send_message, upload_file, search_knowledge_base
```

---

## Step 4: Test It Works

In a **new Terminal 3**:

```bash
# Test health check
curl http://localhost:8001/health
```

Should return:
```json
{"status": "ok", "version": "1.0.0", "timestamp": "..."}
```

---

## Step 5: Get Your Server URL

Where is your server running? Find your IP address:

**Option A: Local Network** (colleagues on same WiFi)
- Get your local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- Example: `http://192.168.1.100:8001`

**Option B: Cloud Server** (colleagues anywhere)
- Example: `http://your-domain.com:8001`
- Example: `http://34.56.78.90:8001`

**Option C: Development** (testing)
- Just use: `http://localhost:8001`

---

## Step 6: Share with Colleagues

Send your colleagues these:

1. **Server URL**: `http://your-server:8001`
2. **File**: `/backend/mcp/COLLEAGUE_SETUP.md`
3. **Example**: `/backend/mcp/examples/client_simple_python.py`

---

## Step 7: Monitor Your Server

Keep these things running:

```
Terminal 1: Backend API (port 8000)
└─ cd backend && python main.py

Terminal 2: MCP Server (port 8001)
└─ cd backend/mcp && python server_simple.py

Terminal 3: Frontend (port 3000) - optional
└─ cd frontend && npm run dev
```

---

## Troubleshooting

### "Port 8001 already in use"
```bash
# Find what's using port 8001
lsof -i :8001  # Mac/Linux
netstat -ano | findstr :8001  # Windows

# Kill it and restart
python server_simple.py
```

### "Cannot connect to backend"
- Make sure `python main.py` is running in `backend/` folder
- Check that backend is on `http://localhost:8000`
- MCP server needs backend to be running

### "Colleague cannot reach my server"
- Check firewall allows port 8001
- Check you gave correct IP address (not `localhost` for remote)
- Make sure both machines on same network or use domain name

---

## That's It!

Your setup is complete. You now have:

✅ Backend API running on port 8000  
✅ MCP Server running on port 8001  
✅ Colleagues can connect with the URL you provide  

Just keep terminals running and share the server URL!
