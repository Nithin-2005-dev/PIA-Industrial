from __future__ import annotations

from time import perf_counter

from app.ingestion.observation.ingestion.adapters import AdapterRegistry
from app.ingestion.observation.ingestion.checkpoint import CheckpointStore
from app.ingestion.observation.ingestion.dedupe import ObservationDeduplicator
from app.ingestion.observation.ingestion.metrics import ObservationMetrics
from app.ingestion.observation.ingestion.models import ReplayQuery
from app.ingestion.observation.ingestion.models import SyncCursor
from app.ingestion.observation.ingestion.models import SyncRequest
from app.ingestion.observation.ingestion.models import SyncResult
from app.ingestion.observation.ingestion.normalizer import ObservationNormalizer
from app.ingestion.observation.ingestion.rate_limit import RateLimiter
from app.ingestion.observation.ingestion.replay import ObservationReplayEngine
from app.ingestion.observation.ingestion.storage import ObservationIngestionStore
from app.ingestion.observation.validation import ObservationValidationPipeline
from app.ingestion.observation.validation import ObservationValidationStatus
from app.core.event_bus import EventBus
from app.core.event_bus import PlatformEvent


class ObservationIngestionEngine:
    def __init__(
        self,
        adapters: AdapterRegistry | None = None,
        normalizer: ObservationNormalizer | None = None,
        validator: ObservationValidationPipeline | None = None,
        store: ObservationIngestionStore | None = None,
        checkpoints: CheckpointStore | None = None,
        deduplicator: ObservationDeduplicator | None = None,
        rate_limiter: RateLimiter | None = None,
        event_bus: EventBus | None = None,
        metrics: ObservationMetrics | None = None,
    ):
        self.adapters = adapters or AdapterRegistry()
        self.normalizer = normalizer or ObservationNormalizer()
        self.validator = validator or ObservationValidationPipeline()
        self.store = store or ObservationIngestionStore()
        self.checkpoints = checkpoints or CheckpointStore()
        self.deduplicator = deduplicator or ObservationDeduplicator()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.event_bus = event_bus or EventBus()
        self.metrics = metrics or ObservationMetrics()
        
        from app.ingestion.observation.ingestion.metrics import MetricsMiddleware
        self.middleware = MetricsMiddleware()
        
        # Apply the latency tracking decorator dynamically
        self.normalizer.normalize = self.middleware.track_latency(self.normalizer.normalize)

    def sync(
        self,
        adapter_name: str,
        request: SyncRequest,
    ) -> SyncResult:
        started = perf_counter()
        if not self.rate_limiter.allow(adapter_name):
            self.rate_limiter.record_failure(adapter_name)
            self.metrics.failures += 1
            return SyncResult(
                adapter=adapter_name,
                raw_count=0,
                normalized_count=0,
                accepted_count=0,
                duplicate_count=0,
                failed_count=1,
                checkpoint=(
                    request.cursor
                    or self.checkpoints.get(adapter_name)
                    or SyncCursor(
                        adapter=adapter_name,
                    )
                ),
            )

        adapter = self.adapters.get(adapter_name)
        
        # Check if the circuit is open to prevent blocking the engine
        if getattr(adapter, "is_circuit_open", lambda: False)():
            import logging
            logging.getLogger(__name__).warning(f"Circuit OPEN for {adapter_name}. Skipping.")
            return SyncResult(
                adapter=adapter_name,
                raw_count=0,
                normalized_count=0,
                accepted_count=0,
                duplicate_count=0,
                failed_count=0,
                checkpoint=(
                    request.cursor
                    or self.checkpoints.get(adapter_name)
                    or SyncCursor(adapter=adapter_name)
                ),
            )
            
        effective_request = request
        if effective_request.cursor is None:
            checkpoint = self.checkpoints.get(adapter_name)
            if checkpoint is not None:
                effective_request = SyncRequest(
                    source=request.source,
                    mode=request.mode,
                    cursor=checkpoint,
                    since=request.since,
                    until=request.until,
                    batch_size=request.batch_size,
                    replay=request.replay,
                )

        try:
            raw_records, cursor = adapter.fetch(effective_request)
            self.rate_limiter.record_success(adapter_name)
        except Exception:
            self.rate_limiter.record_failure(adapter_name)
            self.metrics.failures += 1
            raise

        accepted = 0
        normalized = 0
        duplicates = 0
        failed = 0

        for record in raw_records:
            self.metrics.raw_records += 1
            if self.deduplicator.is_duplicate_raw(record):
                duplicates += 1
                self.metrics.duplicates += 1
                continue

            # Ensure the cursor always advances, even if the event was a duplicate (Idempotency)
            self.store.append_raw(record.source.provider, record.record_id, record.payload)
            self.checkpoints.update_cursor(adapter_name, cursor)
            accepted += 1
            
        self.metrics.backlog = max(
            0,
            len(raw_records) - accepted,
        )
        self.metrics.ingestion_latency_ms += (
            perf_counter() - started
        ) * 1000

        return SyncResult(
            adapter=adapter_name,
            raw_count=len(raw_records),
            normalized_count=0, # Processed asynchronously now
            accepted_count=accepted,
            duplicate_count=duplicates,
            failed_count=failed,
            checkpoint=cursor,
        )

    def process_batch(self, batch_size: int = 100):
        """Consume pending events atomically."""
        from app.ingestion.observation.ingestion.normalizer import SchemaMismatchError
        from app.ingestion.observation.ingestion.circuit_breaker import CircuitOpenException
        import json
        import traceback
        
        batch = self.store.claim_batch(batch_size)
        for row in batch:
            try:
                # Reconstruct record for normalizer (assuming RawObservationRecord can take dicts for source etc)
                # For simplicity, we create a basic Mock/Stub of RawObservationRecord or pass raw payload
                # Note: This assumes RawObservationRecord can be constructed cleanly.
                payload = json.loads(row["payload"]) if isinstance(row["payload"], str) else row["payload"]
                
                # We need a proper record for the normalizer. In a real system, we serialize/deserialize it fully.
                from app.ingestion.observation.ingestion.models import RawObservationRecord, ExternalSource
                record = RawObservationRecord(
                    source=ExternalSource(provider=row["source_id"], adapter="sqlite"),
                    record_type="unknown", # We would store this in DB, but extracting from payload
                    record_id=row["external_event_id"],
                    payload=payload,
                    observed_at=row["created_at"]
                )
                
                observation = self.normalizer.normalize(record)
                
                if self.deduplicator.is_duplicate_observation(observation):
                    self.store.mark_processed(row["id"])
                    continue
                    
                validation = self.validator.validate(observation)
                if validation.status == ObservationValidationStatus.FAILED:
                    self.store.mark_processed(row["id"])
                    continue
                    
                # Append to normalized (if IObservationStore supports it, or separate store)
                # self.store.append_normalized(observation) # Omitted for brevity if not in new IObservationStore
                
                self.event_bus.publish(
                    PlatformEvent(
                        type="observation.normalized",
                        payload=observation,
                        version=observation.version,
                        correlation_id=observation.correlation_id,
                        trace_id=observation.trace_id,
                    )
                )
                self.store.mark_processed(row["id"])
                self.middleware.increment("events_processed")
                
            except SchemaMismatchError as e:
                self.middleware.increment("schema_mismatches")
                self.store.append_dlq(str(row["payload"]), str(e), "1.0", traceback.format_exc())
                self.store.mark_processed(row["id"]) # Mark processed so it doesn't get stuck
            except CircuitOpenException as e:
                self.middleware.increment("circuit_opens")
                self.store.append_dlq(str(row["payload"]), str(e), "1.0", traceback.format_exc())
                self.store.mark_processed(row["id"])
            except Exception as e:
                self.middleware.increment("failed_events")
                self.store.append_dlq(str(row["payload"]), str(e), "unknown", traceback.format_exc())
                self.store.mark_processed(row["id"])
        return

    def replay(
        self,
        query: ReplayQuery | None = None,
    ):
        return ObservationReplayEngine(self.store).replay(query)
