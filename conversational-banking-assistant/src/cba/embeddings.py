import hashlib
from typing import List, Protocol, runtime_checkable

@runtime_checkable
class EmbeddingModel(Protocol):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Convert a list of documents into a list of embeddings.
        """
        ...

    def embed_query(self, text: str) -> List[float]:
        """
        Convert a single query into an embedding.
        """
        ...

class FakeEmbeddingModel:
    """
    A deterministic fake embedding model for testing that doesn't require 
    downloading large models.
    """
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def _hash_text_to_vector(self, text: str) -> List[float]:
        # Simple deterministic vector based on text hash
        h = int(hashlib.sha256(text.encode()).hexdigest()[:16], 16)
        # Seed a pseudo-random sequence with the hash to get stable dimensions
        # This ensures that different texts get different but stable vectors
        import random
        rng = random.Random(h)
        vec = [rng.uniform(-1, 1) for _ in range(self.dimension)]
        
        # Normalize the vector to unit length (L2 norm)
        norm = sum(x*x for x in vec) ** 0.5
        if norm == 0:
            return [1.0] + [0.0] * (self.dimension - 1)
        return [x / norm for x in vec]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._hash_text_to_vector(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._hash_text_to_vector(text)

class SentenceTransformerEmbeddingModel:
    """
    Real implementation using sentence-transformers.
    Note: Model weights will be downloaded on first instantiation.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Please install it to use SentenceTransformerEmbeddingModel."
            )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode([text])[0]
        return embedding.tolist()
