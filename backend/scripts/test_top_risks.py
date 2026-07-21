from app.domain.entity_ref import (
    EntityRef,
)
from app.domain.entity_type import (
    EntityType,
)

from app.risk.risk_level import (
    RiskLevel,
)

from app.knowledge_risk.knowledge_risk import (
    KnowledgeRisk,
)

from app.knowledge_risk.knowledge_risk_query_service import (
    KnowledgeRiskQueryService,
)

from app.knowledge_risk.policies.default_risk_ranking_policy import (
    DefaultRiskRankingPolicy,
)


def main():

    risks = [

        KnowledgeRisk(
            module_ref=EntityRef(
                id="auth.py",
                type=EntityType.FILE,
            ),
            risk_level=RiskLevel.HIGH,
            bus_factor=1,
            ownership_count=1,
            summary="High risk",
        ),

        KnowledgeRisk(
            module_ref=EntityRef(
                id="payment.py",
                type=EntityType.FILE,
            ),
            risk_level=RiskLevel.MEDIUM,
            bus_factor=2,
            ownership_count=2,
            summary="Medium risk",
        ),

        KnowledgeRisk(
            module_ref=EntityRef(
                id="analytics.py",
                type=EntityType.FILE,
            ),
            risk_level=RiskLevel.LOW,
            bus_factor=4,
            ownership_count=4,
            summary="Low risk",
        ),
    ]

    service = (
        KnowledgeRiskQueryService(
            DefaultRiskRankingPolicy(),
        )
    )

    results = service.top_risks(
        risks,
        limit=10,
    )

    print(
        "\n=== TOP KNOWLEDGE RISKS ===\n"
    )

    for result in results:

        print(
            f"Rank #{result.rank}"
        )

        print(
            f"Module: "
            f"{result.risk.module_ref.id}"
        )

        print(
            f"Risk Level: "
            f"{result.risk.risk_level.value}"
        )

        print(
            f"Bus Factor: "
            f"{result.risk.bus_factor}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()