from collections import defaultdict

from app.intelligence.measurement.domain import Measurement


class TemporalMeasurementStore:

    def __init__(
        self,
    ):
        self._measurements = defaultdict(list)

    def append(
        self,
        measurement: Measurement,
    ):
        key = (
            measurement.definition.id,
            tuple(
                measurement.provenance.source_entity_ids
            ),
        )

        self._measurements[key].append(
            measurement
        )

        self._measurements[key].sort(
            key=lambda item: item.timestamp
        )

    def history(
        self,
        definition_id: str,
        entity_ids: tuple[str, ...],
    ) -> list[Measurement]:
        return list(
            self._measurements.get(
                (
                    definition_id,
                    entity_ids,
                ),
                [],
            )
        )


class MeasurementCache:

    def __init__(
        self,
    ):
        self.hot = {}
        self.derived = {}
        self.historical = {}
        self.persistent = {}

    def get(
        self,
        measurement_id: str,
    ):
        for tier in (
            self.hot,
            self.derived,
            self.historical,
            self.persistent,
        ):
            if measurement_id in tier:
                return tier[
                    measurement_id
                ]

        return None

    def put_hot(
        self,
        measurement: Measurement,
    ):
        self.hot[
            measurement.id
        ] = measurement

    def put_derived(
        self,
        measurement: Measurement,
    ):
        self.derived[
            measurement.id
        ] = measurement


