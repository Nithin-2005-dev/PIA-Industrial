from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class ConcentrationReport:
    """
    Expertise concentration
    assessment for a module.
    """

    module_ref: EntityRef

    expert_count: int

    concentration_score: float

    concentration_uncertainty: float

    concentration_confidence: float

    concentration_level: str