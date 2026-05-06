from datetime import date
from typing import Optional
from src.tools.spending_summary import get_spending_summary
from src.tools.schemas import ComparePeriodsResult, PeriodSummary, Evidence
from src.database.connection import db_manager
import time

def compare_periods(
    period_a_from: date,
    period_a_to: date,
    period_b_from: date,
    period_b_to: date,
    category: Optional[str] = None,
    merchant: Optional[str] = None,
    source_bank: Optional[str] = None
) -> ComparePeriodsResult:
    start_time = time.time()
    
    summary_a = get_spending_summary(
        date_from=period_a_from,
        date_to=period_a_to,
        category=category,
        merchant=merchant,
        source_bank=source_bank
    )
    
    summary_b = get_spending_summary(
        date_from=period_b_from,
        date_to=period_b_to,
        category=category,
        merchant=merchant,
        source_bank=source_bank
    )
    
    period_a = PeriodSummary(
        total_outflow=summary_a.total_outflow,
        total_inflow=summary_a.total_inflow,
        net_amount=summary_a.net_amount,
        transaction_count=summary_a.transaction_count
    )
    
    period_b = PeriodSummary(
        total_outflow=summary_b.total_outflow,
        total_inflow=summary_b.total_inflow,
        net_amount=summary_b.net_amount,
        transaction_count=summary_b.transaction_count
    )
    
    # Comparison based on outflow by default as per common requirement
    # But let's calculate absolute change in net amount or outflow?
    # Prompt says: Be explicit whether comparison is based on outflow by default.
    # Let's use outflow for the primary change metric.
    
    val_a = period_a.total_outflow
    val_b = period_b.total_outflow
    
    absolute_change = val_b - val_a
    percentage_change = None
    
    if val_a != 0:
        percentage_change = (absolute_change / val_a) * 100
    
    if absolute_change > 0.01:
        interpretation_label = "increased"
    elif absolute_change < -0.01:
        interpretation_label = "decreased"
    elif period_a.transaction_count == 0 and period_b.transaction_count == 0:
        interpretation_label = "insufficient_data"
    else:
        interpretation_label = "unchanged"

    latency_ms = (time.time() - start_time) * 1000
    
    evidence = Evidence(
        tool_name="compare_periods",
        row_count=period_a.transaction_count + period_b.transaction_count,
        query_scope={
            "period_a": f"{period_a_from} to {period_a_to}",
            "period_b": f"{period_b_from} to {period_b_to}",
            "category": category
        },
        calculation_method="comparative_aggregation"
    )
    
    db_manager.log_event(
        "analytics_query_completed",
        "Compare periods executed",
        {
            "tool": "compare_periods",
            "absolute_change": absolute_change,
            "latency_ms": latency_ms
        }
    )
    
    return ComparePeriodsResult(
        period_a=period_a,
        period_b=period_b,
        absolute_change=round(absolute_change, 2),
        percentage_change=round(percentage_change, 2) if percentage_change is not None else None,
        interpretation_label=interpretation_label,
        evidence=evidence
    )
