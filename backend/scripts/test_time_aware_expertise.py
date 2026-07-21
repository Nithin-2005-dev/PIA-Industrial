from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.domain.evidence import Evidence
from app.domain.expertise_estimate import ExpertiseEstimate
from app.domain.predicate_type import PredicateType

from app.estimator.estimation_context import (
    EstimationContext,
)
from app.estimator.expertise_estimator import (
    ExpertiseEstimator,
)
from app.estimator.policies.rule_expertise_scoring_policy import (
    RuleExpertiseScoringPolicy,
)
from app.estimator.policies.exponential_decay_policy import (
    ExponentialDecayPolicy,
)


def main():

    developer = EntityRef(
        id="alice",
        type=EntityType.DEVELOPER,
    )

    module = EntityRef(
        id="core/auth.py",
        type=EntityType.FILE,
    )

    one_year_ago = (
        datetime.now(UTC)
        - timedelta(days=365)
    )

    current_estimate = ExpertiseEstimate(
        developer_ref=developer,
        module_ref=module,
        raw_score=100.0,
        confidence=1.0,
        updated_at=one_year_ago,
    )

    evidence = Evidence(
        id=uuid4(),
        source_event_id=uuid4(),
        subject_ref=developer,
        predicate=PredicateType.MODIFIED,
        object_ref=module,
        confidence=1.0,
        metadata={
            "strength": 1.0,
        },
    )

    estimator = ExpertiseEstimator(
        RuleExpertiseScoringPolicy(),
        ExponentialDecayPolicy(
            decay_rate=0.002,
        ),
    )

    context = EstimationContext(
        current_time=datetime.now(UTC),
        learning_rate=1.0,
    )

    updated_estimate = estimator.estimate(
        current=current_estimate,
        evidence=evidence,
        context=context,
    )

    print("\n=== BEFORE ===\n")

    print(current_estimate)

    print("\n=== AFTER ===\n")

    print(updated_estimate)

    print("\n=== CHANGE ===\n")

    print(
        f"Original Score: "
        f"{current_estimate.raw_score:.2f}"
    )

    print(
        f"Updated Score: "
        f"{updated_estimate.raw_score:.2f}"
    )


if __name__ == "__main__":
    main()