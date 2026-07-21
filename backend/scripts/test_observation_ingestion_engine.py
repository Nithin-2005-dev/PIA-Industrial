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

from app.measurement.core.engine import MeasurementEngine
from app.observation.domain import ObservationType
from app.observation.ingestion import AdapterRegistry
from app.observation.ingestion import ExternalSource
from app.observation.ingestion import ObservationIngestionEngine
from app.observation.ingestion import RawObservationRecord
from app.observation.ingestion import ReplayQuery
from app.observation.ingestion import StaticObservationAdapter
from app.observation.ingestion import SyncRequest
from app.observation.ingestion import UnifiedIdentityResolver
from app.observation.ingestion.adapters import default_adapter_names
from app.observation.ingestion.normalizer import ObservationNormalizer
from app.platform import PlatformRuntime
from app.platform import default_platform_modules


def record(
    record_id,
    record_type,
    payload,
    source,
):
    return RawObservationRecord(
        source=source,
        record_id=record_id,
        record_type=record_type,
        payload=payload,
        observed_at=datetime(
            2026,
            7,
            1,
            9,
            0,
            tzinfo=UTC,
        ),
        cursor=record_id,
        offset=0,
    )


def main():
    assert {
        "github",
        "gitlab",
        "bitbucket",
        "jira",
        "linear",
        "azure_devops",
        "slack",
        "teams",
        "email",
        "ci_cd",
        "kubernetes",
        "docker",
        "custom_api",
    }.issubset(set(default_adapter_names()))

    source = ExternalSource(
        provider="github",
        adapter="github",
        organization="acme",
        repository="pia",
        tenant_id="tenant-a",
    )
    duplicate_commit = record(
        "c1",
        "commit",
        {
            "author": "octo-alice",
            "message": "Improve ingestion",
            "authored_at": "2026-07-01T09:00:00+00:00",
            "total_additions": 10,
            "total_deletions": 2,
            "total_changes": 12,
            "files": [
                {
                    "path": "backend/app/observation/ingestion/engine.py",
                    "status": "modified",
                    "additions": 10,
                    "deletions": 2,
                    "changes": 12,
                }
            ],
            "targets": [
                "backend/app/observation/ingestion/engine.py"
            ],
        },
        source,
    )
    records = (
        duplicate_commit,
        duplicate_commit,
        record(
            "pr1",
            "pull_request",
            {
                "author": "octo-alice",
                "title": "Add OIE",
                "state": "open",
                "created_at": "2026-07-01T09:01:00+00:00",
                "changed_files": 1,
            },
            source,
        ),
        record(
            "review1",
            "review",
            {
                "reviewer": "octo-bob",
                "subject_id": "pr1",
                "state": "approved",
                "submitted_at": "2026-07-01T09:02:00+00:00",
            },
            source,
        ),
        record(
            "comment1",
            "comment",
            {
                "author": "octo-bob",
                "subject_id": "pr1",
                "body": "Looks good.",
                "created_at": "2026-07-01T09:03:00+00:00",
            },
            source,
        ),
        record(
            "merge1",
            "merge",
            {
                "merged_by": "octo-alice",
                "source_ref": "feature/oie",
                "target_ref": "main",
                "merged_at": "2026-07-01T09:04:00+00:00",
                "commit_id": "c1",
            },
            source,
        ),
        record(
            "build1",
            "build",
            {
                "status": "passed",
                "started_at": "2026-07-01T09:05:00+00:00",
                "completed_at": "2026-07-01T09:06:00+00:00",
                "duration_seconds": 60,
            },
            source,
        ),
        record(
            "deploy1",
            "deployment",
            {
                "environment": "prod",
                "status": "success",
                "deployed_at": "2026-07-01T09:07:00+00:00",
                "version": "39.0",
            },
            source,
        ),
        record(
            "release1",
            "release",
            {
                "author": "octo-alice",
                "version": "39.0",
                "status": "published",
                "released_at": "2026-07-01T09:08:00+00:00",
            },
            source,
        ),
        record(
            "test1",
            "test",
            {
                "status": "passed",
                "started_at": "2026-07-01T09:09:00+00:00",
                "passed": 42,
                "failed": 0,
            },
            source,
        ),
        record(
            "doc1",
            "documentation",
            {
                "path": "docs/milestones/milestone_39.md",
                "state": "updated",
                "title": "M39",
            },
            source,
        ),
    )

    identities = UnifiedIdentityResolver()
    identities.register(
        "github",
        "octo-alice",
        "alice",
        display_name="Alice",
    )
    identities.register(
        "github",
        "octo-bob",
        "bob",
        display_name="Bob",
    )

    registry = AdapterRegistry()
    registry.register(
        StaticObservationAdapter(
            name="github",
            provider="github",
            records=records,
            supported_record_types=(
                "commit",
                "pull_request",
                "review",
                "comment",
                "merge",
                "build",
                "deployment",
                "release",
                "test",
                "documentation",
            ),
        )
    )

    seen_events = []
    engine = ObservationIngestionEngine(
        adapters=registry,
        normalizer=ObservationNormalizer(identities),
    )
    engine.event_bus.subscribe(
        "observation.normalized",
        seen_events.append,
    )
    result = engine.sync(
        "github",
        SyncRequest(
            source=source,
            batch_size=100,
        ),
    )

    assert result.raw_count == len(records)
    assert result.accepted_count == len(records) - 1
    assert result.duplicate_count == 1
    assert result.failed_count == 0
    assert result.checkpoint.offset == len(records)
    assert len(seen_events) == result.accepted_count
    assert engine.metrics.throughput > 0
    assert engine.metrics.duplicate_rate > 0

    normalized = engine.replay(
        ReplayQuery(
            repository="pia",
            adapter="github",
        )
    )
    assert len(normalized) == result.accepted_count
    assert normalized[0].observation_type == ObservationType.COMMIT
    assert normalized[0].actors[0].id == "alice"
    assert all(
        observation.source_platform == "github"
        for observation in normalized
    )

    developer_replay = engine.replay(
        ReplayQuery(
            developer="bob",
        )
    )
    assert {
        observation.observation_type
        for observation in developer_replay
    } == {
        ObservationType.REVIEW,
        ObservationType.COMMENT,
    }

    measurements = MeasurementEngine.default().measure_observations(
        list(normalized)
    )
    assert measurements
    assert all(
        measurement.provenance.source_observation_id
        for measurement in measurements
    )

    platform = PlatformRuntime.create()
    for module in default_platform_modules():
        platform.register_module(module)
    built = platform.build()
    built.initialize()
    built.start()

    platform_engine = built.provider.resolve(ObservationIngestionEngine)
    platform_registry = built.provider.resolve(AdapterRegistry)
    platform_registry.register(
        StaticObservationAdapter(
            name="github-platform",
            provider="github",
            records=(
                record(
                    "c-platform",
                    "commit",
                    {
                        "author": "octo-alice",
                        "message": "Platform OIE",
                        "authored_at": "2026-07-01T10:00:00+00:00",
                    },
                    ExternalSource(
                        provider="github",
                        adapter="github",
                        repository="pia",
                    ),
                ),
            ),
        )
    )
    platform_result = platform_engine.sync(
        "github-platform",
        SyncRequest(
            source=ExternalSource(
                provider="github",
                adapter="github",
                repository="pia",
            )
        ),
    )
    assert platform_result.accepted_count == 1
    assert platform.modules.startup_order()[0] == "observation"

    built.shutdown()

    print(
        "\n=== OBSERVATION INGESTION ENGINE ===\n"
    )
    print(
        "M39 Unified Observation & Ingestion Engine passed."
    )


if __name__ == "__main__":
    main()

