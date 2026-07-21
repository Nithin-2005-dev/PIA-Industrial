# Production Update: Semantic Hardening & Concurrency Safety

## 1. The Problem: Implicit Trust & Data Corruption
During our architectural review of the ingestion layer, we identified two severe failure modes:
1. **Semantic Fragility:** The `normalizer.py` implicitly trusted the raw JSON payloads (`payload.get("author")`). If an adapter changed its schema or passed malformed data, it could poison the downstream knowledge graph or crash the pipeline silently.
2. **Concurrency "Zombie" State:** As we moved to multi-threaded SQLite processing, a worker claiming a batch of events (setting `status = 1`) could crash before finishing. This would leave events stuck in the `1` (Processing) state forever, as subsequent queries only look for `status = 0`.

## 2. The Solution: Defensive Architecture

We implemented a comprehensive suite of defensive mechanisms to guarantee both structural integrity and semantic correctness.

### A. Semantic Contracts (Pydantic)
- **`normalizer.py`:** We replaced implicit dictionary lookups with a formal Pydantic contract (`BaseEventSchema`). 
- **Validation Gate:** Every raw payload is now strictly validated *before* being processed into the internal domain models. If the structure is malformed, the system catches the resulting `ValidationError` and explicitly raises a `SchemaMismatchError`.

### B. The Dead Letter Queue (Envelope Pattern)
- **`migrations.py` & `sqlite_store.py`:** Instead of dropping malformed events or crashing the ingestion loop, we created a `dead_letter_queue` table.
- **Envelope Metadata:** When `SchemaMismatchError` is caught in `engine.py`, the system writes the raw payload to the DLQ wrapped in an "Envelope" containing:
  1. `schema_version` (to ensure future replays know exactly which schema the payload failed against).
  2. `error_message` (e.g., missing fields).
  3. `traceback` (for deep architectural debugging).

### C. Concurrency Safety (Atomic Claims & Watchdog)
- **`sqlite_store.py` (`claim_batch`):** We implemented the Atomic Claim pattern using `BEGIN IMMEDIATE` transactions in SQLite. This explicitly acquires a *Reserved Lock* as soon as the transaction starts, completely preventing the "Read-Modify-Write" contention race condition where two threads read the same `status=0` rows before updating them.
- **SQLite Pragmas:** We enforce `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` at initialization to ensure readers do not block writers and to maximize concurrency throughput.
- **The "Stuck-Job" Watchdog (`reset_stale_jobs`):** To prevent the Zombie State, we added a watchdog method that runs `UPDATE raw_observations SET status = 0 WHERE status = 1 AND updated_at < datetime('now', '-1 hour')`. If a worker dies mid-process, its claimed jobs will time out and return to the pending pool automatically.

### D. Out-of-Band Log Rotation
- **`storage_manager.py`:** To prevent unbounded SQLite file growth, we decoupled archiving from the hot ingestion path. The new `IngestionStorageManager.rotate_logs()` method uses a **Capacity-Based** approach:
  - It checks if the `raw_observations` table exceeds `MAX_CAPACITY` (default 50,000 rows).
  - If exceeded, it extracts the oldest processed rows (where `status = 2`).
  - It archives them to cold storage JSONL files (`/data/archives/observations_*.jsonl`) and atomically `DELETE`s them from SQLite.

## 3. Conclusion
The ingestion layer is now fully decoupled, structurally durable, semantically rigid, and concurrency-safe. It embodies true Event Sourcing principles without risking table bloat or silent data corruption.
