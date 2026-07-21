import time
from functools import wraps
from typing import Callable, Any
from dataclasses import dataclass

@dataclass
class ObservationMetrics:
    raw_records: int = 0
    normalized: int = 0
    accepted: int = 0
    duplicates: int = 0
    failures: int = 0
    backlog: int = 0
    ingestion_latency_ms: float = 0.0

class MetricsMiddleware:
    """Aspect-oriented metrics tracker for the ingestion pipeline."""
    
    def __init__(self):
        self.stats = {
            "normalizer_latency_ms": 0.0,
            "schema_mismatches": 0,
            "circuit_opens": 0,
            "events_processed": 0,
            "archival_events_count": 0,
            "failed_events": 0,
        }
        self.start_time = time.perf_counter()

    def track_latency(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = (time.perf_counter() - start) * 1000
                if self.stats["normalizer_latency_ms"] == 0.0:
                    self.stats["normalizer_latency_ms"] = duration
                else:
                    # Simple rolling average
                    self.stats["normalizer_latency_ms"] = (self.stats["normalizer_latency_ms"] + duration) / 2
        return wrapper

    def increment(self, key: str, count: int = 1):
        if key in self.stats:
            self.stats[key] += count

    @property
    def throughput(self) -> float:
        """Events processed per second."""
        elapsed = time.perf_counter() - self.start_time
        if elapsed <= 0:
            return 0.0
        return self.stats["events_processed"] / elapsed

# In engine.py we will still use ObservationMetrics for other legacy logic if it exists,
# but we will attach MetricsMiddleware for the new Observability.
