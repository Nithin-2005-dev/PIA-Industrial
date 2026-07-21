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
from app.measurement.domain import MeasurementContext
from app.observation.adapters import GitHubObservationTranslator
from app.observation.core import ObservationPipeline
from app.observation.domain import CommitFacts
from app.observation.registry import ObservationRegistry
from app.observation.storage import ObservationStore
from app.observation.streaming import ObservationStream
from app.observation.validation import ObservationValidationPipeline
from app.observation.validation import ObservationValidationStatus


def github_commit_payload():
    raw_commit = {
        "sha": "abc123",
        "author": {
            "login": "alice",
        },
        "commit": {
            "message": "Improve checkout flow",
            "author": {
                "name": "Alice",
                "email": "alice@example.com",
                "date": "2026-06-30T10:00:00Z",
            },
            "committer": {
                "name": "Alice",
                "email": "alice@example.com",
                "date": "2026-06-30T10:01:00Z",
            },
        },
        "parents": [
            {
                "sha": "parent1",
            },
        ],
    }
    details = {
        "stats": {
            "additions": 120,
            "deletions": 35,
            "total": 155,
        },
        "files": [
            {
                "filename": "checkout.py",
                "status": "modified",
                "additions": 80,
                "deletions": 10,
                "changes": 90,
                "patch": "+ if enabled:\n+     for item in cart:\n",
            },
            {
                "filename": "billing.py",
                "status": "modified",
                "additions": 40,
                "deletions": 25,
                "changes": 65,
                "patch": "- if legacy:\n+ while retry:\n",
            },
        ],
        "commit": {
            "verification": {
                "verified": True,
            },
        },
    }
    return raw_commit, details


def main():
    raw_commit, details = github_commit_payload()

    observation = GitHubObservationTranslator().commit(
        raw_commit,
        details,
        repository="example/shop",
        tenant_id="tenant-a",
    )

    assert isinstance(
        observation.facts,
        CommitFacts,
    )
    assert observation.source_platform == "github"
    assert observation.source_adapter == "github_rest"
    assert observation.facts.total_additions == 120
    assert observation.facts.total_deletions == 35
    assert observation.facts.total_changes == 155
    assert len(
        observation.facts.files
    ) == 2
    assert not hasattr(
        observation,
        "payload",
    )

    registry = ObservationRegistry.default()
    assert registry.for_observation(
        observation.observation_type,
        observation.version,
    ).schema == "CommitFacts"
    assert len(
        registry.all()
    ) >= 13

    validator = ObservationValidationPipeline(
        registry
    )
    result = validator.validate(
        observation
    )
    assert result.status == ObservationValidationStatus.PASSED

    duplicate = validator.validate(
        observation
    )
    assert duplicate.status == ObservationValidationStatus.FAILED
    assert "duplicate observation id" in duplicate.errors

    pipeline = ObservationPipeline(
        validator=ObservationValidationPipeline(
            registry
        )
    )
    accepted = pipeline.process(
        (
            observation,
        )
    )
    assert accepted == (
        observation,
    )
    assert pipeline.replay() == (
        observation,
    )

    store = ObservationStore()
    updates = []
    stream = ObservationStream(
        store
    )
    stream.subscribe(
        updates.append
    )
    update = stream.publish(
        (
            observation,
        )
    )
    assert update.sequence == 1
    assert update.offset == 0
    assert updates[
        0
    ].observations == (
        observation,
    )
    assert store.history(
        observation.correlation_id
    ) == (
        observation,
    )
    assert store.since(
        0
    ) == (
        observation,
    )

    measurements = MeasurementEngine.default().measure_observation(
        observation,
        MeasurementContext(
            timestamp=datetime.now(
                UTC
            ),
            tenant_id="tenant-a",
            source_reliability={
                "github": 0.95,
            },
        ),
    )
    by_definition = {
        measurement.definition.id: measurement
        for measurement in measurements
    }
    assert by_definition[
        "code_churn"
    ].value == 155
    assert by_definition[
        "files_changed"
    ].value == 2
    assert all(
        measurement.provenance.source_observation_id
        == observation.observation_id
        for measurement in measurements
    )

    print(
        "M36 observation platform tests passed."
    )


if __name__ == "__main__":
    main()
