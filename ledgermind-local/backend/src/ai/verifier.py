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
    
    # Flat list of all numbers in tool result as floats for robust comparison
    def extract_numbers(d: Any) -> List[float]:
        nums = []
        if isinstance(d, dict):
            for v in d.values():
                nums.extend(extract_numbers(v))
        elif isinstance(d, list):
            for v in d:
                nums.extend(extract_numbers(v))
        else:
            # Extract all potential numbers from the string representation
            # This handles dates (2024-01-01 -> 2024, 1, 1) and other formatted strings
            found = re.findall(r"[-+]?\d*\.\d+|\d+", str(d))
            for f_str in found:
                try:
                    nums.append(float(f_str))
                except (ValueError, TypeError):
                    pass
        return nums

    allowed_nums = extract_numbers(tool_result.result)
    allowed_nums.extend(extract_numbers(tool_result.arguments))
    
    # Basic validation: every number in the answer should be related to the tool result
    for num_str in numbers_in_answer:
        if len(num_str) > 1:
            try:
                num_float = float(num_str)
                # Check if this float exists in allowed_nums (with small epsilon)
                if not any(abs(num_float - an) < 0.001 for an in allowed_nums):
                    # One more check: is it a year? (e.g. 2026)
                    # Years often appear in dates.
                    logger.warning(f"Verification failed: Number '{num_str}' not found in tool result")
                    return False
            except ValueError:
                continue

    return True
