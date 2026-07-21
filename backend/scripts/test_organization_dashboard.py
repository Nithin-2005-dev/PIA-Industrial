from datetime import UTC
from datetime import datetime
from datetime import timedelta
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

from app.health.health_report import (
    HealthReport,
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


def report(
    module_ref,
    health_score,
):

    return HealthReport(
        module_ref=module_ref,
        health_score=health_score,
        health_level="WARNING",
        coverage_score=50,
        concentration_score=0.75,
        bus_factor=2,
    )


def seed_history(
    intelligence,
    module_name,
    scores,
):

    module_ref = module(
        module_name
    )

    now = datetime.now(
        UTC
    )

    for index, score in enumerate(
        scores
    ):

        intelligence.health_projection.apply(
            report(
                module_ref,
                score,
            ),
            now - timedelta(
                days=(
                    len(scores)
                    - index
                    - 1
                )
                * 30
            ),
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

    seed_history(
        intelligence,
        "payments.py",
        [95, 80, 60, 40],
    )

    seed_history(
        intelligence,
        "auth.py",
        [92, 88, 81, 80],
    )

    dashboard = (
        intelligence
        .organization_dashboard_service
        .dashboard()
    )

    print(
        "\n=== ORGANIZATION DASHBOARD ===\n"
    )

    print(
        f"Average Health: "
        f"{dashboard.health.average_health:.2f}"
    )

    print(
        f"Critical Modules: "
        f"{dashboard.health.critical_modules}"
    )

    print()

    print(
        "Top Risk:"
    )

    print(
        dashboard.risks[0]
        .module_ref
        .id
    )

    print()

    print(
        "Weakest Readiness:"
    )

    print(
        dashboard.readiness[0]
        .module_ref
        .id
    )

    print()

    print(
        "Top Transfer:"
    )

    print(
        dashboard.transfers[0]
        .module_ref
        .id
    )


if __name__ == "__main__":
    main()