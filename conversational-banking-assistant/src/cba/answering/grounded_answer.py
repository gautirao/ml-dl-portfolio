from enum import StrEnum

from pydantic import BaseModel, Field

from cba.llm.client import LlmProvider


class GroundedAnswerDecision(StrEnum):
    """Enumeration of possible decisions for grounded answer generation."""

    ANSWER = "answer"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    REFUSAL = "refusal"


class GroundedCitation(BaseModel):
    """Represents a specific citation to a chunk of evidence."""

    chunk_id: str = Field(..., description="The unique identifier of the source chunk.")
    citation_label: str = Field(
        ..., description="The human-readable label for the source (e.g., 'NatWest T&Cs, p. 5')."
    )
    text_segment: str = Field(
        ..., description="The specific segment of text from the chunk being cited."
    )
    page_number: int | None = Field(None, description="The page number if available in metadata.")
    section_heading: str | None = Field(
        None, description="The section heading if available in metadata."
    )


class GroundedAnswer(BaseModel):
    """The final domain model for a grounded answer."""

    decision: GroundedAnswerDecision
    answer: str | None = Field(
        None, description="The generated answer text. Null if decision is not ANSWER."
    )
    citations: list[GroundedCitation] = Field(default_factory=list)
    limitations: list[str] = Field(
        default_factory=list, description="Any limitations or caveats regarding the answer."
    )
    evidence_chunk_ids_used: list[str] = Field(
        default_factory=list, description="Deduplicated list of chunk IDs actually used."
    )
    model: str
    provider: LlmProvider


class CitationValidationError(Exception):
    """Raised when the LLM cites a chunk_id not present in the EvidencePacket."""

    def __init__(self, chunk_id: str):
        super().__init__(f"LLM cited unknown chunk_id: {chunk_id}")
        self.chunk_id = chunk_id
