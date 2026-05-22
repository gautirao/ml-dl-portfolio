import uuid
from typing import Protocol, runtime_checkable

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from cba.common.paths import validate_path_prefix
from cba.domain.models import Chunk, SearchResult

from .embeddings import EmbeddingModel


@runtime_checkable
class VectorIndex(Protocol):
    def add_chunks(self, chunks: list[Chunk]) -> None:
        """
        Add or update chunks in the vector index.
        """
        ...

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """
        Perform a vector similarity search.
        """
        ...

class QdrantVectorIndex:
    """
    Local vector index implementation using Qdrant.
    """
    COLLECTION_NAME = "chunks"

    def __init__(
        self, 
        embedding_model: EmbeddingModel, 
        location: str | None = None, 
        path: str | None = None
    ) -> None:
        """
        Initialize Qdrant index.
        :param embedding_model: The model used to generate embeddings.
        :param location: Qdrant location (e.g., ":memory:").
        :param path: Local disk path for persistence.
        """
        self.embedding_model = embedding_model
        
        if path:
            # Enforce path safety - must be under data/vector_store/
            if not validate_path_prefix(str(path), ["data/vector_store"]):
                 raise ValueError("Persistent vector store must be under data/vector_store/")
            
            self.client = QdrantClient(path=path)
        else:
            self.client = QdrantClient(location=location or ":memory:")
            
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        # We need a dummy embedding to know the dimension if it's not explicitly known
        # Sentence-transformers usually have 384 for all-MiniLM-L6-v2
        # Let's get it from the model
        dummy_embedding = self.embedding_model.embed_query("dummy")
        dimension = len(dummy_embedding)

        collections = self.client.get_collections().collections
        exists = any(c.name == self.COLLECTION_NAME for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
            )

    def _get_point_id(self, chunk_id: str) -> str:
        """
        Deterministic UUID5 from chunk_id.
        """
        return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))

    def add_chunks(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_model.embed_documents(texts)
        
        points = []
        for chunk, vector in zip(chunks, embeddings, strict=True):
            point_id = self._get_point_id(chunk.chunk_id)
            points.append(PointStruct(
                id=point_id,
                vector=vector,
                payload=chunk.model_dump()
            ))
            
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points
        )

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        query_vector = self.embedding_model.embed_query(query)
        
        search_results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            limit=top_k
        ).points
        
        results = []
        for res in search_results:
            # Reconstruct Chunk from payload
            if res.payload:
                chunk = Chunk(**res.payload)
                results.append(SearchResult(
                    chunk=chunk,
                    score=res.score # Cosine similarity, higher is better
                ))
            
        return results
