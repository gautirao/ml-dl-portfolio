---
name: python-code-quality
description: Use this skill when reviewing, refactoring or improving Python code quality in this repository, especially for the Conversational Banking Assistant. Review standards include architecture, style, error handling, testing, security, RAG-specific rules, and refactoring procedures.
---

# Python Code Quality Skill

Use this skill when reviewing, refactoring or improving Python code quality in this repository, especially for the Conversational Banking Assistant.

“Prefer boring, obvious, maintainable Python over clever abstractions.”

## 1. Architecture and boundaries
- Keep domain models separate from ingestion, retrieval and runtime concerns.
- Avoid circular dependencies.
- Keep modules cohesive and small.
- Prefer explicit interfaces/protocols where useful.
- Do not mix feature work with refactoring.
- Do not broaden issue scope without approval.

## 2. Python style and readability
- Prefer clear names over clever names.
- Use small functions with single responsibility.
- Avoid deeply nested control flow.
- Use type hints consistently.
- Prefer pathlib over string path manipulation.
- Prefer dataclasses/Pydantic models where appropriate.
- Use enums for controlled values.
- Keep public APIs obvious.

## 3. Error handling
- Raise domain-meaningful errors where appropriate.
- Do not swallow exceptions silently.
- Error messages should include useful context, such as source_id or local_path.
- Avoid broad except blocks unless re-raising with context.

## 4. Testing standards
- Write or update tests before refactoring when possible.
- Preserve behaviour unless the issue explicitly asks for behaviour change.
- Use deterministic fakes for external dependencies.
- Unit tests must not download models or call network APIs.
- Tests should cover edge cases, not just happy paths.
- Full test command:
  `cd conversational-banking-assistant && PYTHONPATH=src uv run pytest`

## 5. Security and safety
- Do not commit real bank documents.
- Do not commit data/raw, data/processed or data/vector_store.
- Keep path traversal protections.
- Avoid network access unless the issue explicitly asks for it.
- Preserve financial-advice boundaries and governance checks.
- Do not add LLM calls unless the issue explicitly asks for runtime LLM work.

## 6. RAG/retrieval-specific rules
- Preserve citation metadata end-to-end.
- Never drop source_id, citation_label, chunk_id, chunk_hash, page references or section headings.
- Avoid making retrieval code depend directly on LLM runtime.
- Keep embeddings/vector indexing separate from answer generation.
- Tests must use FakeEmbeddingModel unless explicitly doing local smoke validation.

## 7. Refactoring rules
- Run tests before and after.
- Refactor in small, reviewable commits.
- Do not change behaviour unless explicitly approved.
- Prefer mechanical moves first, then cleanup.
- If a cleanup becomes risky, stop and report rather than pushing through.
- No “big bang” rewrites.

## 8. Review output format
When asked to review code, produce:
- Summary verdict
- Top 5 issues by impact
- Suggested refactor plan
- Files affected
- Test plan
- Risks
- Whether it is safe to implement now

## 9. Implementation output format
When asked to implement approved refactoring, produce:
- Changes made
- Behaviour preserved
- Tests run
- Test result
- Files changed
- Commit hash
- Git status
