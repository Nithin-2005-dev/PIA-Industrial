from dataclasses import dataclass
from enum import Enum

from app.intelligence.measurement.domain import MeasurementDefinition
from app.intelligence.measurement.domain import SoftwareSignal
from app.intelligence.measurement.domain.registry import MeasurementRegistry
from app.kernel.classifiers.signal_classifier import SignalClassification


class MappingCardinality(Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"


@dataclass(frozen=True)
class SignalMeasurementMapping:
    id: str
    version: str
    signal_ids: tuple[str, ...]
    concept_id: str
    measurement_definition_ids: tuple[str, ...]
    evaluator: str
    cardinality: MappingCardinality
    confidence: float
    explanation: str
    trace: tuple[str, ...]


class SignalMeasurementMappingRegistry:

    def __init__(
        self,
    ):
        self._mappings = {}

    def register(
        self,
        mapping: SignalMeasurementMapping,
    ):
        key = (
            mapping.id,
            mapping.version,
        )

        if key in self._mappings:
            raise ValueError(
                "mapping version already registered"
            )

        self._mappings[key] = mapping

    def for_signal(
        self,
        signal_id: str,
    ) -> list[SignalMeasurementMapping]:
        return [
            mapping
            for mapping in self._mappings.values()
            if signal_id in mapping.signal_ids
        ]

    def all(
        self,
    ) -> list[SignalMeasurementMapping]:
        return list(
            self._mappings.values()
        )


@dataclass(frozen=True)
class MappingResolution:
    signal: SoftwareSignal
    classification: SignalClassification
    mappings: tuple[SignalMeasurementMapping, ...]
    definitions: tuple[MeasurementDefinition, ...]
    explanation: str


class SignalToMeasurementMapper:

    def __init__(
        self,
        measurement_registry: MeasurementRegistry,
        mapping_registry: SignalMeasurementMappingRegistry,
    ):
        self._measurement_registry = measurement_registry
        self._mapping_registry = mapping_registry

    def resolve(
        self,
        signal: SoftwareSignal,
        classification: SignalClassification,
    ) -> MappingResolution:
        mappings = self._mapping_registry.for_signal(
            signal.id
        )

        if not mappings:
            mappings = tuple(
                self._infer_mappings(
                    signal,
                    classification,
                )
            )
        else:
            mappings = tuple(mappings)

        definitions = []

        for mapping in mappings:
            for definition_id in (
                mapping.measurement_definition_ids
            ):
                definitions.append(
                    self._measurement_registry.get(
                        definition_id
                    )
                )

        return MappingResolution(
            signal=signal,
            classification=classification,
            mappings=mappings,
            definitions=tuple(definitions),
            explanation=(
                "resolved signal to measurement definitions "
                "using registered or inferred mapping"
            ),
        )

    def _infer_mappings(
        self,
        signal: SoftwareSignal,
        classification: SignalClassification,
    ) -> list[SignalMeasurementMapping]:
        definitions = [
            definition
            for definition in self._measurement_registry.all()
            if (
                signal.name in definition.required_signals
                or signal.id in definition.required_signals
                or classification.category == definition.category
                or classification.category == definition.concept_id
            )
        ]

        return [
            SignalMeasurementMapping(
                id=f"inferred:{signal.id}:{definition.id}",
                version="1.0",
                signal_ids=(signal.id,),
                concept_id=definition.concept_id or "unknown",
                measurement_definition_ids=(definition.id,),
                evaluator="registry_resolved",
                cardinality=MappingCardinality.ONE_TO_ONE,
                confidence=classification.confidence,
                explanation=(
                    "inferred from required signals and classification"
                ),
                trace=(
                    "signal",
                    "classification",
                    "measurement_registry",
                ),
            )
            for definition in definitions
        ]


