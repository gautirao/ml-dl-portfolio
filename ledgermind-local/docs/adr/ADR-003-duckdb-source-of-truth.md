# ADR-003: DuckDB as Source of Truth

## Status
Accepted

## Context
Personal finance data is transactional and requires fast analytical aggregations (OLAP). It also needs to be easily accessible from both Python (backend) and potentially external BI tools.

## Decision
We will use **DuckDB** as the primary storage and analytical engine.
1.  Data is stored in a local `.db` file.
2.  Transactions are normalized into a standard schema regardless of the source bank (Monzo, HSBC).
3.  All analytics (summaries, top merchants, search) are performed via SQL queries against DuckDB.

## Consequences
-   **Pros:** Extremely fast analytical performance; zero-config (serverless); single file storage; robust SQL support.
-   **Cons:** Not designed for high-concurrency writes (not an issue for a single-user local app); no built-in user authentication (handled at the application layer).
