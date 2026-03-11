# Retrieval Traces - Full RAG Pipeline Visibility

## Overview

The Retrieval Traces system provides complete observability into the RAG (Retrieval-Augmented Generation) pipeline for every conversation. It tracks the full pipeline from user query through chunk retrieval to final LLM response.

## Data Model

### Database Schema

```
retrieval_traces TABLE:
├── retrieval_trace_id (PK)
├── conversation_id (FK) → conversations.conversation_id
├── query_input (TEXT) - User's original query
├── retrieved_chunks (JSON) - Array of chunks with distances
├── final_answer (TEXT) - LLM's final response
├── num_chunks_retrieved (INT) - Count of retrieved chunks
└── timestamp (DATETIME)

INNER JOIN:
conversations
├── conversation_id (PK)
├── user_id (FK) → users.user_id
├── session_id (FK) → sessions
├── message (TEXT) - User message
├── response (TEXT) - Assistant response
├── conversation_type (TECHNICAL|CASUAL)
├── response_time_ms (INT)
└── timestamp (DATETIME)

users
├── user_id (PK)
├── email (UNIQUE)
├── full_name
└── created_at (DATETIME)
```

## How Traces Are Created

### 1. Message Processing Flow

```
User Message
    ↓
Message Handler (_handle_text or _handle_files)
    ↓
Hybrid Retrieval (retrieve_hybrid)
    ├─ Semantic Search (Vector DB)
    ├─ BM25 Keyword Search
    └─ Merge & Filter Results
    ↓
LLM Generation (generate_response_stream)
    ↓
Save Conversation
    ├─ conversation_id generated
    └─ user_id, session_id recorded
    ↓
Save Retrieval Trace
    ├─ Links to conversation_id
    ├─ Captures query_input
    ├─ Captures retrieved_chunks (with distances)
    ├─ Captures final_answer
    └─ Records num_chunks_retrieved
```

### 2. Retrieved Chunks Structure

Each chunk in `retrieved_chunks` contains:

```json
[
  {
    "text": "Full chunk text content",
    "distance": 0.25,
    "document": "document_name.md",
    "section": "Section Header"
  },
  {
    "text": "Another chunk...",
    "distance": 0.42,
    "document": "other_document.md",
    "section": "Subsection"
  }
]
```

**Distance Metrics:**
- `0.0 - 0.3` → Excellent match (🟢)
- `0.3 - 0.6` → Good match (🟡)
- `0.6 - 1.0` → Fair match (🔴)

## Admin Dashboard Interface

### Access Retrieval Traces Tab

Navigate to **"🔬 Retrieval Traces"** tab in the admin dashboard.

### Search Filters

#### 1. View All
Shows the most recent 100 retrieval traces across all users and sessions.

**Best for:** Monitoring overall system performance, identifying patterns in retrieval quality.

#### 2. By Session ID
Search traces for a specific conversation session.

**Use case:**
```
User starts a chat → System generates session_id (UUID)
All messages in that chat share the same session_id
Enter session_id to see all traces for that conversation
```

**Example:** `550e8400-e29b-41d4-a716-446655440000`

#### 3. By User Email
Search all traces for a specific user.

**Use case:**
```
User logs in with email: user@example.com
All their conversations (across multiple sessions) are tracked
Enter email to see all their retrieval traces
```

**Example:** `john.doe@company.com`

#### 4. By Conversation ID
Search a specific conversation (one message pair).

**Use case:**
```
One conversation_id = One Q&A pair
Useful for debugging specific interactions
```

**Example:** Enter conversation ID `12345`

### Detailed View - Full RAG Pipeline

For each trace, the detailed view shows:

#### Conversation Metadata
- **Conversation ID** - Unique identifier for this Q&A pair
- **User** - Full name and email of the user
- **Session ID** - Which conversation session this belongs to
- **Type** - TECHNICAL or CASUAL
- **Response Time (ms)** - How long LLM took to generate response
- **Timestamp** - When this interaction occurred

#### Query and Answer
- **Input Query** - Exact user question that triggered retrieval
- **Final Answer** - Complete LLM response

#### Retrieved Chunks - Full Pipeline Visibility
For each chunk retrieved:
- **Chunk Number** - Order of relevance
- **Document** - Source document name
- **Section** - Section within document
- **Distance** - Similarity score (0.0-1.0)
  - Indicates how relevant the chunk is to the query
  - Lower = more relevant
  - Color-coded for quick assessment

#### Chunk Text
Full text content of each retrieved chunk.

## Key Relationships

### Session → Conversations → Traces

