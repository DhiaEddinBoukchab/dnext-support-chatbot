# DNEXT v2 Phase 1 - VSCode Quick Start Guide

Step-by-step setup to run the project locally in VSCode.

---

## Prerequisites Check

Before starting, verify you have:
- **Python 3.9+** installed
  - Check: `python --version` or `python3 --version`
- **Node.js 18+** installed
  - Check: `node --version`
- **npm** installed (comes with Node.js)
  - Check: `npm --version`

If anything is missing, install from:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/ (get LTS version)

---

## Step 1: Clone Project & Open in VSCode

```bash
# If not already done
git clone <your-repo-url> dnext-v2
cd dnext-v2

# Open in VSCode
code .
```

**Result:** You should see the project structure in VSCode's File Explorer with:
- `backend/` folder
- `frontend/` folder
- `docs/` and configuration files

---

## Step 2: Get Your API Keys

You'll need OpenAI API key (and optionally Groq).

**For OpenAI:**
1. Go to https://platform.openai.com/api/keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (you'll paste it in Step 4)

**For Groq (Optional):**
1. Go to https://console.groq.com/
2. Create account and generate API key
3. Copy the key

---

## Step 3: Create Environment File

In VSCode, create a `.env` file at the **project root**:

1. Right-click on the root folder (where README.md is)
2. Select "New File"
3. Name it `.env`
4. Paste this content:

```
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# AI Models - PASTE YOUR KEYS HERE
OPENAI_API_KEY=sk-YOUR_KEY_HERE
GROQ_API_KEY=gsk-YOUR_KEY_HERE_OPTIONAL

# Model Selection
OPENAI_MODEL=gpt-4.1
GROQ_VISION_MODEL=meta-llama/llama-4-scout-17b-16e-instruct

# Database & Storage
DATABASE_PATH=data/chatbot.db
CHROMA_DB_PATH=./chroma_db
DOCS_FOLDER=docs_md

# RAG Configuration
CHUNK_SIZE=400
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
```

**Important:** Replace `sk-YOUR_KEY_HERE` with your actual OpenAI key.

---

## Step 4: Setup Backend

### Terminal 1 - Open Backend Terminal in VSCode

```bash
# In VSCode Terminal, navigate to backend
cd backend
```

**If you don't see a terminal:** Press `Ctrl + ~` (backtick) to open it.

### Install Backend Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- fastapi (web framework)
- uvicorn (server)
- openai, groq, langchain (AI libraries)
- chromadb (vector database)
- And all other dependencies

**Wait for it to complete** - This may take 2-5 minutes.

### Start Backend Server

```bash
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

**Success Check:**
- Open browser to http://localhost:8000/api/health
- You should see: `{"status":"healthy"}`

**Keep this terminal open!** The backend must stay running.

---

## Step 5: Setup Frontend

### Terminal 2 - Open New Terminal in VSCode

In VSCode, click the `+` button in the Terminal tab to open a second terminal.

```bash
cd frontend
```

### Install Frontend Dependencies

```bash
npm install
```

This will install:
- React
- Vite
- TypeScript
- And all UI dependencies

**Wait for completion** - This may take 1-3 minutes.

### Start Frontend Dev Server

```bash
npm run dev
```

**Expected Output:**
```
  VITE v5.0.0  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  press h to show help
