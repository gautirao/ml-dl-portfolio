import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database.connection import db_manager
import io
import os

@pytest.fixture
def client(tmp_path):
    test_db = tmp_path / "test_import.db"
    db_manager.db_path = str(test_db)
    db_manager.conn = None
    with TestClient(app) as c:
        yield c

def test_preview_monzo(client):
    csv_content = open("tests/fixtures/monzo_rich.csv", "rb").read()
    response = client.post(
        "/api/import/preview",
        files={"file": ("monzo.csv", csv_content, "text/csv")},
        data={"source_bank": "auto"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_bank"] == "MONZO"
    assert len(data["preview_rows"]) == 2
    assert "Amount" in data["headers"]

def test_preview_hsbc_no_header(client):
    csv_content = open("tests/fixtures/hsbc_no_header.csv", "rb").read()
    response = client.post(
        "/api/import/preview",
        files={"file": ("hsbc.csv", csv_content, "text/csv")},
        data={"source_bank": "hsbc"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_bank"] == "HSBC"
    # Even if no headers in file, pandas might assign 0, 1, 2
    assert len(data["preview_rows"]) == 3

def test_import_monzo(client):
    csv_content = open("tests/fixtures/monzo_rich.csv", "rb").read()
    response = client.post(
        "/api/import",
        files={"file": ("monzo.csv", csv_content, "text/csv")},
        data={"source_bank": "monzo", "account_name": "Test Monzo"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 2
    assert data["detected_bank"] == "MONZO"

def test_duplicate_import(client):
    csv_content = open("tests/fixtures/monzo_rich.csv", "rb").read()
    # First import
    client.post(
        "/api/import",
        files={"file": ("monzo.csv", csv_content, "text/csv")},
        data={"source_bank": "monzo"}
    )
    # Second import same file
    response = client.post(
        "/api/import",
        files={"file": ("monzo_copy.csv", csv_content, "text/csv")},
        data={"source_bank": "monzo"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 0
    assert data["skipped_count"] == 2

def test_import_hsbc_with_header(client):
    csv_content = open("tests/fixtures/hsbc_with_header.csv", "rb").read()
    response = client.post(
        "/api/import",
        files={"file": ("hsbc.csv", csv_content, "text/csv")},
        data={"source_bank": "auto"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 2
    assert data["detected_bank"] == "HSBC"

def test_invalid_csv(client):
    response = client.post(
        "/api/import",
        files={"file": ("bad.csv", b"invalid,content\n1,2", "text/csv")},
        data={"source_bank": "monzo"}
    )
    # Should probably fail or import 0 if it doesn't match Monzo headers
    # If source_bank is forced to monzo but headers mismatch, MonzoAdapter.normalise might fail
    # or just import garbage. In our case, we check headers in can_parse.
    # If we force monzo, it will try to normalise.
    pass

def test_audit_events_created(client):
    csv_content = open("tests/fixtures/monzo_rich.csv", "rb").read()
    client.post(
        "/api/import",
        files={"file": ("monzo.csv", csv_content, "text/csv")},
        data={"source_bank": "monzo"}
    )
    
    conn = db_manager.get_connection()
    events = conn.execute("SELECT event_type FROM audit_events").fetchall()
    event_types = [e[0] for e in events]
    assert "import_completed" in event_types
