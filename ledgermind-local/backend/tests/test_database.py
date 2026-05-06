import pytest
import os
from pathlib import Path
from src.database.connection import DatabaseManager

@pytest.fixture
def test_db_manager(tmp_path):
    db_file = tmp_path / "test_ledger.db"
    manager = DatabaseManager(db_path=str(db_file))
    return manager

def test_database_initialization(test_db_manager):
    test_db_manager.initialize_db()
    conn = test_db_manager.get_connection()
    
    # Check if tables exist
    tables = conn.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]
    
    assert "transactions" in table_names
    assert "uploaded_files" in table_names
    assert "audit_events" in table_names
    assert "merchant_rules" in table_names

def test_audit_log_entry(test_db_manager):
    test_db_manager.initialize_db()
    conn = test_db_manager.get_connection()
    
    # Verify the DB_INIT event was logged
    event = conn.execute("SELECT event_type, description FROM audit_events WHERE event_type = 'DB_INIT'").fetchone()
    assert event is not None
    assert event[0] == "DB_INIT"
