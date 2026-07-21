from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class HealthReport:
    """
    Overall organizational
    health assessment.
    """

    module_ref: EntityRef

    health_score: float

    health_uncertainty: float

    health_confidence: float

    health_level: str

    coverage_score: float

    concentration_score: float

    bus_factor: int