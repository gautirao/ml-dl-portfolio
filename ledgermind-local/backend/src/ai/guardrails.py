import logging

logger = logging.getLogger(__name__)

REFUSAL_MESSAGE = "I can analyse your statement data, but I cannot provide regulated financial advice. I can show spending, income, recurring payments or transaction trends from your imported statements."

FORBIDDEN_KEYWORDS = [
    "invest", "investment", "portfolio", "stock", "share", "crypto", "bitcoin",
    "mortgage", "loan", "borrow", "lending",
    "insurance", "pension", "retirement",
    "tax advice", "tax planning",
    "debt advice", "debt consolidation",
    "should i buy", "should i sell", "should i cancel",
    "what should i do with my savings",
    "financial advice"
]

def check_input_guardrail(message: str) -> tuple[bool, str]:
    """
    Check if the user message violates financial advice guardrails.
    Returns (is_allowed, response_if_not_allowed)
    """
    msg_lower = message.lower()
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in msg_lower:
            logger.warning(f"Input guardrail triggered by keyword: {keyword}")
            return False, REFUSAL_MESSAGE
    return True, ""
