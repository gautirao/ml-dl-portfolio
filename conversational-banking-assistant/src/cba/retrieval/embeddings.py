import hashlib
from typing import List, Protocol, runtime_checkable

@runtime_checkable
class EmbeddingModel(Protocol):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.
        """
        ...

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query.
        """
        ...

class FakeEmbeddingModel:
    """
    Deterministic fake embeddings for testing.
    """
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        # Create a deterministic fake vector from the text hash
        hash_val = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        vector = []
        for i in range(self.dimension):
            # Deterministic pseudo-randomness
            val = ((hash_val >> (i % 32)) & 0xFF) / 255.0
            vector.append(val)
        
        # Normalize to unit length (Cosine similarity requires this for 1.0 match)
        norm = sum(x*x for x in vector) ** 0.5
        return [x / norm for x in vector]
