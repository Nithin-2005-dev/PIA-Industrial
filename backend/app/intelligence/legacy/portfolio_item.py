from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class PortfolioItem:
    """
    Executive portfolio candidate.
    """

    module_ref: EntityRef

    action: str

    expected_health_gain: float

    estimated_cost: float

    roi: float

    rank: int