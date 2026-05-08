# Planner-Executor Method

LedgerMind Local uses a "Planner-Executor" architecture to handle user requests.

## Phase 1: Planning
The user's natural language message is sent to a local LLM (Ollama). The LLM acts as a **Planner**, identifying the user's intent and selecting the appropriate tool from a predefined list. It returns a structured JSON plan.

## Phase 2: Execution
The system's **Executor** takes the JSON plan and runs the corresponding Python code. This might involve querying DuckDB for analytics or searching the vector store.

## Phase 3: Answer Generation
The result from the tool execution is passed back to the LLM (or a specialized Answer Generator) to formulate a natural language response for the user, accompanied by the raw evidence.

This separation ensures that the LLM never "hallucinates" financial numbers, as it only sees the results of verified code execution.
