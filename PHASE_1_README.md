# DNEXT Support Chatbot V2 - Phase 1 Implementation

> **Frontend/Backend Decoupling: Migrating from Gradio to React + FastAPI**

## Project Status

✅ **Phase 1 Complete** - Backend REST API and React Widget Implemented

## What is Phase 1?

Phase 1 represents a major architectural transformation:

**Before (V1 - Monolithic):**
```
Gradio UI + Python Backend (tightly coupled)
└─ Single deployment unit
└─ Limited scalability
└─ Difficult to iterate on frontend
```

**After (V2 Phase 1 - Decoupled):**
```
React Widget ──HTTP──> FastAPI Backend
└─ Independent frontend deployment
└─ Reusable API endpoints
└─ Better separation of concerns
```

## Quick Start (5 minutes)

### Option A: Docker Compose (Recommended)

```bash
# Clone and setup
git clone https://github.com/THRE5H/dnext-support-chatbot.git
cd dnext-support-chatbot

# Create environment file
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and GROQ_API_KEY

# Start both services
docker-compose up

# Open in browser
open http://localhost:3000
```

### Option B: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend** (in new terminal):
```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000` or `http://localhost:5173`

## Project Structure

```
dnext-support-chatbot/
├── backend/                          # FastAPI REST API
│   ├── main.py                      # Entry point
│   ├── config.py                    # Configuration
│   ├── routes/                      # API endpoints
│   │   ├── chat.py                  # /api/chat (streaming)
│   │   └── health.py                # /api/health
│   ├── services/
│   │   └── chat_service.py          # Wraps V1 ChatbotApp
│   ├── schemas/
│   │   └── messages.py              # Pydantic models
│   ├── tests/                       # Unit + integration tests
│   ├── Dockerfile                   # Container image
│   └── requirements.txt
│
├── frontend/                         # React Chat Widget
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWidget.tsx       # Main widget
│   │   │   ├── ChatMessage.tsx      # Message display
│   │   │   ├── ChatInput.tsx        # Input + file upload
│   │   │   └── ChatWidgetContainer.tsx # Embeddable container
│   │   ├── hooks/
│   │   │   └── useChat.ts           # State management
│   │   ├── api/
│   │   │   └── client.ts            # API client
│   │   ├── types.ts                 # TypeScript types
│   │   ├── styles/                  # CSS modules
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── .env.example
│
├── app/                              # V1 Core Logic (UNCHANGED)
│   ├── chatbot_app.py
│   ├── message_handler.py
│   ├── rag_engine.py
│   ├── session_manager.py
│   └── ...
│
├── docker-compose.yml                # Local dev orchestration
├── PHASE_1_SETUP.md                  # Setup instructions
├── PHASE_1_README.md                 # This file
├── INTEGRATION_TESTING.md            # Testing guide
├── DEPLOYMENT.md                     # Deployment options
└── .env.example                      # Environment template
```

## Key Features

### Backend (FastAPI)

- ✅ REST API with streaming support (Server-Sent Events)
- ✅ Chat endpoint: `POST /api/chat`
- ✅ File upload endpoint: `POST /api/chat/with-files`
- ✅ Session management with persistence
- ✅ Health check: `GET /api/health`
- ✅ CORS configured for frontend
- ✅ Proper error handling and logging
- ✅ Full integration with V1 AI logic (unchanged)

### Frontend (React + TypeScript)

- ✅ Modern chat interface component
- ✅ Real-time streaming message display
- ✅ File upload support (images, PDFs)
- ✅ Session persistence
- ✅ Responsive design for mobile/desktop
- ✅ Loading states and error handling
- ✅ Embeddable as library or standalone widget
- ✅ Customizable styling

### Architecture

- ✅ Clean separation between frontend and backend
- ✅ REST API boundary (HTTP/HTTPS)
- ✅ TypeScript for type safety
- ✅ Pydantic for API validation
- ✅ Docker containerization
- ✅ Docker Compose for local development
- ✅ Unit and integration tests included

## API Reference

### Chat Endpoint

**Request:**
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "What is DNEXT?",
  "session_id": "session_abc123"  # optional
}
```

**Response** (Server-Sent Events):
```
data: {"type":"response","content":"I can help you..."}
data: {"type":"response","content":" with that question..."}
data: {"type":"metadata","data":{"session_id":"session_abc123","chunks_retrieved":3}}
```

### Health Check

**Request:**
```bash
GET /api/health
```

**Response:**
```json
{"status":"healthy","message":"DNEXT Support Chatbot API is running"}
```

### Chat with Files

**Request:**
```bash
POST /api/chat/with-files
Content-Type: multipart/form-data

