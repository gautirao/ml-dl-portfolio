from pydantic import BaseModel, Field, field_validator, model_validator
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
        "knowledge_lookup",
        "clarification",
        "out_of_scope"
    ]
    arguments: Dict[str, Any]
    confidence: float = 1.0
    requires_clarification: bool = False
    clarification_question: Optional[str] = None
    risk_level: Optional[Literal["low", "medium", "high"]] = "low"
    reasoning_summary: Optional[str] = ""

    @model_validator(mode="before")
    @classmethod
    def fix_llm_json(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
            
        valid_tools = [
            "spending_summary", "semantic_spending_search", "top_merchants",
            "compare_periods", "recurring_payments", "transaction_search",
            "category_summary", "knowledge_lookup", "clarification", "out_of_scope"
        ]
        
        # If tool is missing or invalid, try to infer from intent
        if data.get("tool") not in valid_tools:
            if data.get("intent") in valid_tools:
                data["tool"] = data["intent"]
            elif not data.get("tool"):
                if "knowledge" in str(data.get("intent", "")).lower():
                    data["tool"] = "knowledge_lookup"
                elif "out_of_scope" in str(data.get("intent", "")).lower():
                    data["tool"] = "out_of_scope"
                else:
                    data["tool"] = "clarification"

        # Ensure arguments exists
        if "arguments" not in data or not isinstance(data["arguments"], dict):
            data["arguments"] = {}
            
        # Move top-level keys to arguments if they belong there
        for key in ["query", "date_from", "date_to", "merchant", "category", "limit"]:
            if key in data and key not in data["arguments"]:
                data["arguments"][key] = data[key]
                
        return data

    @field_validator("tool", mode="before")
    @classmethod
    def validate_tool(cls, v: Any) -> str:
        if v == "" or v is None:
            return "clarification"
        return v

    @field_validator("risk_level", mode="before")
    @classmethod
    def validate_risk_level(cls, v: Any) -> str:
        if v == "" or v is None:
            return "low"
        return v

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
