import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database.connection import db_manager
import os

@pytest.fixture
def client(tmp_path):
    # Override settings for testing
    test_db = tmp_path / "test_app.db"
    db_manager.db_path = str(test_db)
    db_manager.conn = None # Reset connection
    
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["tables_found"] >= 4
