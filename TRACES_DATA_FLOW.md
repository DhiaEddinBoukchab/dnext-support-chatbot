# Retrieval Traces - Data Flow & Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Admin Dashboard                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         🔬 Retrieval Traces Tab                          │   │
│  │                                                           │   │
│  │  Filter Mode: [View All] [By Session] [By User] [By ID] │   │
│  │                                                           │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ Results Table                                      │  │   │
│  │  │ Trace ID │ Conv ID │ User │ Query │ Chunks │ Time │  │   │
│  │  │    123   │   456   │email │...   │   5   │14:30 │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                                                           │   │
│  │  ┌─────────────────────────────────────────────────┐     │   │
│  │  │ Detailed View (click Trace ID)                 │     │   │
│  │  │ ┌──────────────────────────────────────────┐   │     │   │
│  │  │ │ Metadata: Conv ID, User, Session, Type  │   │     │   │
│  │  │ ├──────────────────────────────────────────┤   │     │   │
│  │  │ │ Input Query (full)                       │   │     │   │
│  │  │ ├──────────────────────────────────────────┤   │     │   │
│  │  │ │ Final Answer (full)                      │   │     │   │
│  │  │ ├──────────────────────────────────────────┤   │     │   │
│  │  │ │ Retrieved Chunks:                        │   │     │   │
│  │  │ │ Chunk 1: distance=0.25 🟢 [Document.md] │   │     │   │
│  │  │ │ Chunk 2: distance=0.45 🟡 [Other.md]    │   │     │   │
│  │  │ │ Chunk 3: distance=0.72 🔴 [Old.md]      │   │     │   │
│  │  │ └──────────────────────────────────────────┘   │     │   │
│  │  └─────────────────────────────────────────────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
        ↑
        │ Queries via database.py methods
        │
┌─────────────────────────────────────────────────────────────────┐
│                       Database Layer                             │
│                                                                   │
│  Methods for filtering:                                          │
│  • get_all_retrieval_traces(limit)                               │
│  • get_retrieval_traces_by_session(session_id)                   │
│  • get_retrieval_traces_by_user(user_id)                         │
│  • get_retrieval_trace_with_conversation(trace_id)               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
        ↑ INNER JOINs
        │
┌─────────────────────────────────────────────────────────────────┐
│                      Database Tables                             │
│                                                                   │
│  retrieval_traces                                                │
│  ├─ retrieval_trace_id (PK)                                      │
│  ├─ conversation_id (FK) ──────┐                                 │
│  ├─ query_input                 │                                │
│  ├─ retrieved_chunks (JSON)     │                                │
│  ├─ final_answer                │                                │
│  ├─ num_chunks_retrieved        │                                │
│  └─ timestamp                   │                                │
│                                 │                                │
│  conversations                  │                                │
│  ├─ conversation_id ────────────┘                                │
│  ├─ user_id (FK) ───────────┐                                    │
│  ├─ session_id              │                                    │
│  ├─ message                 │                                    │
│  ├─ response                │                                    │
│  ├─ conversation_type       │                                    │
│  ├─ response_time_ms        │                                    │
│  └─ timestamp               │                                    │
│                             │                                    │
│  users                      │                                    │
│  ├─ user_id ────────────────┘                                    │
│  ├─ email (UNIQUE)                                               │
│  ├─ full_name                                                    │
│  └─ created_at                                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
        ↑ Inserts data
        │
┌─────────────────────────────────────────────────────────────────┐
│                   Message Processing Pipeline                    │
│                                                                   │
│  1. User sends message                                           │
│  2. Message Handler (_handle_text/_handle_files)                 │
│  3. Classify conversation (TECHNICAL/CASUAL)                     │
│  4. Hybrid Retrieval:                                            │
│     ├─ Semantic Search (Vector embeddings)                       │
│     ├─ BM25 Keyword Search                                       │
│     └─ Merge & Filter Results                                    │
│  5. Capture Retrieval Data:                                      │
│     ├─ query_input = user message                                │
│     ├─ retrieved_chunks = [                                      │
│     │    {text, distance, document, section},                    │
│     │    {text, distance, document, section}, ...                │
│     │  ]                                                          │
│     └─ num_chunks_retrieved = count                              │
│  6. LLM Generation (generate_response_stream)                    │
│     └─ Capture: final_answer                                     │
│  7. Save Conversation                                            │
│     └─ Returns: conversation_id                                  │
│  8. Save RetrievalTrace                                          │
│     └─ Links to: conversation_id, user_id, session_id            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Mapping: User → Session → Conversation → Trace

