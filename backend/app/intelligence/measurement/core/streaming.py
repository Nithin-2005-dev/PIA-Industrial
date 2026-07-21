from collections.abc import Callable
from dataclasses import dataclass

from app.intelligence.measurement.core.engine import MeasurementEngine
from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementContext
from app.ingestion.observation.domain import Observation
from app.ingestion.observation.integration import event_to_observation


@dataclass(frozen=True)
class MeasurementUpdate:
    observation_id: str
    measurements: tuple[Measurement, ...]

    @property
    def event_id(
        self,
    ) -> str:
        return self.observation_id


class StreamingMeasurementEngine:

    def __init__(
        self,
        engine: MeasurementEngine,
    ):
        self._engine = engine
        self._subscribers: list[
            Callable[[MeasurementUpdate], None]
        ] = []

    def subscribe(
        self,
        subscriber: Callable[[MeasurementUpdate], None],
    ):
        self._subscribers.append(
            subscriber
        )

    def ingest(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> MeasurementUpdate:
        if not isinstance(
            observation,
            Observation,
        ):
            observation = event_to_observation(
                observation
            )

        measurements = tuple(
            self._engine.measure_observation(
                observation,
                context,
            )
        )

        update = MeasurementUpdate(
            observation_id=observation.observation_id,
            measurements=measurements,
        )

        for subscriber in self._subscribers:
            subscriber(
                update
            )

        return update

    def ingest_event(
        self,
        event,
        context: MeasurementContext,
    ) -> MeasurementUpdate:
        return self.ingest(
            event_to_observation(
                event
            ),
            context,
        )
