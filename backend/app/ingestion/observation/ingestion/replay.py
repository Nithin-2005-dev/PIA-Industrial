from __future__ import annotations
import dataclasses

from app.ingestion.observation.domain import Observation, ProcessingMode
from app.ingestion.observation.ingestion.models import ReplayQuery
from app.ingestion.observation.ingestion.storage import ObservationIngestionStore


class ObservationReplayEngine:
    def __init__(
        self,
        store: ObservationIngestionStore,
    ):
        self._store = store

    def replay(
        self,
        query: ReplayQuery | None = None,
    ) -> tuple[Observation, ...]:
        query = query or ReplayQuery()
        results = []
        for observation in self._store.normalized():
            if query.repository and observation.context.repository != query.repository:
                continue
            if query.organization and observation.context.organization != query.organization:
                continue
            if query.adapter and observation.source_adapter != query.adapter:
                continue
            if query.start and observation.timestamp < query.start:
                continue
            if query.end and observation.timestamp > query.end:
                continue
            if query.developer:
                actor_ids = {
                    actor.id
                    for actor in observation.actors
                }
                if query.developer not in actor_ids:
                    continue
            
            # Explicitly mark as replay to prevent the Infinite Mirror vulnerability
            replayed_observation = dataclasses.replace(
                observation,
                processing_mode=ProcessingMode.REPLAY
            )
            results.append(replayed_observation)
        return tuple(results)

