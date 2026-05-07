import logging
from datetime import date
from typing import Dict, Any, Optional
from .schemas import PlannerPlan, ToolResult
from src.tools.spending_summary import get_spending_summary
from src.tools.top_merchants import get_top_merchants
from src.tools.compare_periods import compare_periods
from src.tools.recurring_payments import detect_recurring_payments
from src.tools.transaction_search import search_transactions
from src.tools.category_summary import get_category_summary

logger = logging.getLogger(__name__)

def execute_plan(plan: PlannerPlan) -> ToolResult:
    """
    Executes the tool specified in the plan.
    """
    tool_name = plan.tool
    args = plan.arguments
    
    try:
        if tool_name == "clarification":
            return ToolResult(
                tool_name=tool_name,
                arguments=args,
                result={"message": plan.clarification_question},
                evidence={},
                execution_status="success"
            )
        
        if tool_name == "out_of_scope":
            return ToolResult(
                tool_name=tool_name,
                arguments=args,
                result={"message": "I'm sorry, that request is out of my current scope."},
                evidence={},
                execution_status="success"
            )

        # Helper to convert string dates to date objects
        def to_date(d: Optional[str]) -> Optional[date]:
            if not d: return None
            return date.fromisoformat(d)

        result = None
        if tool_name == "spending_summary":
            result = get_spending_summary(
                date_from=to_date(args.get("date_from")),
                date_to=to_date(args.get("date_to")),
                category=args.get("category"),
                merchant=args.get("merchant"),
                source_bank=args.get("source_bank")
            )
        elif tool_name == "top_merchants":
            result = get_top_merchants(
                date_from=to_date(args.get("date_from")),
                date_to=to_date(args.get("date_to")),
                limit=int(args.get("limit", 10))
            )
        elif tool_name == "compare_periods":
            result = compare_periods(
                period_a_from=to_date(args.get("period_a_from")),
                period_a_to=to_date(args.get("period_a_to")),
                period_b_from=to_date(args.get("period_b_from")),
                period_b_to=to_date(args.get("period_b_to"))
            )
        elif tool_name == "recurring_payments":
            result = detect_recurring_payments(
                min_occurrences=args.get("min_occurrences", 3)
            )
        elif tool_name == "transaction_search":
            result = search_transactions(
                query=args.get("query"),
                date_from=to_date(args.get("date_from")),
                date_to=to_date(args.get("date_to")),
                min_amount=args.get("min_amount"),
                max_amount=args.get("max_amount"),
                category=args.get("category")
            )
        elif tool_name == "category_summary":
            result = get_category_summary(
                date_from=to_date(args.get("date_from")),
                date_to=to_date(args.get("date_to"))
            )
        else:
            raise ValueError(f"Unsupported tool: {tool_name}")

        # result is a Pydantic model (AnalyticsResult subclass)
        return ToolResult(
            tool_name=tool_name,
            arguments=args,
            result=result.model_dump(),
            evidence=result.evidence.model_dump() if hasattr(result, 'evidence') else {},
            execution_status="success"
        )

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return ToolResult(
            tool_name=tool_name,
            arguments=args,
            result={"error": str(e)},
            evidence={},
            execution_status="failed"
        )
