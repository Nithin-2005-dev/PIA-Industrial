from dataclasses import dataclass

from .health_trend import (
    HealthTrend,
)


@dataclass(frozen=True)
class TrendRisk:
    """
    Ranked trend assessment.
    """

    trend: HealthTrend

    rank: int