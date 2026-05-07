from typing import List, Dict, Any, Optional
from src.search.vector_store import VectorStore
from src.search.embedding_client import EmbeddingClient

class SemanticMatcher:
    def __init__(self, vector_store: VectorStore, embedding_client: EmbeddingClient):
        self.vector_store = vector_store
        self.embedding_client = embedding_client

    async def find_matches(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        results = await self.vector_store.query(query, self.embedding_client, limit=limit)
        
        matches = []
        for r in results:
            matches.append({
                "matched_text": r["text"],
                "type": r["metadata"].get("type"),
                "merchant": r["metadata"].get("merchant"),
                "category": r["metadata"].get("category"),
                "score": r["score"],
                "metadata": r["metadata"]
            })
        return matches

    async def extract_entities(self, query: str, score_threshold: float = 0.5) -> Dict[str, List[str]]:
        """Extracts candidate merchants and categories from a query using semantic search."""
        matches = await self.find_matches(query, limit=20)
        
        merchants = set()
        categories = set()
        
        for m in matches:
            # Note: Chroma distance (cosine) is 0 to 2, where 0 is most similar.
            # So a threshold of 0.5 might be reasonable for similarity.
            if m["score"] is not None and m["score"] > score_threshold:
                continue
                
            if m["type"] == "merchant" and m["merchant"]:
                merchants.add(m["merchant"])
            elif m["type"] == "category" and m["category"]:
                categories.add(m["category"])
            elif m["type"] == "transaction_description":
                if m["merchant"]:
                    merchants.add(m["merchant"])
                if m["category"]:
                    categories.add(m["category"])
                    
        return {
            "merchants": list(merchants),
            "categories": list(categories)
        }
