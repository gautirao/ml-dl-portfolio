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
    
    # Base query
    query = "SELECT id, source_bank, transaction_date, description, merchant, amount, direction, category, raw_row_json FROM transactions WHERE 1=1"
    params = []
    
    # Count query
    count_query = "SELECT count(*) FROM transactions WHERE 1=1"
    count_params = []
    
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
        filter_clauses += " AND source_bank = ?"
        params.append(source_bank)
    if date_from:
        filter_clauses += " AND transaction_date >= ?"
        params.append(date_from)
    if date_to:
        filter_clauses += " AND transaction_date <= ?"
        params.append(date_to)
    if direction:
        filter_clauses += " AND direction = ?"
        params.append(direction)
    if merchant:
        filter_clauses += " AND merchant ILIKE ?"
        params.append(f"%{merchant}%")
    if category:
        filter_clauses += " AND category = ?"
        params.append(category)
    if min_amount is not None:
        filter_clauses += " AND abs(amount) >= ?"
        params.append(min_amount)
    if max_amount is not None:
        filter_clauses += " AND abs(amount) <= ?"
        params.append(max_amount)

    query += filter_clauses
    count_query += filter_clauses
    
    count_params = list(params)
    
    # Sorting and Pagination
    query += " ORDER BY transaction_date DESC, created_at DESC LIMIT ? OFFSET ?"
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
            raw_row_json=json.loads(r[8]) if r[8] else None
        ))
    
    latency_ms = (time.time() - start_time) * 1000
    
    evidence = Evidence(
        tool_name="transaction_search",
        row_count=len(transactions),
        query_scope={k: str(v) for k, v in filters.items() if v is not None},
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
