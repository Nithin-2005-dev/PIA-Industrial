from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class Forecast:
    """
    Predicted future health.
    """

    module_ref: EntityRef

    current_health: float

    predicted_health: float

    horizon: int

    slope: float

    risk_level: str

    confidence: float = 0.5