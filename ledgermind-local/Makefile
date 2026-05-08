.PHONY: backend frontend test build clean reset-local help

help:
	@echo "LedgerMind Local Development Commands:"
	@echo "  make backend      Run the backend dev server"
	@echo "  make frontend     Run the frontend dev server"
	@echo "  make test         Run backend tests"
	@echo "  make build        Build frontend and check types"
	@echo "  make clean        Remove temporary files and caches"
	@echo "  make reset-local  !!!! DANGER !!!! Deletes local database and vector store"

backend:
	cd backend && uv run uvicorn src.main:app --reload

frontend:
	cd frontend && npm run dev

test:
	cd backend && uv run pytest

build:
	cd frontend && npm run build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +

reset-local:
	@echo "WARNING: This will delete your local database and vector store."
	@echo "Press Ctrl+C to cancel or Enter to continue."
	@read _
	rm -rf backend/data/*.db backend/data/vector_store/*
	@echo "Local data reset complete."
