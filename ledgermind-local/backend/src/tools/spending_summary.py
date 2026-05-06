from typing import Optional, Dict, Any
from datetime import date
from src.database.connection import db_manager
from src.tools.schemas import SpendingSummaryResult, Evidence
import time

def get_spending_summary(
    date_from: date,
    date_to: date,
    category: Optional[str] = None,
    merchant: Optional[str] = None,
    source_bank: Optional[str] = None
) -> SpendingSummaryResult:
    start_time = time.time()
    conn = db_manager.get_connection()
    
    query = """
        SELECT 
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_inflow,
            SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as total_outflow,
            SUM(amount) as net_amount,
            COUNT(*) as transaction_count
        FROM transactions 
        WHERE transaction_date >= ? AND transaction_date <= ?
    """
    params = [date_from, date_to]
    
    filters = {
        "date_from": date_from,
        "date_to": date_to,
        "category": category,
        "merchant": merchant,
        "source_bank": source_bank
    }
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if merchant:
        query += " AND merchant ILIKE ?"
        params.append(f"%{merchant}%")
    if source_bank:
        query += " AND source_bank = ?"
        params.append(source_bank)
        
    result = conn.execute(query, params).fetchone()
    
    total_inflow = float(result[0] or 0.0)
    total_outflow = float(result[1] or 0.0)
    net_amount = float(result[2] or 0.0)
    transaction_count = int(result[3] or 0)
    
    # Rule: total_outflow should be returned as a positive display value
    display_outflow = abs(total_outflow)
    
    latency_ms = (time.time() - start_time) * 1000
    
    evidence = Evidence(
        tool_name="spending_summary",
        row_count=transaction_count,
        query_scope={k: str(v) for k, v in filters.items() if v is not None},
        calculation_method="deterministic_sql_aggregation"
    )
    
    db_manager.log_event(
        "analytics_query_completed",
        "Spending summary executed",
        {
            "tool": "spending_summary",
            "filters": {k: str(v) for k, v in filters.items() if v is not None},
            "row_count": transaction_count,
            "latency_ms": latency_ms
        }
    )
    
    return SpendingSummaryResult(
        total_outflow=display_outflow,
        total_inflow=total_inflow,
        net_amount=net_amount,
        transaction_count=transaction_count,
        date_from=date_from,
        date_to=date_to,
        filters_applied={k: v for k, v in filters.items() if v is not None},
        evidence=evidence
    )
