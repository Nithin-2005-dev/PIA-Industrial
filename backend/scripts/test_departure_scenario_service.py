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

from app.scenario.departure_scenario_request import (
    DepartureScenarioRequest,
)

from app.scenario.departure_scenario_service import (
    DepartureScenarioService,
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
                "auth.py"
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
                "auth.py"
            ),
            confidence=1.0,
            metadata={
                "strength": 80.0,
            },
        ),

        Evidence(
            id=uuid4(),
            source_event_id=uuid4(),
            subject_ref=developer(
                "charlie"
            ),
            predicate=(
                PredicateType.MODIFIED
            ),
            object_ref=module(
                "auth.py"
            ),
            confidence=1.0,
            metadata={
                "strength": 70.0,
            },
        ),
    ]

    for evidence in evidence_list:

        projection.apply(
            evidence,
            context,
        )

    intelligence = IntelligenceContext(
        projection
    )

    service = (
        DepartureScenarioService(
            intelligence
        )
    )

    alice = (
        service.evaluate(
            DepartureScenarioRequest(
                strategy_name=(
                    "alice_leaves"
                ),
                module_id=(
                    "auth.py"
                ),
                departing_owner_id=(
                    "alice"
                ),
            )
        )
    )

    bob = (
        service.evaluate(
            DepartureScenarioRequest(
                strategy_name=(
                    "bob_leaves"
                ),
                module_id=(
                    "auth.py"
                ),
                departing_owner_id=(
                    "bob"
                ),
            )
        )
    )

    print(
        "\n=== DEPARTURE SCENARIOS ===\n"
    )

    print(
        "Alice leaves"
    )

    print(
        f"Health Before: "
        f"{alice.health_before:.2f}"
    )

    print(
        f"Health After: "
        f"{alice.health_after:.2f}"
    )

    print(
        f"Knowledge Loss: "
        f"{alice.knowledge_loss:.2f}"
    )

    print(
        f"Severity: "
        f"{alice.severity}"
    )

    print(
        "-" * 50
    )

    print(
        "Bob leaves"
    )

    print(
        f"Health Before: "
        f"{bob.health_before:.2f}"
    )

    print(
        f"Health After: "
        f"{bob.health_after:.2f}"
    )

    print(
        f"Knowledge Loss: "
        f"{bob.knowledge_loss:.2f}"
    )

    print(
        f"Severity: "
        f"{bob.severity}"
    )

    print(
        "-" * 50
    )

    assert (
        alice.health_after
        <
        bob.health_after
    )

    print(
        "\nM30.2 PASSED\n"
    )


if __name__ == "__main__":
    main()
