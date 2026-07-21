from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class ExecutiveRecommendation:
    """
    Executive-level recommendation.
    """

    module_ref: EntityRef

    action: str

    reason: str

    expected_health_gain: float

    estimated_cost: float

    roi: float

    priority: int