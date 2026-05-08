import pytest
import uuid
from datetime import date
from src.database.connection import db_manager
from src.tools.semantic_top_merchants import calculate_semantic_top_merchants
from unittest.mock import AsyncMock, patch

@pytest.fixture
def clean_db():
    db_manager.initialize_db()
    conn = db_manager.get_connection()
    conn.execute("DELETE FROM transaction_category_overrides")
    conn.execute("DELETE FROM transactions")
    yield conn

@pytest.mark.asyncio
async def test_semantic_top_merchants_ranks_by_count(clean_db):
    # 1. Setup transactions
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, merchant, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), "TEST", "2024-01-01", "Starbucks", "Starbucks", -5.0, "outflow", "coffee")
    )
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, merchant, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), "TEST", "2024-01-02", "Starbucks", "Starbucks", -5.0, "outflow", "coffee")
    )
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, merchant, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), "TEST", "2024-01-01", "Costa", "Costa", -10.0, "outflow", "coffee")
    )

    # 2. Mock SemanticMatcher to return 'coffee' category
    with patch("src.tools.semantic_top_merchants.SemanticMatcher") as MockMatcher:
        matcher_instance = MockMatcher.return_value
        matcher_instance.find_matches = AsyncMock(return_value=[])
        matcher_instance.extract_entities = AsyncMock(return_value={
            "merchants": [],
            "categories": ["coffee"]
        })

        # 3. Execute tool ranking by transaction_count
        result = await calculate_semantic_top_merchants(
            query="coffee",
            rank_by="transaction_count"
        )

        # Starbucks (2) should be ahead of Costa (1)
        assert len(result.merchants) == 2
        assert result.merchants[0].merchant == "Starbucks"
        assert result.merchants[0].transaction_count == 2
        assert result.merchants[1].merchant == "Costa"
        assert result.merchants[1].transaction_count == 1

@pytest.mark.asyncio
async def test_semantic_top_merchants_ranks_by_spend(clean_db):
    # 1. Setup transactions
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, merchant, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), "TEST", "2024-01-01", "Starbucks", "Starbucks", -5.0, "outflow", "coffee")
    )
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, merchant, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), "TEST", "2024-01-02", "Starbucks", "Starbucks", -5.0, "outflow", "coffee")
    )
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, merchant, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), "TEST", "2024-01-01", "Costa", "Costa", -15.0, "outflow", "coffee")
    )

    # 2. Mock SemanticMatcher
    with patch("src.tools.semantic_top_merchants.SemanticMatcher") as MockMatcher:
        matcher_instance = MockMatcher.return_value
        matcher_instance.find_matches = AsyncMock(return_value=[])
        matcher_instance.extract_entities = AsyncMock(return_value={
            "merchants": [],
            "categories": ["coffee"]
        })

        # 3. Execute tool ranking by total_spend
        result = await calculate_semantic_top_merchants(
            query="coffee",
            rank_by="total_spend"
        )

        # Costa (15.0) should be ahead of Starbucks (10.0)
        assert len(result.merchants) == 2
        assert result.merchants[0].merchant == "Costa"
        assert result.merchants[0].total_amount == 15.0
        assert result.merchants[1].merchant == "Starbucks"
        assert result.merchants[1].total_amount == 10.0

@pytest.mark.asyncio
async def test_semantic_top_merchants_respects_overrides(clean_db):
    # 1. Setup transaction with wrong category initially
    tx_id = str(uuid.uuid4())
    clean_db.execute(
        "INSERT INTO transactions (id, source_bank, transaction_date, description, merchant, amount, direction, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (tx_id, "TEST", "2024-01-01", "Starbucks", "Starbucks", -5.0, "outflow", "miscellaneous")
    )

    # 2. Apply override to 'coffee'
    clean_db.execute(
        "INSERT INTO transaction_category_overrides (id, transaction_id, new_category) VALUES (?, ?, ?)",
        (str(uuid.uuid4()), tx_id, "coffee")
    )

    # 3. Mock SemanticMatcher to return 'coffee' category
    with patch("src.tools.semantic_top_merchants.SemanticMatcher") as MockMatcher:
        matcher_instance = MockMatcher.return_value
        matcher_instance.find_matches = AsyncMock(return_value=[])
        matcher_instance.extract_entities = AsyncMock(return_value={
            "merchants": [],
            "categories": ["coffee"]
        })

        # 4. Execute tool
        result = await calculate_semantic_top_merchants(
            query="coffee",
            rank_by="transaction_count"
        )

        # Should find Starbucks because of the override
        assert len(result.merchants) == 1
        assert result.merchants[0].merchant == "Starbucks"
