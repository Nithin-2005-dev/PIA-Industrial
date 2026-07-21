from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)

from .trend_direction import (
    TrendDirection,
)


@dataclass(frozen=True)
class HealthTrend:

    module_ref: EntityRef

    previous_score: float

    current_score: float

    delta: float

    slope: float

    direction: TrendDirection

    sample_size: int = 1

    variance: float = 0.0