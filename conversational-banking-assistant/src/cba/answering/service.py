from pydantic import BaseModel, Field

from cba.answering.evidence_support import (
    EvidenceSupportChecker,
    EvidenceSupportConfig,
)
from cba.answering.grounded_answer import (
    GroundedAnswer,
    GroundedAnswerDecision,
    GroundedCitation,
)
from cba.answering.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, format_context_block
from cba.llm.client import LlmClient, LlmMessage, LlmProvider, LlmRequest, LlmRole
from cba.llm.structured_output import StructuredOutputValidator
from cba.retrieval.evidence import EvidencePacket


class _GroundedCitationWire(BaseModel):
    """Schema for citation as expected from the LLM."""

    chunk_id: str
    text_segment: str


class _GroundedAnswerWire(BaseModel):
    """Schema for the full answer as expected from the LLM."""

    decision: GroundedAnswerDecision
    answer: str | None = None
    citations: list[_GroundedCitationWire] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class GroundedAnswerService:
    """Orchestrates grounded answer generation with citation validation."""

    def __init__(
        self,
        llm_client: LlmClient,
        model: str = "qwen2.5:7b",
        provider: LlmProvider = LlmProvider.OLLAMA,
        support_config: EvidenceSupportConfig | None = None,
    ):
        self.llm_client = llm_client
        self.model = model
        self.provider = provider
        self.support_config = support_config or EvidenceSupportConfig()
        self.checker = EvidenceSupportChecker(self.support_config)

    async def generate_answer(
        self, question: str, evidence_packet: EvidencePacket
    ) -> GroundedAnswer:
        """
        Generates a grounded answer from an EvidencePacket.

        Deterministic for empty or insufficient packets based on config.
        """
        if not self.checker.check_pre_generation(evidence_packet):
            return GroundedAnswer(
                decision=GroundedAnswerDecision.INSUFFICIENT_EVIDENCE,
                answer="Insufficient evidence to answer the question.",
                citations=[],
                limitations=["Pre-generation sufficiency check failed."],
                evidence_chunk_ids_used=[],
                model=self.model,
                provider=self.provider,
            )

        context_block = format_context_block(evidence_packet)
        user_prompt = USER_PROMPT_TEMPLATE.format(question=question, context_block=context_block)

        request = LlmRequest(
            messages=[
                LlmMessage(role=LlmRole.SYSTEM, content=SYSTEM_PROMPT),
                LlmMessage(role=LlmRole.USER, content=user_prompt),
            ],
            model=self.model,
            provider=self.provider,
            temperature=0.0,
        )

        llm_response = await self.llm_client.generate(request)

        wire_answer = StructuredOutputValidator.validate_response(llm_response, _GroundedAnswerWire)

        # Map chunk_id to EvidenceItem
        item_map = {item.chunk_id: item for item in evidence_packet.items}
        final_citations: list[GroundedCitation] = []
        used_chunk_ids = set()

        for cit in wire_answer.citations:
            if cit.chunk_id in item_map:
                item = item_map[cit.chunk_id]
                final_citations.append(
                    GroundedCitation(
                        chunk_id=cit.chunk_id,
                        citation_label=item.citation_label,
                        text_segment=cit.text_segment,
                        page_number=item.page_number_start,
                        section_heading=item.section_heading,
                    )
                )
            else:
                # Add citation with placeholder metadata so the checker can catch the bad ID
                final_citations.append(
                    GroundedCitation(
                        chunk_id=cit.chunk_id,
                        citation_label="UNKNOWN",
                        text_segment=cit.text_segment,
                        page_number=None,
                        section_heading=None,
                    )
                )
            used_chunk_ids.add(cit.chunk_id)

        answer = GroundedAnswer(
            decision=wire_answer.decision,
            answer=wire_answer.answer,
            citations=final_citations,
            limitations=wire_answer.limitations,
            evidence_chunk_ids_used=list(used_chunk_ids),
            model=llm_response.model,
            provider=llm_response.provider,
        )

        # Apply deterministic post-generation validation
        self.checker.validate_post_generation(answer, evidence_packet)

        return answer
