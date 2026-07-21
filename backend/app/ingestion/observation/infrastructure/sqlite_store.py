import sqlite3
import json
from typing import Any, Dict, List, Optional
from app.ingestion.observation.ingestion.models import SyncCursor
from .interfaces import ICheckpointStore, IObservationStore

class SQLiteCheckpointStore(ICheckpointStore):
    def __init__(self, db_path: str = "ingestion.db"):
        self.db_path = db_path
        self._initialize_pragmas()
        
    def _initialize_pragmas(self):
        with sqlite3.connect(self.db_path, uri=True) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")

    def get(self, adapter: str) -> Optional[SyncCursor]:
        with sqlite3.connect(self.db_path, uri=True) as conn:
            cursor = conn.execute("SELECT cursor_value FROM checkpoints WHERE source_id = ?", (adapter,))
            row = cursor.fetchone()
            return SyncCursor(adapter=adapter, cursor=row[0]) if row else None

    def update_cursor(self, adapter: str, cursor: SyncCursor) -> None:
        with sqlite3.connect(self.db_path, uri=True) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO checkpoints (source_id, cursor_value) VALUES (?, ?)",
                (adapter, cursor.cursor)
            )

class SQLiteObservationStore(IObservationStore):
    def __init__(self, db_path: str = "ingestion.db"):
        self.db_path = db_path
        self._initialize_pragmas()
        
    def _initialize_pragmas(self):
        with sqlite3.connect(self.db_path, uri=True) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")

    def append_raw(self, source_id: str, external_id: str, payload: Dict[str, Any]) -> bool:
        try:
            with sqlite3.connect(self.db_path, uri=True) as conn:
                conn.execute(
                    "INSERT INTO raw_observations (source_id, external_event_id, payload) VALUES (?, ?, ?)",
                    (source_id, external_id, json.dumps(payload))
                )
            return True
        except sqlite3.IntegrityError:
            # Duplicate event, safely ignored
            return False

    def claim_batch(self, batch_size: int = 100) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path, uri=True) as conn:
            conn.row_factory = sqlite3.Row
            # Use IMMEDIATE transaction to acquire a reserved lock, preventing other readers from acquiring it 
            # and preventing the Read-Modify-Write contention race condition.
            conn.execute("BEGIN IMMEDIATE")
            
            # Select IDs of pending items
            cursor = conn.execute(
                "SELECT id FROM raw_observations WHERE status = 0 ORDER BY created_at ASC LIMIT ?", 
                (batch_size,)
            )
            rows = cursor.fetchall()
            if not rows:
                return []
                
            ids = [row["id"] for row in rows]
            placeholders = ",".join("?" for _ in ids)
            
            # Update status to 1 (Processing)
            conn.execute(
                f"UPDATE raw_observations SET status = 1, updated_at = CURRENT_TIMESTAMP WHERE id IN ({placeholders})",
                ids
            )
            
            # Fetch the actual payloads
            cursor = conn.execute(
                f"SELECT * FROM raw_observations WHERE id IN ({placeholders})",
                ids
            )
            return [dict(row) for row in cursor.fetchall()]

    def mark_processed(self, row_id: int) -> None:
        with sqlite3.connect(self.db_path, uri=True) as conn:
            conn.execute(
                "UPDATE raw_observations SET status = 2 WHERE id = ?",
                (row_id,)
            )

    def append_dlq(self, payload: str, error_message: str, schema_version: str, traceback_str: Optional[str] = None) -> None:
        with sqlite3.connect(self.db_path, uri=True) as conn:
            conn.execute(
                "INSERT INTO dead_letter_queue (original_payload, schema_version, error_message, traceback) VALUES (?, ?, ?, ?)",
                (payload, schema_version, error_message, traceback_str)
            )

    def reset_stale_jobs(self) -> None:
        with sqlite3.connect(self.db_path, uri=True) as conn:
            conn.execute(
                "UPDATE raw_observations SET status = 0 WHERE status = 1 AND updated_at < datetime('now', '-1 hour')"
            )

