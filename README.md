<<<<<<< HEAD
# 🤖 Dnext Customer Support Chatbot

A RAG-based (Retrieval-Augmented Generation) intelligent customer support chatbot powered by Groq's LLM, ChromaDB vector database, and Gradio interface.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🔍 **Semantic Search** - Finds relevant information using vector embeddings
- 🧠 **Intelligent Classification** - Automatically detects casual vs technical conversations
- 💬 **Context-Aware Responses** - Provides accurate answers based on your documentation
- 🎨 **Beautiful UI** - Clean Gradio web interface
- 🐳 **Docker Support** - One-command deployment
- 📚 **Easy Document Management** - Simply add markdown files to `docs_md/`

## 🚀 Quick Start

### Option 1: Docker (Recommended)
````bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/dnext-support-chatbot.git
cd dnext-support-chatbot

# 2. Create .env file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 3. Start with Docker
docker-compose up -d

# 4. Open browser
http://localhost:7860
````

### Option 2: Local Python
````bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/dnext-support-chatbot.git
cd dnext-support-chatbot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Run the app
python app.py

# 6. Open browser
http://localhost:7860
````

## 📋 Prerequisites

- **For Docker**: Docker Desktop installed
- **For Local**: Python 3.11 or higher
- **Groq API Key**: Get one at [console.groq.com](https://console.groq.com/keys)

## 🔧 Configuration

Edit `.env` file:
````env
GROQ_API_KEY=your_groq_api_key_here
DOCS_FOLDER=docs_md
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
GROQ_MODEL=llama-3.3-70b-versatile
SERVER_PORT=7860
````

## 📚 Adding Your Documentation

1. Add `.md` or `.txt` files to the `docs_md/` folder
2. Restart the app or click "Reindex Documents" in the UI
3. The chatbot will automatically index and use your documents

**Example document structure:**
````markdown
# Getting Started with Dnext

## Installation
To install Dnext...

## Usage
To use the platform...

## API Documentation
```python
import requests
...
```
````

## 🐳 Docker Commands
````bash
# Start the chatbot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the chatbot
docker-compose down

# Rebuild after code changes
docker-compose build
docker-compose up -d

# Remove everything (including database)
docker-compose down -v
````

## 🏗️ Project Structure
````
dnext-support-chatbot/
├── .dockerignore           # Docker ignore rules
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── config.py              # Application configuration
├── app.py                 # Main application file
├── src/                   # Source code modules
│   ├── __init__.py
│   ├── embeddings.py      # Embedding management
│   ├── vector_store.py    # ChromaDB operations
│   └── llm_handler.py     # Groq LLM interface
├── docs_md/               # Your documentation files
│   └── sample_guide.md    # Example document
└── chroma_db/             # Vector database (auto-created)
````

## 🛠️ How It Works

1. **Document Indexing**: Your markdown files are chunked and converted to vector embeddings
2. **Vector Storage**: Embeddings are stored in ChromaDB for fast semantic search
3. **Query Processing**: User questions are converted to embeddings
4. **Retrieval**: Most relevant document chunks are retrieved
5. **Response Generation**: Groq's LLM generates answers based on retrieved context

## 🔒 Security Notes

- **Never commit `.env`** - It contains your API key
- **Never commit `chroma_db/`** - It's auto-generated
- The `.gitignore` file protects sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - Fast LLM inference
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Gradio](https://gradio.app/) - Web interface
- [Sentence Transformers](https://www.sbert.net/) - Embeddings

## 📧 Support

For issues and questions, please open an issue on GitHub.

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] PDF document support
- [ ] Advanced analytics dashboard
- [ ] User authentication
- [ ] Conversation history
- [ ] Export chat logs

---

Made with ❤️ for better customer support
=======
# DNEXT-AI-Support
>>>>>>> dnext/main
