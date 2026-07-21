from abc import ABC, abstractmethod

from app.intelligence.risk.knowledge_risk import (
    KnowledgeRisk,
)


class RiskRankingPolicy(ABC):

    @abstractmethod
    def rank(
        self,
        risks: list[KnowledgeRisk],
    ) -> list[KnowledgeRisk]:
        pass