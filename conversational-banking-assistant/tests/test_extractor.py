from datetime import date
from pathlib import Path

import pytest

from cba.domain.models import DocumentType, ProductArea, RiskLevel, Source, SourceType, StalePolicy
from cba.ingestion.extractor import DocumentExtractor


@pytest.fixture
def extractor():
    return DocumentExtractor(project_root=Path("."))

@pytest.fixture
def pdf_source():
    return Source(
        source_id="test-pdf",
        bank="Test Bank",
        title="Test PDF Document",
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
        stale_policy=StalePolicy.WARN_ONLY
    )

@pytest.fixture
def html_source():
    return Source(
        source_id="test-html",
        bank="Test Bank",
        title="Test HTML Document",
        source_type=SourceType.PUBLIC_WEB,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        document_type=DocumentType.TERMS_CONDITIONS,
        url="https://example.com/test.html",
        citation_label="[T]",
        retrieved_at=date.today(),
        local_path="tests/fixtures/documents/sample.html",
        content_hash="hash",
        freshness_threshold_days=30,
        allowed_for_demo=False,
        risk_level=RiskLevel.MEDIUM,
        stale_policy=StalePolicy.WARN_ONLY
    )

def test_extract_pdf(extractor, pdf_source):
    extracted = extractor.extract(pdf_source)
    
    assert extracted.source_id == pdf_source.source_id
    assert extracted.title == pdf_source.title
    assert len(extracted.pages) == 1
    assert "Synthetic PDF Content" in extracted.pages[0].text
    assert "Synthetic PDF Content" in extracted.full_text

def test_extract_html(extractor, html_source):
    extracted = extractor.extract(html_source)
    
    assert extracted.source_id == html_source.source_id
    assert "Current Account Terms" in extracted.full_text
    assert "Monthly fee: £0" in extracted.full_text
    # Check that script/style/noscript content is NOT in full_text
    assert "console.log" not in extracted.full_text
    assert "more-styles" not in extracted.full_text
    assert "noscript content" not in extracted.full_text
    assert len(extracted.pages) == 1

def test_extract_missing_file(extractor, pdf_source):
    pdf_source.local_path = "tests/fixtures/documents/non_existent.pdf"
    
    with pytest.raises(FileNotFoundError) as excinfo:
        extractor.extract(pdf_source)
    
    assert "tests/fixtures/documents/non_existent.pdf" in str(excinfo.value)

def test_extract_unsupported_type(extractor, pdf_source):
    # This shouldn't normally happen if enums are strictly used, but good to check
    pdf_source.source_type = "unsupported" # type: ignore
    
    with pytest.raises(ValueError) as excinfo:
        extractor.extract(pdf_source)
    
    assert "Unsupported source type" in str(excinfo.value)
