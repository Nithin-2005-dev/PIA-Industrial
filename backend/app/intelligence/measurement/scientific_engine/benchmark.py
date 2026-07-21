from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter


@dataclass
class MeasurementBenchmark:
    measurement_latency_ms: float = 0.0
    throughput: float = 0.0
    memory_usage_bytes: int = 0
    cpu_usage: float = 0.0
    allocation_count: int = 0
    cache_efficiency: float = 0.0


class MeasurementBenchmarkRecorder:
    def record(
        self,
        operation,
        item_count: int,
    ):
        started = perf_counter()
        result = operation()
        elapsed_ms = (perf_counter() - started) * 1000.0
        benchmark = MeasurementBenchmark(
            measurement_latency_ms=elapsed_ms,
            throughput=(
                item_count / (elapsed_ms / 1000.0)
                if elapsed_ms > 0
                else float(item_count)
            ),
            allocation_count=item_count,
        )
        return result, benchmark

