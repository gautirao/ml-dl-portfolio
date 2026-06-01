from datetime import datetime

import pytest

from cba.domain.models import DocumentType, ExtractedDocument, ExtractedPage, ProductArea
from cba.ingestion.chunker import SectionAwareChunker, SectionDetector, TextCleaner


@pytest.fixture
def mock_extracted_doc() -> ExtractedDocument:
    pages = [
        ExtractedPage(
            page_number=1,
            text="""
Skip to main content
Log in
Menu
NatWest Personal Banking
1. Introduction
This is the introduction to our terms.
It spans multiple lines.
2. Our Fees
The fee for this service is £10 per month.
The interest rate is 39.49% EAR.
Yes, this is important.
No, it is not optional.
Note: Always read the terms.
Footer: Copyright 2026 NatWest
        """.strip(),
        ),
        ExtractedPage(
            page_number=2,
            text="""
3. Overdrafts
An overdraft allows you to borrow money.
It is a temporary arrangement.
Page 2 Footer
        """.strip(),
        ),
    ]
    return ExtractedDocument(
        source_id="test-doc",
        title="Test Document",
        document_type=DocumentType.TERMS_CONDITIONS,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        local_path="data/raw/test.pdf",
        extracted_at=datetime.fromisoformat("2026-05-20T12:00:00"),
        pages=pages,
    )


def test_text_cleaner_removes_boilerplate() -> None:
    cleaner = TextCleaner()
    raw_text = "Skip to main content\nLog in\nMenu\nActual Policy Content\nFooter: Copyright"
    cleaned = cleaner.clean(raw_text)
    assert "Skip to main content" not in cleaned
    assert "Log in" not in cleaned
    assert "Menu" not in cleaned
    assert "Actual Policy Content" in cleaned


def test_text_cleaner_normalizes_whitespace() -> None:
    cleaner = TextCleaner()
    raw_text = "Multiple    spaces  and\n\n\n\nexcessive newlines."
    cleaned = cleaner.clean(raw_text)
    assert "Multiple spaces" in cleaned
    assert "\n\n\n" not in cleaned


def test_section_detector_identifies_numbered_headings() -> None:
    detector = SectionDetector()
    assert detector.is_heading("1. Introduction") is True
    assert detector.is_heading("2. Our Fees") is True
    assert detector.is_heading("2.3.4 Detailed Section") is True


def test_section_detector_identifies_uppercase_headings() -> None:
    detector = SectionDetector()
    assert detector.is_heading("OVERDRAFTS") is True
    assert detector.is_heading("IMPORTANT INFORMATION") is True


def test_section_detector_ignores_currency_and_rates() -> None:
    detector = SectionDetector()
    assert detector.is_heading("£10") is False
    assert detector.is_heading("39.49% EAR") is False
    assert detector.is_heading("Total: £50.00") is False


def test_section_detector_ignores_generic_short_words() -> None:
    detector = SectionDetector()
    assert detector.is_heading("Yes") is False
    assert detector.is_heading("No") is False
    assert detector.is_heading("Note") is False


def test_chunker_preserves_metadata(mock_extracted_doc: ExtractedDocument) -> None:
    chunker = SectionAwareChunker(max_chars=100, overlap_chars=20)
    chunks = chunker.chunk(mock_extracted_doc, citation_label="NatWest Terms 2026")

    assert len(chunks) > 0
    first_chunk = chunks[0]
    assert first_chunk.source_id == "test-doc"
    assert first_chunk.citation_label == "NatWest Terms 2026"
    assert first_chunk.chunk_id == "test-doc::chunk::0001"
    assert len(first_chunk.chunk_hash) == 64  # SHA256 length


def test_chunks_never_cross_sections(mock_extracted_doc: ExtractedDocument) -> None:
    # Set max_chars large enough that it would normally combine sections
    chunker = SectionAwareChunker(max_chars=5000, overlap_chars=0)
    chunks = chunker.chunk(mock_extracted_doc, citation_label="Test")

    # We expect at least 3 chunks because there are 3 headings (1. Intro, 2. Fees, 3. Overdrafts)
    # Even if they are small, they should be split.
    headings = [c.section_heading for c in chunks]
    assert "1. Introduction" in headings
    assert "2. Our Fees" in headings
    assert "3. Overdrafts" in headings

    # Ensure no chunk contains text from two different sections
    for chunk in chunks:
        if chunk.section_heading == "1. Introduction":
            assert "Our Fees" not in chunk.text
        if chunk.section_heading == "2. Our Fees":
            assert "Overdrafts" not in chunk.text


def test_overlap_resets_at_section_boundary() -> None:
    # This is harder to test without a specific long section, but we can verify
    # that a chunk starting a new section doesn't contain text from the previous section.
    text = "Section 1\nThis is content 1.\nSection 2\nThis is content 2."
    pages = [ExtractedPage(page_number=1, text=text)]
    doc = ExtractedDocument(
        source_id="overlap-test",
        title="Overlap Test",
        document_type=DocumentType.TERMS_CONDITIONS,
        product_area=ProductArea.CURRENT_ACCOUNTS,
        local_path="data/raw/test.pdf",
        extracted_at=datetime.fromisoformat("2026-05-20T12:00:00"),
        pages=pages,
    )
    chunker = SectionAwareChunker(max_chars=100, overlap_chars=50)
    chunks = chunker.chunk(doc, citation_label="Test")

    section_2_chunks = [c for c in chunks if c.section_heading == "Section 2"]
    for c in section_2_chunks:
        assert "Section 1" not in c.text
        assert "content 1" not in c.text


def test_offsets_match_cleaned_text(mock_extracted_doc: ExtractedDocument) -> None:
    chunker = SectionAwareChunker(max_chars=50, overlap_chars=0)
    chunks = chunker.chunk(mock_extracted_doc, citation_label="Test")

    # Concatenate all chunks for a section and check if text matches
    # Note: Overlap might complicate this if overlap > 0, so we use overlap=0
    cleaner = TextCleaner()
    full_cleaned_text = cleaner.clean(mock_extracted_doc.full_text)

    for chunk in chunks:
        extracted_from_cleaned = full_cleaned_text[chunk.character_start : chunk.character_end]
        # Chunks might have internal whitespace normalized, so we compare normalized
        assert " ".join(chunk.text.split()) == " ".join(extracted_from_cleaned.split())


def test_page_number_start_is_preserved(mock_extracted_doc: ExtractedDocument) -> None:
    chunker = SectionAwareChunker(max_chars=1000, overlap_chars=0)
    chunks = chunker.chunk(mock_extracted_doc, citation_label="Test")

    # "3. Overdrafts" is on page 2
    overdraft_chunks = [c for c in chunks if c.section_heading == "3. Overdrafts"]
    assert all(c.page_number_start == 2 for c in overdraft_chunks)
