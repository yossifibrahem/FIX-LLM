from typing import List, Dict
from openai import OpenAI
from functools import lru_cache

class EmbeddingClient:
    def __init__(self, base_url: str = "http://192.168.1.11:1234/v1", api_key: str = "dummy-key"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self._cache: Dict[str, List[float]] = {}

    @lru_cache(maxsize=1000)
    def get_embedding(self, text: str, model: str = "text-embedding-nomic-embed-text-v1.5") -> List[float]:
        """Get embedding for text with caching for better performance."""
        text = self._normalize_text(text)
        if text in self._cache:
            return self._cache[text]
        
        try:
            embedding = self.client.embeddings.create(input=[text], model=model).data[0].embedding
            self._cache[text] = embedding
            return embedding
        except Exception as e:
            raise Exception(f"Failed to get embedding: {str(e)}")

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for consistent embedding."""
        return text.strip().replace("\n", " ")

class TextSplitter:
    @staticmethod
    def split(text: str, max_words: int = 500) -> List[str]:
        """Split text into parts with a maximum number of words."""
        words = text.split()
        parts = []

        for i in range(0, len(words), max_words):
            part = " ".join(words[i:i + max_words])
            parts.append(part.strip())

        return parts
