import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from src.search.vector_store import VectorStore
from src.search.embedding_client import OllamaEmbeddingClient

logger = logging.getLogger(__name__)

class KnowledgeSource(BaseModel):
    id: str
    text: str
    source: str
    section: int
    score: Optional[float] = None

class KnowledgeResult(BaseModel):
    query: str
    matches: List[KnowledgeSource]
    evidence: Dict[str, Any]

async def knowledge_lookup(query: str, limit: int = 3) -> KnowledgeResult:
    """
    Looks up information in the local knowledge base.
    """
    vector_store = VectorStore()
    embedding_client = OllamaEmbeddingClient()
    
    results = await vector_store.query(
        query_text=query,
        embedding_client=embedding_client,
        limit=limit,
        where={"type": "knowledge_base"}
    )
    
    matches = []
    evidence_sources = []
    
    for r in results:
        matches.append(KnowledgeSource(
            id=r["id"],
            text=r["text"],
            source=r["metadata"].get("source", "unknown"),
            section=r["metadata"].get("section", 0),
            score=r.get("score")
        ))
        evidence_sources.append({
            "source": r["metadata"].get("source", "unknown"),
            "section": r["metadata"].get("section", 0),
            "snippet": r["text"][:200] + "..." if len(r["text"]) > 200 else r["text"]
        })
        
    return KnowledgeResult(
        query=query,
        matches=matches,
        evidence={
            "knowledge_sources": evidence_sources,
            "type": "knowledge_base"
        }
    )
