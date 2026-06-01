import json
from typing import Any

import pytest

from cba.answering.grounded_answer import CitationValidationError, GroundedAnswerDecision
from cba.answering.service import GroundedAnswerService
from cba.domain.enums import DocumentType, ProductArea
from cba.domain.models import Chunk, SearchResult
from cba.llm.client import LlmProvider, LlmResponse
from cba.llm.fake import FakeLlmClient
from cba.llm.structured_output import LlmInvalidResponseError
from cba.retrieval.evidence import EvidencePacket


@pytest.fixture
def fake_llm() -> FakeLlmClient:
    return FakeLlmClient()


@pytest.fixture
def service(fake_llm: FakeLlmClient) -> GroundedAnswerService:
    return GroundedAnswerService(fake_llm, model="test-model", provider=LlmProvider.FAKE)


@pytest.fixture
def evidence_packet() -> EvidencePacket:
    chunk1 = Chunk(
        chunk_id="chunk-1",
        source_id="src-1",
        citation_label="Savings T&Cs",
        title="Savings",
        document_type=DocumentType.TERMS_CONDITIONS,
        product_area=ProductArea.SAVINGS,
        chunk_index=0,
        text="The interest rate for savings accounts is 3.5% AER.",
        character_start=0,
        character_end=50,
        page_number_start=5,
        chunk_hash="h1",
    )
    chunk2 = Chunk(
        chunk_id="chunk-2",
        source_id="src-2",
        citation_label="Withdrawal Policy",
        title="Withdrawals",
        document_type=DocumentType.TERMS_CONDITIONS,
        product_area=ProductArea.SAVINGS,
        section_heading="Processing Times",
        chunk_index=0,
        text="Withdrawals take up to 3 business days.",
        character_start=0,
        character_end=40,
        page_number_start=2,
        chunk_hash="h2",
    )

    # Use SearchResult instances
    packet = EvidencePacket.from_results(
        question="What is the interest rate?",
        vector_results=[
            SearchResult(chunk=chunk1, score=0.9),
            SearchResult(chunk=chunk2, score=0.8),
        ],
    )
    return packet


@pytest.mark.anyio
async def test_generate_answer_success(
    service: GroundedAnswerService, fake_llm: FakeLlmClient, evidence_packet: EvidencePacket
) -> None:
    # Setup fake response
    response_data = {
        "decision": "answer",
        "answer": "The interest rate is 3.5% and withdrawals take 3 days.",
        "citations": [
            {"chunk_id": "chunk-1", "text_segment": "interest rate for savings accounts is 3.5%"},
            {"chunk_id": "chunk-2", "text_segment": "Withdrawals take up to 3 business days"},
        ],
        "limitations": ["Applies to standard accounts only"],
    }
    fake_llm.add_response(
        LlmResponse(text=json.dumps(response_data), model="test-model", provider=LlmProvider.FAKE)
    )

    answer = await service.generate_answer("What is the interest rate?", evidence_packet)

    assert answer.decision == GroundedAnswerDecision.ANSWER
    assert answer.answer is not None
    assert "3.5%" in answer.answer
    assert len(answer.citations) == 2
    assert answer.citations[0].chunk_id == "chunk-1"
    assert answer.citations[0].citation_label == "Savings T&Cs"
    assert answer.citations[0].page_number == 5
    assert answer.citations[1].section_heading == "Processing Times"
    assert set(answer.evidence_chunk_ids_used) == {"chunk-1", "chunk-2"}


@pytest.mark.anyio
async def test_generate_answer_insufficient_evidence(
    service: GroundedAnswerService, fake_llm: FakeLlmClient, evidence_packet: EvidencePacket
) -> None:
    response_data: dict[str, Any] = {
        "decision": "insufficient_evidence",
        "answer": None,
        "citations": [],
        "limitations": ["No information about mortgages found"],
    }
    fake_llm.add_response(
        LlmResponse(text=json.dumps(response_data), model="test-model", provider=LlmProvider.FAKE)
    )

    answer = await service.generate_answer("What are mortgage rates?", evidence_packet)

    assert answer.decision == GroundedAnswerDecision.INSUFFICIENT_EVIDENCE
    assert answer.answer is None
    assert len(answer.citations) == 0


@pytest.mark.anyio
async def test_generate_answer_empty_packet(
    service: GroundedAnswerService, fake_llm: FakeLlmClient
) -> None:
    # Should not even call the LLM
    empty_packet = EvidencePacket(question="any")

    answer = await service.generate_answer("How do I pay?", empty_packet)

    assert answer.decision == GroundedAnswerDecision.INSUFFICIENT_EVIDENCE
    assert len(fake_llm.received_requests) == 0


@pytest.mark.anyio
async def test_generate_answer_invalid_json(
    service: GroundedAnswerService, fake_llm: FakeLlmClient, evidence_packet: EvidencePacket
) -> None:
    fake_llm.add_response(
        LlmResponse(text="This is not JSON at all", model="test-model", provider=LlmProvider.FAKE)
    )

    with pytest.raises(LlmInvalidResponseError):
        await service.generate_answer("?", evidence_packet)


@pytest.mark.anyio
async def test_generate_answer_missing_fields(
    service: GroundedAnswerService, fake_llm: FakeLlmClient, evidence_packet: EvidencePacket
) -> None:
    # Missing 'decision' field
    response_data = {"answer": "Broken response"}
    fake_llm.add_response(
        LlmResponse(text=json.dumps(response_data), model="test-model", provider=LlmProvider.FAKE)
    )

    with pytest.raises(LlmInvalidResponseError):
        await service.generate_answer("?", evidence_packet)


@pytest.mark.anyio
async def test_generate_answer_unknown_citation(
    service: GroundedAnswerService, fake_llm: FakeLlmClient, evidence_packet: EvidencePacket
) -> None:
    response_data = {
        "decision": "answer",
        "answer": "Hallucinated info",
        "citations": [{"chunk_id": "hallucinated-id", "text_segment": "I made this up"}],
    }
    fake_llm.add_response(
        LlmResponse(text=json.dumps(response_data), model="test-model", provider=LlmProvider.FAKE)
    )

    with pytest.raises(CitationValidationError) as excinfo:
        await service.generate_answer("?", evidence_packet)

    assert excinfo.value.chunk_id == "hallucinated-id"
