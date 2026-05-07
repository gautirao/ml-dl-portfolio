# Interview Demo Script (5 Minutes)

This script is designed to showcase the technical depth of LedgerMind Local during a recruiter or technical interview.

## Phase 1: The "Why" (30 Seconds)
-   **Action:** Open the browser to the LedgerMind Local home page.
-   **Script:** "LedgerMind Local is a privacy-first AI financial assistant. Most AI tools for finance either leak your data to the cloud or hallucinate numbers. This project solves that using a local-first architecture where a local LLM **plans** the query, but **deterministic SQL tools** do the math."

## Phase 2: Ingestion & Privacy (1 Minute)
-   **Action:** Go to the **Upload** page. Drag in a synthetic Monzo or HSBC CSV. Show the **Import Preview**.
-   **Script:** "Everything you see here is processed locally. We have a pluggable adapter system that handles different bank formats. Before importing, I can preview the data. We also use transaction fingerprinting to prevent duplicate imports."
-   **Action:** Click **Confirm Import**. Point to the "Local Processing" banner.

## Phase 3: Deterministic Analytics (1 Minute)
-   **Action:** Navigate to the **Analytics** page.
-   **Script:** "While there's an AI component, the core dashboard is 100% deterministic. We're using DuckDB, a high-performance OLAP database, to calculate spending summaries, top merchants, and even detect recurring subscriptions using heuristic cadence analysis."
-   **Action:** Change the date filter or bank filter to show reactive updates.

## Phase 4: The AI Planner-Executor (2 Minutes)
-   **Action:** Navigate to the **Chat** page.
-   **Script:** "This is where the 'Planner-Executor' architecture comes in. Instead of feeding the LLM all my data, I'll ask a question."
-   **Query:** "How much did I spend at Amazon last month?"
-   **Action:** Wait for the answer, then **open the Evidence Panel**.
-   **Script:** "Look at the **Execution Trace**. The LLM (llama3.2 running on my machine) interpreted my intent and generated a JSON plan. It decided to call the `spending_summary` tool with `merchant: Amazon`. The backend executed that SQL, and the LLM then summarized the result. This ensures the math is perfect because the LLM never actually did the addition."

## Phase 5: Guardrails & Safety (30 Seconds)
-   **Query:** "Should I buy Tesla stock?"
-   **Action:** Show the system refusing the advice.
-   **Script:** "Safety is built-in. We have input and output guardrails that enforce a 'No Financial Advice' boundary. The system stays strictly within historical reporting, which is critical for trustworthy financial AI."

## Closing (Optional)
-   **Script:** "The tech stack is FastAPI, DuckDB, and React, with Ollama for the local AI orchestration. It's a template for how we can build powerful AI tools that respect user privacy and numerical integrity."
