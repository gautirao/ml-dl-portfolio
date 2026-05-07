import re
from datetime import date
from typing import Dict, Any, Tuple
from .schemas import PlannerPlan

def validate_plan(plan: PlannerPlan) -> Tuple[bool, str]:
    """
    Validates the planner output.
    Returns (is_valid, error_message)
    """
    # 1. Reject unknown tools
    allowed_tools = [
        "spending_summary", "top_merchants", "compare_periods",
        "recurring_payments", "transaction_search", "category_summary",
        "clarification", "out_of_scope"
    ]
    if plan.tool not in allowed_tools:
        return False, f"Unknown tool: {plan.tool}"

    # 2. Reject SQL/code in any field
    sql_patterns = [
        r"SELECT\s", r"INSERT\s", r"UPDATE\s", r"DELETE\s", r"DROP\s", r"TRUNCATE\s",
        r"CREATE\s", r"ALTER\s", r"--", r"\/\*", r"\*\/", r";"
    ]
    code_patterns = [
        r"import\s", r"def\s", r"class\s", r"eval\(", r"exec\(", r"lambda\s"
    ]
    
    all_content = f"{plan.intent} {plan.reasoning_summary} {plan.clarification_question or ''} {str(plan.arguments)}"
    for pattern in sql_patterns + code_patterns:
        if re.search(pattern, all_content, re.IGNORECASE):
            return False, "Security violation: SQL or code detected in plan"

    # 3. Tool-specific validation
    args = plan.arguments
    
    if plan.tool in ["spending_summary", "top_merchants", "category_summary"]:
        if "date_from" in args and "date_to" in args:
            try:
                df = date.fromisoformat(args["date_from"])
                dt = date.fromisoformat(args["date_to"])
                if df > dt:
                    return False, "date_from must be before or equal to date_to"
            except ValueError:
                return False, "Invalid date format. Use YYYY-MM-DD"
    
    if plan.tool == "spending_summary":
        if "direction" in args and args["direction"] not in ["inflow", "outflow", None]:
            return False, "Invalid direction. Must be 'inflow' or 'outflow'"

    if plan.tool == "top_merchants":
        if "limit" in args:
            try:
                limit = int(args["limit"])
                if limit <= 0 or limit > 100:
                    return False, "Limit must be between 1 and 100"
            except ValueError:
                return False, "Limit must be an integer"

    if plan.tool == "compare_periods":
        required = ["period_a_from", "period_a_to", "period_b_from", "period_b_to"]
        for req in required:
            if req not in args:
                return False, f"Missing required argument: {req}"
            try:
                date.fromisoformat(args[req])
            except ValueError:
                return False, f"Invalid date format for {req}"

    return True, ""
