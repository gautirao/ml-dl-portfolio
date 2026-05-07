from typing import Optional, List
from datetime import date
from src.database.connection import db_manager
from src.tools.schemas import TopMerchantsResult, MerchantSummary, Evidence
import time

def get_top_merchants(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
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
        WHERE 1=1
    """
    params = []
    
    if date_from:
        query += " AND transaction_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND transaction_date <= ?"
        params.append(date_to)
        
    query += " AND direction = ?"
    params.append(direction)
    query += " AND COALESCE(merchant, description) IS NOT NULL AND COALESCE(merchant, description) != ''"
    
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
    
    query_scope = {
        k: str(v) for k, v in {
            "date_from": date_from,
            "date_to": date_to,
            "direction": direction,
            "category": category,
            "source_bank": source_bank
        }.items() if v is not None
    }
    if not date_from and not date_to:
        query_scope["time_range"] = "all_time"

    evidence = Evidence(
        tool_name="top_merchants",
        row_count=len(merchants),
        query_scope=query_scope,
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
