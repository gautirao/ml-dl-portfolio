import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app
from src.ai.schemas import PlannerPlan, ToolResult
from src.ai.validator import validate_plan

client = TestClient(app)

@pytest.fixture
def mock_ollama():
    with patch("src.api.chat.ollama_client") as mock:
        yield mock

@pytest.fixture
def mock_planner():
    with patch("src.api.chat.planner") as mock:
        mock.create_plan = AsyncMock()
        yield mock

@pytest.fixture
def mock_answer_gen():
    with patch("src.api.chat.answer_gen") as mock:
        mock.generate_answer = AsyncMock()
        mock.fallback_answer = MagicMock(return_value="Fallback answer")
        yield mock

def test_chat_input_guardrail_refusal():
    response = client.post("/api/chat", json={"message": "Should I invest in Bitcoin?"})
    assert response.status_code == 200
    data = response.json()
    assert "cannot provide regulated financial advice" in data["answer"]
    assert data["guardrails"]["input_allowed"] is False
    assert data["plan"] is None

def test_validator_sql_injection():
    plan = PlannerPlan(
        intent="malicious",
        tool="spending_summary",
        arguments={"date_from": "2023-01-01; DROP TABLE transactions;--"},
        confidence=1.0,
        requires_clarification=False,
        risk_level="high",
        reasoning_summary="Attempting injection"
    )
    is_valid, error = validate_plan(plan)
    assert is_valid is False
    assert "SQL or code detected" in error

def test_validator_invalid_dates():
    plan = PlannerPlan(
        intent="bad dates",
        tool="spending_summary",
        arguments={"date_from": "2024-02-01", "date_to": "2024-01-01"},
        confidence=1.0,
        requires_clarification=False,
        risk_level="low",
        reasoning_summary="df > dt"
    )
    is_valid, error = validate_plan(plan)
    assert is_valid is False
    assert "date_from must be before" in error

@pytest.mark.anyio
async def test_chat_successful_spending_summary(mock_planner, mock_answer_gen):
    # Mock successful plan
    mock_planner.create_plan.return_value = PlannerPlan(
        intent="spending",
        tool="spending_summary",
        arguments={"date_from": "2024-01-01", "date_to": "2024-01-31"},
        confidence=0.95,
        requires_clarification=False,
        risk_level="low",
        reasoning_summary="User wants spending"
    )
    
    # Mock successful answer - use a number that is exactly represented as string of float
    mock_answer_gen.generate_answer.return_value = "You spent 500.0. Based on 10 transactions."
    
    with patch("src.api.chat.execute_plan") as mock_exec:
        mock_exec.return_value = ToolResult(
            tool_name="spending_summary",
            arguments={"date_from": "2024-01-01", "date_to": "2024-01-31"},
            result={"total_outflow": 500.0, "transaction_count": 10},
            evidence={"row_count": 10, "tool_name": "spending_summary"},
            execution_status="success"
        )
        
        response = client.post("/api/chat", json={"message": "How much did I spend?"})
        assert response.status_code == 200
        data = response.json()
        assert "500.0" in data["answer"]
        assert data["guardrails"]["plan_valid"] is True
        assert data["guardrails"]["output_verified"] is True

@pytest.mark.anyio
async def test_chat_verification_failure_fallback(mock_planner, mock_answer_gen):
    mock_planner.create_plan.return_value = PlannerPlan(
        intent="spending",
        tool="spending_summary",
        arguments={"date_from": "2024-01-01", "date_to": "2024-01-31"},
        confidence=0.95,
        requires_clarification=False,
        risk_level="low",
        reasoning_summary="User wants spending"
    )
    
    # LLM invents a number not in tool result
    mock_answer_gen.generate_answer.return_value = "You spent 9999.99 in January."
    mock_answer_gen.fallback_answer.return_value = "Fallback: You spent 500.0."
    
    with patch("src.api.chat.execute_plan") as mock_exec:
        mock_exec.return_value = ToolResult(
            tool_name="spending_summary",
            arguments={"date_from": "2024-01-01", "date_to": "2024-01-31"},
            result={"total_outflow": 500.00},
            evidence={"row_count": 10},
            execution_status="success"
        )
        
        response = client.post("/api/chat", json={"message": "Spending?"})
        assert response.status_code == 200
        data = response.json()
        assert "500.0" in data["answer"]
        assert "9999.99" not in data["answer"]
        assert data["guardrails"]["output_verified"] is False

@pytest.mark.anyio
async def test_chat_clarification(mock_planner):
    mock_planner.create_plan.return_value = PlannerPlan(
        intent="vague",
        tool="clarification",
        arguments={},
        confidence=0.5,
        requires_clarification=True,
        clarification_question="Which month?",
        risk_level="low",
        reasoning_summary="Missing dates"
    )
    
    response = client.post("/api/chat", json={"message": "Show me spending"})
    assert response.status_code == 200
    data = response.json()
    assert "Which month?" in data["answer"]
    assert data["plan"]["tool"] == "clarification"

def test_audit_logging_occurred(caplog):
    import logging
    # Set caplog level to INFO to capture audit events
    caplog.set_level(logging.INFO)
    client.post("/api/chat", json={"message": "Should I invest?"})
    assert "AUDIT_EVENT" in caplog.text
    assert "input_guardrail_refused" in caplog.text
