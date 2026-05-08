import os
import duckdb
from pathlib import Path
from pydantic_settings import BaseSettings
import uuid
import json

class Settings(BaseSettings):
    db_path: str = "data/ledgermind.db"
    schema_path: str = "src/database/schema.sql"
    vector_store_path: str = "data/vector_store"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    class Config:
        env_prefix = "LM_"
        env_file = ".env"
        extra = "ignore"

settings = Settings()

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.db_path
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = None

    def get_connection(self):
        if self.conn is None:
            self.conn = duckdb.connect(self.db_path)
        return self.conn

    def initialize_db(self):
        """Initializes the database with the schema and logs the event."""
        conn = self.get_connection()
        
        # Read and execute schema
        schema_file = Path(__file__).parent / "schema.sql"
        with open(schema_file, "r") as f:
            schema_sql = f.read()
        
        conn.execute(schema_sql)
        
        # Log DB initialization to audit_events
        audit_id = str(uuid.uuid4())
        event_type = "DB_INIT"
        description = "Database initialized with schema"
        metadata = json.dumps({"db_path": self.db_path})
        
        conn.execute(
            "INSERT INTO audit_events (id, event_type, description, metadata) VALUES (?, ?, ?, ?)",
            (audit_id, event_type, description, metadata)
        )
        print(f"Database initialized at {self.db_path}")

    def log_event(self, event_type: str, description: str, metadata: dict = None):
        """Logs an event to the audit_events table."""
        conn = self.get_connection()
        audit_id = str(uuid.uuid4())
        
        # Handle non-serializable objects like UUID
        def default_handler(obj):
            if isinstance(obj, uuid.UUID):
                return str(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        metadata_json = json.dumps(metadata, default=default_handler) if metadata else None
        
        conn.execute(
            "INSERT INTO audit_events (id, event_type, description, metadata) VALUES (?, ?, ?, ?)",
            (audit_id, event_type, description, metadata_json)
        )

# Global instance for dependency injection
db_manager = DatabaseManager()
