# ADR-004: RAG for Explanations Only

## Status
Accepted

## Context
Users often have questions about how the system works (e.g., "How is my spending categorized?" or "What banks are supported?"). While an LLM can answer these, it should do so based on actual project documentation rather than pre-trained "intuition".

## Decision
We will implement a **Retrieval-Augmented Generation (RAG)** pipeline specifically for system explanations.
1.  **Scope:** RAG is used ONLY for questions about the application itself, its logic, and its documentation.
2.  **Boundary:** RAG is NOT used for financial calculations (handled by the Planner-Executor/DuckDB flow).
3.  **Grounding:** The LLM must cite its sources from the local markdown files.

## Consequences
-   **Pros:** Grounded, accurate answers about system behavior; easy to update "knowledge" by editing markdown; clear separation of concerns between documentation and data.
-   **Cons:** Potential for the LLM to confuse "system data" with "user data" if the prompt boundaries are not strict.
