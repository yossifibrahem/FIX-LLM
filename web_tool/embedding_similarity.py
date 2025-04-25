import numpy as np
from openai import OpenAI
import re
from typing import List, Dict, Any
from functools import lru_cache
import concurrent.futures
import os

# Initialize the OpenAI client
client = OpenAI(
    base_url=os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1"),
    api_key=os.getenv("LMSTUDIO_API_KEY", "dummy_key")
)

@lru_cache(maxsize=1000)
def get_embedding(text: str, model: str = "text-embedding-nomic-embed-text-v1.5") -> List[float]:
    """
    Get embedding for text with caching to improve performance.
    """
    text = text.strip().replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    """
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def clean_markdown_content(text: str) -> str:
    """
    Clean markdown content by removing media elements and unnecessary formatting.
    """
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove inline images
    text = re.sub(r'<img.*?>', '', text)
    # Remove video embeds
    text = re.sub(r'<video.*?</video>', '', text)
    # Remove audio embeds
    text = re.sub(r'<audio.*?</audio>', '', text)
    # Remove responsive images
    text = re.sub(r'<picture.*?</picture>', '', text)
    # Remove URLs but keep link text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`.*?`', '', text)
    # Remove multiple newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_by_semantic_units(text: str, max_chunk_size: int = 500, min_chunk_size: int = 50) -> List[str]:
    """
    Split text into chunks based on semantic units (sentences and paragraphs).
    """
    # Split into paragraphs
    paragraphs = re.split(r'\n+', text)
    chunks = []
    current_chunk = []
    current_size = 0

    for paragraph in paragraphs:
        # Split paragraph into sentences
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_words = len(sentence.split())
            
            # If single sentence is longer than max_chunk_size, split it
            if sentence_words > max_chunk_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                
                words = sentence.split()
                for i in range(0, len(words), max_chunk_size):
                    chunk = ' '.join(words[i:i + max_chunk_size])
                    chunks.append(chunk)
                continue
            
            # If adding this sentence exceeds max_chunk_size and current chunk is big enough
            if current_size + sentence_words > max_chunk_size and current_size >= min_chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_words
            else:
                current_chunk.append(sentence)
                current_size += sentence_words
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def process_content(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process a single content item and return chunks.
    """
    if "content" not in item:
        return []
        
    cleaned_content = clean_markdown_content(item["content"])
    chunks = split_by_semantic_units(cleaned_content)
    
    return [{
        "url": item["url"],
        "title": item["title"],
        "citation": chunk
    } for chunk in chunks]

def find_most_similar_content(data: List[Dict[str, Any]], prompt: str, top_n: int = 3) -> List[Dict[str, Any]]:
    """
    Find the most similar content to a given query from a list of data using parallel processing.
    Returns a list of dictionaries containing url, title, and citation for the most similar chunks.
    """
    # Clean and prepare the prompt
    cleaned_prompt = prompt
    query_embedding = get_embedding(cleaned_prompt)
    
    # Process all content items in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        all_chunks = []
        chunk_futures = [executor.submit(process_content, item) for item in data]
        for future in concurrent.futures.as_completed(chunk_futures):
            all_chunks.extend(future.result())
    
    # Calculate similarities in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        similarity_futures = [
            executor.submit(
                lambda x: (x, cosine_similarity(query_embedding, get_embedding(x["citation"]))),
                chunk
            )
            for chunk in all_chunks
        ]
        
        similarities = [
            future.result()
            for future in concurrent.futures.as_completed(similarity_futures)
        ]
    
    # Sort by similarity and select top_n
    similarities.sort(key=lambda x: x[1], reverse=True)
    most_similar = [item[0] for item in similarities[:top_n]]
    
    return most_similar
