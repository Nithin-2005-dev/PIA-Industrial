from app.intelligence.risk.knowledge_risk import (
    KnowledgeRisk,
)

from app.intelligence.risk.bus_factor import (
    BusFactor,
)

from app.intelligence.risk.risk_level import (
    RiskLevel,
)

from .knowledge_risk_policy import (
    KnowledgeRiskPolicy,
)


class BusFactorRiskPolicy(
    KnowledgeRiskPolicy
):

    def evaluate(
        self,
        bus_factor: BusFactor,
        owner_count: int,
    ) -> KnowledgeRisk:

        if (
            bus_factor.risk_level
            == RiskLevel.HIGH
        ):

            summary = (
                "This module depends heavily "
                "on a small number of owners. "
                "Loss of key contributors may "
                "create significant knowledge "
                "concentration risk."
            )

        elif (
            bus_factor.risk_level
            == RiskLevel.MEDIUM
        ):

            summary = (
                "Knowledge is shared across "
                "multiple owners, but further "
                "distribution would improve "
                "resilience."
            )

        else:

            summary = (
                "Knowledge appears well "
                "distributed across owners. "
                "Current organizational risk "
                "is low."
            )

        return KnowledgeRisk(
            module_ref=(
                bus_factor.module_ref
            ),
            risk_level=(
                bus_factor.risk_level
            ),
            bus_factor=(
                bus_factor.value
            ),
            ownership_count=(
                owner_count
            ),
            summary=summary,
        )