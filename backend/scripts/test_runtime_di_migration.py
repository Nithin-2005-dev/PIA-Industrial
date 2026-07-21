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

from app.bootstrap.intelligence_context import IntelligenceContext
from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.domain.evidence import Evidence
from app.domain.predicate_type import PredicateType
from app.estimator.estimation_context import EstimationContext
from app.estimator.expertise_estimator import ExpertiseEstimator
from app.estimator.expertise_projection import ExpertiseProjection
from app.estimator.policies.exponential_decay_policy import ExponentialDecayPolicy
from app.estimator.policies.rule_expertise_scoring_policy import RuleExpertiseScoringPolicy
from app.organization.organization_dashboard_service import OrganizationDashboardService
from app.ownership.ownership_service import OwnershipService
from app.platform.core_modules import IntelligencePlatformModule
from app.query.expertise_query_service import ExpertiseQueryService


def _developer(
    identifier: str,
):
    return EntityRef(
        id=identifier,
        type=EntityType.DEVELOPER,
    )


def _module(
    identifier: str,
):
    return EntityRef(
        id=identifier,
        type=EntityType.FILE,
    )


def _projection(
):
    estimator = ExpertiseEstimator(
        RuleExpertiseScoringPolicy(),
        ExponentialDecayPolicy(),
    )
    projection = ExpertiseProjection(
        estimator
    )
    context = EstimationContext(
        current_time=datetime.now(UTC),
        learning_rate=1.0,
    )
    for developer, strength in (
        ("alice", 50.0),
        ("bob", 20.0),
    ):
        projection.apply(
            Evidence(
                id=uuid4(),
                source_event_id=uuid4(),
                subject_ref=_developer(developer),
                predicate=PredicateType.MODIFIED,
                object_ref=_module("auth.py"),
                confidence=1.0,
                metadata={
                    "strength": strength,
                },
            ),
            context,
        )
    return projection


def main():
    intelligence = IntelligenceContext(
        _projection()
    )
    provider = intelligence.platform.provider

    assert (
        provider.resolve(ExpertiseQueryService)
        is intelligence.query_service
    )
    assert (
        provider.resolve(OwnershipService)
        is intelligence.ownership_service
    )
    assert (
        provider.resolve(OrganizationDashboardService)
        is intelligence.organization_dashboard_service
    )
    assert "intelligence" in (
        intelligence
        .runtime
        .modules
        .startup_order()
    )
    assert "intelligence.context" in (
        IntelligencePlatformModule.capabilities
    )
    successors = (
        intelligence
        .successor_service
        .recommend("auth.py")
    )
    assert successors

    print("runtime_di_migration_ok")


if __name__ == "__main__":
    main()
