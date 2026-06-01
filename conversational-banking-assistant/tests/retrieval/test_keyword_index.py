import pytest

from cba.domain.enums import DocumentType, ProductArea
from cba.domain.models import Chunk
from cba.retrieval.keyword_index import BM25KeywordIndex
from cba.retrieval.metadata_filter import FilterCriteria


@pytest.fixture
def keyword_index() -> BM25KeywordIndex:
    index = BM25KeywordIndex()
    chunks = [
        Chunk(
            chunk_id="c1",
            source_id="s1",
            citation_label="L1",
            title="T1",
            document_type=DocumentType.TERMS_CONDITIONS,
            product_area=ProductArea.CURRENT_ACCOUNTS,
            chunk_index=1,
            text="The monthly fee for this account is £5.",
            character_start=0,
            character_end=38,
            chunk_hash="h1",
        ),
        Chunk(
            chunk_id="c2",
            source_id="s1",
            citation_label="L1",
            title="T1",
            document_type=DocumentType.TERMS_CONDITIONS,
            product_area=ProductArea.CURRENT_ACCOUNTS,
            chunk_index=2,
            text="You can apply for an overdraft online.",
            character_start=39,
            character_end=76,
            chunk_hash="h2",
        ),
        Chunk(
            chunk_id="c3",
            source_id="s2",
            citation_label="L2",
            title="T2",
            document_type=DocumentType.FEE_INFORMATION,
            product_area=ProductArea.SAVINGS,
            chunk_index=1,
            text="Savings accounts do not have overdrafts.",
            character_start=0,
            character_end=39,
            chunk_hash="h3",
        ),
        Chunk(
            chunk_id="c_extra1",
            source_id="s3",
            citation_label="L3",
            title="T3",
            document_type=DocumentType.PRIVACY_POLICY,
            product_area=ProductArea.CREDIT_CARDS,
            chunk_index=1,
            text="This is a privacy policy about data protection.",
            character_start=0,
            character_end=47,
            chunk_hash="he1",
        ),
        Chunk(
            chunk_id="c_extra2",
            source_id="s4",
            citation_label="L4",
            title="T4",
            document_type=DocumentType.DEPOSIT_PROTECTION,
            product_area=ProductArea.SAVINGS,
            chunk_index=1,
            text="Your deposits are protected by FSCS scheme.",
            character_start=0,
            character_end=43,
            chunk_hash="he2",
        ),
    ]
    index.add_chunks(chunks)
    return index


def test_basic_keyword_search(keyword_index: BM25KeywordIndex) -> None:
    results = keyword_index.search("overdraft")
    assert len(results) == 1
    assert results[0].chunk.chunk_id == "c2"

    results = keyword_index.search("overdrafts")
    assert len(results) == 1
    assert results[0].chunk.chunk_id == "c3"


def test_case_insensitive_search(keyword_index: BM25KeywordIndex) -> None:
    results = keyword_index.search("OVERDRAFT")
    assert len(results) > 0
    assert results[0].chunk.chunk_id == "c2"


def test_punctuation_handling(keyword_index: BM25KeywordIndex) -> None:
    results = keyword_index.search("fee!")
    assert len(results) == 1
    assert results[0].chunk.chunk_id == "c1"


def test_no_match(keyword_index: BM25KeywordIndex) -> None:
    results = keyword_index.search("bitcoin")
    assert len(results) == 0


def test_search_with_metadata_filter(keyword_index: BM25KeywordIndex) -> None:
    # Search for 'overdrafts' but only in SAVINGS
    criteria = FilterCriteria(product_area=ProductArea.SAVINGS)
    results = keyword_index.search("overdrafts", criteria=criteria)
    assert len(results) == 1
    assert results[0].chunk.chunk_id == "c3"


def test_ranking_relevance(keyword_index: BM25KeywordIndex) -> None:
    # Add a chunk that has 'fee' multiple times
    more_chunks = [
        Chunk(
            chunk_id="c4",
            source_id="s1",
            citation_label="L1",
            title="T1",
            document_type=DocumentType.TERMS_CONDITIONS,
            product_area=ProductArea.CURRENT_ACCOUNTS,
            chunk_index=4,
            text="fee fee fee fee",
            character_start=0,
            character_end=15,
            chunk_hash="h4",
        )
    ]
    keyword_index.add_chunks(more_chunks)

    # Search for 'fee' (which appears once in c1 and 4 times in c4)
    results = keyword_index.search("fee")
    assert len(results) >= 2
    assert results[0].chunk.chunk_id == "c4"  # Should be higher ranked due to frequency
