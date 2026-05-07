import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Any, Optional
from src.search.embedding_client import EmbeddingClient

class VectorStore:
    def __init__(self, persist_directory: str = "data/vector_store"):
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="ledgermind_semantic",
            metadata={"hnsw:space": "cosine"}
        )

    async def add_documents(
        self, 
        ids: List[str], 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        embedding_client: EmbeddingClient
    ):
        embeddings = await embedding_client.embed_documents(documents)
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

    async def query(
        self, 
        query_text: str, 
        embedding_client: EmbeddingClient, 
        limit: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if not query_text:
            return []
            
        query_embedding = await embedding_client.embed_query(query_text)
        if not query_embedding:
            return []
            
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where
        )
        
        # Format results
        formatted = []
        if results and results.get('ids') and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                formatted.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "score": results['distances'][0][i] if 'distances' in results and results['distances'] else None
                })
        return formatted

    def delete_all(self):
        self.client.delete_collection("ledgermind_semantic")
        self.collection = self.client.get_or_create_collection(
            name="ledgermind_semantic",
            metadata={"hnsw:space": "cosine"}
        )
