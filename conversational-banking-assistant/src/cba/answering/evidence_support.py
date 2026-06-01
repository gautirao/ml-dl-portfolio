from pydantic import BaseModel, Field

from cba.answering.grounded_answer import (
    CitationValidationError,
    GroundedAnswer,
    GroundedAnswerDecision,
)
from cba.retrieval.evidence import EvidencePacket


class EvidenceSupportError(Exception):
    """Raised when the LLM response violates the evidence support protocol."""

    pass


class EvidenceSupportConfig(BaseModel):
    """Configuration for deterministic evidence sufficiency checks."""

    min_evidence_items: int = Field(default=1, ge=0)
    require_citations_for_answer: bool = True
    min_context_chars: int | None = Field(default=None, ge=0)


class EvidenceSupportChecker:
    """Stateless logic for deterministic evidence support validation."""

    def __init__(self, config: EvidenceSupportConfig | None = None):
        self.config = config or EvidenceSupportConfig()

    def check_pre_generation(self, packet: EvidencePacket) -> bool:
        """
        Determines if the EvidencePacket is sufficient to proceed to LLM generation.
        Returns True if sufficient, False otherwise.
        """
        if packet.is_empty:
            return False

        if packet.total_items < self.config.min_evidence_items:
            return False

        if self.config.min_context_chars is not None:
            context = packet.to_context_blocks()
            if len(context) < self.config.min_context_chars:
                return False

        return True

    def validate_post_generation(self, answer: GroundedAnswer, packet: EvidencePacket) -> None:
        """
        Validates that the generated answer is correctly supported by the EvidencePacket.
        Raises EvidenceSupportError or CitationValidationError if validation fails.
        """
        if answer.decision == GroundedAnswerDecision.ANSWER:
            # 1. Answer text must be non-empty
            if not answer.answer or not answer.answer.strip():
                raise EvidenceSupportError("Decision is 'answer' but answer text is empty.")

            # 2. Citations must not be empty if required
            if self.config.require_citations_for_answer and not answer.citations:
                raise EvidenceSupportError("Decision is 'answer' but no citations provided.")

            # 3. Every cited chunk_id must exist in the original EvidencePacket
            packet_chunk_ids = {item.chunk_id for item in packet.items}
            for citation in answer.citations:
                if citation.chunk_id not in packet_chunk_ids:
                    raise CitationValidationError(citation.chunk_id)

            # 4. evidence_chunk_ids_used must not contain unknown IDs
            for chunk_id in answer.evidence_chunk_ids_used:
                if chunk_id not in packet_chunk_ids:
                    raise EvidenceSupportError(
                        f"Unknown chunk_id in evidence_chunk_ids_used: {chunk_id}"
                    )

            # 5. decision=answer requires non-empty evidence_chunk_ids_used
            if not answer.evidence_chunk_ids_used:
                raise EvidenceSupportError(
                    "Decision is 'answer' but evidence_chunk_ids_used is empty."
                )
