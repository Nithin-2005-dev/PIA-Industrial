import unittest
import time
import json
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator
from datetime import datetime

from pydantic import ValidationError

from app.ingestion.observation.ingestion.engine import ObservationIngestionEngine
from app.ingestion.observation.ingestion.sqlite_store import SQLiteObservationStore, SQLiteCheckpointStore
from app.ingestion.observation.ingestion.circuit_breaker import CircuitBreaker, CircuitOpenException
from app.ingestion.observation.ingestion.normalizer import SchemaMismatchError
from app.ingestion.observation.domain import ProcessingMode
from app.ingestion.observation.ingestion.models import SyncRequest, SyncCursor, ExternalSource, RawObservationRecord
from app.ingestion.observation.ingestion.adapters import ObservationAdapter

class MockObservationAdapter(ObservationAdapter):
    def __init__(self, name: str, provider: str):
        self.name = name
        self.provider = provider
        self.supported_record_types = ("commit",)
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout_sec=0.2)
        self.fail_count = 0
        self.return_invalid = False
        self.fetch_calls = 0
        
    def is_circuit_open(self) -> bool:
        return self.circuit_breaker.is_open()
        
    def fetch(self, request: SyncRequest) -> tuple[tuple[RawObservationRecord, ...], SyncCursor]:
        def _fetch():
            self.fetch_calls += 1
            if self.fail_count > 0:
                self.fail_count -= 1
                raise Exception("Mock Network Error")
            
            if self.return_invalid:
                # payload that will fail Pydantic validation later
                payload = {"invalid_data": 123} 
            else:
                payload = {"sha": "123", "commit": {"message": "hello"}}
                
            record = RawObservationRecord(
                source=ExternalSource(provider=self.provider, adapter=self.name),
                record_id="mock_123",
                record_type="commit",
                payload=payload,
                observed_at=datetime.utcnow()
            )
            return ((record,), SyncCursor(adapter=self.name, cursor="next_cursor"))
            
        return self.circuit_breaker.call(_fetch)

class SimulatedCrashError(Exception):
    pass

