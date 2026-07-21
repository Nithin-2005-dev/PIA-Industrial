from datetime import UTC
from datetime import datetime
from uuid import uuid4

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

from app.query.expertise_query_service import (
    ExpertiseQueryService,
)

from app.ownership.ownership_service import (
    OwnershipService,
)

from app.ownership.policies.expertise_ownership_policy import (
    ExpertiseOwnershipPolicy,
)

from app.successor.successor_service import (
    SuccessorService,
)

from app.successor.policies.expertise_successor_policy import (
    ExpertiseSuccessorPolicy,
)

from app.simulation.readiness_service import (
    ReadinessService,
)

from app.simulation.policies.expertise_readiness_policy import (
    ExpertiseReadinessPolicy,
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
            predicate=PredicateType.MODIFIED,
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
            predicate=PredicateType.MODIFIED,
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
            predicate=PredicateType.MODIFIED,
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

    query_service = (
        ExpertiseQueryService(
            projection
        )
    )

    ownership_service = (
        OwnershipService(
            query_service,
            ExpertiseOwnershipPolicy(),
        )
    )

    successor_service = (
        SuccessorService(
            ownership_service,
            ExpertiseSuccessorPolicy(),
        )
    )

    readiness_service = (
        ReadinessService(
            successor_service,
            query_service,
            ExpertiseReadinessPolicy(),
        )
    )

    readiness = (
        readiness_service.rank(
            "auth.py"
        )
    )

    print(
        "\n=== READINESS ===\n"
    )

    for item in readiness:

        print(
            item.successor,
            round(
                item.readiness_score,
                2,
            ),
        )


if __name__ == "__main__":
    main()