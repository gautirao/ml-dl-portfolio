import duckdb
from typing import Optional, List, Any, Dict
from datetime import date
from src.database.connection import db_manager
from src.tools.schemas import TransactionSearchResult, TransactionItem, Evidence
import json
import time

def search_transactions(
    source_bank: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    direction: Optional[str] = None,
    merchant: Optional[str] = None,
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    limit: int = 50,
    offset: int = 0
) -> TransactionSearchResult:
    start_time = time.time()
    conn = db_manager.get_connection()
    
    # Base query with effective_category and category_source
    query = """
        SELECT 
            t.id, t.source_bank, t.transaction_date, t.description, t.merchant, t.amount, t.direction, t.category, t.raw_row_json,
            tco.new_category as override_category,
            CASE 
                WHEN tco.new_category IS NOT NULL THEN 'override'
                WHEN t.category IS NULL OR t.category = '' OR t.category = 'Uncategorized' THEN 'uncategorised'
                WHEN EXISTS (SELECT 1 FROM merchant_rules mr WHERE mr.merchant_name = t.merchant AND mr.category = t.category) THEN 'merchant_rule'
                ELSE 'imported'
            END as category_source
        FROM transactions t
        LEFT JOIN (
            SELECT transaction_id, new_category
            FROM transaction_category_overrides
            QUALIFY ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY created_at DESC) = 1
        ) tco ON t.id = tco.transaction_id
        WHERE 1=1
    """
    params = []
    
    # Count query needs the same join if we filter by effective category
    count_query = """
        SELECT count(*) 
        FROM transactions t
        LEFT JOIN (
            SELECT transaction_id, new_category
            FROM transaction_category_overrides
            QUALIFY ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY created_at DESC) = 1
        ) tco ON t.id = tco.transaction_id
        WHERE 1=1
    """
    
    filters = {
        "source_bank": source_bank,
        "date_from": date_from,
        "date_to": date_to,
        "direction": direction,
        "merchant": merchant,
        "category": category,
        "min_amount": min_amount,
        "max_amount": max_amount
    }
    
    # Filter builder
    filter_clauses = ""
    if source_bank:
        filter_clauses += " AND t.source_bank = ?"
        params.append(source_bank)
    if date_from:
        filter_clauses += " AND t.transaction_date >= ?"
        params.append(date_from)
    if date_to:
        filter_clauses += " AND t.transaction_date <= ?"
        params.append(date_to)
    if direction:
        filter_clauses += " AND t.direction = ?"
        params.append(direction)
    if merchant:
        filter_clauses += " AND t.merchant ILIKE ?"
        params.append(f"%{merchant}%")
    if category:
        filter_clauses += " AND COALESCE(tco.new_category, t.category) = ?"
        params.append(category)
    if min_amount is not None:
        filter_clauses += " AND abs(t.amount) >= ?"
        params.append(min_amount)
    if max_amount is not None:
        filter_clauses += " AND abs(t.amount) <= ?"
        params.append(max_amount)

    query += filter_clauses
    count_query += filter_clauses
    
    count_params = list(params)
    
    # Sorting and Pagination
    query += " ORDER BY t.transaction_date DESC, t.id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    # Execute
    total_count = conn.execute(count_query, count_params).fetchone()[0]
    results = conn.execute(query, params).fetchall()
    
    transactions = []
    for r in results:
        transactions.append(TransactionItem(
            id=str(r[0]),
            source_bank=r[1],
            transaction_date=r[2],
            description=r[3],
            merchant=r[4],
            amount=float(r[5]),
            direction=r[6],
            category=r[7],
            effective_category=r[9] if r[9] else r[7],
            category_source=r[10]
            # raw_row_json is excluded by default for privacy/efficiency
        ))
    
    latency_ms = (time.time() - start_time) * 1000
    
    query_scope = {k: str(v) for k, v in filters.items() if v is not None}
    if not date_from and not date_to:
        query_scope["time_range"] = "all_time"
        
    evidence = Evidence(
        tool_name="transaction_search",
        row_count=len(transactions),
        query_scope=query_scope,
        calculation_method="deterministic_sql_query"
    )
    
    db_manager.log_event(
        "analytics_query_completed",
        "Transaction search executed",
        {
            "tool": "transaction_search",
            "filters": {k: str(v) for k, v in filters.items() if v is not None},
            "row_count": len(transactions),
            "latency_ms": latency_ms
        }
    )
    
    return TransactionSearchResult(
        transactions=transactions,
        total_count=total_count,
        limit=limit,
        offset=offset,
        filters_applied={k: v for k, v in filters.items() if v is not None},
        evidence=evidence
    )
