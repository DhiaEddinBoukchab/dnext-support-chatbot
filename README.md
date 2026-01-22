# 🤖 DNEXT Support Chatbot

An AI-powered customer support assistant that answers questions based on your documentation. Users chat with the bot, and it provides intelligent responses by searching through your knowledge base.

---

## 📋 Quick Overview

**What it does:**
- Users upload files or take screenshots → AI analyzes them
- Users ask questions → Bot searches documentation and provides answers
- Team can manage users, export conversations, view analytics

**Technology Stack:**
- **Backend**: Python
- **AI Models**: OpenAI (text) + Groq Llama (images)
- **UI**: Gradio web interface
- **Database**: Vector embeddings + SQLite

---

## 🚀 Setup (Quick)

### 1. Install Python & Dependencies
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Create `.env` File
```env
OPENAI_API_KEY=sk-your_key_here
GROQ_API_KEY=gsk-your_key_here
```

### 3. Run the App
```bash
python app.py
```
Open: http://localhost:7860

---

## ✨ Features

### User Features
| Feature | What it does |
|---------|-------------|
| **Chat** | Ask questions, get answers from documentation |
| **Image Analysis** | Upload screenshots, extract text, analyze |
| **Conversation History** | View past conversations |

### Admin Features
| Feature | Command |
|---------|---------|
| **List Users** | `python admin_utils.py list-users` |
| **Create Admin** | `python admin_utils.py create-admin username password` |
| **Export Conversations** | `python admin_utils.py export` |
| **Delete User** | `python admin_utils.py delete-user 15 16` |
| **Block/Unblock User** | `python admin_utils.py block-user 5` |

---

## 📁 Project Structure

```
dnext-support-chatbot/
├── app.py                    # Main application
├── config.py                 # Configuration (API keys, etc)
├── database.py              # Database operations
├── models.py                # Data models
├── admin_utils.py           # Admin commands
├── src/
│   ├── llm_handler.py       # OpenAI text processing
│   ├── vlm_handler.py       # Groq image processing
│   ├── vector_store.py      # Embeddings & search
│   └── embeddings.py        # Vector operations
├── docs_md/                 # Your documentation (add here!)
├── data/                    # Database & vectors (auto-created)
└── requirements.txt         # Python packages
```

---

## 🎯 How to Use

### For End Users
1. Go to http://localhost:7860
2. Log in or create account
3. **Chat**: Type questions
4. **Images**: Upload screenshots (right tab)
5. View conversation history

### For Admins
```bash
# See all users
python admin_utils.py list-users

# Export all conversations to CSV
python admin_utils.py export

# Delete conversations for users 51, 52, 53
python admin_utils.py delete-conversations 51 52 53

# Delete entire users (with conversations)
python admin_utils.py delete-user 15 16

# Show system stats
python admin_utils.py stats
```

---

## 🔄 How It Works (Simple)

```
User Question
    ↓
Search Vector Database → Find relevant docs
    ↓
Send to AI Model (OpenAI/Groq) with context
    ↓
AI generates answer
    ↓
Save to database
    ↓
Show to user
```

---

## 🔑 Environment Variables

| Variable | What it is | Example |
|----------|-----------|---------|
| `OPENAI_API_KEY` | OpenAI API key (text) | sk-xxx |
| `GROQ_API_KEY` | Groq API key (images) | gsk-xxx |
| `OPENAI_MODEL` | Text model | gpt-4.1 |
| `GROQ_VISION_MODEL` | Image model | meta-llama/llama-4-scout-17b-16e-instruct |
| `SERVER_PORT` | Port to run on | 7860 |

---

## 📊 Database

- **SQLite database**: `data/chatbot.db`
- **Tables**: users, conversations, admin_users
- **Auto-created** on first run

---

## 🛠️ Common Tasks

### Add Documentation
1. Add `.md` files to `docs_md/` folder
2. Restart app
3. Bot will index them automatically

### View Logs
```bash
python app.py  # Logs appear in terminal
```

### Check System Health
```bash
python admin_utils.py stats
```

### Backup Data
```bash
# Copy database
cp data/chatbot.db data/chatbot_backup.db

# Export conversations
python admin_utils.py export
```

---

## 🐳 Docker (Optional)

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f
```

---

## 📝 File Reference

| File | Purpose |
|------|---------|
| `app.py` | Main web app |
| `config.py` | Settings |
| `database.py` | Database operations |
| `models.py` | Data structures |
| `admin_utils.py` | Admin commands |
| `src/llm_handler.py` | OpenAI integration |
| `src/vlm_handler.py` | Groq image analysis |

---

## ❓ FAQ

**Q: How do I reset the database?**
A: Delete `data/chatbot.db` and restart the app

**Q: Where do users' conversations go?**
A: Stored in SQLite database at `data/chatbot.db`

**Q: Can I see what the AI sent to users?**
A: Yes, run `python admin_utils.py export` to get a CSV

**Q: How do I add more features?**
A: Edit `app.py` for UI, `src/llm_handler.py` for AI logic

---

## 🎓 For Developers

### Code Architecture
- **Models** (`models.py`): User, Conversation, AdminUser classes
- **Handlers** (`llm_handler.py`, `vlm_handler.py`): AI interfaces
- **Database** (`database.py`): CRUD operations
- **App** (`app.py`): Gradio UI + routing

### Adding a New Feature
1. Add method to handler (e.g., `llm_handler.py`)
2. Add UI button in `app.py`
3. Connect button to method
4. Test

---

## 📧 Support

Need help? Check these files:
- **Setup issues**: `config.py` (check API keys)
- **Database issues**: `database.py`
- **AI issues**: `src/llm_handler.py` or `src/vlm_handler.py`
- **UI issues**: `app.py`