```
Session (one user's conversation)
├── Conversation 1 (user message 1)
│   └── Retrieval Trace 1 (chunks retrieved for message 1)
├── Conversation 2 (user message 2)
│   └── Retrieval Trace 2 (chunks retrieved for message 2)
└── Conversation N (user message N)
    └── Retrieval Trace N (chunks retrieved for message N)
```

### User → Sessions → Traces

```
User (user@example.com)
├── Session 1 (chat from today)
│   ├── Conversation 1 → Trace 1
│   ├── Conversation 2 → Trace 2
│   └── Conversation 3 → Trace 3
└── Session 2 (chat from yesterday)
    ├── Conversation 4 → Trace 4
    ├── Conversation 5 → Trace 5
    └── Conversation 6 → Trace 6
```

## Database Query Methods

### Traces by Session
```python
traces = db.get_retrieval_traces_by_session(session_id)
# Returns: List[RetrievalTrace] for a specific conversation
```

### Traces by User
```python
traces = db.get_retrieval_traces_by_user(user_id, limit=100)
# Returns: List[dict] with user details for all user's traces
```

### Trace with Full Context
```python
trace_data = db.get_retrieval_trace_with_conversation(trace_id)
# Returns: dict with trace + conversation + user metadata
```

### All Traces (Admin)
```python
traces = db.get_all_retrieval_traces(limit=100)
# Returns: List[dict] of most recent traces across all users
```

## Practical Examples

### Example 1: Debugging Poor Response Quality

1. User complains about answer quality
2. Get their email: `alice@company.com`
3. Filter by "User Email" → Enter `alice@company.com`
4. View traces for their messages
5. Check retrieved chunks:
   - If distance > 0.6: Retrieval quality is poor → Adjust hybrid search weights
   - If chunks are irrelevant: Knowledge base might need updates
   - If answer is poor but chunks are good: LLM prompt needs improvement

### Example 2: Analyzing a Specific Session

1. User reports a specific chat session had issues
2. Get session ID from chat URL or logs
3. Filter by "Session ID" → Enter session ID
4. View all Q&A pairs in that session
5. Compare traces:
   - Which queries retrieved good chunks?
   - Which retrieved poor chunks?
   - Pattern analysis

### Example 3: Performance Monitoring

1. View All → Shows last 100 traces
2. Monitor:
   - Average num_chunks_retrieved
   - Distribution of distance scores
   - Response times
   - Which users have most queries

## Interpreting Distance Scores

### Perfect Match (0.0 - 0.2)
```
Query: "How to reset password?"
Chunk: "To reset your password, go to Settings → Account → Reset Password"
Distance: 0.15
Assessment: ✅ Excellent - Direct answer to question
```

### Good Match (0.2 - 0.5)
```
Query: "User account locked"
Chunk: "If you enter wrong password 5 times, your account is locked for 24 hours"
Distance: 0.35
Assessment: ✅ Good - Related information that helps answer question
```

### Acceptable Match (0.5 - 0.7)
```
Query: "Payment methods"
Chunk: "We accept credit cards, debit cards, and PayPal for secure transactions"
Distance: 0.55
Assessment: ⚠️ Fair - Somewhat relevant but not perfect match
```

### Poor Match (> 0.7)
```
Query: "API documentation"
Chunk: "Welcome to our company homepage with news and updates"
Distance: 0.85
Assessment: ❌ Poor - Irrelevant to query
```

## Performance Tuning

Use retrieval traces to optimize your RAG system:

### High Distance Scores (Many poor matches)?
- **Root Cause:** Knowledge base doesn't contain relevant information
- **Solution:** Update documents with more relevant content

### Low Chunk Count Retrieved?
- **Root Cause:** Distance threshold too strict
- **Solution:** Adjust `distance_threshold` in `RetrievalConfig`

### Wrong Chunks Retrieved?
- **Root Cause:** Hybrid search weights need adjustment
- **Solution:** Increase `keyword_weight` for exact phrase queries
- **Solution:** Increase `semantic_weight` for conceptual queries

### Inconsistent Results?
- **Root Cause:** Documents might have duplicate content
- **Solution:** Deduplicate knowledge base using chunk hashes

## LangSmith Integration

Traces are also logged to LangSmith (if configured) via `@traceable` decorators on:
- `rag_engine.retrieve_hybrid()` - Full retrieval pipeline
- Message handlers - Complete request-response

This provides cloud-based monitoring alongside local database tracking.

## Summary

The Retrieval Traces system provides:
- ✅ Full visibility into every RAG query
- ✅ User and session-based filtering
- ✅ Distance metrics for quality assessment
- ✅ Complete conversation context
- ✅ Performance monitoring tools
- ✅ LangSmith cloud integration

Use it to debug, monitor, and optimize your chatbot's retrieval quality!
