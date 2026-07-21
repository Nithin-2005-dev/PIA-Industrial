from datetime import UTC
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.estimator.estimation_context import EstimationContext
from app.estimator.expertise_estimator import ExpertiseEstimator
from app.estimator.expertise_projection import ExpertiseProjection
from app.estimator.policies.exponential_decay_policy import ExponentialDecayPolicy
from app.estimator.policies.rule_expertise_scoring_policy import RuleExpertiseScoringPolicy
from app.estimator.semantic_pipeline import SemanticEvidenceExpertiseBridge
from app.estimator.semantic_pipeline import SemanticExpertiseProjectionPipeline
from app.evidence.semantic import SemanticEvidenceEngine
from app.measurement.domain import MeasurementContext
from app.measurement.scientific_engine import ScientificMeasurementEngine
from app.observation.domain import CommitFacts
from app.observation.domain import FileChangeFacts
from app.observation.domain import Observation
from app.observation.domain import ObservationCategory
from app.observation.domain import ObservationContext
from app.observation.domain import ObservationLifecycle
from app.observation.domain import ObservationProvenance
from app.observation.domain import ObservationType
from app.platform import PlatformRuntime
from app.platform import default_platform_modules


def _observation(
) -> Observation:
    timestamp = datetime(
        2026,
        7,
        1,
        13,
        0,
        tzinfo=UTC,
    )
    return Observation(
        observation_id="commit-expertise-1",
        trace_id="trace-expertise-1",
        correlation_id="corr-expertise-1",
        timestamp=timestamp,
        observation_type=ObservationType.COMMIT,
        observation_category=ObservationCategory.SOURCE_CONTROL,
        source_platform="github",
        source_adapter="github_rest",
        version="1.0",
        lifecycle=ObservationLifecycle.PRODUCTION,
        actors=(
            EntityRef(
                id="alice",
                type=EntityType.DEVELOPER,
            ),
        ),
        targets=(
            EntityRef(
                id="backend/app/platform/runtime.py",
                type=EntityType.FILE,
            ),
        ),
        provenance=ObservationProvenance(
            source_platform="github",
            source_adapter="github_rest",
            source_record_id="commit-expertise-1",
        ),
        context=ObservationContext(
            repository="pia",
            organization="acme",
            tenant_id="tenant-a",
        ),
        facts=CommitFacts(
            commit_id="commit-expertise-1",
            message="Improve runtime lifecycle",
            author_name="Alice",
            author_email="alice@example.test",
            authored_at=timestamp,
            total_additions=30,
            total_deletions=5,
            total_changes=35,
            files=(
                FileChangeFacts(
                    path="backend/app/platform/runtime.py",
                    status="modified",
                    additions=30,
                    deletions=5,
                    changes=35,
                    patch="+ if module:\n+     module.start()",
                ),
            ),
        ),
    )


def _projection(
) -> ExpertiseProjection:
    return ExpertiseProjection(
        ExpertiseEstimator(
            RuleExpertiseScoringPolicy(),
            ExponentialDecayPolicy(),
        )
    )


def main():
    observation = _observation()
    measurement_context = MeasurementContext(
        timestamp=observation.timestamp,
        pipeline_version="m46.semantic_expertise.v1",
        tenant_id="tenant-a",
    )
    measurements = ScientificMeasurementEngine().measure_observation(
        observation,
        measurement_context,
    )
    package = SemanticEvidenceEngine().synthesize(
        list(measurements)
    )
    assert package.for_expertise()

    bridge = SemanticEvidenceExpertiseBridge()
    estimator_evidence = bridge.package_to_estimator_evidence(
        package
    )
    assert estimator_evidence
    assert estimator_evidence[0].subject_ref.id == "alice"
    assert estimator_evidence[0].object_ref.id == "backend/app/platform/runtime.py"
    assert estimator_evidence[0].metadata["semantic_evidence_id"]

    projection = _projection()
    result = SemanticExpertiseProjectionPipeline(
        bridge
    ).apply(
        package,
        projection,
        EstimationContext(
            current_time=observation.timestamp,
            learning_rate=1.0,
        ),
    )
    estimates = projection.all_estimates()
    assert result.applied_count >= 1
    assert result.skipped_count == 0
    assert len(estimates) == 1
    assert estimates[0].developer_ref.id == "alice"
    assert estimates[0].module_ref.id == "backend/app/platform/runtime.py"
    assert estimates[0].raw_score > 0
    assert estimates[0].confidence > 0

    platform = PlatformRuntime.create()
    for module in default_platform_modules():
        platform.register_module(module)
    built = platform.build()
    built.initialize()
    platform_pipeline = built.provider.resolve(
        SemanticExpertiseProjectionPipeline
    )
    platform_projection = _projection()
    platform_result = platform_pipeline.apply(
        package,
        platform_projection,
        EstimationContext(
            current_time=observation.timestamp,
            learning_rate=1.0,
        ),
    )
    assert platform_result.applied_count == result.applied_count
    assert platform_projection.all_estimates()
    built.shutdown()

    print("semantic_expertise_estimation_ok")


if __name__ == "__main__":
    main()

