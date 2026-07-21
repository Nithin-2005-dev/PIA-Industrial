from app.ingestion.observation.core import ObservationPipeline
from app.ingestion.observation.domain import Observation


class ObservationApi:

    def __init__(
        self,
        pipeline: ObservationPipeline | None = None,
    ):
        self._pipeline = pipeline or ObservationPipeline()

    def ingest(
        self,
        observations: tuple[Observation, ...],
    ) -> tuple[Observation, ...]:
        return self._pipeline.process(
            observations
        )

    def replay(
        self,
    ) -> tuple[Observation, ...]:
        return self._pipeline.replay()

