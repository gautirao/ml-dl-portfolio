# ADR-002: Planner-Executor vs. Chat-with-CSV

## Status
Accepted

## Context
LLMs are notoriously poor at arithmetic and "hallucinate" when processing long lists of transactions. Users need 100% numerical accuracy for financial reporting.

## Decision
We will use a **Planner-Executor** pattern instead of passing raw CSV data into a chat context.
1.  **Planner:** The LLM receives the user's question and a list of available "Tools" (Python functions that run SQL on DuckDB).
2.  **Plan:** The LLM outputs a JSON plan specifying which tool to use and with what arguments (e.g., date ranges, merchant filters).
3.  **Executor:** A deterministic Python runner executes the tool against the DuckDB database.
4.  **Final Answer:** The LLM summarizes the deterministic result for the user.

## Consequences
-   **Pros:** Guaranteed numerical accuracy (handled by SQL); lower context window usage (only tool definitions are passed, not transactions); traceable reasoning (Execution Trace).
-   **Cons:** The LLM must be capable of reliably outputting structured JSON; complex queries require sophisticated tool definitions.
