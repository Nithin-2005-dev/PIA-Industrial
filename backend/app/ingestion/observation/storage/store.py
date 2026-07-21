from app.ingestion.observation.domain import Observation


class ObservationStore:

    def __init__(
        self,
    ):
        self._observations: list[Observation] = []
        self._ids: set[str] = set()

    def append(
        self,
        observation: Observation,
    ) -> None:
        if observation.observation_id in self._ids:
            raise ValueError(
                "observation already exists"
            )
        self._observations.append(
            observation
        )
        self._ids.add(
            observation.observation_id
        )

    def append_batch(
        self,
        observations: tuple[Observation, ...],
    ) -> None:
        for observation in observations:
            self.append(
                observation
            )

    def replay(
        self,
    ) -> tuple[Observation, ...]:
        return tuple(
            self._observations
        )

    def history(
        self,
        correlation_id: str | None = None,
    ) -> tuple[Observation, ...]:
        if correlation_id is None:
            return self.replay()
        return tuple(
            observation
            for observation in self._observations
            if observation.correlation_id == correlation_id
        )

    def since(
        self,
        offset: int,
    ) -> tuple[Observation, ...]:
        return tuple(
            self._observations[
                offset:
            ]
        )
