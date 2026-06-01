import pytest

from cba.answering.evidence_support import (
    EvidenceSupportChecker,
    EvidenceSupportConfig,
    EvidenceSupportError,
)
from cba.answering.grounded_answer import (
    CitationValidationError,
    GroundedAnswer,
    GroundedAnswerDecision,
    GroundedCitation,
)
from cba.domain.enums import DocumentType, ProductArea
from cba.domain.models import Chunk
from cba.llm.client import LlmProvider
from cba.retrieval.evidence import EvidenceItem, EvidencePacket


@pytest.fixture
def mock_chunk():
    return Chunk(
        chunk_id="chunk-1",
        source_id="src-1",
        citation_label="Label",
        title="Title",
        document_type=DocumentType.TERMS_CONDITIONS,
        product_area=ProductArea.SAVINGS,
        chunk_index=0,
        text="Sample text content for testing.",
        character_start=0,
        character_end=31,
        page_number_start=1,
        chunk_hash="hash1",
    )


@pytest.fixture
def evidence_packet(mock_chunk):
    item = EvidenceItem(
        chunk=mock_chunk, retrieval_methods=[], scores_by_method={}, ranks_by_method={}
    )
    return EvidencePacket(question="test", items=[item])


def test_pre_gen_empty_packet():
    checker = EvidenceSupportChecker()
    packet = EvidencePacket(question="empty")
    assert checker.check_pre_generation(packet) is False


def test_pre_gen_min_items(evidence_packet):
    config = EvidenceSupportConfig(min_evidence_items=2)
    checker = EvidenceSupportChecker(config)
    # Packet has 1 item, config requires 2
    assert checker.check_pre_generation(evidence_packet) is False

    config.min_evidence_items = 1
    assert checker.check_pre_generation(evidence_packet) is True


def test_pre_gen_min_context_chars(evidence_packet):
    # Context length for evidence_packet is roughly 100+ chars with formatting
    config = EvidenceSupportConfig(min_context_chars=500)
    checker = EvidenceSupportChecker(config)
    assert checker.check_pre_generation(evidence_packet) is False

    config.min_context_chars = 10
    assert checker.check_pre_generation(evidence_packet) is True


def test_post_gen_valid_answer(evidence_packet):
    checker = EvidenceSupportChecker()
    answer = GroundedAnswer(
        decision=GroundedAnswerDecision.ANSWER,
        answer="Valid answer",
        citations=[GroundedCitation(chunk_id="chunk-1", citation_label="L", text_segment="T")],
        evidence_chunk_ids_used=["chunk-1"],
        model="m",
        provider=LlmProvider.FAKE,
    )
    # Should not raise
    checker.validate_post_generation(answer, evidence_packet)


def test_post_gen_empty_answer_text(evidence_packet):
    checker = EvidenceSupportChecker()
    answer = GroundedAnswer(
        decision=GroundedAnswerDecision.ANSWER,
        answer=" ",
        citations=[GroundedCitation(chunk_id="chunk-1", citation_label="L", text_segment="T")],
        evidence_chunk_ids_used=["chunk-1"],
        model="m",
        provider=LlmProvider.FAKE,
    )
    with pytest.raises(EvidenceSupportError, match="answer text is empty"):
        checker.validate_post_generation(answer, evidence_packet)


def test_post_gen_no_citations_required(evidence_packet):
    config = EvidenceSupportConfig(require_citations_for_answer=True)
    checker = EvidenceSupportChecker(config)
    answer = GroundedAnswer(
        decision=GroundedAnswerDecision.ANSWER,
        answer="Answer",
        citations=[],
        evidence_chunk_ids_used=["chunk-1"],
        model="m",
        provider=LlmProvider.FAKE,
    )
    with pytest.raises(EvidenceSupportError, match="no citations provided"):
        checker.validate_post_generation(answer, evidence_packet)


def test_post_gen_hallucinated_citation(evidence_packet):
    checker = EvidenceSupportChecker()
    answer = GroundedAnswer(
        decision=GroundedAnswerDecision.ANSWER,
        answer="Answer",
        citations=[GroundedCitation(chunk_id="hallucinated", citation_label="L", text_segment="T")],
        evidence_chunk_ids_used=["chunk-1"],
        model="m",
        provider=LlmProvider.FAKE,
    )
    with pytest.raises(CitationValidationError):
        checker.validate_post_generation(answer, evidence_packet)


def test_post_gen_unknown_used_id(evidence_packet):
    checker = EvidenceSupportChecker()
    answer = GroundedAnswer(
        decision=GroundedAnswerDecision.ANSWER,
        answer="Answer",
        citations=[GroundedCitation(chunk_id="chunk-1", citation_label="L", text_segment="T")],
        evidence_chunk_ids_used=["unknown-id"],
        model="m",
        provider=LlmProvider.FAKE,
    )
    with pytest.raises(EvidenceSupportError, match="Unknown chunk_id in evidence_chunk_ids_used"):
        checker.validate_post_generation(answer, evidence_packet)


def test_post_gen_empty_used_ids(evidence_packet):
    checker = EvidenceSupportChecker()
    answer = GroundedAnswer(
        decision=GroundedAnswerDecision.ANSWER,
        answer="Answer",
        citations=[GroundedCitation(chunk_id="chunk-1", citation_label="L", text_segment="T")],
        evidence_chunk_ids_used=[],
        model="m",
        provider=LlmProvider.FAKE,
    )
    with pytest.raises(EvidenceSupportError, match="evidence_chunk_ids_used is empty"):
        checker.validate_post_generation(answer, evidence_packet)


def test_post_gen_insufficient_evidence_allowed(evidence_packet):
    checker = EvidenceSupportChecker()
    answer = GroundedAnswer(
        decision=GroundedAnswerDecision.INSUFFICIENT_EVIDENCE,
        answer=None,
        citations=[],
        evidence_chunk_ids_used=[],
        model="m",
        provider=LlmProvider.FAKE,
    )
    # Should not raise even with no citations
    checker.validate_post_generation(answer, evidence_packet)
