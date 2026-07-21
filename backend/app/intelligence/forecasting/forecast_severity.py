from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class ForecastSeverity:
    """
    Relative forecast deterioration.
    """

    module_ref: EntityRef

    current_health: float

    predicted_health: float

    severity_score: float

    severity_level: str