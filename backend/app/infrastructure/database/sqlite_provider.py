"""
SQLite implementation of the PersistenceProvider.

Uses a single SQLite database file (pia_operational_store.db) stored in the
project root. All canonical records are serialized as JSON rows inside typed tables.
This provider handles full-text search via SQLite FTS5.

This is the default provider for local workstation use.
Swap out by implementing a PostgresProvider or DuckDBProvider with the same interface.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import datetime
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

from app.infrastructure.database.provider import PersistenceProvider, RecordNotFoundError, PersistenceError
from app.infrastructure.database.models import GlobalIdentity, ALL_RECORD_TYPES, CommitRecord

T = TypeVar("T")

_DEFAULT_DB_PATH = Path(__file__).parent.parent.parent.parent / "pia_store.db"

# Table name -> model class
_TABLE_MAP: Dict[str, type] = {
    cls.__name__.lower().replace("record", ""): cls
    for cls in ALL_RECORD_TYPES
}
_TYPE_TO_TABLE = {v: k for k, v in _TABLE_MAP.items()}

# Reserved SQLite keyword overrides
_TABLE_OVERRIDES: Dict[type, str] = {
    CommitRecord: "repo_commit",
}


def _table_name(model_type: type) -> str:
    if model_type in _TABLE_OVERRIDES:
        return _TABLE_OVERRIDES[model_type]
    name = model_type.__name__.lower()
    if name.endswith("record"):
        name = name[:-6]
    return name


def _to_dict(record: Any) -> Dict[str, Any]:
    """Serialize a dataclass record (with nested GlobalIdentity) to a flat dict for storage."""
    d = {}
    for f_name, f_val in vars(record).items():
        if isinstance(f_val, GlobalIdentity):
            d["object_id"] = f_val.object_id
            d["object_type"] = f_val.object_type
            d["version"] = f_val.version
            d["created_at"] = f_val.created_at
            d["updated_at"] = f_val.updated_at
            d["algorithm_version"] = f_val.algorithm_version
            d["dataset_id"] = f_val.dataset_id
            d["workspace_id"] = f_val.workspace_id
            d["execution_id"] = f_val.execution_id
            d["parent_ids"] = json.dumps(f_val.parent_ids)
        elif isinstance(f_val, (dict, list)):
            d[f_name] = json.dumps(f_val)
        else:
            d[f_name] = f_val
    return d


def _from_dict(model_type: type, row: Dict[str, Any]) -> Any:
    """Reconstruct a canonical record from a stored flat dict row."""
    import dataclasses

    identity_fields = {"object_id", "object_type", "version", "created_at", "updated_at",
                       "algorithm_version", "dataset_id", "workspace_id", "execution_id", "parent_ids"}

    kwargs = {}
    identity_kwargs = {}

    fields = {f.name: f for f in dataclasses.fields(model_type)}

    for key, val in row.items():
        if key in identity_fields:
            if key == "parent_ids":
                identity_kwargs[key] = json.loads(val) if val else []
            else:
                identity_kwargs[key] = val
        elif key in fields:
            field_type = fields[key].type
            # Try to parse JSON blobs back to dict/list
            if isinstance(val, str) and val.startswith(("{", "[")):
                try:
                    kwargs[key] = json.loads(val)
                except (json.JSONDecodeError, TypeError):
                    kwargs[key] = val
            else:
                kwargs[key] = val

    obj = model_type.__new__(model_type)
    # Set identity
    if "identity" in fields:
        obj.identity = GlobalIdentity(**identity_kwargs)
    for k, v in kwargs.items():
        if k != "identity":
            object.__setattr__(obj, k, v) if dataclasses.is_dataclass(obj) else setattr(obj, k, v)
    return obj


class SQLiteProvider(PersistenceProvider):
    """
    SQLite-backed PersistenceProvider.
    Thread-safe via a per-thread connection pattern.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or _DEFAULT_DB_PATH
        self._local = threading.local()

    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            self._local.conn = conn
        return self._local.conn

    def initialize(self) -> None:
        conn = self._conn()
        for model_type in ALL_RECORD_TYPES:
            table = _table_name(model_type)
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    object_id TEXT PRIMARY KEY,
                    object_type TEXT,
                    version INTEGER DEFAULT 1,
                    created_at TEXT,
                    updated_at TEXT,
                    algorithm_version TEXT,
                    dataset_id TEXT,
                    workspace_id TEXT,
                    execution_id TEXT,
                    parent_ids TEXT,
                    data TEXT
                )
            """)
            # FTS5 virtual table for full-text search
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {table}_fts USING fts5(
                    object_id UNINDEXED,
                    object_type UNINDEXED,
                    data,
                    content={table},
                    content_rowid=rowid
                )
            """)
        conn.commit()

    def _insert_fts(self, conn: sqlite3.Connection, table: str, d: Dict[str, Any]) -> None:
        try:
            conn.execute(
                f"INSERT OR REPLACE INTO {table}_fts(object_id, object_type, data) VALUES (?,?,?)",
                (d["object_id"], d["object_type"], d.get("data", ""))
            )
        except Exception:
            pass  # FTS is best-effort; don't block writes

    def insert(self, record: Any) -> Any:
        d = _to_dict(record)
        table = _table_name(type(record))
        data_blob = json.dumps({k: v for k, v in d.items() if k not in {
            "object_id", "object_type", "version", "created_at", "updated_at",
            "algorithm_version", "dataset_id", "workspace_id", "execution_id", "parent_ids"
        }})
        conn = self._conn()
        try:
            conn.execute(
                f"""INSERT INTO {table}
                    (object_id, object_type, version, created_at, updated_at,
                     algorithm_version, dataset_id, workspace_id, execution_id, parent_ids, data)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (d["object_id"], d["object_type"], d.get("version", 1),
                 d.get("created_at", ""), d.get("updated_at", ""),
                 d.get("algorithm_version"), d.get("dataset_id"),
                 d.get("workspace_id"), d.get("execution_id"),
                 d.get("parent_ids", "[]"), data_blob)
            )
            self._insert_fts(conn, table, {**d, "data": data_blob})
            conn.commit()
        except sqlite3.IntegrityError as e:
            raise PersistenceError(f"Insert failed for {table}: {e}")
        return record

    def update(self, record: Any) -> Any:
        d = _to_dict(record)
        table = _table_name(type(record))
        d["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
        data_blob = json.dumps({k: v for k, v in d.items() if k not in {
            "object_id", "object_type", "version", "created_at", "updated_at",
            "algorithm_version", "dataset_id", "workspace_id", "execution_id", "parent_ids"
        }})
        conn = self._conn()
        conn.execute(
            f"""UPDATE {table} SET updated_at=?, data=? WHERE object_id=?""",
            (d["updated_at"], data_blob, d["object_id"])
        )
        conn.commit()
        return record

    def get_by_id(self, model_type: Type[T], object_id: str) -> Optional[T]:
        table = _table_name(model_type)
        conn = self._conn()
        row = conn.execute(f"SELECT * FROM {table} WHERE object_id=?", (object_id,)).fetchone()
        if not row:
            return None
        return self._row_to_record(model_type, row)

    def _row_to_record(self, model_type: type, row: sqlite3.Row) -> Any:
        """Reconstruct a model instance from a SQLite row."""
        import dataclasses

        identity = GlobalIdentity(
            object_id=row["object_id"],
            object_type=row["object_type"],
            version=row["version"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            algorithm_version=row["algorithm_version"],
            dataset_id=row["dataset_id"],
            workspace_id=row["workspace_id"],
            execution_id=row["execution_id"],
            parent_ids=json.loads(row["parent_ids"]) if row["parent_ids"] else [],
        )

        data = json.loads(row["data"]) if row["data"] else {}

        fields = {f.name: f for f in dataclasses.fields(model_type)}
        kwargs = {"identity": identity}
        for k, v in data.items():
            if k in fields and k != "identity":
                if isinstance(v, str) and v.startswith(("{", "[")):
                    try:
                        kwargs[k] = json.loads(v)
                    except (json.JSONDecodeError, TypeError):
                        kwargs[k] = v
                else:
                    kwargs[k] = v

        return model_type(**kwargs)

    def query(self, model_type: Type[T], filters: Optional[Dict[str, Any]] = None,
              limit: int = 100, offset: int = 0) -> List[T]:
        table = _table_name(model_type)
        conn = self._conn()
        rows = conn.execute(
            f"SELECT * FROM {table} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
        return [self._row_to_record(model_type, r) for r in rows]

    def count(self, model_type: Type[T], filters: Optional[Dict[str, Any]] = None) -> int:
        table = _table_name(model_type)
        conn = self._conn()
        row = conn.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
        return row["cnt"] if row else 0

    def delete(self, model_type: Type[T], object_id: str) -> bool:
        table = _table_name(model_type)
        conn = self._conn()
        cursor = conn.execute(f"DELETE FROM {table} WHERE object_id=?", (object_id,))
        conn.commit()
        return cursor.rowcount > 0

    def search(self, query: str, model_types: Optional[List[Type]] = None,
               limit: int = 50) -> List[Any]:
        targets = model_types or ALL_RECORD_TYPES
        conn = self._conn()
        results = []
        per_type_limit = max(5, limit // len(targets))
        for model_type in targets:
            table = _table_name(model_type)
            try:
                rows = conn.execute(
                    f"""SELECT t.* FROM {table} t
                        JOIN {table}_fts fts ON t.object_id = fts.object_id
                        WHERE fts.data MATCH ?
                        LIMIT ?""",
                    (query, per_type_limit)
                ).fetchall()
                for r in rows:
                    results.append(self._row_to_record(model_type, r))
            except Exception:
                # FTS may not be populated; fall back to LIKE
                try:
                    rows = conn.execute(
                        f"SELECT * FROM {table} WHERE data LIKE ? LIMIT ?",
                        (f"%{query}%", per_type_limit)
                    ).fetchall()
                    for r in rows:
                        results.append(self._row_to_record(model_type, r))
                except Exception:
                    pass
        return results[:limit]

    import contextlib

    @contextlib.contextmanager
    def transaction(self):
        conn = self._conn()
        try:
            yield
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def get_table_stats(self) -> Dict[str, int]:
        """Return row counts for every canonical table — used by Database Inspector."""
        conn = self._conn()
        stats = {}
        for model_type in ALL_RECORD_TYPES:
            table = _table_name(model_type)
            row = conn.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
            stats[table] = row["cnt"] if row else 0
        return stats

    def close(self) -> None:
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None


# ─────────────────────────────────────────────────────────
# Module-level singleton (initialized at server startup)
# ─────────────────────────────────────────────────────────

_provider: Optional[SQLiteProvider] = None


def get_provider() -> SQLiteProvider:
    global _provider
    if _provider is None:
        _provider = SQLiteProvider()
        _provider.initialize()
    return _provider
