import os
from datetime import UTC, datetime

from app.adapters.github.adapter import GitHubAdapter
from app.adapters.github.rest_gateway import (
    GitHubRestGateway,
)

from app.extractor.expertise_extractor import (
    ExpertiseExtractor,
)
from app.extractor.policies.github_commit_strength_policy import (
    GitHubCommitStrengthPolicy,
)

from app.estimator.estimation_context import (
    EstimationContext,
)
from app.estimator.expertise_estimator import (
    ExpertiseEstimator,
)
from app.estimator.expertise_projection import (
    ExpertiseProjection,
)

from app.estimator.policies.rule_expertise_scoring_policy import (
    RuleExpertiseScoringPolicy,
)
from app.estimator.policies.exponential_decay_policy import (
    ExponentialDecayPolicy,
)

from app.query.expertise_query_service import (
    ExpertiseQueryService,
)

from app.ownership.ownership_service import (
    OwnershipService,
)
from app.ownership.policies.expertise_ownership_policy import (
    ExpertiseOwnershipPolicy,
)

from app.risk.bus_factor_service import (
    BusFactorService,
)
from app.risk.policies.ownership_bus_factor_policy import (
    OwnershipBusFactorPolicy,
)

from app.knowledge_risk.knowledge_risk_service import (
    KnowledgeRiskService,
)
from app.knowledge_risk.policies.bus_factor_risk_policy import (
    BusFactorRiskPolicy,
)

from app.ports.event_query import EventQuery


def main():

    token = os.environ["GITHUB_TOKEN"]

    gateway = GitHubRestGateway(
        token=token,
    )

    adapter = GitHubAdapter(
        gateway=gateway,
    )

    extractor = ExpertiseExtractor(
        GitHubCommitStrengthPolicy(),
    )

    estimator = ExpertiseEstimator(
        RuleExpertiseScoringPolicy(),
        ExponentialDecayPolicy(),
    )

    projection = ExpertiseProjection(
        estimator,
    )

    query_service = ExpertiseQueryService(
        projection,
    )

    ownership_service = OwnershipService(
        query_service=query_service,
        policy=ExpertiseOwnershipPolicy(),
    )

    bus_factor_service = BusFactorService(
        ownership_service=ownership_service,
        policy=OwnershipBusFactorPolicy(),
    )

    knowledge_risk_service = (
        KnowledgeRiskService(
            ownership_service=ownership_service,
            bus_factor_service=bus_factor_service,
            policy=BusFactorRiskPolicy(),
        )
    )

    context = EstimationContext(
        current_time=datetime.now(UTC),
        learning_rate=1.0,
    )

    events = adapter.collect(
        EventQuery(
            identifier="facebook/react",
            filters={
                "per_page": 10,
            },
        )
    )

    for event in events:

        evidence_list = extractor.extract(
            event,
        )

        for evidence in evidence_list:

            projection.apply(
                evidence,
                context,
            )

    module_id = (
        "packages/react-devtools-facade/src/DevToolsFacade.js"
    )

    risk = knowledge_risk_service.analyze(
        module_id
    )

    print("\n=== KNOWLEDGE RISK ===\n")

    print(
        f"Module: "
        f"{risk.module_ref.id}"
    )

    print(
        f"Risk Level: "
        f"{risk.risk_level.value}"
    )

    print(
        f"Bus Factor: "
        f"{risk.bus_factor}"
    )

    print(
        f"Ownership Count: "
        f"{risk.ownership_count}"
    )

    print(
        f"Summary: "
        f"{risk.summary}"
    )


if __name__ == "__main__":
    main()