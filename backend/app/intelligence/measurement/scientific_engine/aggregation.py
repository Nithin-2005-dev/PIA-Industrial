from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import builtins


@dataclass(frozen=True)
class TimeBucket:
    bucket_start: datetime
    values: tuple[float, ...]


class MeasurementAggregationEngine:
    def sum(
        self,
        values: list[float],
    ) -> float:
        return float(builtins.sum(values))

    def mean(
        self,
        values: list[float],
    ) -> float:
        return self.sum(values) / len(values) if values else 0.0

    def median(
        self,
        values: list[float],
    ) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        middle = len(ordered) // 2
        if len(ordered) % 2:
            return float(ordered[middle])
        return (ordered[middle - 1] + ordered[middle]) / 2.0

    def min(
        self,
        values: list[float],
    ) -> float:
        return float(builtins.min(values)) if values else 0.0

    def max(
        self,
        values: list[float],
    ) -> float:
        return float(builtins.max(values)) if values else 0.0

    def percentile(
        self,
        values: list[float],
        percentile: float,
    ) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = round(max(0.0, min(1.0, percentile)) * (len(ordered) - 1))
        return float(ordered[index])

    def sliding_windows(
        self,
        values: list[float],
        window: int,
    ) -> list[tuple[float, ...]]:
        if window <= 0:
            raise ValueError("window must be positive")
        return [
            tuple(values[max(0, index - window + 1) : index + 1])
            for index in range(len(values))
        ]

    def rolling_mean(
        self,
        values: list[float],
        window: int,
    ) -> list[float]:
        return [
            self.mean(list(segment))
            for segment in self.sliding_windows(values, window)
        ]

    def time_buckets(
        self,
        samples: list[tuple[datetime, float]],
        bucket_seconds: int,
    ) -> tuple[TimeBucket, ...]:
        if bucket_seconds <= 0:
            raise ValueError("bucket_seconds must be positive")
        buckets: dict[datetime, list[float]] = defaultdict(list)
        for timestamp, value in samples:
            epoch = int(timestamp.timestamp())
            bucket_epoch = epoch - (epoch % bucket_seconds)
            buckets[datetime.fromtimestamp(bucket_epoch, tz=timestamp.tzinfo)].append(value)
        return tuple(
            TimeBucket(bucket_start=start, values=tuple(values))
            for start, values in sorted(buckets.items())
        )
