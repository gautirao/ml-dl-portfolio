from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime

class PlannerPlan(BaseModel):
    intent: str
    tool: Literal[
        "spending_summary",
        "semantic_spending_search",
        "top_merchants",
        "compare_periods",
        "recurring_payments",
        "transaction_search",
        "category_summary",
        "clarification",
        "out_of_scope"
    ]
    arguments: Dict[str, Any]
    confidence: float
    requires_clarification: bool
    clarification_question: Optional[str] = None
    risk_level: Literal["low", "medium", "high"]
    reasoning_summary: str

class ToolResult(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Any
    evidence: Dict[str, Any]
    execution_status: Literal["success", "failed"]

class Guardrails(BaseModel):
    input_allowed: bool
    plan_valid: bool
    output_verified: bool

class ChatResponse(BaseModel):
    answer: str
    plan: Optional[PlannerPlan] = None
    tool_result: Optional[ToolResult] = None
    evidence: Optional[Dict[str, Any]] = None
    guardrails: Guardrails

class AuditEvent(BaseModel):
    event_type: str
    conversation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(default_factory=dict)
