from dataclasses import dataclass

from .health_report import (
    HealthReport,
)


@dataclass(frozen=True)
class HealthRisk:
    """
    Ranked health assessment.
    """

    report: HealthReport

    rank: int