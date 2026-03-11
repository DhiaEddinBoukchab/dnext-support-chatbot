# Hybrid Search + Dynamic Retrieval Implementation Guide

## Overview

This implementation enhances your RAG system with:
- **Semantic + BM25 Hybrid Search** - Combines vector similarity with keyword matching
- **Dynamic Distance-Based Retrieval** - Intelligently adapts chunk count based on quality
- **Per-Query Configuration** - Different retrieval strategies for different query types
- **Full Observability** - Track retrieval quality in admin dashboard

## Architecture

### New Components

#### 1. **BM25 Search Module** (`src/bm25_search.py`)
- Lightweight keyword indexing using `rank_bm25`
- Automatically indexed when documents are loaded
- Provides fast keyword-based retrieval independent of semantic search

#### 2. **Retrieval Configuration System** (`src/retrieval_config.py`)
- Flexible per-query settings with sensible defaults
- Two pre-configured profiles: `TECHNICAL_CONFIG` and `CASUAL_CONFIG`
- Configurable weights for blending semantic + keyword results

#### 3. **Enhanced RAG Engine** (`app/rag_engine.py`)
- New `retrieve_hybrid()` method combining both search strategies
- Backward-compatible: old `retrieve()` still works unchanged
- Intelligent filtering with distance thresholds and min/max bounds

### Configuration Options

#### Distance Threshold (0.0 - 1.0)
- **0.0** = Perfect semantic match (very restrictive)
- **0.3** = Excellent match 🟢
- **0.5** = Good match 🟡
- **0.6** = Fair match 🔴
- **1.0** = Any match (very lenient)

#### Min/Max Chunks
- **min_chunks** = Minimum results to return (even if quality is lower)
- **max_chunks** = Maximum results to return (even if more qualify)

#### Hybrid Search Weights
- **semantic_weight** + **keyword_weight** must equal 1.0
- Default: 0.7 semantic + 0.3 keyword (emphasizes semantic understanding)
- Adjust based on your document style

### Default Configurations

#### TECHNICAL Queries (Technical Support, Code Help, etc.)
```python
distance_threshold = 0.5  # Stricter
min_chunks = 2
max_chunks = 10
semantic_weight = 0.7
keyword_weight = 0.3
```

#### CASUAL Queries (Chat, General Questions, etc.)
```python
distance_threshold = 0.6  # More lenient
min_chunks = 1
max_chunks = 5
semantic_weight = 0.8  # More semantic emphasis
keyword_weight = 0.2
```

## How It Works

### Retrieval Pipeline

1. **Semantic Search** (Vector Similarity)
   - Embed the query
   - Find top-k semantically similar chunks
   - Calculate distance for each (0 = perfect, 1 = no match)

2. **Keyword Search** (BM25)
   - Tokenize query and chunks
   - Calculate BM25 relevance scores
   - Find top-k keyword-matched chunks

3. **Merge & Score**
   - Combine both result sets
   - Remove duplicates
   - Calculate combined score: `semantic_weight * semantic_score + keyword_weight * keyword_score`

4. **Filter by Distance**
   - Keep only chunks where: `distance <= distance_threshold`
   - This removes low-quality results

5. **Enforce Bounds**
   - Ensure at least `min_chunks` results
   - Cap at `max_chunks` results
   - If below min, relax threshold and retry

6. **Rank & Return**
   - Sort by combined score (highest first)
   - Return in standard format for LLM context

## Usage Examples

### Default Usage (Recommended)
```python
# Message handler automatically uses correct config
results = rag.retrieve_hybrid(query, retrieval_config)
context = rag.format_context(results)
```

### Custom Configuration
```python
from src.retrieval_config import RetrievalConfig

# Ultra-strict: only high-quality matches
strict_config = RetrievalConfig(
    distance_threshold=0.3,
    min_chunks=1,
    max_chunks=5,
)
results = rag.retrieve_hybrid(query, strict_config)

# Lenient: cast wider net
lenient_config = RetrievalConfig(
    distance_threshold=0.7,
    min_chunks=3,
    max_chunks=15,
)
results = rag.retrieve_hybrid(query, lenient_config)
```

