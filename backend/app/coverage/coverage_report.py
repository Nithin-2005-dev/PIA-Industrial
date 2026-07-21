from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class CoverageReport:
    """
    Coverage assessment
    for a module.
    """

    module_ref: EntityRef

    expert_count: int

    total_expertise: float

    coverage_score: float

    coverage_uncertainty: float

    coverage_confidence: float

    coverage_level: str