from datetime import UTC

import pytest

from cba.domain.models import Chunk, DocumentType, ProductArea, SearchResult
from cba.retrieval.evidence import (
    EvidenceItem,
    EvidencePacket,
    RetrievalMethod,
)
from cba.retrieval.metadata_filter import FilterCriteria


@pytest.fixture
def sample_chunk_1() -> Chunk:
    return Chunk(
        chunk_id="doc-1::chunk-1",
        source_id="doc-1",
        citation_label="Doc 1 Label",
        title="Doc 1 Title",
        document_type=DocumentType.TERMS_CONDITIONS,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        section_heading="Section A",
        chunk_index=1,
        text="This is chunk 1 text.",
        character_start=0,
        character_end=20,
        page_number_start=1,
        chunk_hash="hash1",
    )


@pytest.fixture
def sample_chunk_2() -> Chunk:
    return Chunk(
        chunk_id="doc-2::chunk-2",
        source_id="doc-2",
        citation_label="Doc 2 Label",
        title="Doc 2 Title",
        document_type=DocumentType.FEE_INFORMATION,
        product_area=ProductArea.SAVINGS,
        section_heading="Section B",
        chunk_index=2,
        text="This is chunk 2 text.",
        character_start=20,
        character_end=40,
        page_number_start=5,
        chunk_hash="hash2",
    )


def test_evidence_item_proxies_chunk_fields(sample_chunk_1: Chunk) -> None:
    item = EvidenceItem(
        chunk=sample_chunk_1,
        retrieval_methods=[RetrievalMethod.VECTOR],
        scores_by_method={RetrievalMethod.VECTOR: 0.95},
        ranks_by_method={RetrievalMethod.VECTOR: 1},
    )
    assert item.chunk_id == sample_chunk_1.chunk_id
    assert item.text == sample_chunk_1.text
    assert item.citation_label == sample_chunk_1.citation_label
    assert item.section_heading == sample_chunk_1.section_heading
    assert item.page_number_start == sample_chunk_1.page_number_start


def test_evidence_packet_creation_and_empty(sample_chunk_1: Chunk) -> None:
    empty_packet = EvidencePacket(question="What is X?")
    assert empty_packet.is_empty is True
    assert empty_packet.total_items == 0
    assert empty_packet.to_context_blocks() == ""


def test_evidence_packet_utc_timestamp() -> None:
    packet = EvidencePacket(question="Test?")
    assert packet.created_at.tzinfo == UTC


def test_deduplication_preserves_all_methods(sample_chunk_1: Chunk) -> None:
    # Simulate vector search results
    vector_results = [SearchResult(chunk=sample_chunk_1, score=0.9)]
    # Simulate keyword search results (same chunk)
    keyword_results = [SearchResult(chunk=sample_chunk_1, score=15.5)]

    packet = EvidencePacket.from_results(
        question="How to open account?",
        vector_results=vector_results,
        keyword_results=keyword_results,
    )

    assert len(packet.items) == 1
    item = packet.items[0]
    assert RetrievalMethod.VECTOR in item.retrieval_methods
    assert RetrievalMethod.KEYWORD in item.retrieval_methods
    assert item.scores_by_method[RetrievalMethod.VECTOR] == 0.9
    assert item.scores_by_method[RetrievalMethod.KEYWORD] == 15.5
    assert item.ranks_by_method[RetrievalMethod.VECTOR] == 1
    assert item.ranks_by_method[RetrievalMethod.KEYWORD] == 1


def test_deterministic_ordering(sample_chunk_1: Chunk, sample_chunk_2: Chunk) -> None:
    # Chunk 2 has better rank in keyword (1), Chunk 1 has better rank in vector (1)
    # But let's say we want a stable tie-breaker or specific priority.
    # Requirement: first by best observed rank across methods,
    # then original insertion, then chunk_id.

    vector_results = [
        SearchResult(chunk=sample_chunk_1, score=0.9),  # Rank 1
        SearchResult(chunk=sample_chunk_2, score=0.8),  # Rank 2
    ]
    keyword_results = [
        SearchResult(chunk=sample_chunk_2, score=20.0),  # Rank 1
        SearchResult(chunk=sample_chunk_1, score=10.0),  # Rank 2
    ]

    # Both have best rank 1. Tie-break should be deterministic.
    packet = EvidencePacket.from_results(
        question="Query", vector_results=vector_results, keyword_results=keyword_results
    )

    assert len(packet.items) == 2
    # doc-1::chunk-1 comes before doc-2::chunk-2 if tie-breaking by chunk_id alphabetical
    assert packet.items[0].chunk_id == "doc-1::chunk-1"
    assert packet.items[1].chunk_id == "doc-2::chunk-2"


def test_to_context_blocks_formatting(sample_chunk_1: Chunk) -> None:
    item = EvidenceItem(
        chunk=sample_chunk_1,
        retrieval_methods=[RetrievalMethod.VECTOR],
        scores_by_method={RetrievalMethod.VECTOR: 0.95},
        ranks_by_method={RetrievalMethod.VECTOR: 1},
    )
    packet = EvidencePacket(question="Test?", items=[item])

    context = packet.to_context_blocks()
    assert "[Doc 1 Label]" in context
    assert "Section: Section A" in context
    assert "(Page 1)" in context
    assert "This is chunk 1 text." in context
    assert "Source: doc-1" in context
    assert "Chunk: doc-1::chunk-1" in context


def test_filters_applied_serialization() -> None:
    criteria = FilterCriteria(product_area=ProductArea.SAVINGS)
    packet = EvidencePacket(question="Savings?", filters_applied=criteria)
    dump = packet.model_dump()
    assert dump["filters_applied"]["product_area"] == "savings"
