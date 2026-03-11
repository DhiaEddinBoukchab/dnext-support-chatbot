# Full Conversation History Tracking with RAG Pipeline Visibility

## Overview

This implementation provides **complete conversation tracking** with detailed RAG (Retrieval-Augmented Generation) pipeline visibility. For each conversation, you can now see:

1. **Input Query** - The exact user question
2. **Retrieved Chunks** - All documents retrieved with similarity distances
3. **Metadata** - Document names, sections, and relevance scores
4. **Final Answer** - The AI response generated from the context

## Architecture

### Hybrid Approach

The implementation uses a **hybrid tracking system**:

- **LangSmith** - Cloud-based tracing for production monitoring (already configured with `@traceable` decorators)
- **Local Database** - Retrieval traces stored in SQLite for fast admin dashboard access

## Components

### 1. Database Schema (`database.py`)

New table: `retrieval_traces`

```sql
CREATE TABLE retrieval_traces (
    retrieval_trace_id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    query_input TEXT NOT NULL,
    retrieved_chunks TEXT NOT NULL,  -- JSON array
    final_answer TEXT NOT NULL,
    num_chunks_retrieved INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id) ON DELETE CASCADE
)
```

### 2. Data Model (`models.py`)

New dataclass: `RetrievalTrace`

```python
@dataclass
class RetrievalTrace:
    conversation_id: int
    query_input: str
    retrieved_chunks: str  # JSON format
    final_answer: str
    num_chunks_retrieved: int
    timestamp: datetime
    retrieval_trace_id: Optional[int] = None
```

### 3. Database Methods (`database.py`)

Added three new repository methods:

- `save_retrieval_trace(trace)` - Store a retrieval trace
- `get_retrieval_trace_by_conversation(conversation_id)` - Get trace for a specific conversation
- `get_retrieval_traces_by_session(session_id)` - Get all traces in a session

### 4. Message Processing (`app/message_handler.py`)

Updated both `_handle_text()` and `_handle_files()` methods to:

1. Extract retrieval results (documents, metadata, distances)
2. Format chunk data into structured JSON
3. Save conversation as before
4. Save corresponding retrieval trace to database

### 5. Admin Dashboard (`admin_dashboard/`)

New UI tab: **"🔬 Retrieval Traces"**

#### Features:
- **Search by Session** - Enter a session ID to view all traces in that conversation
- **Detailed View** - Click on any trace to see:
  - Full input query
  - Final AI answer
  - All retrieved chunks with:
    - Text content
    - Similarity distance
    - Source document
    - Section name

## Data Flow

```
User Query
    ↓
Message Handler
    ├─→ RAG Engine (retrieve)
    │   ├─→ Embed query
    │   ├─→ Vector search (Chroma)
    │   └─→ Get results with distances
    │
    ├─→ LLM Handler (generate response)
    │   └─→ LangSmith trace (@traceable)
    │
    ├─→ Save Conversation (DB)
    │
    └─→ Save Retrieval Trace (NEW)
        └─→ Store: query, chunks[], distances, answer
```

## Usage in Admin Dashboard

### Search Traces
1. Open "🔬 Retrieval Traces" tab
2. Enter a session ID
3. Click "Search Traces"
4. View a table of all queries in that session with:
   - Query preview
   - Number of chunks retrieved
   - Answer preview
   - Timestamp

### View Full Details
1. Enter a trace ID in the "Detailed View" section
2. Click "View Full Details"
3. See:
   - Complete input query
   - Complete AI answer
   - All retrieved chunks with metadata and distances

## Retrieved Chunks JSON Format

Each trace stores chunks in this format:

```json
[
  {
    "text": "Full chunk text here...",
    "distance": 0.15,
    "document": "knowledge_base.md",
    "section": "API Documentation"
  },
  {
    "text": "Another chunk...",
    "distance": 0.22,
    "document": "faq.md",
    "section": "Common Issues"
  }
]
```

**Distance Meaning**: Lower = more similar (0.0 = perfect match, higher = less relevant)

## Integration with LangSmith

LangSmith traces are still active via the `@traceable` decorators on:
- `RAGEngine.retrieve()` - Tracks embedding and retrieval
- `RAGEngine.load_documents()` - Tracks document loading
- `MessageHandler.process_stream()` - Tracks full message processing

**Benefit**: LangSmith provides:
- Cloud-based persistence
- Advanced analytics
- Request/response details
- Error tracking
- Cost estimation

## Database Migration

The new table is created automatically on startup via the `_initialize_database()` method in `DatabaseRepository`. If upgrading from an older database, the table will be created with proper indexes.

## Performance Considerations

- **Indexes**: Created on `conversation_id` and `timestamp` for fast queries
- **JSON Storage**: Chunks stored as JSON text for flexibility
- **Cascading Delete**: Traces are automatically deleted when a conversation is deleted
- **Session-based Queries**: Efficient queries using session_id foreign key relationship

## API Reference

### Save a Trace
```python
trace = RetrievalTrace(
    conversation_id=123,
    query_input="What is the API rate limit?",
    retrieved_chunks=json.dumps([...]),
    final_answer="The API rate limit is 1000 requests per hour.",
    num_chunks_retrieved=3,
)
trace_id = db.save_retrieval_trace(trace)
```

### Retrieve a Trace
```python
# Get trace for a specific conversation
trace = db.get_retrieval_trace_by_conversation(conversation_id=123)

# Get all traces in a session
traces = db.get_retrieval_traces_by_session(session_id="session_xyz")
```

## Future Enhancements

1. **Export Traces** - Add CSV/JSON export for offline analysis
2. **Trace Analytics** - Track average chunk retrieval, distance metrics
3. **Query Similarity** - Group similar queries to identify common patterns
4. **Performance Metrics** - Track retrieval time vs. LLM time
5. **Relevance Scoring** - Calculate overall chunk relevance to final answer

## Troubleshooting

### No traces showing in dashboard
1. Verify conversation was "TECHNICAL" type (not "CASUAL")
2. Check that `conversation_id` is being saved correctly
3. Ensure traces are being saved (check database logs)

### Chunks not displaying correctly
1. Verify JSON format in `retrieved_chunks` field
2. Check distance values are numeric (0.0-1.0 range typical)
3. Ensure metadata keys match: "text", "distance", "document", "section"

### Missing distances
If chunk distances are None, vector store may not support distance calculation. Check your vector database configuration (Chroma supports distances by default).

## Summary

This implementation provides **production-ready conversation tracking** with:
- ✅ Full RAG pipeline visibility
- ✅ Local database persistence
- ✅ LangSmith cloud tracing
- ✅ Admin dashboard integration
- ✅ Flexible JSON storage for chunk metadata
- ✅ Automatic database migrations
