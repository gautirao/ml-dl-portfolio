# Guardrails and Limitations

LedgerMind Local is designed with specific boundaries to ensure accuracy and safety.

## No Financial Advice
The system is a tool for data analysis and visualisation. It **cannot** and **will not** provide financial advice, investment recommendations, or tax guidance.

## Calculation Accuracy
All financial totals are calculated using deterministic SQL queries via DuckDB. The LLM (Large Language Model) is never used to perform calculations; it only generates the queries or calls the tools that do.

## Scope Boundaries
- **Local Only**: The system cannot access live bank feeds or external financial APIs.
- **Data Quality**: Insights are only as good as the imported CSV data.
- **Ambiguity**: If a user request is unclear, the assistant will ask for clarification rather than making assumptions.
