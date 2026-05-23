from datetime import date

import pytest

from cba.domain.enums import DocumentType, ProductArea, RiskLevel, SourceType, StalePolicy
from cba.domain.models import Chunk, Source
from cba.retrieval.embeddings import EmbeddingModel, FakeEmbeddingModel


@pytest.fixture
def fake_embedding_model() -> EmbeddingModel:
    return FakeEmbeddingModel(dimension=384)


@pytest.fixture
def sample_chunk() -> Chunk:
    return Chunk(
        chunk_id="test-source::chunk::0001",
        source_id="test-source",
        citation_label="Test Label",
        title="Test Title",
        document_type=DocumentType.TERMS_CONDITIONS,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        section_heading="Test Section",
        chunk_index=1,
        text="This is a test chunk of text about banking policies.",
        character_start=0,
        character_end=52,
        page_number_start=1,
        chunk_hash="fakehash123",
    )


@pytest.fixture
def sample_source() -> Source:
    return Source(
        source_id="test-source",
        bank="Test Bank",
        title="Test Document",
        source_type=SourceType.PUBLIC_PDF,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        document_type=DocumentType.TERMS_CONDITIONS,
        url="https://example.com/test.pdf",
        citation_label="[T]",
        retrieved_at=date.today(),
        local_path="tests/fixtures/documents/sample.pdf",
        content_hash="hash",
        freshness_threshold_days=30,
        allowed_for_demo=False,
        risk_level=RiskLevel.MEDIUM,
        stale_policy=StalePolicy.WARN_ONLY,
    )
