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
from app.measurement.core.recompute import MeasurementDependencyGraph
from app.measurement.domain import MeasurementContext
from app.measurement.domain import MeasurementUnit
from app.measurement.domain import ValidationStatus
from app.measurement.scientific_engine import MeasurementAggregationEngine
from app.measurement.scientific_engine import MeasurementDataType
from app.measurement.scientific_engine import MeasurementProviderRegistry
from app.measurement.scientific_engine import ScientificMeasurementDefinition
from app.measurement.scientific_engine import ScientificMeasurementEngine
from app.measurement.scientific_engine import ScientificMeasurementRegistry
from app.measurement.scientific_engine import ScientificStatistics
from app.measurement.scientific_engine import default_measurement_providers
from app.measurement.scientific_engine import default_scientific_measurements
from app.measurement.scientific_engine.providers import BaseMeasurementProvider
from app.observation.domain import BuildFacts
from app.observation.domain import CommitFacts
from app.observation.domain import DocumentationFacts
from app.observation.domain import FileChangeFacts
from app.observation.domain import IssueFacts
from app.observation.domain import Observation
from app.observation.domain import ObservationCategory
from app.observation.domain import ObservationContext
from app.observation.domain import ObservationLifecycle
from app.observation.domain import ObservationProvenance
from app.observation.domain import ObservationType
from app.observation.domain import PullRequestFacts
from app.observation.domain import ReviewFacts
from app.observation.domain import TestFacts
from app.platform import PlatformRuntime
from app.platform import default_platform_modules


def obs(
    observation_id,
    observation_type,
    category,
    facts,
    targets=(),
):
    return Observation(
        observation_id=observation_id,
        trace_id=f"trace-{observation_id}",
        correlation_id=f"corr-{observation_id}",
        timestamp=datetime(
            2026,
            7,
            1,
            12,
            0,
            tzinfo=UTC,
        ),
        observation_type=observation_type,
        observation_category=category,
        source_platform="github",
        source_adapter="github",
        version="1.0",
        lifecycle=ObservationLifecycle.PRODUCTION,
        actors=(
            EntityRef(
                id="alice",
                type=EntityType.DEVELOPER,
            ),
        ),
        targets=targets,
        provenance=ObservationProvenance(
            source_platform="github",
            source_adapter="github",
            source_record_id=observation_id,
        ),
        context=ObservationContext(
            repository="pia",
            organization="acme",
            tenant_id="tenant-a",
        ),
        facts=facts,
    )


class CustomCommitProvider(BaseMeasurementProvider):
    name = "custom_commit_provider"
    version = "1.0"
    supported_types = (ObservationType.COMMIT,)

    def measure(
        self,
        observation,
        context,
        registry,
    ):
        return (
            self._measurement(
                observation,
                context,
                registry,
                "custom_commit_constant",
                1.0,
            ),
        )


