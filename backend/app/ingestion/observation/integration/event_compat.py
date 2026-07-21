from datetime import datetime
from uuid import NAMESPACE_URL, uuid5
from uuid import UUID

from app.domain.event import Event
from app.domain.event_type import EventType
from app.ingestion.observation.domain import CommitFacts
from app.ingestion.observation.domain import FileChangeFacts
from app.ingestion.observation.domain import Observation
from app.ingestion.observation.domain import ObservationCategory
from app.ingestion.observation.domain import ObservationContext
from app.ingestion.observation.domain import ObservationLifecycle
from app.ingestion.observation.domain import ObservationProvenance
from app.ingestion.observation.domain import ObservationType


def event_to_observation(
    event: Event,
) -> Observation:
    if event.type != EventType.COMMIT:
        raise ValueError(
            "only commit event compatibility is supported"
        )

    payload = event.payload
    observation_payload = payload.get(
        "observation",
        {},
    )
    behavior = (
        observation_payload.get(
            "behavioral",
            {},
        ).get(
            "commit",
            {},
        )
    )
    artifact = observation_payload.get(
        "artifact",
        {},
    )
    semantic = observation_payload.get(
        "semantic",
        {},
    )
    commit_semantic = semantic.get(
        "commit",
        {},
    )

    files = tuple(
        FileChangeFacts(
            path=str(
                file.get(
                    "filename",
                    "",
                )
            ),
            previous_path=file.get(
                "previous_filename"
            ),
            status=str(
                file.get(
                    "status",
                    "modified",
                )
            ),
            additions=int(
                file.get(
                    "additions",
                    0,
                )
                or 0
            ),
            deletions=int(
                file.get(
                    "deletions",
                    0,
                )
                or 0
            ),
            changes=int(
                file.get(
                    "changes",
                    0,
                )
                or 0
            ),
            patch=file.get(
                "patch"
            ),
        )
        for file in artifact.get(
            "files",
            [],
        )
    )

    authored_at = event.occurred_at
    if isinstance(
        authored_at,
        str,
    ):
        authored_at = datetime.fromisoformat(
            authored_at
        )

    return Observation(
        observation_id=str(
            event.id
        ),
        trace_id=str(
            event.id
        ),
        correlation_id=str(
            event.id
        ),
        timestamp=event.occurred_at,
        observation_type=ObservationType.COMMIT,
        observation_category=ObservationCategory.SOURCE_CONTROL,
        source_platform=str(
            event.metadata.get(
                "source",
                "legacy",
            )
        ),
        source_adapter=str(
            event.metadata.get(
                "gateway",
                "event_compat",
            )
        ),
        version="1.0",
        lifecycle=ObservationLifecycle.PRODUCTION,
        actors=(
            event.actor_ref,
        ),
        targets=event.target_refs,
        provenance=ObservationProvenance(
            source_platform=str(
                event.metadata.get(
                    "source",
                    "legacy",
                )
            ),
            source_adapter="event_compat",
            source_record_id=str(
                event.id
            ),
        ),
        context=ObservationContext(
            tenant_id=event.metadata.get(
                "tenant_id"
            )
        ),
        facts=CommitFacts(
            commit_id=str(
                payload.get(
                    "sha",
                    event.id,
                )
            ),
            message=str(
                payload.get(
                    "message",
                    commit_semantic.get(
                        "message",
                        "",
                    ),
                )
            ),
            author_name=None,
            author_email=None,
            authored_at=authored_at,
            committed_at=authored_at,
            parent_ids=(),
            total_additions=int(
                behavior.get(
                    "total_additions",
                    payload.get(
                        "additions",
                        0,
                    ),
                )
                or 0
            ),
            total_deletions=int(
                behavior.get(
                    "total_deletions",
                    payload.get(
                        "deletions",
                        0,
                    ),
                )
                or 0
            ),
            total_changes=int(
                behavior.get(
                    "total_changes",
                    payload.get(
                        "total_changes",
                        0,
                    ),
                )
                or 0
            ),
            files=files,
        ),
    )


def stable_observation_id(
    *parts: object,
) -> str:
    return str(
        uuid5(
            NAMESPACE_URL,
            ":".join(
                str(part)
                for part in parts
            ),
        )
    )


def observation_to_event(
    observation: Observation,
) -> Event:
    """
    Deprecated compatibility bridge.

    The returned Event carries canonical observation facts only. It does not
    include vendor raw payloads or adapter DTOs.
    """
    if not isinstance(
        observation.facts,
        CommitFacts,
    ):
        raise ValueError(
            "only commit observation compatibility is supported"
        )

    facts = observation.facts
    files = [
        {
            "filename": file.path,
            "previous_filename": file.previous_path,
            "status": file.status,
            "additions": file.additions,
            "deletions": file.deletions,
            "changes": file.changes,
            "patch": file.patch,
        }
        for file in facts.files
    ]

    return Event(
        id=UUID(
            observation.observation_id
        ),
        type=EventType.COMMIT,
        actor_ref=observation.actors[0],
        target_refs=observation.targets,
        occurred_at=observation.timestamp,
        payload={
            "sha": facts.commit_id,
            "message": facts.message,
            "additions": facts.total_additions,
            "deletions": facts.total_deletions,
            "total_changes": facts.total_changes,
            "observation": {
                "artifact": {
                    "files": files,
                },
                "behavioral": {
                    "commit": {
                        "files_changed": len(
                            files
                        ),
                        "total_additions": facts.total_additions,
                        "total_deletions": facts.total_deletions,
                        "total_changes": facts.total_changes,
                    },
                },
                "semantic": {
                    "commit": {
                        "message": facts.message,
                    },
                },
            },
        },
        metadata={
            "source": observation.source_platform,
            "gateway": observation.source_adapter,
            "source_observation_id": observation.observation_id,
        },
    )
