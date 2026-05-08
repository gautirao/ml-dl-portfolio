# Portfolio Summary: LedgerMind Local

## 2-Line Summary
A privacy-first personal finance assistant that uses a local Planner-Executor AI architecture to provide 100% numerically accurate insights from bank statements without data ever leaving the user's machine.

## Key Highlights
-   **Local AI Orchestration:** Integrated Ollama/llama3.2 for reasoning, eliminating cloud dependency and ensuring data privacy.
-   **Planner-Executor Pattern:** Built a robust system that separates LLM intent recognition from deterministic SQL execution via DuckDB, preventing "math hallucinations."
-   **Hybrid Semantic Search:** Engineered a local vector search layer using **ChromaDB** to enable broad conceptual queries (e.g., "takeaway spending") while maintaining deterministic accuracy for the final totals.
-   **Human-in-the-loop AI:** Developed a category suggestion and approval workflow that combines AI-assisted semantic matching with mandatory human oversight, preventing "categorization drift" and ensuring long-term data integrity.
-   **Local RAG Knowledge Base:** Integrated a grounded explanation system using local markdown files and vector search, allowing the assistant to explain its own logic and guardrails using retrieved documentation rather than internal training data.
-   **High-Performance OLAP:** Leveraged DuckDB for near-instant analytical queries across thousands of financial transactions.
-   **Multi-Layer Guardrails:** Implemented input/output safety checks to enforce a "No Financial Advice" policy and protect against prompt injection.
-   **Transparent AI:** Developed an "Execution Trace" evidence panel in React to provide users with a clear audit trail for all AI-generated answers.

## Skills Demonstrated
-   **Backend:** Python, FastAPI, Pydantic, DuckDB, SQL.
-   **Frontend:** React, TypeScript, Tailwind CSS, Vite.
-   **AI/ML:** LLM Prompt Engineering, Planner-Executor Architecture, Local LLM deployment (Ollama).
-   **Engineering:** Test-Driven Development (Pytest), Clean Architecture, API Design, Security Guardrails.

---

## Suggested CV Entry
**LedgerMind Local | Full-Stack AI Engineer Portfolio Project**
-   Architected a local-first AI financial assistant using a **Planner-Executor** pattern and **Hybrid Semantic Search** (ChromaDB + DuckDB) to solve LLM arithmetic inaccuracies and enable conceptual queries, achieving 100% numerical precision.
-   Integrated a **Local RAG Knowledge Base** to provide grounded system explanations and guardrail enforcement using local documentation.
-   Engineered a high-performance data pipeline using **FastAPI** and **DuckDB** to ingest and analyze heterogeneous bank statements (Monzo, HSBC).
-   Implemented multi-stage **AI Guardrails** and a React-based **Execution Trace** panel to ensure system safety and provide users with auditable evidence for AI responses.
-   Deployed local LLM orchestration using **Ollama** and **llama3.2**, ensuring zero data leakage to third-party cloud providers.

---

## Suggested LinkedIn Post
I’ve just finalized **LedgerMind Local**, a project that explores how we can build AI financial tools that are actually trustworthy and private.

Most "Chat with your Data" apps have two massive flaws:
1. They send your sensitive data to the cloud.
2. They hallucinate when doing math.

LedgerMind Local fixes this with a **Planner-Executor** architecture. A local LLM (`llama3.2` via `Ollama`) acts as the "brain" to understand your question, but it never does the math. Instead, it generates a plan for **DuckDB** to execute deterministic SQL queries.

**Result?** 100% numerical accuracy, zero data leakage, and a full "Execution Trace" so you can audit the AI’s work.

Check out the repo here: [Link to Repo]

#AI #PersonalFinance #PrivacyFirst #FastAPI #React #Ollama #DuckDB #PortfolioProject
