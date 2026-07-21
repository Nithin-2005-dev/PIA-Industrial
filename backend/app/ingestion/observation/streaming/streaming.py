from collections.abc import Callable
from dataclasses import dataclass

from app.ingestion.observation.domain import Observation
from app.ingestion.observation.storage import ObservationStore


@dataclass(frozen=True)
class ObservationUpdate:
    sequence: int
    observations: tuple[Observation, ...]
    offset: int


class ObservationStream:

    def __init__(
        self,
        store: ObservationStore,
    ):
        self._store = store
        self._subscribers: list[
            Callable[[ObservationUpdate], None]
        ] = []
        self._sequence = 0

    def subscribe(
        self,
        subscriber: Callable[[ObservationUpdate], None],
    ) -> None:
        self._subscribers.append(
            subscriber
        )

    def publish(
        self,
        observations: tuple[Observation, ...],
    ) -> ObservationUpdate:
        offset = len(
            self._store.replay()
        )
        self._store.append_batch(
            observations
        )
        self._sequence += 1
        update = ObservationUpdate(
            sequence=self._sequence,
            observations=observations,
            offset=offset,
        )
        for subscriber in self._subscribers:
            subscriber(
                update
            )
        return update
