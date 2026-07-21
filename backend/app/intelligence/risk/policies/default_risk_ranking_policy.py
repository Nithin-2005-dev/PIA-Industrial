from app.intelligence.risk.risk_level import (
    RiskLevel,
)

from .risk_ranking_policy import (
    RiskRankingPolicy,
)


class DefaultRiskRankingPolicy(
    RiskRankingPolicy
):

    _PRIORITY = {
        RiskLevel.HIGH: 3,
        RiskLevel.MEDIUM: 2,
        RiskLevel.LOW: 1,
    }

    def rank(
        self,
        risks,
    ):

        return sorted(
            risks,
            key=lambda risk: (
                self._PRIORITY[
                    risk.risk_level
                ],
                -risk.bus_factor,
            ),
            reverse=True,
        )