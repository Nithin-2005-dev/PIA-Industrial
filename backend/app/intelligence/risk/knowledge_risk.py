from dataclasses import dataclass

from app.domain.entity_ref import EntityRef

from app.intelligence.risk.risk_level import (
    RiskLevel,
)


@dataclass(frozen=True)
class KnowledgeRisk:
    """
    Actionable knowledge risk
    assessment for a module.
    """

    module_ref: EntityRef

    risk_level: RiskLevel

    bus_factor: int

    ownership_count: int

    summary: str