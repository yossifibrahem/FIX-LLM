# search_vector_index.py
import numpy as np
import faiss
from RAG.embed import EmbeddingClient

INDEX_PATH = "vector_db/faiss.index"
CHUNKS_PATH = "vector_db/chunks.npy"

def search(query, top_k=5):
    # Load index and chunks
    index = faiss.read_index(INDEX_PATH)
    chunks = np.load(CHUNKS_PATH, allow_pickle=True)

    # Embed the query
    embedder = EmbeddingClient()
    query_vec = np.array(embedder.get_embedding(query), dtype=np.float32).reshape(1, -1)

    # Normalize for cosine similarity
    faiss.normalize_L2(query_vec)
    faiss.normalize_L2(index.reconstruct_n(0, index.ntotal))

    # Search
    result = []
    D, I = index.search(query_vec, top_k)
    
    # Create list of (score, index) tuples and sort by score in descending order
    scored_indices = [(D[0][i], I[0][i]) for i in range(len(I[0]))]
    scored_indices.sort(reverse=True)  # Sort by score in descending order
    
    # Build result list with correct ranking
    for i, (score, idx) in enumerate(scored_indices):
        result.append(f"Rank {i+1} (Score: {score:.4f}):\n{chunks[idx]}")
    return result
