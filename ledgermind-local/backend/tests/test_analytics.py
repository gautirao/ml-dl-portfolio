import pytest
from datetime import date, timedelta
import uuid
import json
from src.database.connection import db_manager
from src.tools.transaction_search import search_transactions
from src.tools.spending_summary import get_spending_summary
from src.tools.top_merchants import get_top_merchants
from src.tools.compare_periods import compare_periods
from src.tools.category_summary import get_category_summary
from src.tools.recurring_payments import detect_recurring_payments
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture(autouse=True)
def setup_db():
    # Initialize DB and clear transactions before each test
    db_manager.initialize_db()
    conn = db_manager.get_connection()
    conn.execute("DELETE FROM transactions")
    conn.execute("DELETE FROM audit_events")
    yield

def seed_transactions(transactions):
    conn = db_manager.get_connection()
    for t in transactions:
        t_id = str(uuid.uuid4())
        # Fix date serialization for JSON
        raw_json = json.dumps(t, default=lambda x: x.isoformat() if isinstance(x, date) else str(x))
        conn.execute(
            """INSERT INTO transactions 
               (id, source_bank, transaction_date, description, merchant, amount, direction, category, transaction_fingerprint, raw_row_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                t_id, t.get("source_bank", "MONZO"), t["date"], t.get("description", "Test Transaction"), 
                t.get("merchant"), t["amount"], t["direction"], t.get("category"),
                str(uuid.uuid4()), raw_json
            )
        )

def test_spending_summary_basic_totals():
    seed_transactions([
        {"date": date(2024, 1, 1), "amount": -10.0, "direction": "outflow", "description": "Coffee"},
        {"date": date(2024, 1, 2), "amount": -20.0, "direction": "outflow", "description": "Lunch"},
        {"date": date(2024, 1, 3), "amount": 100.0, "direction": "inflow", "description": "Salary"},
    ])
    
    result = get_spending_summary(date(2024, 1, 1), date(2024, 1, 3))
    
    assert result.total_outflow == 30.0
    assert result.total_inflow == 100.0
    assert result.net_amount == 70.0
    assert result.transaction_count == 3
    assert result.evidence.tool_name == "spending_summary"

def test_spending_summary_filters():
    seed_transactions([
        {"date": date(2024, 1, 1), "amount": -10.0, "direction": "outflow", "description": "Coffee", "category": "Food", "merchant": "Starbucks"},
        {"date": date(2024, 1, 2), "amount": -20.0, "direction": "outflow", "description": "Lunch", "category": "Food", "merchant": "Pret"},
        {"date": date(2024, 1, 3), "amount": -50.0, "direction": "outflow", "description": "Train", "category": "Transport", "merchant": "TFL"},
    ])
    
    # Category filter
    res_cat = get_spending_summary(date(2024, 1, 1), date(2024, 1, 3), category="Food")
    assert res_cat.total_outflow == 30.0
    assert res_cat.transaction_count == 2
    
    # Merchant filter
    res_merch = get_spending_summary(date(2024, 1, 1), date(2024, 1, 3), merchant="Starbucks")
    assert res_merch.total_outflow == 10.0
    assert res_merch.transaction_count == 1

def test_top_merchants_ranking():
    seed_transactions([
        {"date": date(2024, 1, 1), "amount": -10.0, "direction": "outflow", "merchant": "Starbucks"},
        {"date": date(2024, 1, 2), "amount": -10.0, "direction": "outflow", "merchant": "Starbucks"},
        {"date": date(2024, 1, 3), "amount": -50.0, "direction": "outflow", "merchant": "Amazon"},
        {"date": date(2024, 1, 4), "amount": -30.0, "direction": "outflow", "merchant": "TFL"},
    ])
    
    result = get_top_merchants(date(2024, 1, 1), date(2024, 1, 5), limit=2)
    
    assert len(result.merchants) == 2
    assert result.merchants[0].merchant == "Amazon"
    assert result.merchants[0].total_amount == 50.0
    assert result.merchants[1].merchant == "TFL"
    assert result.merchants[1].total_amount == 30.0

def test_compare_periods():
    # Period A: 30 spent
    seed_transactions([
        {"date": date(2024, 1, 1), "amount": -30.0, "direction": "outflow", "description": "A"},
    ])
    # Period B: 45 spent
    seed_transactions([
        {"date": date(2024, 2, 1), "amount": -45.0, "direction": "outflow", "description": "B"},
    ])
    
    result = compare_periods(
        date(2024, 1, 1), date(2024, 1, 31),
        date(2024, 2, 1), date(2024, 2, 28)
    )
    
    assert result.period_a.total_outflow == 30.0
    assert result.period_b.total_outflow == 45.0
    assert result.absolute_change == 15.0
    assert result.percentage_change == 50.0
    assert result.interpretation_label == "increased"

def test_compare_periods_zero_baseline():
    # Period A: 0 spent
    # Period B: 45 spent
    seed_transactions([
        {"date": date(2024, 2, 1), "amount": -45.0, "direction": "outflow", "description": "B"},
    ])
    
    result = compare_periods(
        date(2024, 1, 1), date(2024, 1, 31),
        date(2024, 2, 1), date(2024, 2, 28)
    )
    
    assert result.period_a.total_outflow == 0.0
    assert result.period_b.total_outflow == 45.0
    assert result.percentage_change is None
    assert result.interpretation_label == "increased"

def test_category_summary():
    seed_transactions([
        {"date": date(2024, 1, 1), "amount": -10.0, "direction": "outflow", "category": "Food"},
        {"date": date(2024, 1, 2), "amount": -20.0, "direction": "outflow", "category": "Food"},
        {"date": date(2024, 1, 3), "amount": -50.0, "direction": "outflow", "category": None}, # Uncategorised
    ])
    
    result = get_category_summary(date(2024, 1, 1), date(2024, 1, 3))
    
    assert len(result.categories) == 2
    food = next(c for c in result.categories if c.category == "Food")
    assert food.total_outflow == 30.0
    assert result.uncategorised_count == 1

def test_recurring_payment_monthly():
    # Monthly pattern
    base_date = date(2024, 1, 1)
    txs = []
    for i in range(4):
        txs.append({
            "date": base_date + timedelta(days=i*30),
            "amount": -15.99,
            "direction": "outflow",
            "merchant": "Netflix",
            "description": "Netflix Subscription"
        })
    seed_transactions(txs)
    
    result = detect_recurring_payments(min_occurrences=3)
    
    assert len(result.candidates) == 1
    netflix = result.candidates[0]
    assert netflix.merchant == "Netflix"
    assert netflix.cadence == "monthly"
    assert netflix.confidence > 0.8

def test_recurring_payment_false_positive():
    # Irregular pattern
    seed_transactions([
        {"date": date(2024, 1, 1), "amount": -10.0, "direction": "outflow", "merchant": "Shop A"},
        {"date": date(2024, 1, 5), "amount": -15.0, "direction": "outflow", "merchant": "Shop A"},
        {"date": date(2024, 1, 20), "amount": -12.0, "direction": "outflow", "merchant": "Shop A"},
    ])
    
    result = detect_recurring_payments(min_occurrences=3)
    # With confidence threshold and irregular cadence, it should either be filtered or have low confidence
    # In my implementation, irregular with < 4 rows is skipped.
    assert len(result.candidates) == 0

def test_transaction_search_filters():
    seed_transactions([
        {"date": date(2024, 1, 1), "amount": -10.0, "direction": "outflow", "category": "A", "merchant": "M1"},
        {"date": date(2024, 1, 2), "amount": -20.0, "direction": "outflow", "category": "B", "merchant": "M2"},
        {"date": date(2024, 1, 3), "amount": -30.0, "direction": "outflow", "category": "A", "merchant": "M3"},
    ])
    
    result = search_transactions(category="A", limit=10)
    assert result.total_count == 2
    assert len(result.transactions) == 2
    
    result_amt = search_transactions(min_amount=15, max_amount=25)
    assert result_amt.total_count == 1
    assert result_amt.transactions[0].amount == -20.0

def test_audit_events_written():
    get_spending_summary(date(2024, 1, 1), date(2024, 1, 31))
    
    conn = db_manager.get_connection()
    events = conn.execute("SELECT event_type, metadata FROM audit_events WHERE event_type = 'analytics_query_completed'").fetchall()
    
    assert len(events) > 0
    meta = json.loads(events[0][1])
    assert meta["tool"] == "spending_summary"

client = TestClient(app)

def test_invalid_date_range_returns_400():
    response = client.get("/api/analytics/spending-summary?date_from=2024-01-31&date_to=2024-01-01")
    assert response.status_code == 400
    assert "date_from must be before or equal to date_to" in response.json()["detail"]

def test_invalid_direction_returns_400():
    response = client.get("/api/transactions?direction=invalid")
    assert response.status_code == 422 # FastAPI returns 422 for validation errors by default

def test_pagination_and_limit_bounds():
    seed_transactions([{"date": date(2024, 1, 1), "amount": -10.0, "direction": "outflow"}] * 10)
    
    response = client.get("/api/transactions?limit=5&offset=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["transactions"]) == 5
    assert data["limit"] == 5
    assert data["offset"] == 2
    assert data["total_count"] == 10