```

---

## Step 6: Open the App

1. Open your browser
2. Go to **http://localhost:3000**
3. You should see the chat widget!

**Test it out:**
- Type a message: "Hello, how are you?"
- Click Send
- Watch the AI response stream in real-time

---

## Project Structure Overview

```
dnext-v2/
├── backend/                          # Python FastAPI backend
│   ├── main.py                       # Start here - main FastAPI app
│   ├── routes/
│   │   ├── chat.py                   # API endpoint logic
│   │   └── health.py                 # Health check
│   ├── services/
│   │   └── chat_service.py           # Wraps AI logic (V1)
│   ├── schemas/
│   │   └── messages.py               # Data validation
│   ├── requirements.txt              # Python dependencies
│   └── Dockerfile                    # Docker container config
│
├── frontend/                         # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWidget.tsx        # Main chat component
│   │   │   ├── ChatMessage.tsx       # Message display
│   │   │   ├── ChatInput.tsx         # Input field
│   │   │   └── ChatWidgetContainer.tsx
│   │   ├── hooks/
│   │   │   └── useChat.ts            # State management
│   │   ├── api/
│   │   │   └── client.ts             # API calls
│   │   ├── main.tsx                  # React entry point
│   │   └── styles/                   # CSS files
│   ├── index.html                    # HTML template
│   ├── package.json                  # Node dependencies
│   └── vite.config.ts                # Build config
│
├── .env                              # Your API keys (CREATE THIS)
├── PHASE_1_README.md                 # Full documentation
├── PHASE_1_SETUP.md                  # Setup details
└── docker-compose.yml                # Docker setup (optional)
```

---

## Testing the Backend API

### Option 1: Browser Test

Open a new browser tab:

```
http://localhost:8000/api/health
```

Should return: `{"status":"healthy"}`

### Option 2: VSCode REST Client

1. Install extension: "REST Client" by Huachao Mao
2. Create file `test.http` at project root
3. Paste:

```http
### Health Check
GET http://localhost:8000/api/health

### Send Message
POST http://localhost:8000/api/chat
Content-Type: application/json

{
  "message": "What is machine learning?",
  "session_id": "test-session"
}
```

4. Click "Send Request" above each request
5. See response in panel below

---

## Common Issues & Fixes

### ❌ "Port 8000 already in use"

**Solution:** Change port in `.env`:
```
API_PORT=8001
```
Then start backend with: `python main.py`

### ❌ "OPENAI_API_KEY not found"

**Solution:** 
1. Check `.env` file exists in project root
2. Verify key is pasted correctly (starts with `sk-`)
3. Restart backend after changing .env

### ❌ "Cannot connect to backend from frontend"

**Solution:**
1. Make sure backend terminal shows: `Application startup complete`
2. Check frontend `.env` has: `VITE_API_BASE_URL=http://localhost:8000`
3. Both terminals must be running

### ❌ "npm: command not found"

**Solution:** Node.js not installed. Download from https://nodejs.org/

### ❌ "pip: command not found"

**Solution:** Python not installed properly. Use `python3 -m pip` instead:
```bash
python3 -m pip install -r requirements.txt
```

### ❌ "Module not found" errors in backend

**Solution:** Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

---

## VSCode Useful Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Terminal | `Ctrl + ~` |
| New Terminal | Click `+` in Terminal tab |
| Split Terminal | Click split icon or right-click |
| Kill Terminal | Click `X` on terminal |
| Go to File | `Ctrl + P` then type filename |
| Search Project | `Ctrl + Shift + F` |
| Debug Console | `Ctrl + Shift + Y` |

---

## Next: Monitor Logs in VSCode

### Backend Logs
Watch the backend terminal for API requests:
```
INFO:     127.0.0.1:... "POST /api/chat HTTP/1.1" 200 OK
```

### Frontend Logs
1. Open browser DevTools: `F12`
2. Go to "Console" tab
3. Watch for errors or debug messages

---

## What's Working Now

✅ FastAPI backend running on `http://localhost:8000`
✅ React frontend running on `http://localhost:3000`
✅ Chat widget with streaming responses
✅ File upload support (images, PDFs)
✅ Session management
✅ All V1 AI logic preserved

---

## Next Steps

### When Ready for Production:
1. Read `DEPLOYMENT.md` for cloud setup
2. Read `INTEGRATION_TESTING.md` for testing procedures
3. Configure JWT authentication (Phase 2)

### Want to Make Changes?
1. **Backend changes:** Edit files in `backend/`
   - Changes auto-reload with Uvicorn
2. **Frontend changes:** Edit files in `frontend/src/`
   - Changes auto-reload with Vite (see browser refresh)

### Want to Embed in Your App?
See integration examples in `PHASE_1_README.md`

---

## Stopping the Servers

**Terminal 1 (Backend):** Press `Ctrl + C`
**Terminal 2 (Frontend):** Press `Ctrl + C`

---

## Support

If something doesn't work:
1. Check the issue in "Common Issues & Fixes" above
2. Check `.env` file has your API keys
3. Make sure **both terminals** are running
4. Try restarting both servers

For detailed troubleshooting, see `INTEGRATION_TESTING.md`

---

**You're all set! Happy coding! 🚀**
