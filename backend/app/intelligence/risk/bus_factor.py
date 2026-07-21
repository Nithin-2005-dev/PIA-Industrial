from dataclasses import dataclass

from app.domain.entity_ref import EntityRef

from .risk_level import RiskLevel


@dataclass(frozen=True)
class BusFactor:

    module_ref: EntityRef

    value: int

    coverage: float

    risk_level: RiskLevel

    shannon_entropy: float = 0.0

    gini_coefficient: float = 0.0

    hhi: float = 0.0

    uncertainty: float = 0.0

    confidence: float = 1.0