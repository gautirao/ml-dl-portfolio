# Privacy and Local-First

Privacy is a core tenet of LedgerMind Local.

## Data Residency
All your financial data, including transaction history, category rules, and vector embeddings, are stored locally on your machine in the `data/` directory.

## No External Calls
- **Database**: DuckDB is an in-process SQL OLAP database.
- **Vector Store**: ChromaDB runs locally.
- **AI/LLM**: Ollama runs models on your local hardware.
- **Embeddings**: Generated locally using a small transformer model.

## Security
The system does not require an internet connection to function once the local models are downloaded. Your sensitive financial information never leaves your device.
