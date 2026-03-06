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