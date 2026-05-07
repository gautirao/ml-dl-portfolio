import json
import logging
from datetime import date
from typing import Optional
from .ollama_client import OllamaClient
from .schemas import PlannerPlan

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are the LedgerMind Planner. Your job is to translate user requests into a structured JSON plan.
You have access to several deterministic tools. You must return ONLY valid JSON.

TOOLS:
- spending_summary: Get total inflow/outflow for a date range. Args: date_from (YYYY-MM-DD), date_to (YYYY-MM-DD), direction (optional: 'inflow'|'outflow').
- top_merchants: Get top merchants by spending. Args: date_from (YYYY-MM-DD), date_to (YYYY-MM-DD), limit (optional, default 10).
- compare_periods: Compare two date ranges. Args: period_a_from, period_a_to, period_b_from, period_b_to.
- recurring_payments: Detect potential recurring payments. Args: min_occurrences (optional, default 3).
- transaction_search: Search for specific transactions. Args: query (optional), date_from (optional), date_to (optional), min_amount (optional), max_amount (optional), category (optional).
- category_summary: Summary of spending by category. Args: date_from, date_to.
- clarification: Use when the request is ambiguous (e.g. missing dates).
- out_of_scope: Use when the request cannot be handled by the tools.

RULES:
- Return ONLY JSON.
- No chain-of-thought, no SQL, no code.
- No filesystem paths.
- No raw CSV access.
- Current date is {current_date}.
- If dates are missing and cannot be reasonably inferred (e.g. 'last month' is okay), use 'clarification'.
- Default date range for vague requests is the last 30 days if appropriate, otherwise ask for clarification.

JSON SCHEMA:
{{
  "intent": "string",
  "tool": "spending_summary|top_merchants|compare_periods|recurring_payments|transaction_search|category_summary|clarification|out_of_scope",
  "arguments": {{}},
  "confidence": 0.0,
  "requires_clarification": false,
  "clarification_question": null,
  "risk_level": "low|medium|high",
  "reasoning_summary": "brief user-visible summary"
}}
"""

class Planner:
    def __init__(self, ollama: OllamaClient, model: str = "llama3"):
        self.ollama = ollama
        self.model = model

    async def create_plan(self, message: str) -> PlannerPlan:
        system_prompt = PLANNER_SYSTEM_PROMPT.format(current_date=date.today().isoformat())
        
        response_text = await self.ollama.generate(
            model=self.model,
            prompt=message,
            system=system_prompt,
            json_format=True
        )
        
        try:
            plan_dict = json.loads(response_text)
            return PlannerPlan(**plan_dict)
        except Exception as e:
            logger.error(f"Failed to parse planner response: {e}. Raw response: {response_text}")
            # Fallback to clarification if LLM fails to provide valid JSON
            return PlannerPlan(
                intent="unknown",
                tool="clarification",
                arguments={},
                confidence=0.0,
                requires_clarification=True,
                clarification_question="I'm sorry, I couldn't understand that request. Could you please rephrase it?",
                risk_level="low",
                reasoning_summary="Failed to parse LLM response"
            )
