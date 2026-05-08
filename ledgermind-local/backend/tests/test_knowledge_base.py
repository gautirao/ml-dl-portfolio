import pytest
from src.search.vector_store import VectorStore
from src.search.embedding_client import OllamaEmbeddingClient
from src.search.indexer import Indexer
from src.tools.knowledge_lookup import knowledge_lookup
from src.ai.planner import Planner
from src.ai.ollama_client import OllamaClient

@pytest.mark.asyncio
async def test_kb_indexing():
    vector_store = VectorStore()
    embedding_client = OllamaEmbeddingClient()
    indexer = Indexer(vector_store, embedding_client)
    
    # Rebuild KB index
    counts = await indexer.rebuild_knowledge_index()
    assert counts["documents"] > 0
    
    # Query knowledge base
    results = await vector_store.query(
        query_text="Monzo import formats",
        embedding_client=embedding_client,
        limit=5,
        where={"type": "knowledge_base"}
    )
    assert len(results) > 0
    # Check if Monzo is mentioned in any of the top results
    texts = [r["text"].lower() for r in results]
    assert any("monzo" in t for t in texts)
    assert results[0]["metadata"]["type"] == "knowledge_base"

@pytest.mark.asyncio
async def test_knowledge_lookup_tool():
    result = await knowledge_lookup(query="privacy policy")
    assert result.matches
    assert any("privacy" in match.text.lower() for match in result.matches)
    assert result.evidence["type"] == "knowledge_base"
    assert "knowledge_sources" in result.evidence

@pytest.mark.asyncio
async def test_planner_selects_knowledge_for_system_questions():
    ollama = OllamaClient()
    planner = Planner(ollama)
    
    # System question
    plan = await planner.create_plan("How does LedgerMind calculate totals?")
    assert plan.tool == "knowledge_lookup"
    
    # Another system question
    plan = await planner.create_plan("What does uncategorised mean?")
    assert plan.tool == "knowledge_lookup"

@pytest.mark.asyncio
async def test_planner_avoids_knowledge_for_financial_questions():
    ollama = OllamaClient()
    planner = Planner(ollama)
    
    # Financial question
    plan = await planner.create_plan("How much did I spend on groceries last month?")
    assert plan.tool != "knowledge_lookup"
    # Should probably be spending_summary or semantic_spending_search

@pytest.mark.asyncio
async def test_financial_advice_refusal():
    ollama = OllamaClient()
    planner = Planner(ollama)
    
    # Financial advice
    plan = await planner.create_plan("Should I invest in Bitcoin?")
    assert plan.tool == "out_of_scope"
