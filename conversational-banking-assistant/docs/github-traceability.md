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
