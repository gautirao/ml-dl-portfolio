from typing import Optional, List
from datetime import date
from src.database.connection import db_manager
from src.tools.schemas import CategorySummaryResult, CategoryItem, Evidence
import time

def get_category_summary(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    source_bank: Optional[str] = None
) -> CategorySummaryResult:
    start_time = time.time()
    conn = db_manager.get_connection()
    
    query = """
        SELECT 
            COALESCE(category, 'uncategorised') as cat_name,
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
    
    if source_bank:
        query += " AND source_bank = ?"
        params.append(source_bank)
        
    query += " GROUP BY cat_name"
    query += " ORDER BY abs(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END)) DESC"
    
    results = conn.execute(query, params).fetchall()
    
    categories = []
    uncategorised_count = 0
    
    for r in results:
        cat_name = r[0]
        item = CategoryItem(
            category=cat_name,
            total_inflow=float(r[1] or 0.0),
            total_outflow=abs(float(r[2] or 0.0)),
            net_amount=float(r[3] or 0.0),
            transaction_count=int(r[4] or 0)
        )
        categories.append(item)
        if cat_name == 'uncategorised':
            uncategorised_count = item.transaction_count
            
    latency_ms = (time.time() - start_time) * 1000
    
    evidence = Evidence(
        tool_name="category_summary",
        row_count=sum(c.transaction_count for c in categories),
        query_scope={
            "date_from": str(date_from),
            "date_to": str(date_to),
            "source_bank": source_bank
        },
        calculation_method="deterministic_sql_group_by"
    )
    
    db_manager.log_event(
        "analytics_query_completed",
        "Category summary executed",
        {
            "tool": "category_summary",
            "row_count": evidence.row_count,
            "latency_ms": latency_ms
        }
    )
    
    return CategorySummaryResult(
        categories=categories,
        uncategorised_count=uncategorised_count,
        evidence=evidence
    )
