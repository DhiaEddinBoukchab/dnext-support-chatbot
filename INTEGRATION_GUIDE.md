# DNEXT Support Chatbot - Frontend & Backend Integration Guide

This guide explains how to integrate the modern React frontend with the existing Python Gradio backend.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  React Frontend                          │
│            (Next.js 16 - Port 3000)                     │
│  • Authentication Pages                                  │
│  • Chat Interface                                        │
│  • Modern UI/UX                                          │
│  • Light/Dark Mode                                       │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/REST API
                         ↓
┌─────────────────────────────────────────────────────────┐
│              API Routes (Next.js)                        │
│  • /api/auth/login                                       │
│  • /api/chat/send                                        │
│  • Proxy to Python Backend                              │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/REST API
                         ↓
┌─────────────────────────────────────────────────────────┐
│         Python Backend (Flask/FastAPI)                   │
│            (Port 8000 - New)                            │
│  • Authentication Service                               │
│  • RAG Engine                                            │
│  • Session Management                                    │
│  • Document Processing                                  │
│  • Database Operations                                  │
└─────────────────────────────────────────────────────────┘
```

## Step 1: Setup Python Backend as REST API

Convert the existing Gradio app to expose REST endpoints:

### 1.1 Create `backend/api_server.py`

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.chatbot_app import ChatbotApp
from app.session_manager import SessionManager
from auth_service import authenticate_user
import os

app = Flask(__name__)
CORS(app)

chatbot = ChatbotApp()
session_manager = SessionManager()

# Authentication Endpoint
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    
    if not email or not name:
        return jsonify({'error': 'Email and name required'}), 400
    
    try:
        user = authenticate_user(email, name)
        session_id = session_manager.create_session(user)
        
        return jsonify({
            'user_id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'session_id': session_id
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Chat Endpoint
@app.route('/api/chat/send', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message')
    conversation_id = data.get('conversation_id')
    session_id = request.headers.get('X-Session-ID')
    
    if not message or not session_id:
        return jsonify({'error': 'Message and session required'}), 400
    
    try:
        response = chatbot.process_message(
            message=message,
            conversation_id=conversation_id,
            session_id=session_id
        )
        
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Conversations Endpoint
@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    session_id = request.headers.get('X-Session-ID')
    
    if not session_id:
        return jsonify({'error': 'Session required'}), 401
    
    try:
        conversations = session_manager.get_conversations(session_id)
        return jsonify({'conversations': conversations}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Upload File Endpoint
@app.route('/api/upload', methods=['POST'])
def upload_file():
    session_id = request.headers.get('X-Session-ID')
    file = request.files.get('file')
    
    if not session_id or not file:
        return jsonify({'error': 'Session and file required'}), 400
    
    try:
        result = chatbot.process_document(file, session_id)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = os.getenv('BACKEND_PORT', 8000)
    app.run(debug=True, host='0.0.0.0', port=port)
```

### 1.2 Install Required Dependencies

```bash
pip install flask flask-cors python-dotenv
```

### 1.3 Update `config.py` for Backend

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Server
BACKEND_PORT = int(os.getenv('BACKEND_PORT', 8000))
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///chatbot.db')

# API
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))

# RAG
RAG_MODEL = os.getenv('RAG_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './chroma_db')

# Authentication
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 86400))  # 24 hours
```

### 1.4 Create `backend/.env`

```env
# Server
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000

# Database
DATABASE_URL=sqlite:///chatbot.db

# RAG Configuration
RAG_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DB_PATH=./chroma_db
MAX_FILE_SIZE=10485760

# Authentication
JWT_SECRET=your-super-secret-key-change-this
SESSION_TIMEOUT=86400

# API
API_TIMEOUT=30
```

## Step 2: Update Frontend API Routes

The frontend already has placeholder API routes. Update them to match your backend:

### 2.1 Update `frontend/app/api/auth/login/route.ts`

The existing route is ready, just ensure the backend URL is correct:

```typescript
const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
```

### 2.2 Create Additional API Routes

**Get Conversations** (`frontend/app/api/conversations/route.ts`):

```typescript
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const sessionId = request.headers.get('x-session-id')
    
    if (!sessionId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/conversations`, {
      headers: { 'X-Session-ID': sessionId },
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}
```

## Step 3: Environment Setup

### Frontend (frontend/.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_THEME=system
```

### Backend (backend/.env)

See Section 1.4 above

## Step 4: Running Both Services

### Terminal 1 - Python Backend

```bash
cd /vercel/share/v0-project

# Install dependencies (if not already done)
pip install -r requirements.txt
pip install flask flask-cors

# Run backend
python backend/api_server.py
# Server running on http://localhost:8000
```

### Terminal 2 - React Frontend

```bash
cd /vercel/share/v0-project/frontend

# Install dependencies
npm install

# Run frontend
npm run dev
# App running on http://localhost:3000
```

## Step 5: Testing the Integration

### 1. Test Authentication

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User"}'
```

### 2. Test Chat

```bash
curl -X POST http://localhost:8000/api/chat/send \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <session_id>" \
  -d '{"message": "Hello", "conversation_id": "conv_123"}'
```

### 3. Frontend Testing

1. Open http://localhost:3000
2. Sign in with email and name
3. Send a message
4. Verify response in browser console and UI

## Step 6: Production Deployment

### Deploy Backend

**Using Gunicorn**:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 backend.api_server:app
```

**Using Docker**:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn flask flask-cors

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "backend.api_server:app"]
```

### Deploy Frontend

**Vercel** (Recommended):

```bash
cd frontend
vercel deploy
```

Set environment variables in Vercel:
- `NEXT_PUBLIC_API_URL`: Your backend URL

**Docker**:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

## Important Notes

### CORS Configuration

Ensure your Python backend has CORS properly configured:

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": [os.getenv("FRONTEND_URL", "http://localhost:3000")],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "X-Session-ID"]
    }
})
```

### Session Management

- Frontend stores session in memory (Zustand store)
- Backend validates session on each request
- Sessions expire after 24 hours by default
- Consider implementing refresh tokens for production

### Security Best Practices

1. **HTTPS**: Always use HTTPS in production
2. **API Keys**: Implement API key authentication for sensitive endpoints
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Input Validation**: Validate all inputs on backend
5. **CSRF Protection**: Implement CSRF tokens if needed
6. **Secrets**: Never commit `.env` files with secrets

## Troubleshooting

### CORS Errors

```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution**: Check `flask-cors` is installed and configured correctly

### Connection Refused

```
Error: connect ECONNREFUSED 127.0.0.1:8000
```

**Solution**: Ensure Python backend is running on port 8000

### Session Not Persisting

**Solution**: Sessions are in-memory. For persistence, use database:

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
```

## Architecture Decisions

### Why Next.js API Routes?

- Abstraction layer between frontend and Python backend
- Better error handling and response transformation
- Easy to add middleware (logging, auth, rate limiting)
- Deployment flexibility

### Why Zustand for State?

- Lightweight (~2KB)
- Simple API
- No boilerplate
- Perfect for this use case

### Why Tailwind CSS?

- Utility-first approach
- Excellent dark mode support
- Highly customizable
- Great community

## Next Steps

1. ✅ Create Python REST API
2. ✅ Setup frontend with React
3. Test integration end-to-end
4. Add file upload functionality
5. Implement admin dashboard
6. Deploy to production
7. Monitor and optimize

## Support

For issues or questions, refer to:
- Frontend: `frontend/README.md`
- Backend: Python app documentation
- Integration: This guide

---

Last Updated: 2026-03-05
