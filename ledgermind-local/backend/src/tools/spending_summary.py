from typing import Optional, Dict, Any, List, Union
from datetime import date
from src.database.connection import db_manager
from src.tools.schemas import SpendingSummaryResult, Evidence
import time

def get_spending_summary(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    category: Optional[Union[str, List[str]]] = None,
    merchant: Optional[Union[str, List[str]]] = None,
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
        WHERE 1=1
    """
    params = []
    
    if date_from:
        query += " AND transaction_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND transaction_date <= ?"
        params.append(date_to)
    
    filters = {
        "date_from": date_from,
        "date_to": date_to,
        "category": category,
        "merchant": merchant,
        "source_bank": source_bank
    }
    
    if category:
        if isinstance(category, list):
            placeholders = ", ".join(["?" for _ in category])
            query += f" AND category IN ({placeholders})"
            params.extend(category)
        else:
            query += " AND category = ?"
            params.append(category)
            
    if merchant:
        if isinstance(merchant, list):
            placeholders = ", ".join(["?" for _ in merchant])
            query += f" AND merchant IN ({placeholders})"
            params.extend(merchant)
        else:
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
    
    query_scope = {k: str(v) for k, v in filters.items() if v is not None}
    if not date_from and not date_to:
        query_scope["time_range"] = "all_time"
        
    evidence = Evidence(
        tool_name="spending_summary",
        row_count=transaction_count,
        query_scope=query_scope,
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
