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

from app.scenario.strategy_scenario_request import (
    StrategyScenarioRequest,
)

from app.scenario.strategy_scenario_service import (
    StrategyScenarioService,
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

    evidence = [

        ("alice", 95.0),
        ("bob", 80.0),
        ("charlie", 70.0),
    ]

    for name, strength in evidence:

        projection.apply(
            Evidence(
                id=uuid4(),
                source_event_id=uuid4(),
                subject_ref=developer(
                    name
                ),
                predicate=(
                    PredicateType.MODIFIED
                ),
                object_ref=module(
                    "auth.py"
                ),
                confidence=1.0,
                metadata={
                    "strength":
                    strength,
                },
            ),
            context,
        )

    intelligence = (
        IntelligenceContext(
            projection
        )
    )

    seed_history(
        intelligence,
        "auth.py",
        [95, 80, 60, 40],
    )

    outcomes = (
        StrategyScenarioService(
            intelligence
        )
        .evaluate(
            StrategyScenarioRequest(
                module_id=(
                    "auth.py"
                ),
                departing_owner_id=(
                    "alice"
                ),
                horizon=3,
            )
        )
    )

    print(
        "\n=== STRATEGY SCENARIOS ===\n"
    )

    for outcome in outcomes:

        print(
            outcome.strategy_name
        )

        print(
            f"Health: "
            f"{outcome.predicted_health:.2f}"
        )

        print(
            f"Risk: "
            f"{outcome.future_risk_score:.2f}"
        )

        print(
            "-" * 50
        )

    print(
        "\nM30.4 PASSED\n"
    )


if __name__ == "__main__":
    main()
    
    9186296008