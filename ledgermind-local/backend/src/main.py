from fastapi import FastAPI, Depends
from src.database.connection import db_manager
from src.api.imports import router as import_router
from src.api.analytics import router as analytics_router
import duckdb

app = FastAPI(title="LedgerMind Local API")

app.include_router(import_router)
app.include_router(analytics_router)

@app.on_event("startup")
async def startup_event():
    # Initialize the database schema
    db_manager.initialize_db()

@app.get("/health")
async def health_check():
    try:
        conn = db_manager.get_connection()
        # Verify connectivity
        conn.execute("SELECT 1").fetchone()
        
        # Count tables to ensure schema is applied
        table_count = conn.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchone()[0]
        
        return {
            "status": "healthy",
            "database": "connected",
            "tables_found": table_count,
            "local_storage": db_manager.db_path
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
