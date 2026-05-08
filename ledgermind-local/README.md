# LedgerMind Local

**Privacy-first, local-AI financial assistant with deterministic execution.**

LedgerMind Local is a recruiter-ready portfolio project demonstrating a **Planner-Executor architecture** for personal finance. Unlike "Chat with CSV" tools that suffer from LLM "math hallucinations," LedgerMind uses a local LLM to **plan** a query and **deterministic tools** to calculate totals, ensuring 100% numerical accuracy while keeping sensitive bank data on your machine.

---

## 🚀 Quickstart Demo

Follow these steps to see LedgerMind Local in action with safe, synthetic data.

### 1. Prerequisites
-   Python 3.10+ (recommend [uv](https://github.com/astral-sh/uv) for fast dependency management)
-   Node.js 18+
-   [Ollama](https://ollama.com/) (installed and running)

### 2. Setup Ollama
```bash
ollama pull llama3.2
```

### 3. Installation
```bash
# Clone the repository
git clone <this-repo-url>
cd ledgermind-local

# Install Backend
cd backend
pip install uv # if not installed
uv sync

# Install Frontend
cd ../frontend
npm install
```

### 4. Running the App
Use the provided `Makefile` for convenience (or see commands in `Makefile` if `make` is not available):

```bash
# Terminal 1: Start Backend
make backend

# Terminal 2: Start Frontend
make frontend
```
Visit `http://localhost:5173`.

### 5. Step-by-Step Demo
1.  **Import Demo Data:** Go to the "Import" page. Upload `sample-data/monzo_demo.csv`.
2.  **View Analytics:** Navigate to "Analytics" to see the spending breakdown.
3.  **Chat with AI:** Ask "How much did I spend at Starbucks?" or "What was my total income?"
4.  **See the Evidence:** Click the "Planner & Evidence" icon in the chat to see the SQL and Execution Trace.
5.  **Rebuild Index:** Go to "Search" and click "Rebuild Index" to enable semantic search on the demo data.
6.  **Try Semantic Search:** Ask "How much did I spend on coffee?" (This uses semantic matching for "Starbucks").

---

## 🏗️ Development Commands
A `Makefile` is provided in the root directory:
- `make backend`: Run backend dev server
- `make frontend`: Run frontend dev server
- `make test`: Run backend tests
- `make build`: Build frontend and check types
- `make reset-local`: Wipes local database and vector store (use with caution)

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
-   **Local Semantic Search:**
    -   Uses **ChromaDB** for local vector storage of merchants, categories, and descriptions.
    -   Semantic matching for broad queries like "Show my coffee spending" or "commuting costs".
    -   **Hybrid Approach:** Semantic search identifies candidates; DuckDB performs the final deterministic calculation.
-   **Deterministic Analytics:**
    -   Spending summaries (Inflow/Outflow/Net).
    -   Top merchant analysis.
    -   Recurring payment detection (heuristic cadence analysis).
    -   Category-based aggregations.
-   **Local RAG Knowledge Base:**
    -   Answers system-related questions ("How are totals calculated?", "What does uncategorised mean?") using a local knowledge base.
    -   Uses local markdown files for explanations, ensuring the AI is grounded in system documentation.
    -   Maintains a strict boundary: RAG is for explanations; DuckDB is for financial calculations.
-   **Conversational Interface:** Ask questions like "How much did I spend at Amazon last month?" or "Why does the app say it cannot give financial advice?"
-   **Human-in-the-Loop Category Approval:**
    -   AI suggests categories and merchant normalization based on semantic matching.
    -   Users approve, reject, or edit suggestions before they become deterministic rules.
    -   Approved rules are automatically applied to future imports, ensuring long-term data consistency.
-   **Execution Trace:** A collapsible "Planner & Evidence" panel in the UI that proves how the AI reached its answer.
-   **Privacy-First:** No cloud sync, no tracking, no data leaves your device.

---

## 🛠️ Tech Stack
| Tier | Technology |
| :--- | :--- |
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, Lucide |
| **Backend** | Python, FastAPI, Pydantic, DuckDB |
| **LLM** | Ollama (llama3.2) |
| **Search** | ChromaDB (Vector Store) |
| **Testing** | Pytest |

---

## 📸 Screenshots (Checklist)
See `docs/screenshots/README.md` for the full portfolio screenshot checklist.
-   **Import Workflow**
-   **Financial Dashboard**
-   **AI Evidence Panel**
-   **Category Review Flow**

---

## 🛡️ Guardrails & Safety
LedgerMind implements a "No Financial Advice" boundary. It will refuse to give investment tips (e.g., "Should I buy Bitcoin?") and focuses strictly on reporting historical facts from your data.
-   **Input Guardrails:** Detects and blocks malicious SQL injection or out-of-scope prompts.
-   **Plan Validation:** Ensures the LLM only selects from the approved tool registry.
-   **Output Verification:** Cross-checks the LLM's final answer against the deterministic tool results.

---

## 🗺️ Roadmap
-   [x] **Local RAG Knowledge Base:** Grounded system explanations using local markdown files.
-   [ ] **Multi-Currency Support:** Automatic conversion and normalization for international transactions.
-   [ ] **Advanced Forecasting:** Using lightweight time-series models for budget predictions.
-   [ ] **Direct API Integration:** Support for Plaid or Open Banking APIs.

---

## 📜 License
Built as a professional portfolio project. Distributed under the MIT License.
