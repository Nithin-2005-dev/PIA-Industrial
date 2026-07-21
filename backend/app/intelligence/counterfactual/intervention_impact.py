from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class InterventionImpact:
    """
    Estimated intervention benefit.
    """

    module_ref: EntityRef

    action: str

    expected_health_gain: float

    reason: str