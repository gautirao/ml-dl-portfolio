# Release Readiness Checklist

Complete these steps before presenting LedgerMind Local as a portfolio piece.

## 1. Data Safety & Privacy
- [ ] **No Real Data Tracked:** Run `git status` and ensure no real bank statements (`.csv`), DuckDB files (`.db`), or ChromaDB folders are tracked.
- [ ] **Gitignore Verification:** Check `.gitignore` for `*.db`, `vector_store/`, and `data/`.
- [ ] **Sample Data Only:** Verify that only `sample-data/*_demo.csv` files are committed.

## 2. Setup & Documentation
- [ ] **README Updated:** Quickstart demo section is clear and works from a fresh clone.
- [ ] **Makefile Tested:** `make backend`, `make frontend`, and `make test` all work.
- [ ] **Env Examples:** `.env.example` exists in both `backend/` and `frontend/`.
- [ ] **Architecture Docs:** ADRs are present and reflect the final implementation.
- [ ] **Knowledge Base:** Local RAG markdown files in `docs/kb/` are accurate.

## 3. Technical Integrity
- [ ] **Backend Tests:** Run `make test` and ensure all 50+ tests pass.
- [ ] **Frontend Build:** Run `make build` and ensure no type errors or build failures.
- [ ] **Ollama Model:** Documentation explicitly mentions `llama3.2` as the required model.
- [ ] **Python Version:** `.python-version` or `pyproject.toml` specifies Python 3.10+.

## 4. Demo Walkthrough
- [ ] **Import Flow:** Can import `monzo_demo.csv` without errors.
- [ ] **Analytics:** Charts and totals display correctly for demo data.
- [ ] **Chat:** AI answers "How much spent on groceries?" correctly (using deterministic tools).
- [ ] **Search:** Semantic search matches "Starbucks" when searching for "coffee" (after index rebuild).
- [ ] **Trace:** Execution Trace correctly shows the SQL used.
- [ ] **Guardrails:** Refuses financial advice and SQL injection attempts.

## 5. Visual Polish
- [ ] **Screenshots:** All items in `docs/screenshots/README.md` are captured and placed in the folder.
- [ ] **UI Consistency:** No broken icons, consistent padding, and mobile-responsive (basic).
- [ ] **Loading States:** UI shows spinners/ghost-loaders during AI generation or data fetching.
