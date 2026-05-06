# LedgerMind Local

A privacy-first conversational AI assistant for bank statements.

## Milestone 1: Foundation & Persistence

### Features
- FastAPI backend skeleton.
- DuckDB local file database for high-performance financial queries.
- Normalized schema for transactions, uploaded files, and audit logs.
- Audit logging for every database initialization.
- Local-only data storage in `backend/data/`.

### Prerequisites
- Python 3.10+
- `uv` (FastAPI dependency management)

### Setup & Run

1. **Install dependencies:**
   ```bash
   cd backend
   uv sync
   ```

2. **Run the backend:**
   ```bash
   uv run python src/main.py
   ```
   The API will be available at `http://localhost:8000`.

3. **Check health:**
   ```bash
   curl http://localhost:8000/health
   ```

### Running Tests
```bash
cd backend
uv run pytest
```

### Data Privacy
All data is stored locally in `backend/data/ledgermind.db`. This directory is gitignored and will never be committed to source control.
