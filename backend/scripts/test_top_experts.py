import os
from datetime import UTC, datetime

from app.adapters.github.adapter import GitHubAdapter
from app.adapters.github.rest_gateway import GitHubRestGateway
from app.estimator.policies.exponential_decay_policy import (
    ExponentialDecayPolicy,
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

from app.query.expertise_query_service import (
    ExpertiseQueryService,
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

    results = query_service.top_experts(
        module_id=module_id,
    )

    print("\n=== TOP EXPERTS ===\n")

    print(f"Module: {module_id}\n")

    for rank, result in enumerate(
        results,
        start=1,
    ):

        estimate = result.estimate

        print(f"Rank #{rank}")

        print(
            f"Developer: "
            f"{estimate.developer_ref.id}"
        )

        print(
            f"Raw Score: "
            f"{estimate.raw_score}"
        )

        print(
            f"Confidence: "
            f"{estimate.confidence}"
        )

        print(
            f"Effective Score: "
            f"{result.effective_score}"
        )

        print("-" * 60)


if __name__ == "__main__":
    main()