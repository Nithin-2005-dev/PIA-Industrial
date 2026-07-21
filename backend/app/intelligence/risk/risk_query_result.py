from dataclasses import dataclass

from .knowledge_risk import (
    KnowledgeRisk,
)


@dataclass(frozen=True)
class RiskQueryResult:

    risk: KnowledgeRisk

    rank: int