```
┌─ USER (john@company.com, user_id=123)
│
├─ SESSION 1 (session_id=uuid-1, Today 2:00 PM)
│  │
│  ├─ CONVERSATION 1 (conv_id=456)
│  │  ├─ Message: "How to reset password?"
│  │  ├─ Response: "Go to Settings > Account > Reset..."
│  │  └─ RETRIEVAL TRACE 1 (trace_id=1001)
│  │      ├─ query_input: "How to reset password?"
│  │      ├─ num_chunks_retrieved: 3
│  │      ├─ retrieved_chunks: [
│  │      │    {text: "...", distance: 0.12, doc: "faq.md"},
│  │      │    {text: "...", distance: 0.34, doc: "guide.md"},
│  │      │    {text: "...", distance: 0.58, doc: "help.md"}
│  │      │  ]
│  │      └─ final_answer: "Go to Settings > Account > Reset..."
│  │
│  ├─ CONVERSATION 2 (conv_id=457)
│  │  ├─ Message: "Payment methods?"
│  │  ├─ Response: "We accept credit card, PayPal..."
│  │  └─ RETRIEVAL TRACE 2 (trace_id=1002)
│  │      ├─ query_input: "Payment methods?"
│  │      ├─ num_chunks_retrieved: 2
│  │      └─ retrieved_chunks: [...]
│  │
│  └─ CONVERSATION 3 (conv_id=458)
│     ├─ Message: "What's your API?"
│     ├─ Response: "Our API provides..."
│     └─ RETRIEVAL TRACE 3 (trace_id=1003)
│         └─ ...
│
└─ SESSION 2 (session_id=uuid-2, Yesterday 10:00 AM)
   │
   ├─ CONVERSATION 4 (conv_id=459)
   │  └─ RETRIEVAL TRACE 4 (trace_id=1004)
   │     └─ ...
   │
   └─ CONVERSATION 5 (conv_id=460)
      └─ RETRIEVAL TRACE 5 (trace_id=1005)
         └─ ...
```

## Filter Modes - How Data Flows

### Mode 1: View All
```
Database Query:
  get_all_retrieval_traces(limit=100)
    ↓
  SELECT * FROM retrieval_traces
  JOIN conversations ON rt.conversation_id = c.conversation_id
  JOIN users ON c.user_id = u.user_id
  ORDER BY rt.timestamp DESC
  LIMIT 100
    ↓
Returns: [Trace1, Trace2, ..., Trace100]
  ↓
Display: All columns (Trace ID, Conv ID, User, Query, Chunks, Type, Answer, Time)
```

### Mode 2: By Session ID
```
Input: session_id = "550e8400-e29b-41d4-a716-446655440000"
  ↓
Database Query:
  get_retrieval_traces_by_session(session_id)
    ↓
  SELECT rt.* FROM retrieval_traces rt
  JOIN conversations c ON rt.conversation_id = c.conversation_id
  WHERE c.session_id = ?
  ORDER BY rt.timestamp ASC
    ↓
Returns: [Trace1, Trace2, ..., TraceN] (all traces for that session)
  ↓
Display: Chronologically ordered traces from one conversation
```

### Mode 3: By User Email
```
Input: email = "john@company.com"
  ↓
Step 1: Convert email to user_id
  get_user_by_email(email) → user_id = 123
    ↓
Step 2: Get all traces for user
  get_retrieval_traces_by_user(user_id=123, limit=100)
    ↓
  SELECT rt.* FROM retrieval_traces rt
  JOIN conversations c ON rt.conversation_id = c.conversation_id
  JOIN users u ON c.user_id = u.user_id
  WHERE c.user_id = 123
  ORDER BY rt.timestamp DESC
  LIMIT 100
    ↓
Returns: [TraceA, TraceB, ..., TraceZ] (all user's traces)
  ↓
Display: User's traces across ALL sessions (most recent first)
```

