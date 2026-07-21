from datetime import UTC
from datetime import datetime
from uuid import uuid4

from app.bootstrap.intelligence_context import (
    IntelligenceContext,
)

from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.domain.evidence import (
    Evidence,
)

from app.domain.predicate_type import (
    PredicateType,
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

from app.estimator.policies.exponential_decay_policy import (
    ExponentialDecayPolicy,
)

from app.estimator.policies.rule_expertise_scoring_policy import (
    RuleExpertiseScoringPolicy,
)


def developer(name):

    return EntityRef(
        id=name,
        type=EntityType.DEVELOPER,
    )


def module(name):

    return EntityRef(
        id=name,
        type=EntityType.FILE,
    )


def add_expertise(
    projection,
    context,
    developer_name,
    module_name,
    strength,
):

    projection.apply(
        Evidence(
            id=uuid4(),
            source_event_id=uuid4(),
            subject_ref=developer(
                developer_name
            ),
            predicate=(
                PredicateType.MODIFIED
            ),
            object_ref=module(
                module_name
            ),
            confidence=1.0,
            metadata={
                "strength": strength,
            },
        ),
        context,
    )


def main():

    estimator = ExpertiseEstimator(
        RuleExpertiseScoringPolicy(),
        ExponentialDecayPolicy(),
    )

    projection = ExpertiseProjection(
        estimator
    )

    context = EstimationContext(
        current_time=datetime.now(
            UTC
        ),
        learning_rate=1.0,
    )

    add_expertise(
        projection,
        context,
        "alice",
        "payments.py",
        95,
    )

    add_expertise(
        projection,
        context,
        "bob",
        "payments.py",
        5,
    )

    add_expertise(
        projection,
        context,
        "charlie",
        "auth.py",
        60,
    )

    add_expertise(
        projection,
        context,
        "david",
        "auth.py",
        40,
    )

    intelligence = IntelligenceContext(
        projection
    )

    rankings = (
        intelligence
        .organization_readiness_service
        .weakest_modules()
    )

    print(
        "\n=== ORGANIZATION READINESS ===\n"
    )

    for item in rankings:

        print(
            f"#{item.rank} "
            f"{item.module_ref.id}"
        )

        print(
            f"Readiness: "
            f"{item.readiness_score:.2f}"
        )

        print(
            "-" * 50
        )


if __name__ == "__main__":
    main()