## Monitoring & Observability

### Admin Dashboard
Access the new **"🔬 Retrieval Traces"** tab to:
- Search traces by session ID
- View all retrieved chunks with distances
- See distance quality indicators (🟢 🟡 🔴)
- Click to inspect full query input and answer

### Distance Interpretation
- **< 0.3** (🟢 Excellent) - High confidence match
- **< 0.6** (🟡 Good) - Acceptable match
- **>= 0.6** (🔴 Fair) - Lower confidence match

### Retrieval Traces Data
Each trace captures:
- Query input
- Retrieved chunks with:
  - Full text
  - Distance metric
  - Source document
  - Section name
- Final answer
- Timestamp

## Performance Tuning

### If Retrieving Too Few Chunks
```python
config = RetrievalConfig(
    distance_threshold=0.6,  # Raise threshold
    min_chunks=5,             # Increase minimum
)
```

### If Retrieving Too Many Low-Quality Chunks
```python
config = RetrievalConfig(
    distance_threshold=0.4,  # Lower threshold
    max_chunks=8,             # Reduce maximum
)
```

### If BM25 Isn't Helping
- Increase `keyword_weight` to 0.4-0.5
- Or disable hybrid search: `use_hybrid_search=False`

### If Semantic Search Isn't Helping
- Increase `semantic_weight` to 0.8+
- Or check if embedding model is appropriate for your domain

## Technical Details

### BM25 Algorithm
- Uses **BM25Okapi** from `rank_bm25` library
- Language: English (automatic tokenization)
- Document frequency weighting for better relevance

### Merging Strategy
```
combined_score = (semantic_weight * (1 - distance)) + (keyword_weight * normalized_bm25_score)
```

- Distance is inverted so lower distance = higher semantic score
- BM25 scores are normalized to 0-1 range
- Both components weighted equally in final ranking

### Backward Compatibility
- Old `rag.retrieve(query, top_k)` still works
- Uses default `RetrievalConfig()` internally
- No breaking changes to existing code

## Troubleshooting

### "BM25 not indexed" warning
- Solution: Restart the app (BM25 auto-indexes on initialization)

### Chunks too repetitive
- Increase `distance_threshold` to filter out near-duplicates
- Or increase `semantic_weight` to emphasize semantic diversity

### Missing relevant chunks
- Lower `distance_threshold` (0.3 instead of 0.5)
- Increase `max_chunks`
- Check if BM25 is catching them: compare hybrid vs semantic-only

### Too slow
- Reduce `top_k_semantic` and `top_k_keyword` in config
- Reduce `max_chunks` to limit final processing

## Files Modified

| File | Change | Type |
|------|--------|------|
| `src/bm25_search.py` | New BM25 indexer | CREATE |
| `src/retrieval_config.py` | Configuration system | CREATE |
| `app/rag_engine.py` | Added `retrieve_hybrid()` | EDIT |
| `app/message_handler.py` | Uses hybrid retrieval | EDIT |
| `admin_dashboard/retrieval_traces.py` | Enhanced traces display | EDIT |
| `requirements.txt` | Added `rank_bm25` | EDIT |

## Next Steps

1. **Test the system** - Run queries and check admin dashboard traces
2. **Tune thresholds** - Adjust distance thresholds based on your domain
3. **Monitor quality** - Use retrieval traces to identify pattern mismatches
4. **Optimize weights** - Experiment with semantic/keyword weights for your use case

## Support

For issues or questions:
- Check retrieval traces in admin dashboard
- Review logs for BM25 initialization
- Test with simple queries first
- Compare `retrieve()` vs `retrieve_hybrid()` results
