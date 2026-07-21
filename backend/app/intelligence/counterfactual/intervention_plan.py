from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)

from .intervention_impact import (
    InterventionImpact,
)


@dataclass(frozen=True)
class InterventionPlan:
    """
    Ordered intervention plan
    for a module.
    """

    module_ref: EntityRef

    interventions: list[InterventionImpact]

    total_expected_gain: float