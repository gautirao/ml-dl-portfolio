# System Overview

LedgerMind Local is a private, local-first financial intelligence tool. It allows users to import bank transactions from CSV files (Monzo, HSBC, etc.) and perform deterministic analytics and semantic searches.

## Key Features
- **Deterministic Analytics**: Uses DuckDB to calculate exact totals, averages, and comparisons.
- **Semantic Search**: Uses a local vector store (ChromaDB) and local embeddings to find transactions based on meaning rather than just keyword matching.
- **AI Assistant**: A local LLM (Ollama) acts as a planner and executor, translating natural language into tool calls.
- **Privacy**: All data stays on your machine. No cloud APIs or external tracking are used.

## Methodology
The system separates "fact-finding" (calculating totals) from "interpretation" (answering questions about the system). Analytics are always performed against the database, never guessed by the LLM.
