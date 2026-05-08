from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from src.categories.suggestions import SuggestionService
from src.search.vector_store import VectorStore
from src.search.embedding_client import OllamaEmbeddingClient
from src.search.semantic_matcher import SemanticMatcher
from src.search.indexer import Indexer
from src.database.connection import settings

router = APIRouter(prefix="/api/categories", tags=["categories"])

class SuggestionEdit(BaseModel):
    suggested_merchant: str
    suggested_category: str
    suggested_subcategory: Optional[str] = None
    apply_to_matching: bool = False

class ApproveRequest(BaseModel):
    apply_to_matching: bool = False

def get_suggestion_service():
    # We don't use Depends in the factory function itself to avoid complexity,
    # but we can instantiate dependencies here or pass them from the endpoint.
    vector_store = VectorStore(persist_directory=settings.vector_store_path)
    embedding_client = OllamaEmbeddingClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model
    )
    matcher = SemanticMatcher(vector_store, embedding_client)
    indexer = Indexer(vector_store, embedding_client)
    return SuggestionService(semantic_matcher=matcher, indexer=indexer)

@router.get("/suggestions")
async def get_suggestions(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    service: SuggestionService = Depends(get_suggestion_service)
):
    return service.get_suggestions(status=status, limit=limit, offset=offset)

@router.post("/suggestions/generate")
async def generate_suggestions(
    limit: int = 50,
    service: SuggestionService = Depends(get_suggestion_service)
):
    return await service.generate_suggestions(limit=limit)

@router.post("/suggestions/{suggestion_id}/approve")
async def approve_suggestion(
    suggestion_id: str,
    request: ApproveRequest,
    service: SuggestionService = Depends(get_suggestion_service)
):
    try:
        return await service.approve_suggestion(suggestion_id, apply_to_matching=request.apply_to_matching)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/suggestions/{suggestion_id}/reject")
async def reject_suggestion(
    suggestion_id: str,
    service: SuggestionService = Depends(get_suggestion_service)
):
    return service.reject_suggestion(suggestion_id)

@router.post("/suggestions/{suggestion_id}/edit")
async def edit_suggestion(
    suggestion_id: str,
    edit_data: SuggestionEdit,
    service: SuggestionService = Depends(get_suggestion_service)
):
    try:
        return await service.edit_suggestion(
            suggestion_id, 
            edit_data.dict(), 
            apply_to_matching=edit_data.apply_to_matching
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
