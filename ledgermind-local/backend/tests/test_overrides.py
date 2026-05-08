import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database.connection import db_manager
import uuid

client = TestClient(app)

@pytest.fixture
def clean_db():
    db_manager.initialize_db()
    conn = db_manager.get_connection()
    conn.execute("DELETE FROM transaction_category_overrides")
    conn.execute("DELETE FROM transactions")
    conn.execute("DELETE FROM merchant_rules")
    conn.execute("DELETE FROM audit_events")
    yield conn

def test_transaction_override_changes_effective_category(clean_db):
    # 1. Insert a transaction
    tx_id = str(uuid.uuid4())
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (tx_id, "TEST_BANK", "2024-01-01", "Sainsbury's", -10.0, "outflow", "groceries")
    )
    
    # 2. Check initial state
    response = client.get("/api/transactions")
    data = response.json()
    assert data["transactions"][0]["category"] == "groceries"
    assert data["transactions"][0]["effective_category"] == "groceries"
    assert data["transactions"][0]["category_source"] == "imported"
    
    # 3. Apply override
    client.post(
        f"/api/transactions/{tx_id}/category-override",
        json={"new_category": "fuel", "reason": "It was petrol"}
    )
    
    # 4. Check updated state
    response = client.get("/api/transactions")
    data = response.json()
    assert data["transactions"][0]["category"] == "groceries"
    assert data["transactions"][0]["effective_category"] == "fuel"
    assert data["transactions"][0]["category_source"] == "override"
    
    # 5. Check audit event
    audit = clean_db.execute("SELECT event_type FROM audit_events WHERE event_type = 'transaction_category_override_created'").fetchone()
    assert audit is not None

def test_category_summary_uses_override(clean_db):
    tx_id = str(uuid.uuid4())
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (tx_id, "TEST_BANK", "2024-01-01", "Sainsbury's", -10.0, "outflow", "groceries")
    )
    
    # Apply override
    client.post(
        f"/api/transactions/{tx_id}/category-override",
        json={"new_category": "fuel"}
    )
    
    response = client.get("/api/analytics/category-summary")
    data = response.json()
    
    # Should find fuel, not groceries
    categories = [c["category"] for c in data["categories"]]
    assert "fuel" in categories
    assert "groceries" not in categories

def test_spending_summary_category_filter_uses_override(clean_db):
    tx_id = str(uuid.uuid4())
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (tx_id, "TEST_BANK", "2024-01-01", "Sainsbury's", -10.0, "outflow", "groceries")
    )
    
    # Apply override to fuel
    client.post(
        f"/api/transactions/{tx_id}/category-override",
        json={"new_category": "fuel"}
    )
    
    # Filter by groceries - should be 0
    response = client.get("/api/analytics/spending-summary?category=groceries")
    assert response.json()["transaction_count"] == 0
    
    # Filter by fuel - should be 1
    response = client.get("/api/analytics/spending-summary?category=fuel")
    assert response.json()["transaction_count"] == 1

def test_removing_override_restores_previous_category(clean_db):
    tx_id = str(uuid.uuid4())
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (tx_id, "TEST_BANK", "2024-01-01", "Sainsbury's", -10.0, "outflow", "groceries")
    )
    
    client.post(f"/api/transactions/{tx_id}/category-override", json={"new_category": "fuel"})
    client.delete(f"/api/transactions/{tx_id}/category-override")
    
    response = client.get("/api/transactions")
    assert response.json()["transactions"][0]["effective_category"] == "groceries"
    assert response.json()["transactions"][0]["category_source"] == "imported"

def test_merchant_rule_source(clean_db):
    tx_id = str(uuid.uuid4())
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, merchant, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (tx_id, "TEST_BANK", "2024-01-01", "Sainsbury's Store", "Sainsbury's", -10.0, "outflow", "groceries")
    )
    
    # Add a merchant rule that matches
    clean_db.execute(
        "INSERT INTO merchant_rules (id, pattern, merchant_name, category) VALUES (?, ?, ?, ?)",
        (str(uuid.uuid4()), "Sainsbury's", "Sainsbury's", "groceries")
    )
    
    response = client.get("/api/transactions")
    assert response.json()["transactions"][0]["category_source"] == "merchant_rule"
