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
from app.measurement.domain import MeasurementContext
from app.measurement.scientific_engine import ScientificMeasurementEngine
from app.measurement.scientific_engine import StaticAnalysisMeasurementProvider
from app.measurement.scientific_engine import default_measurement_providers
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


def _commit_observation(
) -> Observation:
    timestamp = datetime(
        2026,
        7,
        1,
        12,
        30,
        tzinfo=UTC,
    )
    return Observation(
        observation_id="commit-static-1",
        trace_id="trace-static-1",
        correlation_id="corr-static-1",
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
                id="backend/app/core.py",
                type=EntityType.FILE,
            ),
        ),
        provenance=ObservationProvenance(
            source_platform="github",
            source_adapter="github_rest",
            source_record_id="commit-static-1",
        ),
        context=ObservationContext(
            repository="pia",
            organization="acme",
            tenant_id="tenant-a",
        ),
        facts=CommitFacts(
            commit_id="commit-static-1",
            message="Add static analysis measurements",
            author_name="Alice",
            author_email="alice@example.test",
            authored_at=timestamp,
            total_additions=18,
            total_deletions=6,
            total_changes=24,
            files=(
                FileChangeFacts(
                    path="backend/app/core.py",
                    status="modified",
                    additions=10,
                    deletions=4,
                    changes=14,
                    patch="+ if enabled:\n+     for item in items:\n+         run(item)",
                ),
                FileChangeFacts(
                    path="backend/tests/test_core.py",
                    status="modified",
                    additions=8,
                    deletions=2,
                    changes=10,
                    patch="+ if result:\n+     assert result.ok",
                ),
            ),
        ),
    )


def main():
    providers = default_measurement_providers()
    assert any(
        isinstance(provider, StaticAnalysisMeasurementProvider)
        for provider in providers
    )

    engine = ScientificMeasurementEngine()
    observation = _commit_observation()
    context = MeasurementContext(
        timestamp=datetime.now(UTC),
        pipeline_version="m45.static_analysis.v1",
        tenant_id="tenant-a",
    )
    measurements = engine.measure_observation(
        observation,
        context,
    )
    by_id = {
        measurement.definition.id: measurement
        for measurement in measurements
    }

    assert by_id["code_churn_ratio"].value == 1.0
    assert by_id["test_file_touch_ratio"].value == 0.5
    assert by_id["largest_file_delta"].value == 14
    assert by_id["patch_complexity_score"].value >= 5
    assert by_id["patch_complexity_score"].metadata["provider"] == "static_analysis"
    assert by_id["code_churn_ratio"].unit.value == "ratio"

    platform = PlatformRuntime.create()
    for module in default_platform_modules():
        platform.register_module(module)
    built = platform.build()
    built.initialize()
    platform_engine = built.provider.resolve(
        ScientificMeasurementEngine
    )
    platform_ids = {
        measurement.definition.id
        for measurement in platform_engine.measure_observation(
            observation,
            context,
        )
    }
    assert {
        "code_churn_ratio",
        "test_file_touch_ratio",
        "largest_file_delta",
        "patch_complexity_score",
    }.issubset(platform_ids)
    built.shutdown()

    print("static_analysis_measurements_ok")


if __name__ == "__main__":
    main()

