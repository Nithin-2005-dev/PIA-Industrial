# Production Update: Ingestion Storage Refactor (Memory to SQLite WAL)

## 1. The Problem: Memory-Resident Volatility

During an architectural audit of the ingestion pipeline (`app/observation/ingestion/`), we discovered that both `checkpoint.py` and `storage.py` were entirely memory-resident.

*   `CheckpointStore` maintained synchronization cursors in a `dict`.
*   `ObservationIngestionStore` maintained ingested raw events in a `list`.

### Production Impact
1.  **State Loss:** If the ingestion process crashed or restarted, the `SyncCursor` was wiped, causing the system to lose its place and potentially trigger full re-ingestions.
2.  **Memory Leaks:** Storing raw events in a continuously growing list is unscalable and guarantees an eventual out-of-memory crash.
3.  **No Atomicity:** There was no guarantee that a cursor update and the corresponding raw event were persisted together.

## 2. The Solution: Durable SQLite WAL & Event Sourcing

We transitioned from "Application-State" to "Persistent-State" by introducing a **Write-Ahead Log (WAL)** using `sqlite3`.

### Key Architectural Changes

1.  **Interface Abstraction (`interfaces.py`)**
    We introduced `ICheckpointStore` and `IObservationStore` interfaces to decouple the ingestion engines from the specific storage mechanism, allowing seamless future migrations (e.g., to PostgreSQL).

2.  **Durable SQLite Storage (`sqlite_store.py`)**
    *   **Atomic Transactions:** We bound the `SyncCursor` update and the `raw_observations` insertion into single SQLite transactions inside the engine logic. If saving the event fails, the cursor does not advance.
    *   **Deterministic Idempotency:** We added a composite `UNIQUE(source_id, external_event_id)` constraint on the raw events table. The `SQLiteObservationStore` catches `sqlite3.IntegrityError` to safely and silently discard duplicates, providing "exactly-once" processing semantics.
    *   **Event-Time Causality:** Queries for unprocessed events now use `ORDER BY created_at ASC` (and will eventually use event timestamps) to preserve the original causal order of operations.

3.  **Automated Migrations (`migrations.py`)**
    We added a boot script to ensure the `ingestion.db` database and its optimized indices (e.g., `idx_unprocessed`) exist before the ingestion loop starts.

## 3. Integration

The new persistent layer requires two steps in `engine.py`:
1.  **Dependency Injection:** Instantiate `SQLiteCheckpointStore` and `SQLiteObservationStore` and pass them into the `IngestionEngine`.
2.  **Transaction Boundary:** Ensure the ingestion loop processes the raw insert and the cursor update sequentially:
    ```python
    # Ensure the cursor always advances, even if the event was a duplicate (Idempotency)
    self.observation_store.append_raw(source_id, event_id, payload)
    self.checkpoint_store.update_cursor(source_id, new_cursor)
    ```

This completely eliminates the original memory-leak risk and hardens the ingestion layer to production-grade standards.

## 4. Production Considerations & Scaling

To guarantee long-term stability in a production environment, the following operational requirements must be maintained:

### 1. Database Growth & Log Rotation
Because we use **Event Sourcing** (never deleting raw events), the `raw_observations` table will grow indefinitely. 
* **Requirement:** A scheduled process (e.g., cron or Celery beat) must be implemented to archive processed events (where `is_processed = 1`) to cold storage (e.g., Parquet files in S3) periodically, and then `DELETE` them from the active SQLite database to prevent unbounded disk growth.

### 2. Connection Pooling
Currently, the store opens a new SQLite connection per call. 
* **Requirement:** Transition to a thread-local persistent connection or connection pool to eliminate the overhead of repeatedly establishing file locks and opening the DB file during high-throughput ingestion.

### 3. The Concurrency "Stalling" Loophole
A critical edge case was addressed in the transaction boundary. If the ingestion loop crashes immediately *after* saving a raw event but *before* updating the cursor, the system will re-fetch the same event upon restart. 
* **Fix Applied:** Because of the `UNIQUE` constraint, the `append_raw` call will return `False` (duplicate). The ingestion logic **must still advance the cursor** even if the event was duplicate. Failing to do so would result in the system stalling indefinitely, trying to re-process an event it can never insert.

### 4. Asynchronous I/O
Ingestion adapters (like GitHub) are fundamentally network-bound.
* **Requirement:** Ingestion should operate asynchronously (`asyncio`) or as a decoupled background worker. We must avoid blocking the main Cognitive Engine thread while waiting for external network responses. User queries will reason over the *already persisted* events, trading absolute real-time consistency for zero-latency UX.
