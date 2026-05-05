# Split Instructions: You vs Colleagues

---

## YOUR SIDE (Server Owner)

### What You Do:

**1. Make sure backend is running:**
```bash
cd backend
python main.py
# Wait for: "Application startup complete"
```

**2. Start MCP server in new terminal:**
```bash
cd backend/mcp
pip install -r requirements.txt  # Only first time
python server_simple.py
# Should show: "[MCP] Server running on http://0.0.0.0:8001"
```

**3. Test it works:**
```bash
curl http://localhost:8001/health
# Should return: {"status": "ok", ...}
```

**4. Get your server URL:**
- Local: `http://localhost:8001` (testing only)
- Network: `http://192.168.1.100:8001` (get IP from `ipconfig` or `ifconfig`)
- Cloud: `http://your-domain.com:8001`

**5. Share with colleagues:**
- Send them the server URL
- Send them the file: `/backend/mcp/COLLEAGUE_SETUP.md`
- Tell them to pick their preferred method (Python, cURL, JavaScript, Postman)

**That's it!** Keep those two terminals running and you're done.

---

## COLLEAGUE SIDE (User)

### What Colleagues Do:

They get ONE URL from you and pick ONE method:

**Method 1: Python (Recommended)**
```python
pip install requests
# Create script with the code from COLLEAGUE_SETUP.md
python script.py
```

**Method 2: cURL (Command line)**
```bash
curl -X POST http://YOUR-SERVER:8001/tools/send-message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

**Method 3: JavaScript (Node.js)**
```bash
npm install axios
# Create script with code from COLLEAGUE_SETUP.md
node script.js
```

**Method 4: Postman (GUI)**
- Download Postman
- Create POST request to: `http://YOUR-SERVER:8001/tools/send-message`
- Add JSON body and click Send

---

## One-Page Reference

### YOU:
```
Terminal 1: cd backend && python main.py
Terminal 2: cd backend/mcp && python server_simple.py
Share URL with colleagues → Done!
```

### COLLEAGUES:
```
Pick method (Python/cURL/JS/Postman)
Use the URL you provided
Start chatting → Done!
```

---

## Files to Share

Send to colleagues:
- `COLLEAGUE_SETUP.md` - Complete instructions
- Their preferred example:
  - Python: `/backend/mcp/examples/client_simple_python.py`
  - cURL: `/backend/mcp/examples/curl_examples.sh`
  - JavaScript: Code in COLLEAGUE_SETUP.md

---

## Quick Troubleshooting

| Issue | You | Colleague |
|-------|-----|-----------|
| "Port 8001 in use" | Kill process, restart | Contact you |
| "Connection refused" | Check if running | Ask for correct URL |
| "Cannot reach server" | Check firewall, IP | Check URL format |
| "Server error" | Check backend running | Ask you to check backend |

---

## Files You Have

Already in your repo:
```
backend/mcp/
├── server_simple.py              ✅ Main MCP server
├── requirements.txt              ✅ Dependencies
├── SIMPLE_START.md               ✅ Detailed guide
├── examples/
│   ├── client_simple_python.py   ✅ Python example
│   └── curl_examples.sh          ✅ cURL examples
```

New files created for clarity:
```
YOUR_SETUP.md                      ← Read this (you)
COLLEAGUE_SETUP.md                 ← Send to colleagues
SPLIT_INSTRUCTIONS.md              ← This file
```

---

## Summary

### You need to:
1. Run backend (`python main.py`)
2. Run MCP server (`python server_simple.py`)
3. Get the server URL
4. Share URL + COLLEAGUE_SETUP.md

### Colleagues need to:
1. Get the server URL from you
2. Pick their method
3. Follow 3-4 steps
4. Start using

**Everything else is automatic!**
