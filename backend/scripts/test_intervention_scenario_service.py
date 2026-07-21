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

from app.scenario.intervention_scenario_request import (
    InterventionScenarioRequest,
)

from app.scenario.intervention_scenario_service import (
    InterventionScenarioService,
)

from app.scenario.strategy_comparison_service import (
    StrategyComparisonService,
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

    evidence_list = [

        Evidence(
            id=uuid4(),
            source_event_id=uuid4(),
            subject_ref=developer(
                "alice"
            ),
            predicate=(
                PredicateType.MODIFIED
            ),
            object_ref=module(
                "payments.py"
            ),
            confidence=1.0,
            metadata={
                "strength": 95.0,
            },
        ),

        Evidence(
            id=uuid4(),
            source_event_id=uuid4(),
            subject_ref=developer(
                "bob"
            ),
            predicate=(
                PredicateType.MODIFIED
            ),
            object_ref=module(
                "payments.py"
            ),
            confidence=1.0,
            metadata={
                "strength": 5.0,
            },
        ),
    ]

    for evidence in evidence_list:

        projection.apply(
            evidence,
            context,
        )

    intelligence = (
        IntelligenceContext(
            projection
        )
    )

    seed_history(
        intelligence,
        "payments.py",
        [95, 80, 60, 40],
    )

    outcomes = (
        InterventionScenarioService(
            intelligence
        )
        .evaluate(
            InterventionScenarioRequest(
                strategy_name=(
                    "baseline"
                ),
                module_id=(
                    "payments.py"
                ),
                horizon=3,
            )
        )
    )

    outcomes = (
        StrategyComparisonService()
        .compare(
            outcomes
        )
    )

    print(
        "\n=== INTERVENTION SCENARIOS ===\n"
    )

    for outcome in outcomes:

        print(
            f"Strategy: "
            f"{outcome.strategy_name}"
        )

        print(
            f"Predicted Health: "
            f"{outcome.predicted_health:.2f}"
        )

        print(
            f"Future Risk: "
            f"{outcome.future_risk_score:.2f}"
        )

        print(
            "-" * 50
        )

    assert (
        outcomes[0]
        .predicted_health
        >=
        outcomes[-1]
        .predicted_health
    )

    print(
        "\nM30.3 PASSED\n"
    )


if __name__ == "__main__":
    main()

