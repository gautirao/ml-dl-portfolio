from typing import List, Protocol
from src.ai.ollama_client import OllamaClient

class EmbeddingClient(Protocol):
    async def embed_query(self, text: str) -> List[float]:
        ...
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        ...

class OllamaEmbeddingClient:
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.client = OllamaClient(base_url=base_url)
        self.model = model

    async def embed_query(self, text: str) -> List[float]:
        return await self.client.embeddings(self.model, text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # For now, embed sequentially to avoid overloading Ollama if it doesn't handle batching well
        # or if we want to stay simple.
        embeddings = []
        for text in texts:
            emb = await self.client.embeddings(self.model, text)
            embeddings.append(emb)
        return embeddings

class MockEmbeddingClient:
    """Useful for testing without a running Ollama instance."""
    def __init__(self, dimension: int = 3072): # llama3.2 default dimension
        self.dimension = dimension

    async def embed_query(self, text: str) -> List[float]:
        return [0.1] * self.dimension

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * self.dimension for _ in texts]
