from typing import Optional, List, Dict, Any
from datetime import date
import time
from src.database.connection import db_manager
from src.tools.schemas import SemanticTopMerchantsResult, MerchantSummary, Evidence
from src.search.vector_store import VectorStore
from src.search.embedding_client import OllamaEmbeddingClient, MockEmbeddingClient
from src.search.semantic_matcher import SemanticMatcher

async def calculate_semantic_top_merchants(
    query: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    rank_by: str = "transaction_count", # "transaction_count" | "total_spend"
    limit: int = 10,
    mock: bool = False
) -> SemanticTopMerchantsResult:
    start_time = time.time()
    
    if mock:
        embedding_client = MockEmbeddingClient()
    else:
        embedding_client = OllamaEmbeddingClient()
        
    vector_store = VectorStore()
    matcher = SemanticMatcher(vector_store, embedding_client)
    
    # 1. Semantic Search
    matches = await matcher.find_matches(query, limit=20)
    
    # 2. Extract Entities
    entities = await matcher.extract_entities(query)
    merchants_included = entities["merchants"]
    categories_included = entities["categories"]
    
    # 3. Deterministic Ranking via DuckDB
    conn = db_manager.get_connection()
    
    # Base query for merchant ranking
    # We use effective_category (from transaction_category_overrides) for filtering by category
    sql = """
        SELECT 
            COALESCE(t.merchant, t.description) as merchant_name,
            SUM(t.amount) as total_amount,
            COUNT(*) as transaction_count,
            MIN(t.transaction_date) as first_date,
            MAX(t.transaction_date) as last_date
        FROM transactions t
        LEFT JOIN (
            SELECT transaction_id, new_category
            FROM transaction_category_overrides
            QUALIFY ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY created_at DESC) = 1
        ) tco ON t.id = tco.transaction_id
        WHERE t.direction = 'outflow'
    """
    params = []
    
    if date_from:
        sql += " AND t.transaction_date >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND t.transaction_date <= ?"
        params.append(date_to)
        
    # Apply semantic filters
    filter_conditions = []
    if merchants_included:
        placeholders = ", ".join(["?" for _ in merchants_included])
        filter_conditions.append(f"t.merchant IN ({placeholders})")
        params.extend(merchants_included)
    
    if categories_included:
        placeholders = ", ".join(["?" for _ in categories_included])
        filter_conditions.append(f"COALESCE(tco.new_category, t.category) IN ({placeholders})")
        params.extend(categories_included)
        
    if filter_conditions:
        sql += " AND (" + " OR ".join(filter_conditions) + ")"
    else:
        # If no semantic matches found that map to merchants/categories, we return empty
        # to avoid returning all merchants for a specific concept that failed to match.
        return SemanticTopMerchantsResult(
            merchants=[],
            semantic_matches=matches,
            merchants_included=[],
            categories_included=[],
            evidence=Evidence(
                tool_name="semantic_top_merchants",
                row_count=0,
                query_scope={"query": query},
                calculation_method="semantic_candidates_then_duckdb_group_by"
            )
        )
        
    sql += " GROUP BY merchant_name"
    
    if rank_by == "total_spend":
        sql += " ORDER BY abs(SUM(t.amount)) DESC"
    else:
        sql += " ORDER BY COUNT(*) DESC"
        
    sql += " LIMIT ?"
    params.append(limit)
    
    results = conn.execute(sql, params).fetchall()
    
    merchants = []
    for r in results:
        merchants.append(MerchantSummary(
            merchant=r[0],
            total_amount=abs(float(r[1])),
            transaction_count=int(r[2]),
            first_date=r[3],
            last_date=r[4]
        ))
        
    latency_ms = (time.time() - start_time) * 1000
    
    query_scope = {
        "query": query,
        "date_from": str(date_from) if date_from else None,
        "date_to": str(date_to) if date_to else None,
        "rank_by": rank_by,
        "semantic_match_count": len(matches)
    }
    
    evidence = Evidence(
        tool_name="semantic_top_merchants",
        row_count=len(merchants),
        query_scope=query_scope,
        calculation_method="semantic_candidates_then_duckdb_group_by"
    )
    
    db_manager.log_event(
        "analytics_query_completed",
        "Semantic top merchants executed",
        {
            "tool": "semantic_top_merchants",
            "query": query,
            "row_count": len(merchants),
            "latency_ms": latency_ms
        }
    )
    
    return SemanticTopMerchantsResult(
        merchants=merchants,
        semantic_matches=matches,
        merchants_included=merchants_included,
        categories_included=categories_included,
        evidence=evidence
    )
