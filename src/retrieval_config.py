"""Semantic retrieval configuration for the FastAPI service."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalConfig:
    """Semantic retrieval parameters with threshold-based filtering."""

    distance_threshold: float = 0.5
    min_chunks: int = 2
    max_chunks: int = 5
    top_k_semantic: int = 5


TECHNICAL_CONFIG = RetrievalConfig(distance_threshold=0.5, min_chunks=2, max_chunks=5, top_k_semantic=5)
CASUAL_CONFIG = RetrievalConfig(distance_threshold=0.6, min_chunks=1, max_chunks=5, top_k_semantic=5)


def get_config_for_conversation_type(conversation_type: str) -> RetrievalConfig:
    """Return the semantic retrieval config for the requested conversation type."""
    return CASUAL_CONFIG if conversation_type == "CASUAL" else TECHNICAL_CONFIG
