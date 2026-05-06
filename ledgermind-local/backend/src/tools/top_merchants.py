from typing import Optional, List
from datetime import date
from src.database.connection import db_manager
from src.tools.schemas import TopMerchantsResult, MerchantSummary, Evidence
import time

def get_top_merchants(
    date_from: date,
    date_to: date,
    direction: str = "outflow",
    limit: int = 10,
    category: Optional[str] = None,
    source_bank: Optional[str] = None
) -> TopMerchantsResult:
    start_time = time.time()
    conn = db_manager.get_connection()
    
    # Use merchant field where available; fallback to description-derived merchant if we want, 
    # but the prompt says: Use merchant field where available; fallback to description-derived merchant.
    # Actually, the transactions table has merchant and description. 
    # If merchant is null, we can try to use description.
    
    query = """
        SELECT 
            COALESCE(merchant, description) as merchant_name,
            SUM(amount) as total_amount,
            COUNT(*) as transaction_count,
            MIN(transaction_date) as first_date,
            MAX(transaction_date) as last_date
        FROM transactions 
        WHERE transaction_date >= ? AND transaction_date <= ?
          AND direction = ?
          AND COALESCE(merchant, description) IS NOT NULL
          AND COALESCE(merchant, description) != ''
    """
    params = [date_from, date_to, direction]
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if source_bank:
        query += " AND source_bank = ?"
        params.append(source_bank)
        
    query += " GROUP BY merchant_name"
    
    if direction == "outflow":
        query += " ORDER BY abs(SUM(amount)) DESC"
    else:
        query += " ORDER BY SUM(amount) DESC"
        
    query += " LIMIT ?"
    params.append(limit)
    
    results = conn.execute(query, params).fetchall()
    
    merchants = []
    for r in results:
        merchants.append(MerchantSummary(
            merchant=r[0],
            total_amount=abs(float(r[1])), # Return as positive display value for outflows
            transaction_count=int(r[2]),
            first_date=r[3],
            last_date=r[4]
        ))
    
    latency_ms = (time.time() - start_time) * 1000
    
    evidence = Evidence(
        tool_name="top_merchants",
        row_count=len(merchants),
        query_scope={
            "date_from": str(date_from),
            "date_to": str(date_to),
            "direction": direction,
            "category": category,
            "source_bank": source_bank
        },
        calculation_method="deterministic_sql_group_by"
    )
    
    db_manager.log_event(
        "analytics_query_completed",
        "Top merchants executed",
        {
            "tool": "top_merchants",
            "row_count": len(merchants),
            "latency_ms": latency_ms
        }
    )
    
    return TopMerchantsResult(
        merchants=merchants,
        evidence=evidence
    )
