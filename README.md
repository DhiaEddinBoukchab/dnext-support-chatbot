# Customer AI Assistant - Prototype

A client-side chatbot assistant built for customer support. This is a working prototype that uses modern AI techniques to provide intelligent responses.

## What it does

- **Smart Answers**: Uses retrieval-augmented generation (RAG) to find and combine information from your documents
- **Visual Understanding**: Can analyze images and documents with vision-language models
- **Document Search**: Automatically indexes your knowledge base and finds relevant information
- **Multi-format Support**: Handles text files, PDFs, and images
- **Chat Memory**: Remembers conversation history per session
- **User Management**: Simple authentication system with admin controls


## Quick Start

**Live Demo**: https://dnext-support-chatbot-production.up.railway.app/


## Tech Stack

- **Frontend**: Gradio web interface with modern dark/light theme toggle
- **AI Models**: OpenAI GPT-4.1 for text, Groq Llama-4 for vision tasks
- **Vector Database**: ChromaDB for document embeddings and semantic search
- **Database**: SQLite3 for user data and conversation storage
- **Embeddings**: OpenAI text-embedding-3-large for document indexing
- **Processing**: LangChain for document chunking and retrieval


## Key Features

- **Document Indexing**: Automatically processes and indexes your knowledge base
- **Semantic Search**: Finds relevant information using vector similarity
- **Streaming Responses**: Real-time chat with typing indicators
- **File Uploads**: Support for images, PDFs, and text files during conversations
- **Session Management**: Keeps conversations organized and persistent
- **Admin Dashboard**: Manage users and view system stats

## Project Structure

- `app/` - Main application code
  - `rag_engine.py` - Document indexing and retrieval
  - `message_handler.py` - Chat processing and streaming
  - `session_manager.py` - Conversation management
  - `ui_builder.py` - Gradio interface
- `src/` - Core AI components
  - `llm_handler.py` - Text generation
  - `vlm_handler.py` - Vision-language processing
- `database.py` - SQLite database operations
- `config.py` - Application settings
- `docs_md/` - Our fundamental database containing different sources (emails, documentation)
- `admin_dashboard/` - To track users' conversations

## FastAPI API

The project now also includes a FastAPI service under `api/` for API-based chatbot access alongside the Gradio interface.

Run the API locally:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Main endpoints:

- `GET /health`
- `POST /api/v1/auth/login`
- `POST /api/v1/chat/query`
- `GET /api/v1/chat/sessions`
- `GET /api/v1/chat/sessions/{session_id}`
- `POST /api/v1/knowledge/reindex`

## Docker

Build the container:

```bash
docker build -t dnext-support-chatbot .
```

Run the container:

```bash
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -e JWT_SECRET_KEY=change-me \
  dnext-support-chatbot
```
