from app.ingestion.observation.domain import Observation
from app.ingestion.observation.registry import ObservationRegistry
from app.ingestion.observation.storage import ObservationStore
from app.ingestion.observation.validation import ObservationValidationPipeline
from app.ingestion.observation.validation import ObservationValidationStatus


class ObservationPipeline:

    def __init__(
        self,
        validator: ObservationValidationPipeline | None = None,
        registry: ObservationRegistry | None = None,
        store: ObservationStore | None = None,
    ):
        self._registry = registry or ObservationRegistry.default()
        self._validator = (
            validator
            or ObservationValidationPipeline(
                self._registry
            )
        )
        self._store = store or ObservationStore()

    def process(
        self,
        observations: tuple[Observation, ...],
    ) -> tuple[Observation, ...]:
        accepted = []
        for observation in observations:
            result = self._validator.validate(
                observation
            )
            if result.status == ObservationValidationStatus.FAILED:
                continue
            self._store.append(
                observation
            )
            accepted.append(
                observation
            )
        return tuple(
            accepted
        )

    def replay(
        self,
    ) -> tuple[Observation, ...]:
        return self._store.replay()
