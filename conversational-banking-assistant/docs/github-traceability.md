# GitHub Traceability and Commit Policy

## Purpose
This document defines the engineering standards for maintaining traceability between requirements (GitHub issues), implementation (commits), and roadmap (milestones/project board) for the Conversational Banking Assistant.

## Issue → commit → milestone workflow
1. **Requirement:** Every task starts with a GitHub Issue.
2. **Implementation:** Every commit must be linked to an issue using the naming convention below.
3. **Roadmap:** Issues are grouped into Milestones to track progress toward major project goals.
4. **Visibility:** The project board reflects the real-time status of each issue.

## Future commit message convention
All future commits must follow this format:
`<type>(#<issue-number>): <short issue title>`

### Allowed commit types
- `feat`: New feature or capability.
- `fix`: Bug fix.
- `test`: Adding or updating tests.
- `docs`: Documentation changes.
- `refactor`: Code changes that neither fix a bug nor add a feature.
- `chore`: Maintenance tasks or dependency updates.
- `ci`: CI/CD configuration changes.

### Examples
- `feat(#14): generate grounded answers with citations`
- `test(#38): reorganize conversational assistant test suite`
- `docs(#30): define LangChain and LangGraph boundaries`
- `refactor(#13): improve Ollama client session management`

## Validation gates before closing an issue
Before closing an issue, ensure the implementation passes the following checks:
```bash
cd conversational-banking-assistant && uv run pytest
cd conversational-banking-assistant && uv run ruff check .
cd conversational-banking-assistant && uv run mypy .
```

## Project board status rules
- **Todo**: Issues that are planned but implementation has not started.
- **In Progress**: The single active issue currently being worked on by the agent.
- **Review**: (Optional) Implementation complete, awaiting review.
- **Done**: Issue is closed and linked to one or more implementation commits.

## No git history rewriting rule
Maintain a linear and immutable history. Do not use `git rebase` or `git commit --amend` on commits that have been pushed to the remote repository.

## Legacy commit mapping note
Older commits in this repository may not include issue numbers. These should not be rewritten. Refer to the `GITHUB_AUDIT_REPORT` in the project history for mappings of legacy commits to issues.

## Traceability Audit Mapping
Commit history was rewritten intentionally for portfolio traceability. A backup branch was created before rewriting.

| New Hash | Commit Message | Issue # |
| :--- | :--- | :---: |
| 6e74a4c | docs(#1): add Conversational Banking Assistant portfolio entry | #1 |
| ac3dd1e | docs(#2): create project README and architecture summary | #2 |
| 4a7fbd6 | docs(#3): define TDD and BDD delivery approach | #3 |
| 0a972fc | docs(#4): design public banking source registry | #4 |
| 45a719a | docs(#5): document initial NatWest source candidates | #5 |
| e2477b7 | feat(#6): implement source registry loader | #6 |
| 75f8601 | chore(#6): add uv lockfile for conversational banking assistant | #6 |
| 8b8427e | feat(#7): implement local document extraction | #7 |
| 2df1c80 | feat(#8): implement section-aware chunking | #8 |
| 10adc04 | feat(#9): implement vector indexing for chunks | #9 |
| d044b1b | refactor(#22): reorganize package boundaries | #22 |
| fe70199 | feat(#10): implement keyword and metadata retrieval | #10 |
| a7f2783 | test(#10): fix typing issues for retrieval validation | #10 |
| d611f1e | feat(#11): add evidence packet model | #11 |
| b028538 | feat(#23): implement hybrid retrieval fusion | #23 |
| 694a62e | docs(#30): define LangChain and LangGraph boundaries | #30 |
| 2cf5aee | feat(#12): add provider-swappable LLM client interface | #12 |
| a6d5d3e | feat(#13): integrate Ollama local LLM client | #13 |
| 1bcf484 | refactor(#13): improve Ollama client session management | #13 |
| 20789ca | test(#38): reorganize conversational assistant test suite | #38 |
| 26e3aa1 | feat(#24): validate structured LLM JSON output | #24 |
| b896ca4 | docs(#14): add GitHub traceability policy | #14 |
| 63de660 | docs(#14): add grounded answering design and test plan | #14 |
| 633c74b | feat(#14): generate grounded answers with citations | #14 |
| 3a52a8d | chore(#14): fix line length and linting in answering module | #14 |
