from typing import Optional, List, Dict, Any
from datetime import date, timedelta
from src.database.connection import db_manager
from src.tools.schemas import RecurringPaymentsResult, RecurringCandidate, TransactionItem, Evidence
import time
import json
from collections import defaultdict
import statistics

def detect_recurring_payments(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    min_occurrences: int = 3,
    amount_tolerance_percent: float = 10.0,
    direction: str = "outflow"
) -> RecurringPaymentsResult:
    start_time = time.time()
    conn = db_manager.get_connection()
    
    # Fetch candidate groups (merchant or description)
    query = """
        SELECT 
            COALESCE(merchant, description) as description_key,
            id, source_bank, transaction_date, description, merchant, amount, direction, category, raw_row_json
        FROM transactions 
        WHERE direction = ?
    """
    params = [direction]
    
    if date_from:
        query += " AND transaction_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND transaction_date <= ?"
        params.append(date_to)
        
    query += " ORDER BY transaction_date ASC"
    
    results = conn.execute(query, params).fetchall()
    
    groups = defaultdict(list)
    for r in results:
        key = r[0]
        groups[key].append(r)
        
    candidates = []
    
    for key, rows in groups.items():
        if len(rows) < min_occurrences:
            continue
            
        amounts = [abs(float(r[6])) for r in rows]
        dates = [r[3] for r in rows]
        
        # Stability of amounts
        avg_amount = statistics.mean(amounts)
        std_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
        amount_stability = 1.0 - (std_amount / avg_amount if avg_amount > 0 else 0)
        
        # Check if amounts are within tolerance
        out_of_tolerance = False
        if avg_amount > 0:
            out_of_tolerance = any(abs(a - avg_amount) / avg_amount > (amount_tolerance_percent / 100) for a in amounts)
        
        if out_of_tolerance and len(amounts) < 5: 
             # Check if at least min_occurrences are within tolerance?
             # For now, let's just use confidence.
             pass

        # Cadence analysis
        intervals = []
        for i in range(1, len(dates)):
            intervals.append((dates[i] - dates[i-1]).days)
            
        avg_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
        cadence_stability = 1.0 - (std_interval / avg_interval if avg_interval > 0 else 0)
        
        cadence = "irregular"
        if 6 <= avg_interval <= 8:
            cadence = "weekly"
        elif 13 <= avg_interval <= 15:
            cadence = "fortnightly"
        elif 25 <= avg_interval <= 35:
            cadence = "monthly"
        elif 26 <= avg_interval <= 30: # Overlap with monthly, but specific to 4-weeks
            cadence = "four-weekly"
        elif 85 <= avg_interval <= 95:
            cadence = "quarterly"
        elif 360 <= avg_interval <= 370:
            cadence = "yearly"
            
        if cadence == "irregular" and len(rows) < 4:
            continue # Too irregular for a small sample
            
        confidence = (amount_stability * 0.4) + (cadence_stability * 0.4) + (min(len(rows), 10) / 10 * 0.2)
        if out_of_tolerance:
            confidence *= 0.5
            
        if confidence < 0.4:
            continue
            
        example_transactions = []
        for r in rows[:3]: # Just return first 3 as examples
            example_transactions.append(TransactionItem(
                id=str(r[1]),
                source_bank=r[2],
                transaction_date=r[3],
                description=r[4],
                merchant=r[5],
                amount=float(r[6]),
                direction=r[7],
                category=r[8],
                raw_row_json=json.loads(r[9]) if r[9] else None
            ))
            
        candidates.append(RecurringCandidate(
            merchant=rows[0][5],
            description_key=key,
            average_amount=round(avg_amount, 2),
            occurrence_count=len(rows),
            first_seen=dates[0],
            last_seen=dates[-1],
            cadence=cadence,
            confidence=round(max(0, min(1, confidence)), 2),
            example_transactions=example_transactions
        ))
        
    candidates.sort(key=lambda x: x.confidence, reverse=True)
    
    latency_ms = (time.time() - start_time) * 1000
    
    evidence = Evidence(
        tool_name="recurring_payments",
        row_count=len(candidates),
        query_scope={
            "min_occurrences": min_occurrences,
            "direction": direction
        },
        calculation_method="heuristic_cadence_analysis"
    )
    
    db_manager.log_event(
        "analytics_query_completed",
        "Recurring payments executed",
        {
            "tool": "recurring_payments",
            "candidates_found": len(candidates),
            "latency_ms": latency_ms
        }
    )
    
    return RecurringPaymentsResult(
        candidates=candidates,
        evidence=evidence
    )
