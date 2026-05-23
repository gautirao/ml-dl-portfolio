import pytest

from cba.domain.enums import DocumentType, ProductArea
from cba.domain.models import Chunk, SearchResult
from cba.retrieval.evidence import RetrievalMethod
from cba.retrieval.hybrid import HybridRetriever
from cba.retrieval.metadata_filter import FilterCriteria


class FakeVectorIndex:
    """A fake vector index."""
    def __init__(self, results: list[SearchResult]):
        self.results = results

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        return self.results[:top_k]

    def add_chunks(self, chunks: list[Chunk]) -> None:
        pass


class FakeKeywordIndex:
    """A fake keyword index."""
    def __init__(self, results: list[SearchResult]):
        self.results = results

    def search(
        self,
        query: str,
        criteria: FilterCriteria | None = None,
        top_k: int = 5
    ) -> list[SearchResult]:
        return self.results[:top_k]

    def add_chunks(self, chunks: list[Chunk]) -> None:
        pass


@pytest.fixture
def chunk_v1() -> Chunk:
    return Chunk(
        chunk_id="v1", source_id="s1", citation_label="C1", title="T1",
        document_type=DocumentType.TERMS_CONDITIONS,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        chunk_index=1, text="Vector only chunk",
        character_start=0, character_end=10, chunk_hash="h1"
    )


@pytest.fixture
def chunk_k1() -> Chunk:
    return Chunk(
        chunk_id="k1", source_id="s2", citation_label="C2", title="T2",
        document_type=DocumentType.FEE_INFORMATION,
        product_area=ProductArea.SAVINGS,
        chunk_index=1, text="Keyword only chunk",
        character_start=0, character_end=10, chunk_hash="h2"
    )


@pytest.fixture
def chunk_both() -> Chunk:
    return Chunk(
        chunk_id="both", source_id="s3", citation_label="C3", title="T3",
        document_type=DocumentType.OVERDRAFT_GUIDANCE,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        chunk_index=1, text="Common chunk",
        character_start=0, character_end=10, chunk_hash="h3"
    )


def test_hybrid_retriever_combines_results(
    chunk_v1: Chunk, chunk_k1: Chunk, chunk_both: Chunk
) -> None:
    # Vector: both (1), v1 (2)
    # Keyword: both (1), k1 (2)
    vector_results = [
        SearchResult(chunk=chunk_both, score=0.9),
        SearchResult(chunk=chunk_v1, score=0.8),
    ]
    keyword_results = [
        SearchResult(chunk=chunk_both, score=20.0),
        SearchResult(chunk=chunk_k1, score=15.0),
    ]

    v_index = FakeVectorIndex(vector_results)
    k_index = FakeKeywordIndex(keyword_results)
    retriever = HybridRetriever(v_index, k_index)

    packet = retriever.retrieve("test query", top_k=5)

    assert len(packet.items) == 3
    # 'both' should be first due to RRF
    assert packet.items[0].chunk_id == "both"
    assert RetrievalMethod.VECTOR in packet.items[0].retrieval_methods
    assert RetrievalMethod.KEYWORD in packet.items[0].retrieval_methods
    
    # Check preserved scores and ranks
    assert packet.items[0].scores_by_method[RetrievalMethod.VECTOR] == 0.9
    assert packet.items[0].ranks_by_method[RetrievalMethod.VECTOR] == 1
    assert packet.items[0].scores_by_method[RetrievalMethod.KEYWORD] == 20.0
    assert packet.items[0].ranks_by_method[RetrievalMethod.KEYWORD] == 1


def test_hybrid_retriever_deterministic_rrf_sorting(chunk_v1: Chunk, chunk_k1: Chunk) -> None:
    # v1 is rank 1 in vector, rank 2 in keyword
    # k1 is rank 1 in keyword, rank 2 in vector
    # They should have the SAME RRF score. 
    # Sorting should fall back to chunk_id (k1 < v1)
    
    vector_results = [
        SearchResult(chunk=chunk_v1, score=0.9),
        SearchResult(chunk=chunk_k1, score=0.8),
    ]
    keyword_results = [
        SearchResult(chunk=chunk_k1, score=20.0),
        SearchResult(chunk=chunk_v1, score=15.0),
    ]

    v_index = FakeVectorIndex(vector_results)
    k_index = FakeKeywordIndex(keyword_results)
    retriever = HybridRetriever(v_index, k_index)

    packet = retriever.retrieve("test query")

    assert packet.items[0].chunk_id == "k1"
    assert packet.items[1].chunk_id == "v1"


def test_hybrid_retriever_metadata_filtering(chunk_v1: Chunk, chunk_both: Chunk) -> None:
    vector_results = [
        SearchResult(chunk=chunk_both, score=0.9),
        SearchResult(chunk=chunk_v1, score=0.8),
    ]
    keyword_results = [
        SearchResult(chunk=chunk_both, score=20.0),
    ]

    v_index = FakeVectorIndex(vector_results)
    k_index = FakeKeywordIndex(keyword_results)
    retriever = HybridRetriever(v_index, k_index)

    # Filter for SAVINGS (chunk_v1 and chunk_both are CURRENT_ACCOUNTS and OVERDRAFT_GUIDANCE)
    # Actually let's filter for SAVINGS which should return nothing.
    criteria = FilterCriteria(product_area=ProductArea.SAVINGS)
    packet = retriever.retrieve("test query", criteria=criteria)
    assert len(packet.items) == 0

    # Filter for CURRENT_ACCOUNTS (only chunk_v1 matches in vector, chunk_both is OVERDRAFT)
    # Wait, my fixture says chunk_both is CURRENT_ACCOUNTS. Let me check.
    # chunk_v1: CURRENT_ACCOUNTS
    # chunk_both: CURRENT_ACCOUNTS
    # criteria = CURRENT_ACCOUNTS should return both.
    criteria2 = FilterCriteria(product_area=ProductArea.CURRENT_ACCOUNTS)
    packet2 = retriever.retrieve("test query", criteria=criteria2)
    assert len(packet2.items) == 2


def test_hybrid_retriever_empty_results() -> None:
    v_index = FakeVectorIndex([])
    k_index = FakeKeywordIndex([])
    retriever = HybridRetriever(v_index, k_index)

    packet = retriever.retrieve("test query")
    assert packet.is_empty is True
    assert len(packet.items) == 0


def test_hybrid_retriever_respects_top_k(
    chunk_v1: Chunk, chunk_k1: Chunk, chunk_both: Chunk
) -> None:
    vector_results = [
        SearchResult(chunk=chunk_both, score=0.9),
        SearchResult(chunk=chunk_v1, score=0.8),
    ]
    keyword_results = [
        SearchResult(chunk=chunk_both, score=20.0),
        SearchResult(chunk=chunk_k1, score=15.0),
    ]

    v_index = FakeVectorIndex(vector_results)
    k_index = FakeKeywordIndex(keyword_results)
    retriever = HybridRetriever(v_index, k_index)

    packet = retriever.retrieve("test query", top_k=1)
    assert len(packet.items) == 1
    assert packet.items[0].chunk_id == "both"
