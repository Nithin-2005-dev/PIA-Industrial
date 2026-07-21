from collections.abc import Mapping
from dataclasses import dataclass

@dataclass(frozen=True)
class CalibrationProfile:
    """Statistical profile of a measurement population."""
    mean: float
    median: float
    stddev: float
    mad: float
    min_value: float
    max_value: float
    percentiles: Mapping[int, float]
    sample_size: int
    distribution: str
    confidence: float


@dataclass(frozen=True)
class CalibrationResult:
    """The outcome of applying a calibration strategy to a raw value."""
    raw_value: float
    normalized: float
    z_score: float | None
    percentile: float | None
    robust_z: float | None
    baseline: CalibrationProfile
    method: str
