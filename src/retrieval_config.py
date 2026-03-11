"""
Retrieval configuration system for flexible, per-query RAG settings.
Supports hybrid search with configurable distance thresholds and chunk limits.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RetrievalConfig:
    """
    Configuration for RAG retrieval with support for hybrid search
    and dynamic chunk selection based on distance thresholds.
    """
    
    # Distance-based filtering
    distance_threshold: float = 0.5  # Max distance to include chunk (0.0-1.0)
    min_chunks: int = 2  # Minimum chunks to retrieve
    max_chunks: int = 10  # Maximum chunks to retrieve
    
    # Hybrid search settings
    use_hybrid_search: bool = True  # Enable BM25 + semantic blending
    semantic_weight: float = 0.7  # Weight for semantic (vector) results
    keyword_weight: float = 0.3  # Weight for BM25 keyword results
    
    # Search parameters
    top_k_semantic: int = 15  # Top-k for semantic search (before filtering)
    top_k_keyword: int = 15  # Top-k for BM25 search (before filtering)
    
    def __post_init__(self):
        """Validate configuration"""
        assert 0.0 <= self.distance_threshold <= 1.0, "distance_threshold must be between 0.0 and 1.0"
        assert self.min_chunks > 0, "min_chunks must be > 0"
        assert self.max_chunks >= self.min_chunks, "max_chunks must be >= min_chunks"
        assert 0.0 <= self.semantic_weight <= 1.0, "semantic_weight must be between 0.0 and 1.0"
        assert 0.0 <= self.keyword_weight <= 1.0, "keyword_weight must be between 0.0 and 1.0"
        assert abs(self.semantic_weight + self.keyword_weight - 1.0) < 0.01, \
            "semantic_weight + keyword_weight must equal 1.0"


# Default configurations for different conversation types

TECHNICAL_CONFIG = RetrievalConfig(
    distance_threshold=0.5,  # Stricter threshold for technical accuracy
    min_chunks=2,
    max_chunks=10,
    use_hybrid_search=True,
    semantic_weight=0.7,
    keyword_weight=0.3,
    top_k_semantic=15,
    top_k_keyword=15,
)

CASUAL_CONFIG = RetrievalConfig(
    distance_threshold=0.6,  # More lenient for casual queries
    min_chunks=1,
    max_chunks=5,
    use_hybrid_search=True,
    semantic_weight=0.8,  # More reliance on semantic understanding
    keyword_weight=0.2,
    top_k_semantic=10,
    top_k_keyword=10,
)

# Pure semantic search (no hybrid)
SEMANTIC_ONLY_CONFIG = RetrievalConfig(
    distance_threshold=0.5,
    min_chunks=2,
    max_chunks=10,
    use_hybrid_search=False,
    semantic_weight=1.0,
    keyword_weight=0.0,
)


def get_config_for_conversation_type(conversation_type: str) -> RetrievalConfig:
    """
    Get appropriate retrieval config based on conversation type.
    
    Args:
        conversation_type: "TECHNICAL" or "CASUAL"
        
    Returns:
        RetrievalConfig instance
    """
    if conversation_type == "TECHNICAL":
        return TECHNICAL_CONFIG
    elif conversation_type == "CASUAL":
        return CASUAL_CONFIG
    else:
        return TECHNICAL_CONFIG  # Default to technical
