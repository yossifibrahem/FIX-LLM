# build_vector_index.py
import os
import numpy as np
import faiss
from embed import EmbeddingClient, TextSplitter

DATA_PATH = "RAG/text/data.txt"
INDEX_PATH = "RAG/vector_db/faiss.index"
CHUNKS_PATH = "RAG/vector_db/chunks.npy"

# 1. Read and split the text
def load_and_split(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return TextSplitter.split(text)

# 2. Embed each chunk
def embed_chunks(chunks, embedder):
    vectors = []
    for chunk in chunks:
        emb = embedder.get_embedding(chunk)
        vectors.append(np.array(emb, dtype=np.float32))
    return np.vstack(vectors)

# 3. Store in FAISS index
def build_faiss_index(vectors):
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index

def main():
    os.makedirs("vector_db", exist_ok=True)
    print("Loading and splitting text...")

    chunks = load_and_split(DATA_PATH)
    print(f"Total chunks: {len(chunks)}")

    print("Embedding chunks...")
    embedder = EmbeddingClient()

    vectors = embed_chunks(chunks, embedder)
    print(f"Vectors shape: {vectors.shape}")
    
    print("Building FAISS index...")
    index = build_faiss_index(vectors)
    faiss.write_index(index, INDEX_PATH)
    np.save(CHUNKS_PATH, np.array(chunks))

    print(f"Index and chunks saved to {INDEX_PATH} and {CHUNKS_PATH}")

if __name__ == "__main__":
    main()