def main():
    commit = obs(
        "commit-1",
        ObservationType.COMMIT,
        ObservationCategory.SOURCE_CONTROL,
        CommitFacts(
            commit_id="commit-1",
            message="Add deterministic SME",
            author_name="Alice",
            author_email="alice@example.com",
            authored_at=datetime(
                2026,
                7,
                1,
                12,
                0,
                tzinfo=UTC,
            ),
            total_additions=40,
            total_deletions=10,
            total_changes=50,
            files=(
                FileChangeFacts(
                    path="backend/app/measurement/scientific_engine/engine.py",
                    status="modified",
                    additions=30,
                    deletions=8,
                    changes=38,
                ),
                FileChangeFacts(
                    path="backend/app/measurement/scientific_engine/providers.py",
                    status="modified",
                    additions=10,
                    deletions=2,
                    changes=12,
                ),
            ),
        ),
        targets=(
            EntityRef(
                id="backend/app/measurement/scientific_engine/engine.py",
                type=EntityType.FILE,
            ),
        ),
    )
    pull_request = obs(
        "pr-1",
        ObservationType.PULL_REQUEST,
        ObservationCategory.CODE_REVIEW,
        PullRequestFacts(
            pull_request_id="pr-1",
            title="M40",
            state="merged",
            author="alice",
            created_at=datetime(2026, 7, 1, 10, 0, tzinfo=UTC),
            merged_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
            changed_files=2,
        ),
    )
    review = obs(
        "review-1",
        ObservationType.REVIEW,
        ObservationCategory.CODE_REVIEW,
        ReviewFacts(
            review_id="review-1",
            subject_id="pr-1",
            reviewer="bob",
            state="approved",
            submitted_at=datetime(2026, 7, 1, 11, 0, tzinfo=UTC),
            comment_count=3,
        ),
    )
    issue = obs(
        "issue-1",
        ObservationType.ISSUE,
        ObservationCategory.PROJECT_MANAGEMENT,
        IssueFacts(
            issue_id="issue-1",
            title="Bug",
            state="closed",
            author="alice",
            created_at=datetime(2026, 7, 1, 9, 0, tzinfo=UTC),
            closed_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
            labels=("bug", "m40"),
        ),
    )
    build = obs(
        "build-1",
        ObservationType.BUILD,
        ObservationCategory.CI_CD,
        BuildFacts(
            build_id="build-1",
            status="passed",
            started_at=datetime(2026, 7, 1, 11, 0, tzinfo=UTC),
            completed_at=datetime(2026, 7, 1, 11, 5, tzinfo=UTC),
            duration_seconds=300,
        ),
    )
    test = obs(
        "test-1",
        ObservationType.TEST,
        ObservationCategory.TESTING,
        TestFacts(
            test_run_id="test-1",
            status="passed",
            started_at=datetime(2026, 7, 1, 11, 5, tzinfo=UTC),
            failed=0,
            passed=120,
        ),
    )
    documentation = obs(
        "doc-1",
        ObservationType.DOCUMENTATION,
        ObservationCategory.DOCUMENTATION,
        DocumentationFacts(
            document_id="doc-1",
            path="docs/milestones/milestone_40.md",
            observed_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
            state="updated",
        ),
    )

    registry = ScientificMeasurementRegistry(
        default_scientific_measurements()
    )
    registry.register(
        ScientificMeasurementDefinition(
            id="custom_commit_constant",
            name="Custom Commit Constant",
            description="Plugin measurement used by the M40 smoke test.",
            unit=MeasurementUnit.COUNT,
            data_type=MeasurementDataType.FLOAT,
            provider="custom_commit_provider",
            version="1.0",
            minimum=0.0,
        )
    )

    providers = MeasurementProviderRegistry(
        (
            *default_measurement_providers(),
            CustomCommitProvider(),
        )
    )
    engine = ScientificMeasurementEngine(
        providers=providers,
        registry=registry,
    )
    context = MeasurementContext(
        timestamp=datetime.now(UTC),
        pipeline_version="sme.v1",
        tenant_id="tenant-a",
        source_reliability={
            "github": 0.96,
        },
    )
    observations = [
        commit,
        pull_request,
        review,
        issue,
        build,
        test,
        documentation,
    ]
    measurements = engine.measure_observations(
        observations,
        context,
    )
    by_id = {
        measurement.definition.id: measurement
        for measurement in measurements
    }

    assert by_id["lines_added"].value == 40
    assert by_id["lines_deleted"].value == 10
    assert by_id["files_modified"].value == 2
    assert by_id["directories_changed"].value == 1
    assert by_id["review_latency_seconds"].value == 7200
    assert by_id["review_count"].value == 1
    assert by_id["comment_count"].value == 3
    assert by_id["issue_resolution_seconds"].value == 10800
    assert by_id["label_count"].value == 2
    assert by_id["build_duration_seconds"].value == 300
    assert by_id["test_failures"].value == 0
    assert by_id["document_path_depth"].value == 3
    assert by_id["custom_commit_constant"].value == 1

    for measurement in measurements:
        assert measurement.provenance.source_observation_id
        assert measurement.traceability.evaluator
        assert measurement.version == "1.0"
        assert measurement.validation_status in {
            ValidationStatus.PASSED,
            ValidationStatus.WARNING,
        }
        assert 0.0 <= measurement.confidence <= 1.0
        assert "provider" in measurement.metadata
        assert "precision" in measurement.metadata

    repeated = engine.measure_observations(
        observations,
        context,
    )
    assert [
        measurement.id
        for measurement in measurements
    ] == [
        measurement.id
        for measurement in repeated
    ]

    aggregation = MeasurementAggregationEngine()
    values = [
        1,
        2,
        3,
        4,
    ]
    assert aggregation.sum(values) == 10
    assert aggregation.mean(values) == 2.5
    assert aggregation.median(values) == 2.5
    assert aggregation.min(values) == 1
    assert aggregation.max(values) == 4
    assert aggregation.percentile(values, 0.5) in {2, 3}
    assert aggregation.rolling_mean(values, 2) == [
        1.0,
        1.5,
        2.5,
        3.5,
    ]
    assert aggregation.time_buckets(
        [
            (
                commit.timestamp,
                1.0,
            ),
            (
                review.timestamp,
                2.0,
            ),
        ],
        3600,
    )

    stats = ScientificStatistics()
    assert stats.mean(values) == 2.5
    assert round(stats.variance(values), 5) == 1.66667
    assert stats.standard_deviation(values) > 0
    assert stats.entropy(values) > 0
    assert stats.quantile(values, 0.95) == 4
    assert stats.histogram(values, 2)
    assert stats.correlation(values, values) == 1.0
    assert stats.distribution_analysis(values)["p50"] in {2, 3}

    graph = MeasurementDependencyGraph()
    graph.register(
        "architectural_complexity",
        (
            "cyclomatic_complexity",
            "complexity_score",
        ),
    )
    assert graph.affected_by(
        "cyclomatic_complexity"
    ) == {
        "architectural_complexity",
    }

    assert engine.last_benchmark.measurement_latency_ms >= 0
    assert engine.last_benchmark.throughput > 0
    assert engine.last_benchmark.allocation_count == len(observations)

    platform = PlatformRuntime.create()
    for module in default_platform_modules():
        platform.register_module(module)
    built = platform.build()
    built.initialize()
    built.start()
    platform_engine = built.provider.resolve(
        ScientificMeasurementEngine
    )
    platform_measurements = platform_engine.measure_observations(
        [
            commit,
        ],
        context,
    )
    assert platform.modules.startup_order()[:2] == (
        "observation",
        "measurement",
    )
    assert platform_measurements
    built.shutdown()

    print(
        "\n=== SCIENTIFIC MEASUREMENT ENGINE ===\n"
    )
    for measurement in measurements:
        print(
            f"{measurement.definition.id:<30}"
            f"value={measurement.value:<10.2f}"
            f"confidence={measurement.confidence:.2f}"
        )
    print(
        "\nM40 Scientific Measurement Engine passed."
    )


if __name__ == "__main__":
    main()

