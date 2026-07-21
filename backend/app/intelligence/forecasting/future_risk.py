from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class FutureRisk:
    """
    Predicted future deterioration.
    """

    module_ref: EntityRef

    current_health: float

    predicted_health: float

    risk_score: float