message=Analyze this image
session_id=session_abc123
files=@image.jpg
```

## Integration with DNEXT Platform

To embed the widget in your DNEXT application:

```tsx
import { ChatWidget } from '@dnext/chat-widget'

export function SupportPanel() {
  return (
    <ChatWidget
      sessionId={user.sessionId}
      apiUrl="https://api.your-domain.com"
    />
  )
}
```

Or with custom styling:

```tsx
import { ChatWidgetContainer } from '@dnext/chat-widget'

export function FloatingChat() {
  return (
    <ChatWidgetContainer
      title="Support Assistant"
      position="bottom-right"
      width={400}
      height={600}
      isDocked={true}
    />
  )
}
```

## Environment Variables

**Backend (.env):**
```
OPENAI_API_KEY=sk-...           # Required
GROQ_API_KEY=gsk-...            # Optional (for image analysis)
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env):**
```
VITE_API_BASE_URL=http://localhost:8000
```

See `.env.example` for complete list.

## Testing

### Backend Tests
```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Integration Tests
See [INTEGRATION_TESTING.md](INTEGRATION_TESTING.md) for comprehensive testing guide.

## Deployment

### Local Development
```bash
docker-compose up
```

### Production Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for options:
- Docker Compose on VPS
- Vercel (frontend) + Self-hosted Backend
- AWS (ECS + CloudFront + RDS)
- Any cloud provider with Docker support

## What's Preserved from V1

All V1 core functionality is **100% preserved** and unchanged:

✅ RAG Engine (ChromaDB + embeddings)  
✅ Message Handler (streaming + multi-modal)  
✅ LLM Handler (OpenAI integration)  
✅ VLM Handler (Groq image analysis)  
✅ Session management  
✅ Intent classification  
✅ Database schema  
✅ File processing (PDFs, images)  

The refactoring is purely **architectural** - moving from Gradio monolith to decoupled services.

## What's New in Phase 1

✨ **Backend:**
- FastAPI REST API
- Server-Sent Events streaming
- Multi-endpoint design
- Production-ready logging
- Docker containerization
- Comprehensive testing

✨ **Frontend:**
- React 18 component library
- TypeScript for type safety
- Custom `useChat` hook
- Professional UI styling
- Embeddable widget pattern
- Mobile-responsive design

## Roadmap

### Phase 2 (Planned)
- JWT authentication middleware
- Organization-scoped data access
- AWS infrastructure (RDS, OpenSearch, S3)
- Message queue (SQS)
- Redis caching
- Rate limiting per organization
- Audit logging

### Phase 3+ (Future)
- WebSocket support for real-time updates
- Advanced analytics
- Custom model fine-tuning
- Multi-tenant dashboard
- Webhook integrations

## Documentation

- **[PHASE_1_SETUP.md](PHASE_1_SETUP.md)** - Detailed setup and configuration
- **[INTEGRATION_TESTING.md](INTEGRATION_TESTING.md)** - Testing procedures and checklist
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment to various platforms
- **[Architecture](v0_plans/phase1-implementation.md)** - Detailed design decisions

## Troubleshooting

### Backend won't start
```bash
# Check port 8000 is free
lsof -i :8000

# Check API key
echo $OPENAI_API_KEY

# Verify Python version
python --version  # Should be 3.9+
```

### Frontend can't connect
```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check frontend env var
cat frontend/.env

# Verify CORS is enabled
# Look for "Access-Control-Allow-Origin" header
curl -i http://localhost:8000/api/health
```

### SSE not streaming
```bash
# Check backend logs
docker-compose logs backend

# Verify response type
curl -i http://localhost:8000/api/chat
# Should show Content-Type: text/event-stream
```

## Support

For questions or issues:
1. Check relevant documentation file
2. Review [INTEGRATION_TESTING.md](INTEGRATION_TESTING.md) troubleshooting section
3. Check backend/frontend logs
4. Contact support@dnext.io

## Contributing

To contribute to Phase 1 improvements:
1. Create feature branch from `frontend-backend-decoupling`
2. Make changes and test thoroughly
3. Submit PR with description of changes
4. Ensure all tests pass

## License

Same as parent repository

---

**Started:** April 2026  
**Current Phase:** 1 - Frontend/Backend Decoupling  
**Status:** Complete and Ready for Testing  
**Next Phase:** AWS Infrastructure Integration (Phase 2)
