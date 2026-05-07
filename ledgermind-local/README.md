# LedgerMind Local

**Privacy-first, local-AI financial assistant with deterministic execution.**

LedgerMind Local is a recruiter-ready portfolio project demonstrating a **Planner-Executor architecture** for personal finance. Unlike "Chat with CSV" tools that suffer from LLM "math hallucinations," LedgerMind uses a local LLM to **plan** a query and **deterministic tools** to calculate totals, ensuring 100% numerical accuracy while keeping sensitive bank data on your machine.

---

## 🛑 The Problem
Standard LLMs are notoriously bad at arithmetic and often "hallucinate" financial figures when reading large datasets. Additionally, uploading sensitive bank statements to cloud-based AI providers (ChatGPT, Claude) poses significant privacy risks for personal financial data.

## ✅ The Solution: LedgerMind Local
LedgerMind solves this by:
1.  **Local Execution:** Using **Ollama** and **llama3.2** to process data entirely on your local machine.
2.  **Planner-Executor Pattern:** Separating the "reasoning" (planning which tool to use) from the "calculation" (running SQL on DuckDB).
3.  **Deterministic Tools:** Using high-performance SQL via **DuckDB** for all aggregations and searches.
4.  **Evidence-Based AI:** Every answer includes an **Execution Trace** showing exactly which tool was used and what data was retrieved.

---

## 🏗️ Architecture Summary
-   **Frontend:** React (TypeScript) + Vite + Tailwind CSS + Lucide Icons.
-   **Backend:** FastAPI (Python) + DuckDB (Embedded OLAP Database).
-   **AI Orchestration:** Planner-Executor pattern with **llama3.2** via Ollama.
-   **Safety:** Multi-stage guardrails (Input, Plan, Output) and deterministic tool validation.
-   **Persistence:** Local DuckDB file storage with audit logging.

---

## ✨ Key Features
-   **Bank Statement Ingestion:**
    -   **Monzo:** Support for rich Monzo CSV exports including merchant metadata and categories.
    -   **HSBC:** Support for minimal HSBC transaction-history CSVs.
-   **Deterministic Analytics:**
    -   Spending summaries (Inflow/Outflow/Net).
    -   Top merchant analysis.
    -   Recurring payment detection (heuristic cadence analysis).
    -   Category-based aggregations.
-   **Conversational Interface:** Ask questions like "How much did I spend at Amazon last month?" or "What are my recurring subscriptions?"
-   **Execution Trace:** A collapsible "Planner & Evidence" panel in the UI that proves how the AI reached its answer.
-   **Privacy-First:** No cloud sync, no tracking, no data leaves your device.

---

## 🛠️ Tech Stack
| Tier | Technology |
| :--- | :--- |
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, Lucide |
| **Backend** | Python, FastAPI, Pydantic |
| **Database** | DuckDB (SQL-based OLAP) |
| **LLM** | Ollama, llama3.2 (3B) |
| **Testing** | Pytest, Axios-mock-adapter |

---

## 🚀 Getting Started

### 1. Prerequisites
-   Python 3.10+
-   Node.js 18+
-   [Ollama](https://ollama.com/) (installed and running)

### 2. Setup Ollama
```bash
ollama pull llama3.2
```

### 3. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install uv
uv sync
PYTHONPATH=. uv run pytest  # Verify setup
uv run python src/main.py   # Start server
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:5173`.

---

## 📸 Screenshots (Placeholders)
-   **Import Workflow:** `docs/images/upload-page.png`
-   **Financial Dashboard:** `docs/images/analytics-page.png`
-   **AI Evidence Panel:** `docs/images/chat-evidence-panel.png`

---

## 🗨️ Example Questions
-   "What was my total spending in January 2026?"
-   "Show me my top 5 merchants for outflows."
-   "How much have I spent on groceries lately?"
-   "What are my recurring payments?"
-   "Summarize my spending across all banks."

---

## 🛡️ Guardrails & Safety
LedgerMind implements a "No Financial Advice" boundary. It will refuse to give investment tips (e.g., "Should I buy Bitcoin?") and focuses strictly on reporting historical facts from your data.
-   **Input Guardrails:** Detects and blocks malicious SQL injection or out-of-scope prompts.
-   **Plan Validation:** Ensures the LLM only selects from the approved tool registry.
-   **Output Verification:** Cross-checks the LLM's final answer against the deterministic tool results.

---

## 🗺️ Roadmap
-   [ ] **RAG (Retrieval-Augmented Generation):** Vector search for deep semantic search across transaction descriptions.
-   [ ] **Multi-Currency Support:** Automatic conversion and normalization for international transactions.
-   [ ] **Advanced Forecasting:** Using lightweight time-series models for budget predictions.
-   [ ] **Direct API Integration:** Support for Plaid or Open Banking APIs.

---

## 📜 License
Built as a professional portfolio project. Distributed under the MIT License.
