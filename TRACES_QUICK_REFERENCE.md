# Retrieval Traces - Quick Reference Guide

## Dashboard Access

1. Open Admin Dashboard
2. Go to **"🔬 Retrieval Traces"** tab
3. Choose filter mode and search

## Filter Modes at a Glance

| Mode | Input | Use Case | Example |
|------|-------|----------|---------|
| **View All** | None | See recent traces across all users | Monitor system health |
| **By Session ID** | Session UUID | See all messages in one chat session | Debug a specific conversation |
| **By User Email** | User email | See all traces for one user across sessions | Analyze user's interactions |
| **By Conversation ID** | Trace ID | See one specific Q&A pair | Detailed inspection |

## Results Table Columns

```
Trace ID        → Click to see full details
Conversation ID → Maps to one Q&A exchange
User            → Email of person who asked
Query           → Their question (shortened)
Chunks          → How many chunks were retrieved
Type            → TECHNICAL or CASUAL
Answer Preview  → LLM response (shortened)
Timestamp       → When it happened
```

## Detailed View - What You See

### Conversation Metadata (top)
```
Conversation ID: 456
User: John Doe (john@company.com)
Session ID: 550e8400-e29b-41d4
Type: TECHNICAL
Response Time: 1250 ms
Timestamp: 2024-03-11 14:30:45
```

### Query & Answer (middle)
```
Input Query
"How do I reset my password?"

Final Answer
"To reset your password, click Settings in the top right..."
```

### Retrieved Chunks (bottom)
```
Chunk 1
Document: faq.md | Section: Account Management
Distance: 0.12 🟢 Excellent
"To reset your password, click on Settings..."

Chunk 2
Document: guide.md | Section: Security & Password
Distance: 0.34 🟡 Good
"Password reset link expires after 24 hours..."
```

## Distance Score Guide

```
🟢 Excellent (0.0 - 0.3)   → Direct answer to question
🟡 Good (0.3 - 0.6)        → Related, helpful information
🔴 Fair (0.6 - 1.0)        → Tangentially relevant or poor match
```

## Common Tasks

### Task: Debug Poor Response Quality

1. Filter by "User Email" → Enter user's email
2. View their traces
3. Find problematic message (check distance scores)
4. If distances all > 0.6: Retrieval quality poor
5. If chunks are irrelevant: Knowledge base needs updates

### Task: Analyze Conversation Flow

1. Filter by "Session ID" → Enter session ID
2. View all messages in that session
3. Compare chunk quality across messages
4. Identify where retrieval broke down

### Task: Inspect Single Message

1. Find trace ID in any results table
2. Enter trace ID in "Detailed View"
3. Click "View Full Details"
4. See complete RAG pipeline for that message

### Task: Monitor System Health

1. Filter: "View All"
2. Check recent 100 traces
3. Scan distance scores
4. Look for patterns in poor matches
5. Check response times

## Quick Statistics

**What the numbers mean:**

- **Chunks: 3-5** → Normal good retrieval
- **Chunks: 1-2** → Either casual conversation or low-quality matches
- **Distance < 0.3** → Excellent relevance
- **Distance 0.3-0.6** → Good relevance
- **Distance > 0.7** → Poor relevance

## Database Behind the Scenes

```python
# What the UI calls:

# View All
db.get_all_retrieval_traces(limit=100)

# By Session
db.get_retrieval_traces_by_session(session_id)

# By User Email
user = db.get_user_by_email(email)
db.get_retrieval_traces_by_user(user.user_id)

# By Conversation
db.get_retrieval_trace_with_conversation(trace_id)
```

## Retrieved Chunks Data Structure

```json
{
  "text": "Full chunk text content",
  "distance": 0.25,
  "document": "filename.md",
  "section": "Section Name"
}
```

- **text** → What the chunk says
- **distance** → How relevant (lower = better)
- **document** → Which knowledge base file
- **section** → Location within that file

## Troubleshooting

### "No traces found"
- Wrong session ID? Check format
- Wrong email? Verify spelling
- New user? They may have no traces yet
- Try "View All" to see if system has any traces

### "Chunks seem irrelevant"
- Distance scores high (> 0.6)?
- Knowledge base might not contain relevant info
- May need to add/update documents

### "Always retrieving same chunks"
- Check if knowledge base has duplicates
- May need deduplication

### "Response time very slow"
- Check `response_time_ms` in metadata
- High time → LLM generation was slow
- May indicate system load or model issues

## Key Relationships

```
USER
  └─ All traces for that user
  
SESSION
  └─ All messages in one chat
  
CONVERSATION
  └─ One Q&A pair
  
RETRIEVAL TRACE
  └─ Chunks retrieved for that Q&A
```

## Pro Tips

1. **Use Session ID for understanding context**
   - See how conversation evolved
   - Which messages had good retrieval
   - Which had poor retrieval

2. **Use User Email for pattern analysis**
   - Do this user always get good results?
   - Do they ask similar questions?
   - Are they using the system correctly?

3. **Use Trace ID for debugging**
   - Detailed view shows everything
   - Export detailed view for analysis
   - Share with team for discussion

4. **Monitor distances weekly**
   - Track trends
   - Identify knowledge gaps
   - Plan documentation updates

## Integration with LangSmith

- Traces ALSO logged to LangSmith (if configured)
- Cloud-based backup of trace data
- Additional analytics available in LangSmith
- Use both for complete observability

## Summary

The Retrieval Traces system gives you:
✅ Full visibility into RAG pipeline
✅ Easy filtering by user/session/message
✅ Quality metrics (distances)
✅ Complete conversation context
✅ Performance monitoring

Use it to debug, optimize, and monitor your chatbot!
