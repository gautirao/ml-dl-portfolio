import pytest
from src.ai.planner import Planner
from src.ai.ollama_client import OllamaClient
from unittest.mock import AsyncMock

@pytest.fixture
def mock_ollama():
    mock = AsyncMock(spec=OllamaClient)
    return mock

@pytest.mark.asyncio
async def test_planner_selects_semantic_top_merchants(mock_ollama):
    planner = Planner(mock_ollama)
    
    # Mock response for "Which shops do I drink coffee at the most?"
    mock_ollama.generate.return_value = """
    {
      "intent": "merchant_ranking",
      "tool": "semantic_top_merchants",
      "arguments": {
        "query": "coffee",
        "rank_by": "transaction_count"
      },
      "confidence": 0.95,
      "requires_clarification": false,
      "reasoning_summary": "User is asking for a ranking of merchants related to coffee."
    }
    """
    
    plan = await planner.create_plan("Which shops do I drink coffee at the most?")
    assert plan.tool == "semantic_top_merchants"
    assert plan.arguments["query"] == "coffee"
    assert plan.arguments["rank_by"] == "transaction_count"

@pytest.mark.asyncio
async def test_planner_selects_semantic_spending_for_totals(mock_ollama):
    planner = Planner(mock_ollama)
    
    # Mock response for "How much did I spend on coffee?"
    mock_ollama.generate.return_value = """
    {
      "intent": "spending_total",
      "tool": "semantic_spending_search",
      "arguments": {
        "query": "coffee"
      },
      "confidence": 0.95,
      "requires_clarification": false,
      "reasoning_summary": "User is asking for total spending on coffee."
    }
    """
    
    plan = await planner.create_plan("How much did I spend on coffee?")
    assert plan.tool == "semantic_spending_search"
    assert plan.arguments["query"] == "coffee"

@pytest.mark.asyncio
async def test_planner_selects_top_merchants_for_general_request(mock_ollama):
    planner = Planner(mock_ollama)
    
    # Mock response for "Who are my top merchants?"
    mock_ollama.generate.return_value = """
    {
      "intent": "general_merchant_ranking",
      "tool": "top_merchants",
      "arguments": {},
      "confidence": 0.95,
      "requires_clarification": false,
      "reasoning_summary": "User is asking for top merchants across all categories."
    }
    """
    
    plan = await planner.create_plan("Who are my top merchants?")
    assert plan.tool == "top_merchants"
