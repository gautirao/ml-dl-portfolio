from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import date, datetime

class Evidence(BaseModel):
    tool_name: str
    row_count: int
    query_scope: Dict[str, Any]
    calculation_method: str
    generated_at: datetime = Field(default_factory=datetime.now)

class AnalyticsResult(BaseModel):
    evidence: Evidence

class TransactionItem(BaseModel):
    id: str
    source_bank: str
    transaction_date: date
    description: str
    merchant: Optional[str]
    amount: float
    direction: str
    category: Optional[str]
    raw_row_json: Optional[Dict[str, Any]]

class TransactionSearchResult(AnalyticsResult):
    transactions: List[TransactionItem]
    total_count: int
    limit: int
    offset: int
    filters_applied: Dict[str, Any]

class SpendingSummaryResult(AnalyticsResult):
    total_outflow: float
    total_inflow: float
    net_amount: float
    transaction_count: int
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    filters_applied: Dict[str, Any]

class MerchantSummary(BaseModel):
    merchant: str
    total_amount: float
    transaction_count: int
    first_date: date
    last_date: date

class TopMerchantsResult(AnalyticsResult):
    merchants: List[MerchantSummary]

class PeriodSummary(BaseModel):
    total_outflow: float
    total_inflow: float
    net_amount: float
    transaction_count: int

class ComparePeriodsResult(AnalyticsResult):
    period_a: PeriodSummary
    period_b: PeriodSummary
    absolute_change: float
    percentage_change: Optional[float]
    interpretation_label: str

class CategoryItem(BaseModel):
    category: str
    total_outflow: float
    total_inflow: float
    net_amount: float
    transaction_count: int

class CategorySummaryResult(AnalyticsResult):
    categories: List[CategoryItem]
    uncategorised_count: int

class RecurringCandidate(BaseModel):
    merchant: Optional[str]
    description_key: str
    average_amount: float
    occurrence_count: int
    first_seen: date
    last_seen: date
    cadence: str
    confidence: float
    example_transactions: List[TransactionItem]

class RecurringPaymentsResult(AnalyticsResult):
    candidates: List[RecurringCandidate]
