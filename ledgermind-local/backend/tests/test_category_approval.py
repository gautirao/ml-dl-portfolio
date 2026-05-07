import pytest
import uuid
import json
import asyncio
from src.categories.suggestions import SuggestionService
from src.categories.rules import RuleService
from src.database.connection import db_manager

@pytest.fixture
def clean_db():
    db_manager.initialize_db()
    conn = db_manager.get_connection()
    # Disable foreign key checks for clean up if necessary, 
    # but DuckDB handles it or we delete in order.
    conn.execute("DELETE FROM category_suggestions")
    conn.execute("DELETE FROM merchant_rules")
    conn.execute("DELETE FROM transactions")
    yield conn

def test_generate_suggestions(clean_db):
    conn = clean_db
    # Add an uncategorised transaction
    trans_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, amount, direction) VALUES (?, ?, ?, ?, ?, ?)",
        (trans_id, 'TEST_BANK', '2023-01-01', 'AMAZON.CO.UK', -10.50, 'outflow')
    )
    
    service = SuggestionService()
    # Using run() because tests might not be async themselves
    loop = asyncio.get_event_loop()
    suggestions = loop.run_until_complete(service.generate_suggestions(limit=10))
    
    assert len(suggestions) == 1
    assert suggestions[0]['merchant_text'] == 'AMAZON.CO.UK'
    assert suggestions[0]['status'] == 'pending'
    
    # Verify in DB
    saved = conn.execute("SELECT * FROM category_suggestions").df()
    assert len(saved) == 1
    assert saved.iloc[0]['merchant_text'] == 'AMAZON.CO.UK'

def test_approve_suggestion_creates_rule(clean_db):
    conn = clean_db
    suggestion_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO category_suggestions (
            id, merchant_text, suggested_merchant, suggested_category, status
        ) VALUES (?, ?, ?, ?, ?)""",
        (suggestion_id, 'TESCO STORES', 'Tesco', 'Groceries', 'pending')
    )
    
    service = SuggestionService()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(service.approve_suggestion(suggestion_id))
    
    # Check status
    status = conn.execute("SELECT status FROM category_suggestions WHERE id = ?", (suggestion_id,)).fetchone()[0]
    assert status == 'approved'
    
    # Check rule
    rule = conn.execute("SELECT * FROM merchant_rules WHERE pattern = ?", ('TESCO STORES',)).df()
    assert len(rule) == 1
    assert rule.iloc[0]['merchant_name'] == 'Tesco'
    assert rule.iloc[0]['category'] == 'Groceries'

def test_reject_suggestion(clean_db):
    conn = clean_db
    suggestion_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO category_suggestions (id, merchant_text, status) VALUES (?, ?, ?)",
        (suggestion_id, 'RANDOM SPEND', 'pending')
    )
    
    service = SuggestionService()
    service.reject_suggestion(suggestion_id)
    
    status = conn.execute("SELECT status FROM category_suggestions WHERE id = ?", (suggestion_id,)).fetchone()[0]
    assert status == 'rejected'
    
    # No rule should be created
    rules_count = conn.execute("SELECT count(*) FROM merchant_rules").fetchone()[0]
    assert rules_count == 0

def test_apply_rules(clean_db):
    conn = clean_db
    # Add rule
    conn.execute(
        "INSERT INTO merchant_rules (id, pattern, merchant_name, category) VALUES (?, ?, ?, ?)",
        (str(uuid.uuid4()), 'TESCO', 'Tesco', 'Groceries')
    )
    
    # Add transaction
    conn.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, amount, direction) VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), 'TEST_BANK', '2023-01-01', 'TESCO STORES 1234', -20.0, 'outflow')
    )
    
    RuleService.apply_rules()
    
    # Verify transaction updated
    trans = conn.execute("SELECT merchant, category FROM transactions").df()
    assert trans.iloc[0]['merchant'] == 'Tesco'
    assert trans.iloc[0]['category'] == 'Groceries'

def test_audit_events_logged(clean_db):
    conn = clean_db
    suggestion_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO category_suggestions (id, merchant_text, status) VALUES (?, ?, ?)",
        (suggestion_id, 'AUDIT TEST', 'pending')
    )
    
    service = SuggestionService()
    service.reject_suggestion(suggestion_id)
    
    # We check that at least one such event exists (ignoring DB_INIT)
    audit = conn.execute("SELECT * FROM audit_events WHERE event_type = 'category_suggestion_rejected'").df()
    assert len(audit) >= 1
    assert audit.iloc[0]['event_type'] == 'category_suggestion_rejected'
