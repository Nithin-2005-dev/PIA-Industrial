from .risk_query_result import (
    RiskQueryResult,
)

from .policies.risk_ranking_policy import (
    RiskRankingPolicy,
)


class KnowledgeRiskQueryService:

    def __init__(
        self,
        ranking_policy: RiskRankingPolicy,
    ):
        self._ranking_policy = (
            ranking_policy
        )

    def top_risks(
        self,
        risks,
        limit: int = 10,
    ):

        ranked = (
            self._ranking_policy.rank(
                risks
            )
        )

        return [
            RiskQueryResult(
                risk=risk,
                rank=index + 1,
            )
            for index, risk in enumerate(
                ranked[:limit]
            )
        ]