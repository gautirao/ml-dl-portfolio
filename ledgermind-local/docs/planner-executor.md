# Planner-Executor Pattern

The core design principle of LedgerMind Local is the **separation of reasoning from calculation**.

## Why not just "Chat with CSV"?
Most naive AI finance apps use a "long context" approach where they feed the entire CSV content into an LLM prompt and ask "What is the total?". This fails for three reasons:
1.  **Context Limits:** Bank statements can have thousands of rows, exceeding the LLM's context window.
2.  **Arithmetic Hallucinations:** LLMs are probabilistic text generators, not calculators. They often get sums wrong or skip rows.
3.  **Lack of Auditability:** There is no way to verify *how* the LLM reached a specific number.

## The LedgerMind Approach
LedgerMind uses a **Planner-Executor** architecture that treats the LLM as a router and the SQL database as the source of truth.

### 1. The Planner
The Planner is a specialized prompt for `llama3.2` that instructs it to act as a **Strategic Dispatcher**.
-   **Input:** Natural language query.
-   **Output:** A structured JSON **Plan**.
-   **Goal:** Identify the user's *intent* and extract *parameters* (dates, merchants, categories).

**Example Plan:**
```json
{
  "intent": "analyze_merchant_spending",
  "tool": "spending_summary",
  "arguments": {
    "merchant": "Amazon",
    "date_from": "2026-01-01"
  },
  "reasoning_summary": "User wants to know total spending at Amazon since the start of the year.",
  "confidence": 0.95
}
```

### 2. The Executor
The Executor is a deterministic Python module that takes the Plan and routes it to the correct **Deterministic Tool**.
-   It translates the JSON arguments into Python function calls.
-   It handles date parsing and validation.
-   It executes the query against DuckDB.
-   It captures **Evidence Metadata** (query scope, row counts, calculation methods).

### 3. The Tool Registry
LedgerMind has a fixed registry of tools. The Planner is strictly forbidden from inventing new tools.
-   `spending_summary`: Basic aggregation for specific entities.
-   `semantic_spending_search`: **Hybrid tool** introduced in Milestone 7. It uses a local vector store (ChromaDB) to find related merchants/categories before running a deterministic summary.
-   `top_merchants`: Ranking tool.
-   `compare_periods`: Period-over-period analysis.
-   `recurring_payments`: Cadence detection.
-   `transaction_search`: Filtering and raw data retrieval.

### 4. The Hybrid Semantic Flow
When a user asks a broad query like "What did I spend on takeaways?", the workflow expands:
1.  **Planner:** Recognizes the semantic nature and selects `semantic_spending_search`.
2.  **Semantic Matcher:** Queries ChromaDB for "takeaways" and finds matches like "Uber Eats", "Deliveroo", and the category "Food & Drink".
3.  **Executor:** Passes these candidates to the deterministic engine.
4.  **Evidence:** The Evidence Panel shows the semantic matches used, ensuring the user knows *why* specific merchants were included in the "takeaway" total.

### 5. Answer Generation & Evidence
Once the tool returns data, a final LLM pass (the **Answer Generator**) converts the raw numbers into a user-friendly response. Crucially, the UI displays the **Execution Trace** alongside the answer.

**The user can see:**
-   Which tool was selected.
-   What arguments were passed (e.g., exactly which date range was interpreted).
-   How many rows were actually analyzed by the SQL engine.

This "Show Your Work" model builds trust and ensures that the user is never guessing where a number came from.
