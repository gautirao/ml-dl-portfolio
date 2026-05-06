import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database.connection import db_manager

@pytest.fixture
def client(tmp_path):
    test_db = tmp_path / "test_identical.db"
    db_manager.db_path = str(test_db)
    db_manager.conn = None
    with TestClient(app) as c:
        yield c

def test_identical_rows_in_one_file(client):
    # HSBC-style no header with two identical rows
    content = b"01/01/2026,IDENTICAL,-10.00\n01/01/2026,IDENTICAL,-10.00"
    
    response = client.post(
        "/api/import",
        files={"file": ("hsbc.csv", content, "text/csv")},
        data={"source_bank": "hsbc"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 2
    
    # Verify they have different fingerprints in DB
    conn = db_manager.get_connection()
    fps = conn.execute("SELECT transaction_fingerprint FROM transactions").fetchall()
    assert len(fps) == 2
    assert fps[0][0] != fps[1][0]
    
    # Re-import should skip both
    response2 = client.post(
        "/api/import",
        files={"file": ("hsbc_copy.csv", content, "text/csv")},
        data={"source_bank": "hsbc"}
    )
    data2 = response2.json()
    assert data2["imported_count"] == 0
    assert data2["skipped_count"] == 2
