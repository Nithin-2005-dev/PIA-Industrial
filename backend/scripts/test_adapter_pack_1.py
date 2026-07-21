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

from app.observation.adapters import GitHubActionsObservationAdapter
from app.observation.adapters import GitHubRestObservationAdapter
from app.observation.adapters import JiraObservationAdapter
from app.observation.adapters import SlackObservationAdapter
from app.observation.domain import ObservationType
from app.observation.ingestion import AdapterRegistry
from app.observation.ingestion import ExternalSource
from app.observation.ingestion import ObservationIngestionEngine
from app.observation.ingestion import SyncRequest
from app.observation.ingestion import UnifiedIdentityResolver
from app.observation.ingestion.normalizer import ObservationNormalizer
from app.platform import PlatformRuntime
from app.platform import default_platform_modules


def _sync(
    adapter,
    source,
    identities,
):
    registry = AdapterRegistry()
    registry.register(adapter)
    engine = ObservationIngestionEngine(
        adapters=registry,
        normalizer=ObservationNormalizer(identities),
    )
    result = engine.sync(
        adapter.name,
        SyncRequest(
            source=source,
            batch_size=25,
        ),
    )
    assert result.failed_count == 0
    assert result.accepted_count > 0
    return engine.store.normalized()


def main():
    identities = UnifiedIdentityResolver()
    identities.register("github", "octo-alice", "alice")
    identities.register("jira", "jira-bob", "bob")
    identities.register("slack", "U123", "carol")
    identities.register("github_actions", "ci-bot", "ci-bot")

    github_observations = _sync(
        GitHubRestObservationAdapter(
            records=(
                {
                    "sha": "abc123",
                    "author": {
                        "login": "octo-alice",
                    },
                    "commit": {
                        "author": {
                            "name": "Alice",
                            "email": "alice@example.test",
                            "date": "2026-07-01T09:00:00Z",
                        },
                        "committer": {
                            "name": "Alice",
                            "email": "alice@example.test",
                            "date": "2026-07-01T09:01:00Z",
                        },
                        "message": "Add adapter pack",
                    },
                    "stats": {
                        "additions": 12,
                        "deletions": 2,
                        "total": 14,
                    },
                    "files": [
                        {
                            "filename": "backend/app/observation/adapters/provider_pack.py",
                            "status": "added",
                            "additions": 12,
                            "deletions": 2,
                            "changes": 14,
                        }
                    ],
                },
                {
                    "event": "pull_request",
                    "pull_request": {
                        "id": 42,
                        "title": "Adapter pack",
                        "state": "open",
                        "user": {
                            "login": "octo-alice",
                        },
                        "created_at": "2026-07-01T09:05:00Z",
                        "updated_at": "2026-07-01T09:06:00Z",
                        "head": {
                            "ref": "feature/adapters",
                        },
                        "base": {
                            "ref": "main",
                        },
                        "changed_files": 1,
                    },
                },
            )
        ),
        ExternalSource(
            provider="github",
            adapter="github_rest",
            organization="acme",
            repository="pia",
        ),
        identities,
    )
    assert {
        observation.observation_type
        for observation in github_observations
    } == {
        ObservationType.COMMIT,
        ObservationType.PULL_REQUEST,
    }
    assert github_observations[0].actors[0].id == "alice"

    jira_observations = _sync(
        JiraObservationAdapter(
            records=(
                {
                    "key": "PIA-123",
                    "fields": {
                        "summary": "Normalize issue payloads",
                        "issuetype": {
                            "name": "Task",
                        },
                        "status": {
                            "name": "In Progress",
                        },
                        "creator": {
                            "accountId": "jira-bob",
                        },
                        "created": "2026-07-01T10:00:00+00:00",
                        "updated": "2026-07-01T10:10:00+00:00",
                        "labels": [
                            "ingestion",
                        ],
                    },
                },
            )
        ),
        ExternalSource(
            provider="jira",
            adapter="jira",
            organization="acme",
        ),
        identities,
    )
    assert jira_observations[0].observation_type == ObservationType.ISSUE
    assert jira_observations[0].actors[0].id == "bob"

    slack_observations = _sync(
        SlackObservationAdapter(
            records=(
                {
                    "client_msg_id": "m1",
                    "channel": "C123",
                    "user": "U123",
                    "text": "Deployment notes are ready",
                    "ts": "1782900600.000000",
                },
            )
        ),
        ExternalSource(
            provider="slack",
            adapter="slack",
            organization="acme",
        ),
        identities,
    )
    assert slack_observations[0].observation_type == ObservationType.COMMENT
    assert slack_observations[0].actors[0].id == "carol"

    actions_observations = _sync(
        GitHubActionsObservationAdapter(
            records=(
                {
                    "run_id": 9001,
                    "actor": "ci-bot",
                    "status": "completed",
                    "conclusion": "success",
                    "run_started_at": "2026-07-01T11:00:00Z",
                    "completed_at": "2026-07-01T11:02:00Z",
                    "duration_seconds": 120,
                },
                {
                    "record_type": "test",
                    "id": "tests-9001",
                    "actor": "ci-bot",
                    "status": "success",
                    "started_at": "2026-07-01T11:00:00Z",
                    "completed_at": "2026-07-01T11:02:00Z",
                    "passed": 20,
                    "failed": 0,
                    "skipped": 1,
                },
            )
        ),
        ExternalSource(
            provider="github_actions",
            adapter="github_actions",
            repository="pia",
        ),
        identities,
    )
    assert {
        observation.observation_type
        for observation in actions_observations
    } == {
        ObservationType.BUILD,
        ObservationType.TEST,
    }

    platform = PlatformRuntime.create()
    for module in default_platform_modules():
        platform.register_module(module)
    built = platform.build()
    built.initialize()
    registry = built.provider.resolve(AdapterRegistry)
    assert {
        "github_rest",
        "jira",
        "slack",
        "github_actions",
    }.issubset(
        {
            adapter.name
            for adapter in registry.all()
        }
    )
    assert isinstance(
        built.provider.resolve(ObservationIngestionEngine),
        ObservationIngestionEngine,
    )
    built.shutdown()

    print("adapter_pack_1_ok")


if __name__ == "__main__":
    main()
