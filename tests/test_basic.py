
import pytest
from src.embeddings import EmbeddingManager
from src.vector_store import VectorStore

def test_embedding_manager():
    em = EmbeddingManager("all-MiniLM-L6-v2")
    embedding = em.encode("test text")
    assert len(embedding) == 384

def test_vector_store():
    vs = VectorStore("./test_db")
    collection = vs.create_collection("test", reset=True)
    assert collection is not None