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

    context = EstimationContext(
        current_time=datetime.now(UTC),
        learning_rate=1.0,
    )

    events = adapter.collect(
        EventQuery(
            identifier="facebook/react",
            filters={
                "per_page": 1,
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

    print("\n=== EXPERTISE ESTIMATES ===\n")

    for estimate in projection.all_estimates():

        print(estimate)


if __name__ == "__main__":
    main()