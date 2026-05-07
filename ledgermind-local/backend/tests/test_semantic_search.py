import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import date
from src.search.vector_store import VectorStore
from src.search.embedding_client import MockEmbeddingClient
from src.search.indexer import Indexer
from src.search.semantic_matcher import SemanticMatcher
from src.tools.semantic_spending import calculate_semantic_spending
from src.database.connection import db_manager

@pytest.fixture
def mock_embedding_client():
    return MockEmbeddingClient(dimension=3072)

@pytest.fixture
def vector_store(tmp_path):
    # Use a temporary directory for the vector store
    return VectorStore(persist_directory=str(tmp_path / "test_vec_store"))

@pytest.mark.anyio
async def test_indexer_rebuild(vector_store, mock_embedding_client):
    # Setup: Ensure some data exists in DuckDB
    conn = db_manager.get_connection()
    conn.execute("DELETE FROM transactions")
    conn.execute("""
        INSERT INTO transactions (id, source_bank, transaction_date, description, merchant, amount, direction, category, raw_row_json)
        VALUES 
        ('550e8400-e29b-41d4-a716-446655440000', 'monzo', '2026-01-01', 'Starbucks London', 'Starbucks', -5.50, 'outflow', 'Coffee', '{}'),
        ('550e8400-e29b-41d4-a716-446655440001', 'hsbc', '2026-01-02', 'TFL Travel', 'TFL', -2.40, 'outflow', 'Transport', '{}')
    """)
    
    indexer = Indexer(vector_store, mock_embedding_client)
    counts = await indexer.rebuild_index()
    
    assert counts["merchants"] == 2
    assert counts["categories"] == 2
    assert counts["descriptions"] == 2

@pytest.mark.anyio
async def test_semantic_matcher(vector_store, mock_embedding_client):
    indexer = Indexer(vector_store, mock_embedding_client)
    await indexer.rebuild_index()
    
    matcher = SemanticMatcher(vector_store, mock_embedding_client)
    matches = await matcher.find_matches("coffee", limit=5)
    
    assert len(matches) > 0
    # With MockEmbeddingClient returning [0.1] * dim, all distances will be near 0.
    assert matches[0]["score"] == pytest.approx(0.0, abs=1e-4)

@pytest.mark.anyio
async def test_semantic_spending_calculation(vector_store, mock_embedding_client):
    indexer = Indexer(vector_store, mock_embedding_client)
    await indexer.rebuild_index()
    
    # We need to mock calculate_semantic_spending to use our test vector store and mock embedding client
    # Or just call it with parameters if it supports them. 
    # I'll update calculate_semantic_spending to allow passing these or just mock it here.
    
    from src.tools.semantic_spending import calculate_semantic_spending
    
    # Actually, calculate_semantic_spending creates its own VectorStore and EmbeddingClient.
    # For testing, I'll mock the internal components.
    
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("src.tools.semantic_spending.VectorStore", lambda: vector_store)
        mp.setattr("src.tools.semantic_spending.OllamaEmbeddingClient", lambda: mock_embedding_client)
        
        result = await calculate_semantic_spending(
            query="coffee",
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 31)
        )
        
        assert result.deterministic_result.total_outflow > 0
        assert "Starbucks" in result.evidence.query_scope["merchants_included"]
        assert "Coffee" in result.evidence.query_scope["categories_included"]

@pytest.mark.anyio
async def test_vector_search_does_not_calculate_totals(vector_store, mock_embedding_client):
    matcher = SemanticMatcher(vector_store, mock_embedding_client)
    matches = await matcher.find_matches("coffee")
    
    for m in matches:
        assert "amount" not in m
        assert "total" not in m
