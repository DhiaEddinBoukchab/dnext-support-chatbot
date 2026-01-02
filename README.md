"""
# 🤖 Dnext Customer Support Chatbot

A RAG-based (Retrieval-Augmented Generation) customer support chatbot powered by Groq's LLM and ChromaDB vector database.

## 📋 Features

- 🔍 Semantic search across documentation
- 💬 Natural language interaction
- 📚 Automatic document indexing
- 🎨 Clean Gradio web interface
- 🔄 Live document reindexing
- 📊 Context-aware responses

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API key ([Get one here](https://console.groq.com/keys))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/dnext-support-chatbot.git
cd dnext-support-chatbot
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_actual_key_here
```

5. **Add your documentation**
Place your markdown/text files in the `docs_md/` folder.

6. **Run the application**
```bash
python app.py
```

7. **Access the interface**
Open your browser at: `http://localhost:7860`

## 📁 Project Structure

```
dnext-support-chatbot/
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── requirements.txt     # Python dependencies
├── config.py            # Configuration management
├── app.py              # Main application file
├── docs_md/            # Documentation folder
│   └── sample_guide.md
├── src/                # Source modules
│   ├── __init__.py
│   ├── embeddings.py   # Embedding handling
│   ├── vector_store.py # ChromaDB operations
│   └── llm_handler.py  # Groq LLM interface
└── tests/              # Unit tests
    └── test_basic.py
```

## 🔧 Configuration

Edit `.env` file to customize:

```env
GROQ_API_KEY=your_key_here
DOCS_FOLDER=docs_md
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
GROQ_MODEL=llama3-70b-8192
SERVER_PORT=7860
```

## 📖 Usage

### Adding Documents

1. Add `.md` or `.txt` files to `docs_md/` folder
2. Click "Reindex Documents" in the interface
3. Documents are automatically chunked and embedded

### Asking Questions

Simply type your question in the chat interface. The bot will:
1. Search relevant documentation
2. Generate contextual answers
3. Provide accurate, source-based responses

### Example Questions

- "How do I download a dataset?"
- "What are the authentication steps?"
- "Show me Python code to use the API"
- "How do I reset my password?"

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Code Style

This project follows PEP 8 guidelines. Format code using:

```bash
pip install black
black .
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for fast LLM inference
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Gradio](https://gradio.app/) for the web interface
- [Sentence Transformers](https://www.sbert.net/) for embeddings

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/yourusername/dnext-support-chatbot](https://github.com/yourusername/dnext-support-chatbot)

## 🐛 Known Issues

- Large documents (>10MB) may take time to index
- First run downloads embedding model (~80MB)

## 🗺️ Roadmap

- [ ] Add support for PDF documents
- [ ] Implement conversation history
- [ ] Add authentication
- [ ] Deploy to cloud platform
- [ ] Add analytics dashboard
"""