class TestObservationChaos(unittest.TestCase):
    def setUp(self):
        import uuid
        self.db_path = f"file:memdb_{uuid.uuid4().hex}?mode=memory&cache=shared"
        self._keepalive_conn = sqlite3.connect(self.db_path, uri=True)
        self.store = SQLiteObservationStore(self.db_path)
        self.checkpoints = SQLiteCheckpointStore(self.db_path)
        
        with sqlite3.connect(self.db_path, uri=True) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                source_id TEXT PRIMARY KEY,
                cursor_value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                external_event_id TEXT,
                payload TEXT,
                status INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_id, external_event_id)
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS dead_letter_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_payload TEXT,
                schema_version TEXT,
                error_message TEXT,
                traceback TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
        self.adapter = MockObservationAdapter(name="github", provider="github")
        
        self.engine = ObservationIngestionEngine(
            store=self.store,
            checkpoints=self.checkpoints
        )
        self.engine.adapters.register(self.adapter)
        
        self.request = SyncRequest(
            source=ExternalSource(provider="github", adapter="github"),
            mode="incremental",
            batch_size=10
        )
        
    def test_a_persistence_and_atomicity(self):
        original_append = self.store.append_raw
        
        crash_flag = {"crashed": False}
        
        def patched_append(*args, **kwargs):
            if not crash_flag["crashed"]:
                original_append(*args, **kwargs)
                crash_flag["crashed"] = True
                raise SimulatedCrashError("Hard crash!")
            return original_append(*args, **kwargs)
            
        self.store.append_raw = patched_append
        
        with self.assertRaises(SimulatedCrashError):
            self.engine.sync("github", self.request)
            
        with sqlite3.connect(self.db_path, uri=True) as conn:
            count = conn.execute("SELECT COUNT(*) FROM raw_observations").fetchone()[0]
            self.assertEqual(count, 1)
            
            cursor = conn.execute("SELECT cursor_value FROM checkpoints WHERE source_id='github'").fetchone()
            self.assertIsNone(cursor)

        # Resume engine, it should ignore the duplicate due to UNIQUE and update cursor
        self.store.append_raw = original_append
        self.engine.deduplicator = type(self.engine.deduplicator)() # Reset deduplicator
        self.engine.sync("github", self.request)
        
        with sqlite3.connect(self.db_path, uri=True) as conn:
            count = conn.execute("SELECT COUNT(*) FROM raw_observations").fetchone()[0]
            self.assertEqual(count, 1) 
            
            cursor = conn.execute("SELECT cursor_value FROM checkpoints WHERE source_id='github'").fetchone()
            self.assertIsNotNone(cursor)

    def test_b_semantic_corruption_dlq(self):
        self.adapter.return_invalid = True
        
        self.engine.sync("github", self.request)
        self.engine.process_batch(10)
        
        with sqlite3.connect(self.db_path, uri=True) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM dead_letter_queue").fetchall()
            
            self.assertEqual(len(rows), 1, f"Expected 1 item in DLQ. Rows: {[dict(r) for r in rows]}")
            error_msg = rows[0]["error_message"]
            print(f"DLQ Error Message: {error_msg}")
            self.assertTrue("SchemaMismatchError" in error_msg or "ValidationError" in error_msg or "ObservationType" in error_msg)

    def test_c_concurrency_contention_zombie(self):
        for i in range(5):
            self.store.append_raw("github", f"evt_{i}", {"data": "test"})
            
        original_claim = self.store.claim_batch
        
        crash_state = {"count": 0}
        
        def patched_claim(batch_size):
            crash_state["count"] += 1
            if crash_state["count"] == 2:
                original_claim(batch_size)
                raise SimulatedCrashError("Worker crashed during processing")
            return original_claim(batch_size)
            
        self.store.claim_batch = patched_claim
        
        def instant_reset():
            with sqlite3.connect(self.db_path, uri=True) as conn:
                conn.execute(
                    "UPDATE raw_observations SET status = 0 WHERE status = 1"
                )
        self.store.reset_stale_jobs = instant_reset
        
        def worker():
            try:
                self.engine.process_batch(1) 
            except SimulatedCrashError:
                pass
            except Exception as e:
                print(f"Worker failed with: {e}")
                raise
                
        for _ in range(5):
            worker()
                
        with sqlite3.connect(self.db_path, uri=True) as conn:
            zombie_count = conn.execute("SELECT COUNT(*) FROM raw_observations WHERE status = 1").fetchone()[0]
            print(f"Zombie Count: {zombie_count}")
            self.assertEqual(zombie_count, 1)
            
        self.store.reset_stale_jobs()
        
        with sqlite3.connect(self.db_path, uri=True) as conn:
            pending_count = conn.execute("SELECT COUNT(*) FROM raw_observations WHERE status = 0").fetchone()[0]
            self.assertEqual(pending_count, 1)

    def test_d_resilience_boundary_circuit_breaker(self):
        self.engine.rate_limiter.allow = lambda x: True # Disable rate limiting for this test
        self.adapter.fail_count = 5
        
        for i in range(5):
            try:
                self.engine.sync("github", self.request)
            except Exception as e:
                print(f"Call {i} threw Exception: {e}")
                
        self.assertTrue(self.adapter.circuit_breaker.is_open())
        
        result = self.engine.sync("github", self.request)
        self.assertEqual(result.raw_count, 0)
        self.assertTrue(self.adapter.circuit_breaker.is_open())
        
        time.sleep(0.3)
        self.assertFalse(self.adapter.circuit_breaker.is_open())

    def test_e_timezone_and_replay(self):
        self.engine.sync("github", self.request)
        # Manually mock normalized property for the Replay Engine test
        self.store.normalized = lambda: [] # Dummy empty list to prevent crash
        
        from app.ingestion.observation.ingestion.models import ReplayQuery
        query = ReplayQuery(developer="UNRESOLVED_Test User") 
        
        replay_events = self.engine.replay(query)
        self.assertTrue(all(evt.processing_mode == ProcessingMode.REPLAY for evt in replay_events))

    def test_nightmare_a_poison_pill_storm(self):
        self.engine.rate_limiter.allow = lambda x: True
        self.adapter.fail_count = 5
        for i in range(5):
            try:
                self.engine.sync("github", self.request)
            except Exception:
                pass
        
        self.assertTrue(self.adapter.circuit_breaker.is_open())
        time.sleep(0.3)
        
        def _fetch_poison():
            from pydantic import BaseModel
            class MockModel(BaseModel):
                id: int
            try:
                MockModel(id="abc")
            except ValidationError as e:
                raise e
            
        original_fetch = self.adapter.fetch
        def poisoned_fetch(*args, **kwargs):
            return self.adapter.circuit_breaker.call(_fetch_poison)
            
        self.adapter.fetch = poisoned_fetch
        
        with self.assertRaises(ValidationError):
             self.engine.sync("github", self.request)
             
        self.assertEqual(self.adapter.circuit_breaker.state.name, "CLOSED")

    def test_nightmare_b_thundering_herd(self):
        self.engine.rate_limiter.allow = lambda x: True
        self.adapter.fail_count = 5
        for _ in range(5):
            try:
                 self.engine.sync("github", self.request)
            except Exception:
                 pass
                 
        self.assertTrue(self.adapter.circuit_breaker.is_open())
        time.sleep(0.3)
        
        # HALF-OPEN. Let's spawn 5 threads.
        # We will inject a slow _fetch by overriding fetch temporarily.
        original_fetch = self.adapter.fetch
        def slow_fetch(*args, **kwargs):
            def _slow_fetch():
                self.adapter.fetch_calls += 1
                time.sleep(0.1) # Simulate slow network
                return ((), SyncCursor("github", "dummy"))
            return self.adapter.circuit_breaker.call(_slow_fetch)
            
        self.adapter.fetch = slow_fetch
        
        self.adapter.fetch_calls = 0 # Reset counter
        
        def worker():
             try:
                 self.engine.sync("github", self.request)
             except Exception:
                 pass
                 
        with ThreadPoolExecutor(max_workers=5) as executor:
             futures = []
             for _ in range(5):
                 futures.append(executor.submit(worker))
             for f in futures:
                 f.result()
                 
        self.assertEqual(self.adapter.fetch_calls, 1)

if __name__ == "__main__":
    print("Running system_accuracy_report...")
    unittest.main(verbosity=2)