### Mode 4: By Conversation ID
```
Input: trace_id = 1001
  ↓
Database Query:
  get_retrieval_trace_with_conversation(trace_id=1001)
    ↓
  SELECT rt.*, c.*, u.* FROM retrieval_traces rt
  JOIN conversations c ON rt.conversation_id = c.conversation_id
  JOIN users u ON c.user_id = u.user_id
  WHERE rt.retrieval_trace_id = 1001
    ↓
Returns: {
  retrieval_trace_id: 1001,
  conversation_id: 456,
  query_input: "How to reset password?",
  retrieved_chunks: [...],
  final_answer: "...",
  num_chunks_retrieved: 3,
  session_id: "uuid-1",
  message: "How to reset password?",
  conversation_type: "TECHNICAL",
  response_time_ms: 1250,
  email: "john@company.com",
  full_name: "John Doe",
  ...
}
  ↓
Display: Detailed view with all conversation context
```

## Retrieved Chunks Structure

```
retrieved_chunks (stored as JSON in database):
[
  {
    "text": "To reset your password, click on Settings in the top right menu.",
    "distance": 0.12,
    "document": "faq.md",
    "section": "Account Management"
  },
  {
    "text": "Password reset link expires after 24 hours. You can request a new one.",
    "distance": 0.34,
    "document": "guide.md",
    "section": "Security & Password"
  },
  {
    "text": "Common issues when resetting password include outdated browser cache.",
    "distance": 0.58,
    "document": "troubleshooting.md",
    "section": "Password Issues"
  }
]

Distance Interpretation:
0.12 → 🟢 Excellent - Direct answer
0.34 → 🟡 Good - Related information
0.58 → 🔴 Fair - Tangentially relevant
```

## Complete Message Trace Example

```
TIMESTAMP: 2024-03-11 14:30:45

1. USER SENDS MESSAGE
   john@company.com (user_id=123)
   Session: "550e8400-e29b-41d4" (session_id)
   Input: "How do I reset my password?"

2. MESSAGE HANDLER PROCESSES
   Conversation Type: TECHNICAL
   
3. HYBRID RETRIEVAL
   Semantic Search → [chunk1, chunk2, chunk3]
   BM25 Search → [chunk2, chunk4]
   Merged & Filtered → [chunk1, chunk2, chunk3]
   
4. CAPTURE RETRIEVAL DATA
   query_input: "How do I reset my password?"
   retrieved_chunks: [
     {text: "To reset...", distance: 0.12, document: "faq.md", section: "Account"},
     {text: "Password reset...", distance: 0.34, document: "guide.md", section: "Security"},
     {text: "Common issues...", distance: 0.58, document: "troubleshooting.md", section: "Password"}
   ]
   num_chunks_retrieved: 3
   
5. LLM GENERATION
   final_answer: "To reset your password, click Settings in top right. The reset link expires in 24 hours. If you have issues, it might be your browser cache."
   response_time_ms: 1250
   
6. SAVE CONVERSATION
   INSERT INTO conversations (user_id, session_id, message, response, ...)
   Returns: conversation_id = 456
   
7. SAVE RETRIEVAL TRACE
   INSERT INTO retrieval_traces (
     conversation_id=456,
     query_input="How do I reset my password?",
     retrieved_chunks='[{"text": "...", ...}]',
     final_answer="To reset your password...",
     num_chunks_retrieved=3,
     timestamp=2024-03-11 14:30:45
   )
   Returns: retrieval_trace_id = 1001

8. TRACE NOW VISIBLE IN DASHBOARD
   - Filter by user email "john@company.com" → See trace 1001
   - Filter by session "550e8400-e29b-41d4" → See trace 1001
   - Search trace ID 1001 → See full details with all chunks
```

## Performance Characteristics

```
Query Type                    | Time      | Records | Indexed?
----------------------------------------------------------
View All (limit 100)         | ~50ms     | 100     | ✓ timestamp DESC
By Session (10 messages)     | ~20ms     | 10      | ✓ session_id
By User (100 messages)       | ~30ms     | 100     | ✓ user_id
Single Trace Detail          | ~10ms     | 1       | ✓ trace_id (PK)
```

## Summary

The system provides:
- **Hierarchical Organization:** User → Session → Conversation → Trace
- **Flexible Filtering:** 4 different ways to find traces
- **Complete Context:** Every trace shows full conversation metadata
- **Quality Metrics:** Distance scores for each chunk with color coding
- **Audit Trail:** Full RAG pipeline captured for every message
- **Performance:** Fast queries with proper indexing
