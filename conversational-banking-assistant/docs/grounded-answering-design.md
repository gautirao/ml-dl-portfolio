# Design Document - Issue #14: Grounded Answer Generation

## Status: Proposed Design
This document outlines the implementation plan and architectural design for generating citation-backed answers within the Conversational Banking Assistant. Implementation will follow once this design is finalized.

## 1. Proposed Files
- `src/cba/answering/models.py`: Pydantic models for grounded answers and citations.
- `src/cba/answering/service.py`: `GroundedAnswerService` implementation.
- `src/cba/answering/prompts.py`: Prompt templates and constants.
- `tests/answering/test_grounded_answer.py`: Unit tests using `FakeLlmClient`.

## 2. Model Design

### `GroundedAnswerDecision` (Enum)
- `ANSWER`: Question answered using context.
- `INSUFFICIENT_EVIDENCE`: Context lacks necessary information.
- `REFUSAL`: Question falls outside safety/scope (e.g., financial advice).

### `GroundedCitation` (BaseModel)
- `chunk_id`: str (ID of the source chunk)
- `text_segment`: str (The snippet of text being cited)
- `page_number`: int | None (Extracted from context if available)

### `GroundedAnswer` (BaseModel)
- `decision`: GroundedAnswerDecision
- `answer`: str | None (The generated answer text)
- `citations`: list[GroundedCitation]
- `limitations`: list[str]
- `evidence_chunk_ids_used`: list[str] (Deduplicated list of chunk IDs from citations)
- `model`: str
- `provider`: LlmProvider

## 3. Input/Output Design

### Input: `GroundedAnswerService.generate_answer`
- `question`: str
- `evidence_packet`: EvidencePacket
- `llm_client`: LlmClient

### Output
- `GroundedAnswer` object.

## 4. Prompt Strategy
- **System Prompt**:
    - Defines the persona (Safe Banking Assistant).
    - Enforces strict grounding: "Only use the provided context."
    - Mandatory citations: "Every factual claim must include a `chunk_id`."
    - Refusal instructions: "If the user asks for financial advice or something not in context, use the appropriate decision code."
    - Output format: "Return ONLY a JSON object matching the schema."
- **User Prompt**:
    - Provides serialized `EvidencePacket`. Each chunk will be presented as:
      ```
      [Chunk ID: {chunk_id}]
      [Source: {citation_label}]
      {text}
      ```
    - Includes the user's `question`.

## 5. Structured JSON Validation
- Use `StructuredOutputValidator.validate_response`.
- Define a internal `_GroundedAnswerWireSchema` to match the LLM's expected JSON output, which `GroundedAnswerService` then maps to the domain `GroundedAnswer` model.

## 6. Fake Client Testing Strategy
- Use `FakeLlmClient` to return predefined JSON strings.
- Test scenarios:
    - Well-formed answer with multiple citations.
    - `insufficient_evidence` response.
    - Malformed JSON (ensure `LlmInvalidResponseError` is handled or propagated).
    - Missing required JSON fields.
    - Empty context scenario (Service should handle this gracefully without calling LLM).

## 7. Citation Validation
The service will:
1. Extract all `chunk_id`s from the LLM's `citations` list.
2. Verify every `chunk_id` exists in the `evidence_packet`.
3. If a `chunk_id` is hallucinated:
    - Option A: Raise `LlmInvalidResponseError`. (Preferred for this stage to ensure strict quality).
    - Option B: Filter out invalid citations and log a warning.
4. Populate `evidence_chunk_ids_used` from the validated citations.

## 8. Test Plan
- `test_generate_answer_success`: Verifies full flow with valid LLM output and context.
- `test_generate_answer_insufficient_evidence`: Verifies decision when LLM can't find info.
- `test_generate_answer_empty_packet`: Service returns `INSUFFICIENT_EVIDENCE` immediately.
- `test_generate_answer_hallucinated_citation`: Service rejects answer if it cites non-existent chunk.
- `test_generate_answer_invalid_json`: `StructuredOutputValidator` integration check.
- `test_generate_answer_missing_fields`: Ensure Pydantic validation catches incomplete responses.

## 9. Acceptance Criteria
- [ ] `GroundedAnswerService` implemented and tested.
- [ ] Citations are validated against `EvidencePacket`.
- [ ] Structured JSON output is enforced via `StructuredOutputValidator`.
- [ ] `Ruff` and `Mypy` pass.
- [ ] No real LLM/network calls in tests.

## 10. Risks and Mitigations
- **Hallucination**: Mitigated by strict system prompt and mandatory citations.
- **Citation Hallucination**: Mitigated by cross-referencing `chunk_id`s against the `EvidencePacket`.
- **JSON Fragility**: Mitigated by `StructuredOutputValidator`'s robust extraction (regex for markdown fences).
- **Prompt Injection**: Basic mitigation by keeping context separate from instructions (though retrieved text remains a risk for future hardening).

## 11. Out of Scope
- LangGraph/Workflow orchestration.
- Gemini provider implementation.
- Real Ollama model downloads/execution.
- Complex financial advice guardrails (beyond simple prompt instructions).
- Audit logging or database persistence.
