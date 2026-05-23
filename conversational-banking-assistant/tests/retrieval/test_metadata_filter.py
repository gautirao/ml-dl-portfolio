import pytest

from cba.domain.enums import DocumentType, ProductArea
from cba.domain.models import Chunk
from cba.retrieval.metadata_filter import FilterCriteria, MetadataFilter


@pytest.fixture
def sample_chunks() -> list[Chunk]:
    return [
        Chunk(
            chunk_id="c1", source_id="s1", citation_label="L1", title="T1",
            document_type=DocumentType.TERMS_CONDITIONS, product_area=ProductArea.CURRENT_ACCOUNTS,
            chunk_index=1, text="text 1", character_start=0, character_end=6, chunk_hash="h1"
        ),
        Chunk(
            chunk_id="c2", source_id="s1", citation_label="L1", title="T1",
            document_type=DocumentType.TERMS_CONDITIONS, product_area=ProductArea.CURRENT_ACCOUNTS,
            chunk_index=2, text="text 2", character_start=7, character_end=13, chunk_hash="h2"
        ),
        Chunk(
            chunk_id="c3", source_id="s2", citation_label="L2", title="T2",
            document_type=DocumentType.FEE_INFORMATION, product_area=ProductArea.SAVINGS,
            chunk_index=1, text="text 3", character_start=0, character_end=6, chunk_hash="h3"
        ),
    ]

def test_filter_by_source_id(sample_chunks: list[Chunk]) -> None:
    criteria = FilterCriteria(source_id="s1")
    results = MetadataFilter.filter_chunks(sample_chunks, criteria)
    assert len(results) == 2
    assert all(r.source_id == "s1" for r in results)

def test_filter_by_document_type(sample_chunks: list[Chunk]) -> None:
    criteria = FilterCriteria(document_type=DocumentType.FEE_INFORMATION)
    results = MetadataFilter.filter_chunks(sample_chunks, criteria)
    assert len(results) == 1
    assert results[0].chunk_id == "c3"

def test_filter_by_product_area(sample_chunks: list[Chunk]) -> None:
    criteria = FilterCriteria(product_area=ProductArea.SAVINGS)
    results = MetadataFilter.filter_chunks(sample_chunks, criteria)
    assert len(results) == 1
    assert results[0].chunk_id == "c3"

def test_filter_combined(sample_chunks: list[Chunk]) -> None:
    criteria = FilterCriteria(source_id="s1", chunk_index=2)
    results = MetadataFilter.filter_chunks(sample_chunks, criteria)
    assert len(results) == 1
    assert results[0].chunk_id == "c2"

def test_filter_no_match(sample_chunks: list[Chunk]) -> None:
    criteria = FilterCriteria(source_id="non-existent")
    results = MetadataFilter.filter_chunks(sample_chunks, criteria)
    assert len(results) == 0

def test_filter_empty_criteria(sample_chunks: list[Chunk]) -> None:
    criteria = FilterCriteria()
    results = MetadataFilter.filter_chunks(sample_chunks, criteria)
    assert len(results) == 3
