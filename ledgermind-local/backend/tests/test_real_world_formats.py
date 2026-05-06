import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database.connection import db_manager
import os

@pytest.fixture
def client(tmp_path):
    test_db = tmp_path / "test_real_world.db"
    db_manager.db_path = str(test_db)
    db_manager.conn = None
    with TestClient(app) as c:
        yield c

def test_monzo_synthetic_import(client):
    csv_path = "tests/fixtures/synthetic_monzo.csv"
    with open(csv_path, "rb") as f:
        content = f.read()
    
    response = client.post(
        "/api/import",
        files={"file": ("monzo.csv", content, "text/csv")},
        data={"source_bank": "auto"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_bank"] == "MONZO"
    assert data["imported_count"] == 3
    assert data["date_min"] == "2026-02-01"
    assert data["date_max"] == "2026-02-03"

def test_hsbc_synthetic_import(client):
    csv_path = "tests/fixtures/synthetic_hsbc.csv"
    with open(csv_path, "rb") as f:
        content = f.read()
    
    response = client.post(
        "/api/import",
        files={"file": ("hsbc.csv", content, "text/csv")},
        data={"source_bank": "auto"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_bank"] == "HSBC"
    assert data["imported_count"] == 3
    assert data["date_min"] == "2026-01-01"
    assert data["date_max"] == "2026-01-03"

def test_monzo_duplicate_handling(client):
    csv_path = "tests/fixtures/synthetic_monzo.csv"
    with open(csv_path, "rb") as f:
        content = f.read()
    
    # Import once
    client.post("/api/import", files={"file": ("monzo.csv", content, "text/csv")})
    
    # Import again
    response = client.post("/api/import", files={"file": ("monzo_copy.csv", content, "text/csv")})
    data = response.json()
    assert data["imported_count"] == 0
    assert data["skipped_count"] == 3

def test_hsbc_duplicate_handling(client):
    csv_path = "tests/fixtures/synthetic_hsbc.csv"
    with open(csv_path, "rb") as f:
        content = f.read()
    
    # Import once
    client.post("/api/import", files={"file": ("hsbc.csv", content, "text/csv")})
    
    # Import again
    response = client.post("/api/import", files={"file": ("hsbc_copy.csv", content, "text/csv")})
    data = response.json()
    assert data["imported_count"] == 0
    assert data["skipped_count"] == 3
