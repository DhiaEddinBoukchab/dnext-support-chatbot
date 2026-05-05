# Phase 1: Frontend/Backend Decoupling - Setup Guide

This document covers the setup and deployment of Phase 1 of the DNEXT Support Chatbot V2 evolution.

## Overview

Phase 1 separates the monolithic Gradio application into:
- **Backend**: FastAPI REST API with streaming support
- **Frontend**: React chat widget component

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file from root project
cp ../.env .env

# Ensure environment variables are set
# Required: OPENAI_API_KEY, GROQ_API_KEY (optional)

# Start the FastAPI server
python main.py
```

The backend will start on `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

The frontend will start on `http://localhost:3000`

## Architecture

### Backend (FastAPI)

**Directory Structure:**
```
backend/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration
├── requirements.txt     # Python dependencies
├── routes/
│   ├── chat.py          # POST /api/chat endpoint
│   └── health.py        # GET /api/health
├── services/
│   └── chat_service.py  # Wraps V1 ChatbotApp
└── schemas/
    └── messages.py      # Pydantic models
```

**API Endpoints:**

1. **Chat (Streaming)**
   - `POST /api/chat`
   - Request: `{ "message": "...", "session_id": "..." }`
   - Response: Server-Sent Events stream

2. **Chat with Files**
   - `POST /api/chat/with-files`
   - Request: Multipart form data with files
   - Response: Server-Sent Events stream

3. **Health Check**
   - `GET /api/health`
   - Response: `{ "status": "healthy" }`

4. **Session Management**
   - `GET /api/sessions/{session_id}`
   - `DELETE /api/sessions/{session_id}`

### Frontend (React)

**Directory Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget.tsx        # Main widget
│   │   ├── ChatMessage.tsx       # Message display
│   │   ├── ChatInput.tsx         # Input & file upload
│   │   └── ChatWidgetContainer.tsx # Embeddable container
│   ├── hooks/
│   │   └── useChat.ts            # Chat state management
│   ├── api/
│   │   └── client.ts             # API client
│   ├── types.ts                  # TypeScript types
│   ├── main.tsx                  # Dev entry point
│   └── styles/
│       ├── widget.css            # Widget styles
│       └── container.css         # Container styles
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

**Key Components:**

1. **ChatWidget** - Main interface with message display and input
2. **ChatMessage** - Individual message renderer with attachments
3. **ChatInput** - Message input with file upload support
4. **ChatWidgetContainer** - Embeddable container with header and controls
5. **useChat** - Hook managing message state and streaming

## Testing

### Test the API with curl

```bash
# Health check
curl http://localhost:8000/api/health

# Send a message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "session_id": "session123"}'
```

### Test the Widget

1. Open `http://localhost:3000` in your browser
2. Type a message and send
3. Watch the streaming response appear in real-time

## Integration with DNEXT Platform

To embed the widget in your application:

```tsx
import { ChatWidget } from '@dnext/chat-widget'

export default function Dashboard() {
  return (
    <ChatWidget
      sessionId={userSessionId}
      apiUrl="https://api.your-domain.com"
    />
  )
}
```

Or use the container version:

```tsx
import { ChatWidgetContainer } from '@dnext/chat-widget'

export default function App() {
  return (
    <ChatWidgetContainer
      title="Support Assistant"
      position="bottom-right"
      width={400}
      height={600}
    />
  )
}
```

## Environment Variables

### Backend (.env)

```
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# AI Models
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk-...

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

# Optional: LangSmith Tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=dnext-support-chatbot
```

### Frontend (.env)

```
VITE_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### Backend Issues

**"OPENAI_API_KEY not found"**
- Ensure `.env` file exists in backend directory with valid API key

**"Port 8000 already in use"**
- Change port: `API_PORT=8001 python main.py`

**"Module not found errors"**
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

**"Cannot GET /api/chat"**
- Ensure backend is running on `http://localhost:8000`
- Check `VITE_API_BASE_URL` in `.env`

**"CORS error"**
- Backend CORS is open by default in Phase 1
- For production, set `CORS_ORIGINS` env var properly

## Next Steps (Phase 2)

- JWT authentication middleware
- Organization scoping in retrieval
- AWS infrastructure (RDS, OpenSearch, S3)
- Database migration

## Support

For issues or questions, please refer to the main README.md or contact support@dnext.io
