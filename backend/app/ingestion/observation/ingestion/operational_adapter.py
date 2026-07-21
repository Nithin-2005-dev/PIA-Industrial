import uuid
from typing import Iterator
from datetime import datetime

from app.infrastructure.ports.event_source_port import ObservationSourcePort
from app.infrastructure.ports.event_query import EventQuery
from app.ingestion.observation.domain import (
    Observation, ObservationType, ObservationCategory,
    ObservationLifecycle, ObservationProvenance, ObservationContext,
    CommitFacts, FileChangeFacts, ProcessingMode
)
from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.infrastructure.database.sqlite_provider import get_provider
from app.infrastructure.database.models import CommitRecord, DeveloperRecord


class OperationalStoreAdapter(ObservationSourcePort):
    """
    Translates canonical records from the Operational Store back into
    Observation objects for the Platform Runtime.
    """

    def __init__(self, provider=None):
        self._provider = provider or get_provider()

    def is_circuit_open(self) -> bool:
        return False

    def collect(self, query: EventQuery) -> Iterator[Observation]:
        workspace_id = query.identifier
        
        # Load all developers for author resolution
        devs = self._provider.query(DeveloperRecord, limit=10000)
        dev_map = {d.email: d for d in devs if d.email}
        
        since_sha = query.filters.get("since_sha") if query.filters else None
        commits = self._provider.query(CommitRecord, limit=1000)
        commits.sort(key=lambda c: c.timestamp or "", reverse=True)
        
        if since_sha:
            filtered = []
            for c in commits:
                if c.sha == since_sha:
                    break
                filtered.append(c)
            commits = filtered
        
        for commit in commits:
            try:
                if commit.timestamp:
                    if commit.timestamp.endswith("Z"):
                        dt_str = commit.timestamp[:-1] + "+00:00"
                    else:
                        dt_str = commit.timestamp
                    ts = datetime.fromisoformat(dt_str)
                else:
                    ts = datetime.utcnow()
            except ValueError:
                ts = datetime.utcnow()
            
            author_id = dev_map.get(commit.author_email, None)
            actor_id = author_id.object_id if author_id else commit.author_email
            
            actors = (EntityRef(id=actor_id, type=EntityType.DEVELOPER),)
            targets = (EntityRef(id=commit.sha, type=EntityType.REPOSITORY),)
            
            facts = CommitFacts(
                commit_id=commit.sha,
                message=commit.message,
                author_name=commit.author_name,
                author_email=commit.author_email,
                authored_at=ts,
                total_additions=commit.additions,
                total_deletions=commit.deletions,
                total_changes=commit.additions + commit.deletions,
                files=() # DB doesn't currently link files cleanly to commits in SQLite without join
            )
            
            obs_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"obs:{commit.object_id}"))
            trace_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"trace:{commit.object_id}"))
            
            yield Observation(
                observation_id=obs_id,
                trace_id=trace_id,
                correlation_id=commit.object_id,
                timestamp=ts,
                observation_type=ObservationType.COMMIT,
                observation_category=ObservationCategory.SOURCE_CONTROL,
                source_platform="operational_store",
                source_adapter="operational_store_adapter",
                version="1.0",
                lifecycle=ObservationLifecycle.VALIDATED,
                actors=actors,
                targets=targets,
                provenance=ObservationProvenance(
                    source_platform="operational_store",
                    source_adapter="operational_store",
                    source_record_id=commit.object_id,
                    fetched_at=datetime.utcnow()
                ),
                context=ObservationContext(
                    repository=workspace_id,
                    branch="main", # Or pass from query
                ),
                facts=facts,
                processing_mode=ProcessingMode.REPLAY
            )

    def collect_events(self, query: EventQuery):
        from app.ingestion.observation.integration import observation_to_event
        return [observation_to_event(obs) for obs in self.collect(query)]

class OperationalStoreAdapterFactory:
    def create(self, token: str = "") -> OperationalStoreAdapter:
        return OperationalStoreAdapter()
