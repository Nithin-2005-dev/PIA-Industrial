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

from app.decision.reviewer_recommendation_service import (
    ReviewerRecommendationService,
)
from app.decision.policies.coverage_recommendation_policy import (
    CoverageRecommendationPolicy,
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

    recommendation_service = (
        ReviewerRecommendationService(
            query_service=query_service,
            policy=CoverageRecommendationPolicy(),
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

    recommendations = (
        recommendation_service.recommend_reviewers(
            file_ids=[
                "packages/react-devtools-facade/src/DevToolsFacade.js",
                "packages/react-devtools-facade/src/__tests__/DevToolsFacade-test.js",
            ],
            limit=5,
        )
    )

    print(
        "\n=== REVIEWER RECOMMENDATIONS ===\n"
    )

    for rank, recommendation in enumerate(
        recommendations,
        start=1,
    ):

        print(f"Rank #{rank}")

        print(
            f"Reviewer: "
            f"{recommendation.reviewer_ref.id}"
        )

        print(
            f"Score: "
            f"{recommendation.score}"
        )

        print(
            f"Covered Files: "
            f"{recommendation.covered_files}"
        )

        print("-" * 60)


if __name__ == "__main__":
    main()