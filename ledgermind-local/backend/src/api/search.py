from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date
from src.search.vector_store import VectorStore
from src.search.embedding_client import OllamaEmbeddingClient
from src.search.indexer import Indexer
from src.search.semantic_matcher import SemanticMatcher
from src.tools.semantic_spending import calculate_semantic_spending, SemanticSpendingResult

router = APIRouter(prefix="/api/search", tags=["search"])

class SemanticSpendingRequest(BaseModel):
    query: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    limit: int = 20

def get_vector_store():
    return VectorStore()

def get_embedding_client():
    return OllamaEmbeddingClient()

@router.post("/rebuild-index")
async def rebuild_index(
    vector_store: VectorStore = Depends(get_vector_store),
    embedding_client: OllamaEmbeddingClient = Depends(get_embedding_client)
):
    indexer = Indexer(vector_store, embedding_client)
    counts = await indexer.rebuild_index()
    return {"status": "success", "indexed_counts": counts}

@router.get("/semantic")
async def semantic_search(
    q: str,
    limit: int = 10,
    vector_store: VectorStore = Depends(get_vector_store),
    embedding_client: OllamaEmbeddingClient = Depends(get_embedding_client)
):
    matcher = SemanticMatcher(vector_store, embedding_client)
    matches = await matcher.find_matches(q, limit=limit)
    return matches

@router.post("/semantic-spending", response_model=SemanticSpendingResult)
async def semantic_spending(
    request: SemanticSpendingRequest
):
    return await calculate_semantic_spending(
        query=request.query,
        date_from=request.date_from,
        date_to=request.date_to,
        limit=request.limit
    )
