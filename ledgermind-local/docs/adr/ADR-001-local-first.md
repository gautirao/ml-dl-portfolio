# ADR-001: Local-First Privacy Architecture

## Status
Accepted

## Context
Personal financial data is highly sensitive. Standard LLM-based solutions often require uploading CSV files to cloud providers (OpenAI, Anthropic), which compromises user privacy and creates data residency concerns.

## Decision
We will build a "Local-First" architecture where:
1.  All data storage (DuckDB) resides on the user's local disk.
2.  All AI processing (Ollama + llama3.2) happens on the user's local hardware.
3.  No external API calls are made for data processing or analysis.
4.  Vector embeddings and semantic search are handled locally via ChromaDB.

## Consequences
-   **Pros:** 100% data privacy; zero latency for cloud round-trips; no subscription costs for the user.
-   **Cons:** Higher hardware requirements for the user (RAM/GPU); model quality is limited to what can run locally (e.g., 3B-7B parameters); no cross-device sync without manual file transfer.
