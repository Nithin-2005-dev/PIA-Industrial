from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class OrganizationRisk:

    module_ref: EntityRef

    health_score: float

    future_risk_score: float

    severity_level: str

    rank: int