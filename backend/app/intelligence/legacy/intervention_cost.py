from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class InterventionCost:
    """
    Estimated execution cost
    of an intervention.
    """

    module_ref: EntityRef

    action: str

    estimated_cost: float