from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class TransferPlan:
    """
    Recommended knowledge transfer
    action.
    """

    module_ref: EntityRef

    mentor_ref: EntityRef

    learner_ref: EntityRef

    priority_score: float

    reason: str

    bus_factor: int

    concentration_score: float