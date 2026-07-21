from collections.abc import Callable
from dataclasses import dataclass

from app.knowledge.evidence.core import EvidenceContext
from app.knowledge.evidence.core import EvidencePackage
from app.knowledge.evidence.synthesis import EvidenceSynthesisEngine
from app.intelligence.measurement.domain import Measurement


@dataclass(frozen=True)
class EvidenceUpdate:
    tenant_id: str | None
    package: EvidencePackage
    replay_sequence: int
    recomputed_measurement_ids: tuple[str, ...]


class StreamingEvidenceEngine:

    def __init__(
        self,
        engine: EvidenceSynthesisEngine,
    ):
        self._engine = engine
        self._subscribers: list[
            Callable[[EvidenceUpdate], None]
        ] = []
        self._measurements: dict[str, Measurement] = {}
        self._sequence = 0

    def subscribe(
        self,
        subscriber: Callable[[EvidenceUpdate], None],
    ) -> None:
        self._subscribers.append(
            subscriber
        )

    def ingest(
        self,
        measurements: tuple[Measurement, ...],
        context: EvidenceContext,
    ) -> EvidenceUpdate:
        for measurement in measurements:
            self._measurements[
                measurement.id
            ] = measurement

        self._sequence += 1
        package = self._engine.synthesize(
            list(
                self._measurements.values()
            ),
            context,
        )
        update = EvidenceUpdate(
            tenant_id=context.tenant_id,
            package=package,
            replay_sequence=self._sequence,
            recomputed_measurement_ids=tuple(
                measurement.id
                for measurement in measurements
            ),
        )

        for subscriber in self._subscribers:
            subscriber(
                update
            )

        return update

    def replay(
        self,
        context: EvidenceContext,
    ) -> EvidenceUpdate:
        return self.ingest(
            (),
            context,
        )

