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
        policy=OwnershipBusFactorPolicy(
            coverage_threshold=0.8,
        ),
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

    result = bus_factor_service.analyze(
        module_id
    )

    print("\n=== BUS FACTOR ===\n")

    print(
        f"Module: {module_id}"
    )

    print(
        f"Bus Factor: {result.value}"
    )

    print(
        f"Coverage: "
        f"{result.coverage * 100:.2f}%"
    )

    print(
        f"Risk Level: "
        f"{result.risk_level.value}"
    )


if __name__ == "__main__":
    main()