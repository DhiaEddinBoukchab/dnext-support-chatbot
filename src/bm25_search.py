"""
BM25 keyword search indexer and retriever.
Provides fast keyword-based retrieval to complement semantic (vector) search.
"""

import logging
from typing import List, Dict, Tuple, Optional
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


class BM25Indexer:
    """
    BM25 keyword search engine using rank_bm25.
    Indexes all chunks at initialization for fast keyword retrieval.
    """

    def __init__(self):
        """Initialize BM25 indexer"""
        self.corpus: List[str] = []  # List of chunk texts
        self.chunk_ids: List[str] = []  # Corresponding chunk IDs
        self.bm25: Optional[BM25Okapi] = None
        self.is_indexed = False

    def index_chunks(self, chunks: List[str], chunk_ids: Optional[List[str]] = None) -> None:
        """
        Index chunks for BM25 search.
        
        Args:
            chunks: List of text chunks to index
            chunk_ids: Optional list of chunk IDs (defaults to indices)
        """
        try:
            if not chunks:
                logger.warning("No chunks to index for BM25")
                return

            # Tokenize: split by whitespace and convert to lowercase
            tokenized_corpus = [chunk.lower().split() for chunk in chunks]

            # Initialize BM25 with tokenized corpus
            self.bm25 = BM25Okapi(tokenized_corpus)
            self.corpus = chunks
            self.chunk_ids = chunk_ids if chunk_ids else [str(i) for i in range(len(chunks))]
            self.is_indexed = True

            logger.info(f"BM25 indexed {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Error indexing chunks for BM25: {e}")
            self.is_indexed = False

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float, str]]:
        """
        Search using BM25.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of (chunk_index, bm25_score, chunk_text) tuples
        """
        if not self.is_indexed or self.bm25 is None:
            logger.warning("BM25 not indexed. Returning empty results.")
            return []

        try:
            # Tokenize query same way as corpus
            tokenized_query = query.lower().split()

            # Get BM25 scores for all chunks
            scores = self.bm25.get_scores(tokenized_query)

            # Get top-k indices by score
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

            # Return results as (index, score, text) tuples
            results = [
                (idx, scores[idx], self.corpus[idx])
                for idx in top_indices
                if scores[idx] > 0  # Only include chunks with positive scores
            ]

            return results
        except Exception as e:
            logger.error(f"Error searching with BM25: {e}")
            return []

    def update_index(self, new_chunks: List[str], new_chunk_ids: Optional[List[str]] = None) -> None:
        """
        Update the BM25 index with new chunks (e.g., when new documents are added).
        
        Args:
            new_chunks: New chunks to add
            new_chunk_ids: Optional IDs for new chunks
        """
        try:
            combined_chunks = self.corpus + new_chunks
            combined_ids = self.chunk_ids + (new_chunk_ids if new_chunk_ids else [str(len(self.corpus) + i) for i in range(len(new_chunks))])
            self.index_chunks(combined_chunks, combined_ids)
            logger.info(f"BM25 index updated with {len(new_chunks)} new chunks")
        except Exception as e:
            logger.error(f"Error updating BM25 index: {e}")

    def clear(self) -> None:
        """Clear the BM25 index"""
        self.corpus = []
        self.chunk_ids = []
        self.bm25 = None
        self.is_indexed = False
        logger.info("BM25 index cleared")


# Global BM25 instance (lazy-loaded)
_bm25_instance: Optional[BM25Indexer] = None


def get_bm25_indexer() -> BM25Indexer:
    """Get or create the global BM25 indexer instance"""
    global _bm25_instance
    if _bm25_instance is None:
        _bm25_instance = BM25Indexer()
    return _bm25_instance
