"""
PIA Immutable Event Store.

Every significant event that happens in the system — ingestion, measurement generation,
evidence creation, reasoning, graph projection updates, sync completions — is written
here as an immutable append-only log entry.

This is NOT the Operational Store (which holds current canonical state).
This is the audit log that enables:
  - Deterministic replay
  - Complete provenance
  - Time-travel debugging
  - Incident forensics
"""
from __future__ import annotations

import uuid
import json
import sqlite3
import threading
import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


_DEFAULT_EVENT_DB_PATH = Path(__file__).parent.parent.parent.parent / "pia_events.db"


class EventType(str, Enum):
    # Ingestion Events
    SYNC_STARTED = "sync.started"
    SYNC_COMPLETED = "sync.completed"
    SYNC_FAILED = "sync.failed"
    COMMIT_INGESTED = "commit.ingested"
    DEVELOPER_INGESTED = "developer.ingested"
    FILE_INGESTED = "file.ingested"

    # Measurement Events
    MEASUREMENT_CREATED = "measurement.created"
    MEASUREMENT_VERSIONED = "measurement.versioned"

    # Evidence Events
    EVIDENCE_CREATED = "evidence.created"
    EVIDENCE_VERSIONED = "evidence.versioned"

    # Projection Events
    PROJECTION_BUILD_STARTED = "projection.build_started"
    PROJECTION_BUILD_COMPLETED = "projection.build_completed"
    PROJECTION_BUILD_FAILED = "projection.build_failed"
    PROJECTION_INVALIDATED = "projection.invalidated"

    # Execution Events
    EXECUTION_STARTED = "execution.started"
    CAPABILITY_STARTED = "capability.started"
    CAPABILITY_COMPLETED = "capability.completed"
    REASONING_COMPLETED = "reasoning.completed"
    EXECUTION_COMPLETED = "execution.completed"
    EXECUTION_FAILED = "execution.failed"

    # Algorithm Events
    ALGORITHM_REGISTERED = "algorithm.registered"
    ALGORITHM_VERSIONED = "algorithm.versioned"

    # System Events
    SYSTEM_STARTED = "system.started"
    HEALTH_CHANGED = "health.changed"


@dataclass
class StoreEvent:
    """A single immutable event in the event log."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    occurred_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    schema_version: str = "v1"

    # Who/What produced this event
    source_component: str = ""     # "sync_engine" | "projection_engine" | "cognitive_runtime" | ...
    algorithm_version: Optional[str] = None

    # Context
    workspace_id: Optional[str] = None
    repository_session_id: Optional[str] = None
    execution_id: Optional[str] = None
    dataset_id: Optional[str] = None

    # Payload (fully serializable)
    payload: Dict[str, Any] = field(default_factory=dict)

    # References to affected canonical objects
    affected_object_ids: List[str] = field(default_factory=list)
    affected_object_types: List[str] = field(default_factory=list)


class ImmutableEventStore:
    """
    Append-only SQLite event log. Records are NEVER updated or deleted.
    Provides replay, time-range queries, and object-level event history.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or _DEFAULT_EVENT_DB_PATH
        self._local = threading.local()

    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn = conn
        return self._local.conn

    def initialize(self) -> None:
        conn = self._conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                schema_version TEXT DEFAULT 'v1',
                source_component TEXT,
                algorithm_version TEXT,
                workspace_id TEXT,
                repository_session_id TEXT,
                execution_id TEXT,
                dataset_id TEXT,
                payload TEXT,
                affected_object_ids TEXT,
                affected_object_types TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_occurred ON events(occurred_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_execution ON events(execution_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON events(repository_session_id)")
        conn.commit()

    def append(self, event: StoreEvent) -> StoreEvent:
        """Write an immutable event. This is the ONLY write operation."""
        conn = self._conn()
        conn.execute(
            """INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                event.event_id, event.event_type, event.occurred_at, event.schema_version,
                event.source_component, event.algorithm_version,
                event.workspace_id, event.repository_session_id,
                event.execution_id, event.dataset_id,
                json.dumps(event.payload),
                json.dumps(event.affected_object_ids),
                json.dumps(event.affected_object_types),
            )
        )
        conn.commit()
        return event

    def get_events(
        self,
        event_types: Optional[List[str]] = None,
        execution_id: Optional[str] = None,
        repository_session_id: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> List[StoreEvent]:
        """Query events with optional filters."""
        conn = self._conn()
        clauses = []
        params: List[Any] = []

        if event_types:
            placeholders = ",".join("?" * len(event_types))
            clauses.append(f"event_type IN ({placeholders})")
            params.extend(event_types)
        if execution_id:
            clauses.append("execution_id=?")
            params.append(execution_id)
        if repository_session_id:
            clauses.append("repository_session_id=?")
            params.append(repository_session_id)
        if since:
            clauses.append("occurred_at >= ?")
            params.append(since)
        if until:
            clauses.append("occurred_at <= ?")
            params.append(until)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.extend([limit, offset])
        rows = conn.execute(
            f"SELECT * FROM events {where} ORDER BY occurred_at DESC LIMIT ? OFFSET ?",
            params
        ).fetchall()
        return [self._row_to_event(r) for r in rows]

    def get_events_for_object(self, object_id: str, limit: int = 50) -> List[StoreEvent]:
        """Get all events that affected a specific canonical object."""
        conn = self._conn()
        rows = conn.execute(
            "SELECT * FROM events WHERE affected_object_ids LIKE ? ORDER BY occurred_at DESC LIMIT ?",
            (f"%{object_id}%", limit)
        ).fetchall()
        return [self._row_to_event(r) for r in rows]

    def count(self, event_types: Optional[List[str]] = None) -> int:
        conn = self._conn()
        if event_types:
            ph = ",".join("?" * len(event_types))
            row = conn.execute(f"SELECT COUNT(*) as cnt FROM events WHERE event_type IN ({ph})", event_types).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) as cnt FROM events").fetchone()
        return row["cnt"] if row else 0

    def _row_to_event(self, row: sqlite3.Row) -> StoreEvent:
        return StoreEvent(
            event_id=row["event_id"],
            event_type=row["event_type"],
            occurred_at=row["occurred_at"],
            schema_version=row["schema_version"],
            source_component=row["source_component"] or "",
            algorithm_version=row["algorithm_version"],
            workspace_id=row["workspace_id"],
            repository_session_id=row["repository_session_id"],
            execution_id=row["execution_id"],
            dataset_id=row["dataset_id"],
            payload=json.loads(row["payload"]) if row["payload"] else {},
            affected_object_ids=json.loads(row["affected_object_ids"]) if row["affected_object_ids"] else [],
            affected_object_types=json.loads(row["affected_object_types"]) if row["affected_object_types"] else [],
        )

    def close(self) -> None:
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None


# ─────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────

_event_store: Optional[ImmutableEventStore] = None


def get_event_store() -> ImmutableEventStore:
    global _event_store
    if _event_store is None:
        _event_store = ImmutableEventStore()
        _event_store.initialize()
    return _event_store
