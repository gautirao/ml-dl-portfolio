from typing import Optional, List, Dict, Any
from datetime import date
from src.tools.spending_summary import get_spending_summary
from src.tools.schemas import SpendingSummaryResult, Evidence, AnalyticsResult
from src.search.vector_store import VectorStore
from src.search.embedding_client import OllamaEmbeddingClient, MockEmbeddingClient
from src.search.semantic_matcher import SemanticMatcher

class SemanticSpendingResult(AnalyticsResult):
    semantic_matches: List[Dict[str, Any]]
    deterministic_result: SpendingSummaryResult

async def calculate_semantic_spending(
    query: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = 20,
    mock: bool = False
) -> SemanticSpendingResult:
    
    if mock:
        embedding_client = MockEmbeddingClient()
    else:
        embedding_client = OllamaEmbeddingClient()
        
    vector_store = VectorStore()
    matcher = SemanticMatcher(vector_store, embedding_client)
    
    # 1. Semantic Search
    matches = await matcher.find_matches(query, limit=limit)
    
    # 2. Extract Entities
    entities = await matcher.extract_entities(query)
    merchants = entities["merchants"]
    categories = entities["categories"]
    
    # 3. Deterministic Calculation
    result = get_spending_summary(
        date_from=date_from,
        date_to=date_to,
        merchant=merchants if merchants else None,
        category=categories if categories else None
    )
    
    evidence = result.evidence
    evidence.tool_name = "semantic_spending_search"
    evidence.calculation_method = "semantic_extraction_then_deterministic_sql"
    evidence.query_scope.update({
        "semantic_query": query,
        "merchants_included": merchants,
        "categories_included": categories,
        "semantic_match_count": len(matches)
    })
    
    return SemanticSpendingResult(
        semantic_matches=matches,
        deterministic_result=result,
        evidence=evidence
    )
