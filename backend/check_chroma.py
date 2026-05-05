import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from src.vector_store import VectorStore
from src.embeddings import EmbeddingManager

vs = VectorStore(Config.CHROMA_DB_PATH)
collection = vs.get_collection()
print(f"Chroma path: {Config.CHROMA_DB_PATH}")
print(f"Collection count: {collection.count()}")

if collection.count() > 0:
    # Use proper embedding manager to encode query
    embedding_manager = EmbeddingManager(Config.EMBEDDING_MODEL)
    query_embedding = embedding_manager.encode("test")
    results = collection.query(query_embeddings=[query_embedding], n_results=1)
    print(f"Sample documents: {len(results['documents'][0])}")
    if results['documents'][0]:
        print(f"First document preview: {results['documents'][0][0][:200]}...")
else:
    print("No documents in collection")
