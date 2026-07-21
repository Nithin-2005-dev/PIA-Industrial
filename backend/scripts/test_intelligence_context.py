from datetime import UTC
from datetime import datetime
from pathlib import Path
import sys
from uuid import uuid4

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)

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
                "strength": 70.0,
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
                "strength": 20.0,
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
                "strength": 10.0,
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

    successors = (
        intelligence
        .successor_service
        .recommend(
            "auth.py"
        )
    )

    print(
        "\n=== INTELLIGENCE CONTEXT ===\n"
    )

    for candidate in successors:

        print(
            f"Rank #{candidate.rank}"
        )

        print(
            f"Developer: "
            f"{candidate.developer_ref.id}"
        )

        print(
            f"Score: "
            f"{candidate.score:.2f}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()
