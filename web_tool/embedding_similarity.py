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

def split_by_semantic_units(text: str, max_chunk_size: int = 256, min_chunk_size: int = 64) -> List[str]:
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
        "content": chunk
    } for chunk in chunks]

def find_most_similar_content(data: List[Dict[str, Any]], 
                                        keywords: List[str], 
                                        top_n: int = 3,
                                        min_match_keywords: int = 1) -> List[Dict[str, Any]]:
    """
    Find content that matches multiple keywords using embeddings.
    """
    # Clean and prepare the keywords
    keyword_embeddings = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        keyword_futures = [executor.submit(get_embedding, kw) for kw in keywords]
        keyword_embeddings = [future.result() for future in concurrent.futures.as_completed(keyword_futures)]
    
    # Process all content items in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        all_chunks = []
        chunk_futures = [executor.submit(process_content, item) for item in data]
        for future in concurrent.futures.as_completed(chunk_futures):
            all_chunks.extend(future.result())
    
    # Calculate similarities in parallel for each chunk against all keywords
    chunk_scores = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for chunk in all_chunks:
            chunk_embedding = get_embedding(chunk["content"])
            keyword_matches = 0
            total_similarity = 0
            
            # Calculate similarity with each keyword
            for kw_embedding in keyword_embeddings:
                similarity = cosine_similarity(chunk_embedding, kw_embedding)
                if similarity > 0.5:  # Threshold for considering a keyword match
                    keyword_matches += 1
                total_similarity += similarity
            
            # Calculate average similarity
            avg_similarity = total_similarity / len(keywords)
            
            if keyword_matches >= min_match_keywords:
                chunk_scores.append((chunk, avg_similarity, keyword_matches))
    
    # Sort by number of keyword matches first, then by average similarity
    chunk_scores.sort(key=lambda x: (x[2], x[1]), reverse=True)
    
    return [item[0] for item in chunk_scores[:top_n]]
