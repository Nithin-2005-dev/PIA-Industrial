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

    owners = ownership_service.owners_of(
        module_id
    )

    print("\n=== OWNERSHIP ===\n")

    print(
        f"Module: {module_id}\n"
    )

    for rank, owner in enumerate(
        owners,
        start=1,
    ):

        print(
            f"Owner #{rank}"
        )

        print(
            f"Developer: "
            f"{owner.owner_ref.id}"
        )

        print(
            f"Ownership: "
            f"{owner.ownership_percentage * 100:.2f}%"
        )

        print(
            f"Level: "
            f"{owner.ownership_level.value}"
        )

        print(
            f"Effective Score: "
            f"{owner.effective_score:.2f}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()