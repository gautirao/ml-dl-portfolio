import re
import logging
from typing import List, Any, Dict
from .schemas import ToolResult

logger = logging.getLogger(__name__)

def verify_answer(answer: str, tool_result: ToolResult) -> bool:
    """
    Verifies that the generated answer does not introduce unsupported numbers
    and includes evidence.
    Returns True if verified, False if rejected.
    """
    # 1. Check for evidence in tool_result
    if tool_result.tool_name not in ["clarification", "out_of_scope"] and not tool_result.evidence:
        logger.warning("Verification failed: No evidence in tool result")
        return False

    # 2. Extract numbers from answer and check if they exist in tool_result
    # This is a basic check. A more robust one would use fuzzy matching or named entity recognition.
    numbers_in_answer = re.findall(r"[-+]?\d*\.\d+|\d+", answer)
    
    # Flatten tool_result.result to check for numbers
    def flatten_values(d: Any) -> List[str]:
        values = []
        if isinstance(d, dict):
            for v in d.values():
                values.extend(flatten_values(v))
        elif isinstance(d, list):
            for v in d:
                values.extend(flatten_values(v))
        else:
            # Convert to string
            s = str(d)
            values.append(s)
            # If it's a number, also add its float representation as a string
            try:
                f = float(s)
                values.append(str(f))
                # Also add integer if it's a whole number
                if f == int(f):
                    values.append(str(int(f)))
            except (ValueError, TypeError):
                pass
        return values

    allowed_values = flatten_values(tool_result.result)
    
    # Also allow numbers from arguments (e.g. dates, limits)
    allowed_values.extend(flatten_values(tool_result.arguments))
    
    # Basic validation: every number in the answer should be related to the tool result
    # We allow small numbers (like 1, 2, 3) which might be used for lists or phrasing
    for num in numbers_in_answer:
        if len(num) > 1 and num not in allowed_values:
            # Check if it's a substring of any allowed value (e.g. "100" in "100.0")
            if not any(num in av for av in allowed_values):
                logger.warning(f"Verification failed: Number '{num}' not found in tool result")
                return False

    return True
