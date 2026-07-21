import sqlite3
import json
import os
from datetime import datetime

class IngestionStorageManager:
    """Manages the operational lifecycle of the SQLite ingestion store."""
    
    def __init__(self, db_path: str = "ingestion.db", archive_dir: str = "data/archives"):
        self.db_path = db_path
        self.archive_dir = archive_dir
        os.makedirs(self.archive_dir, exist_ok=True)

    def rotate_logs(self, max_capacity: int = 50000, archive_chunk: int = 5000, metrics = None) -> None:
        """
        Check table capacity and archive old processed rows if exceeding max_capacity.
        This should be called as an out-of-band maintenance task, NOT in the ingestion hot path.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT count(*) as count FROM raw_observations")
            row = cursor.fetchone()
            if not row or row["count"] <= max_capacity:
                return

            # Exceeds capacity, archive the oldest processed chunk
            cursor = conn.execute(
                "SELECT * FROM raw_observations WHERE status = 2 ORDER BY created_at ASC LIMIT ?",
                (archive_chunk,)
            )
            rows = cursor.fetchall()
            
            if not rows:
                return # Nothing to archive yet (still processing)

            # Write to JSONL
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = os.path.join(self.archive_dir, f"observations_{timestamp}.jsonl")
            
            with open(archive_path, "w") as f:
                for r in rows:
                    f.write(json.dumps(dict(r)) + "\n")
                    
            # Delete from SQLite
            ids = [r["id"] for r in rows]
            placeholders = ",".join("?" for _ in ids)
            conn.execute(
                f"DELETE FROM raw_observations WHERE id IN ({placeholders})",
                ids
            )
            
            if metrics is not None:
                metrics.increment("archival_events_count", len(rows))
