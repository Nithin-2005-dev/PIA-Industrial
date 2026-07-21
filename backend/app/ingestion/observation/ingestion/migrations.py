import sqlite3

def run_migrations(db_path: str = "ingestion.db"):
    with sqlite3.connect(db_path) as conn:
        # Checkpoints Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                source_id TEXT PRIMARY KEY,
                cursor_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Observations Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                external_event_id TEXT,
                payload TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status INTEGER DEFAULT 0,
                UNIQUE(source_id, external_event_id)
            )
        """)
        
        # Dead Letter Queue
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dead_letter_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_payload TEXT NOT NULL,
                schema_version TEXT NOT NULL,
                error_message TEXT NOT NULL,
                traceback TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Performance Index
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_unprocessed ON raw_observations(status) 
            WHERE status = 0
        """)
