from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List
from datetime import date
from src.tools.transaction_search import search_transactions
from src.tools.spending_summary import get_spending_summary
from src.tools.top_merchants import get_top_merchants
from src.tools.compare_periods import compare_periods
from src.tools.category_summary import get_category_summary
from src.tools.recurring_payments import detect_recurring_payments
from src.tools.schemas import (
    TransactionSearchResult, SpendingSummaryResult, TopMerchantsResult,
    ComparePeriodsResult, CategorySummaryResult, RecurringPaymentsResult
)
from src.database.connection import db_manager

router = APIRouter(prefix="/api", tags=["analytics"])

@router.get("/transactions", response_model=TransactionSearchResult)
async def get_transactions(
    source_bank: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    direction: Optional[str] = Query(None, pattern="^(inflow|outflow)$"),
    merchant: Optional[str] = None,
    category: Optional[str] = None,
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be before or equal to date_to")
        
    try:
        return search_transactions(
            source_bank=source_bank,
            date_from=date_from,
            date_to=date_to,
            direction=direction,
            merchant=merchant,
            category=category,
            min_amount=min_amount,
            max_amount=max_amount,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        db_manager.log_event("analytics_query_failed", f"Transaction search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/spending-summary", response_model=SpendingSummaryResult)
async def spending_summary(
    date_from: date,
    date_to: date,
    category: Optional[str] = None,
    merchant: Optional[str] = None,
    source_bank: Optional[str] = None
):
    if date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be before or equal to date_to")
        
    try:
        return get_spending_summary(
            date_from=date_from,
            date_to=date_to,
            category=category,
            merchant=merchant,
            source_bank=source_bank
        )
    except Exception as e:
        db_manager.log_event("analytics_query_failed", f"Spending summary failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/top-merchants", response_model=TopMerchantsResult)
async def top_merchants(
    date_from: date,
    date_to: date,
    direction: str = Query("outflow", pattern="^(inflow|outflow)$"),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = None,
    source_bank: Optional[str] = None
):
    if date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be before or equal to date_to")
        
    try:
        return get_top_merchants(
            date_from=date_from,
            date_to=date_to,
            direction=direction,
            limit=limit,
            category=category,
            source_bank=source_bank
        )
    except Exception as e:
        db_manager.log_event("analytics_query_failed", f"Top merchants failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/compare-periods", response_model=ComparePeriodsResult)
async def compare_periods_endpoint(
    period_a_from: date,
    period_a_to: date,
    period_b_from: date,
    period_b_to: date,
    category: Optional[str] = None,
    merchant: Optional[str] = None,
    source_bank: Optional[str] = None
):
    if period_a_from > period_a_to or period_b_from > period_b_to:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date for both periods")
        
    try:
        return compare_periods(
            period_a_from=period_a_from,
            period_a_to=period_a_to,
            period_b_from=period_b_from,
            period_b_to=period_b_to,
            category=category,
            merchant=merchant,
            source_bank=source_bank
        )
    except Exception as e:
        db_manager.log_event("analytics_query_failed", f"Compare periods failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/category-summary", response_model=CategorySummaryResult)
async def category_summary(
    date_from: date,
    date_to: date,
    source_bank: Optional[str] = None
):
    if date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be before or equal to date_to")
        
    try:
        return get_category_summary(
            date_from=date_from,
            date_to=date_to,
            source_bank=source_bank
        )
    except Exception as e:
        db_manager.log_event("analytics_query_failed", f"Category summary failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/recurring-payments", response_model=RecurringPaymentsResult)
async def recurring_payments(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    min_occurrences: int = Query(3, ge=2),
    amount_tolerance_percent: float = Query(10.0, ge=0, le=100),
    direction: str = Query("outflow", pattern="^(inflow|outflow)$")
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be before or equal to date_to")
        
    try:
        return detect_recurring_payments(
            date_from=date_from,
            date_to=date_to,
            min_occurrences=min_occurrences,
            amount_tolerance_percent=amount_tolerance_percent,
            direction=direction
        )
    except Exception as e:
        db_manager.log_event("analytics_query_failed", f"Recurring payments failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
