import logging
from .ollama_client import OllamaClient
from .schemas import ToolResult

logger = logging.getLogger(__name__)

ANSWER_SYSTEM_PROMPT = """You are the LedgerMind Answer Generator. Your job is to summarize data or explain system behavior to the user.
You will be provided with a Tool Result containing structured data.

RULES:
- Use plain, professional English.
- If the tool is 'knowledge_lookup', use the retrieved snippets to answer the user's question.
- Cite your sources. If the tool result contains 'knowledge_sources', mention the source file names (e.g., 'Source: system-overview.md').
- DO NOT introduce any numbers, dates, or merchants that are not present in the Tool Result.
- Be concise.
- Include a brief summary of the evidence (e.g., 'Based on 50 transactions...' or 'Based on the system documentation...').
- If the tool failed or returned an error, explain this to the user safely.
- Do not provide financial advice.
"""

class AnswerGenerator:
    def __init__(self, ollama: OllamaClient, model: str = "llama3.2"):
        self.ollama = ollama
        self.model = model

    async def generate_answer(self, user_message: str, tool_result: ToolResult) -> str:
        prompt = f"User asked: {user_message}\n\nTool Result: {tool_result.model_dump_json()}"
        
        try:
            answer = await self.ollama.generate(
                model=self.model,
                prompt=prompt,
                system=ANSWER_SYSTEM_PROMPT
            )
            return answer.strip()
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return self.fallback_answer(tool_result)

    def fallback_answer(self, tool_result: ToolResult) -> str:
        """
        Deterministic fallback template if LLM fails.
        """
        if tool_result.execution_status == "failed":
            return "I'm sorry, I encountered an error while processing your request."
        
        tool = tool_result.tool_name
        res = tool_result.result
        evidence = tool_result.evidence
        
        summary = f"I've processed your request using the {tool} tool. "
        if evidence:
            summary += f"Based on {evidence.get('row_count', 0)} transactions. "
            
        if tool == "spending_summary":
            summary += f"Total inflow: {res.get('total_inflow')}, Total outflow: {res.get('total_outflow')}, Net: {res.get('net_amount')}."
        elif tool == "semantic_spending_search":
            det_res = res.get("deterministic_result", {})
            summary += f"Total inflow: {det_res.get('total_inflow')}, Total outflow: {det_res.get('total_outflow')}, Net: {det_res.get('net_amount')}."
        elif tool == "top_merchants":
            merchants = [f"{m['merchant']} ({m['total_amount']})" for m in res.get("merchants", [])[:3]]
            summary += f"Top merchants: {', '.join(merchants)}."
        elif tool == "clarification":
            summary = res.get("message", "I need more information to help you.")
        elif tool == "knowledge_lookup":
            matches = res.get("matches", [])
            if matches:
                summary = f"Based on the system documentation ({matches[0].get('source')}): {matches[0].get('text')[:300]}..."
            else:
                summary = "I couldn't find any specific information about that in my knowledge base."
        else:
            summary += "The analysis is complete, but I'm having trouble generating a detailed summary right now."
            
        return summary
