from datetime import UTC
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1]),
)

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.evidence.core import EvidenceContext
from app.evidence.semantic import SemanticEvidenceEngine
from app.measurement.domain import MeasurementContext
from app.measurement.scientific_engine import ScientificMeasurementEngine
from app.observation.domain import BuildFacts
from app.observation.domain import CommitFacts
from app.observation.domain import DocumentationFacts
from app.observation.domain import FileChangeFacts
from app.observation.domain import Observation
from app.observation.domain import ObservationCategory
from app.observation.domain import ObservationContext
from app.observation.domain import ObservationLifecycle
from app.observation.domain import ObservationProvenance
from app.observation.domain import ObservationType
from app.observation.domain import ReviewFacts
from app.observation.domain import TestFacts
from app.platform import PlatformRuntime
from app.platform import default_platform_modules


def observation(observation_id, observation_type, category, facts):
    return Observation(
        observation_id=observation_id,
        trace_id=f"trace-{observation_id}",
        correlation_id=f"corr-{observation_id}",
        timestamp=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
        observation_type=observation_type,
        observation_category=category,
        source_platform="github",
        source_adapter="github",
        version="1.0",
        lifecycle=ObservationLifecycle.PRODUCTION,
        actors=(EntityRef(id="alice", type=EntityType.DEVELOPER),),
        targets=(EntityRef(id="src/app.py", type=EntityType.FILE),),
        provenance=ObservationProvenance(
            source_platform="github",
            source_adapter="github",
            source_record_id=observation_id,
        ),
        context=ObservationContext(
            repository="pia",
            tenant_id="tenant-a",
        ),
        facts=facts,
    )


def main():
    observations = [
        observation(
            "commit-1",
            ObservationType.COMMIT,
            ObservationCategory.SOURCE_CONTROL,
            CommitFacts(
                commit_id="commit-1",
                message="Add feature",
                author_name="Alice",
                author_email="alice@example.com",
                authored_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
                total_additions=20,
                total_deletions=5,
                total_changes=25,
                files=(
                    FileChangeFacts(
                        path="src/app.py",
                        status="modified",
                        additions=20,
                        deletions=5,
                        changes=25,
                    ),
                ),
            ),
        ),
        observation(
            "review-1",
            ObservationType.REVIEW,
            ObservationCategory.CODE_REVIEW,
            ReviewFacts(
                review_id="review-1",
                subject_id="pr-1",
                reviewer="bob",
                state="approved",
                submitted_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
                comment_count=2,
            ),
        ),
        observation(
            "build-1",
            ObservationType.BUILD,
            ObservationCategory.CI_CD,
            BuildFacts(
                build_id="build-1",
                status="passed",
                started_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
                duration_seconds=120,
            ),
        ),
        observation(
            "test-1",
            ObservationType.TEST,
            ObservationCategory.TESTING,
            TestFacts(
                test_run_id="test-1",
                status="passed",
                started_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
                passed=10,
                failed=0,
            ),
        ),
        observation(
            "doc-1",
            ObservationType.DOCUMENTATION,
            ObservationCategory.DOCUMENTATION,
            DocumentationFacts(
                document_id="doc-1",
                path="docs/milestones/milestone_41.md",
                observed_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
                state="updated",
            ),
        ),
    ]

    measurements = ScientificMeasurementEngine().measure_observations(
        observations,
        MeasurementContext(
            timestamp=datetime.now(UTC),
            tenant_id="tenant-a",
            pipeline_version="sme.v1",
            source_reliability={"github": 0.96},
        ),
    )
    package = SemanticEvidenceEngine().synthesize(
        list(measurements),
        EvidenceContext(
            tenant_id="tenant-a",
            pipeline_version="m41.semantic.v1",
        ),
    )
    evidence_ids = {
        item.provenance.evidence_definition_id
        for item in package.evidence
    }

    assert package.evidence
    assert "code_change_volume_signal" in evidence_ids
    assert "review_activity_signal" in evidence_ids
    assert "build_execution_signal" in evidence_ids
    assert "test_execution_signal" in evidence_ids
    assert "documentation_update_signal" in evidence_ids
    assert all(item.is_valid_for_expertise() for item in package.evidence)
    assert all(item.lineage.source_measurement_ids for item in package.evidence)
    assert all(item.traceability.confidence_factors for item in package.evidence)

    platform = PlatformRuntime.create()
    for module in default_platform_modules():
        platform.register_module(module)
    built = platform.build()
    built.initialize()
    built.start()
    platform_engine = built.provider.resolve(SemanticEvidenceEngine)
    assert platform_engine.synthesize(list(measurements)).evidence
    built.shutdown()

    print("\n=== SEMANTIC EVIDENCE ENGINE ===\n")
    for item in package.evidence:
        print(f"{item.provenance.evidence_definition_id:<32} confidence={item.confidence:.2f}")
    print("\nM41 Semantic Evidence Engine passed.")


if __name__ == "__main__":
    main()

