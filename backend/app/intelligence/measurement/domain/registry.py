from dataclasses import dataclass

from app.intelligence.measurement.domain import MeasurementDefinition
from app.intelligence.measurement.core.interfaces import MeasurementEvaluator


@dataclass(frozen=True)
class RegistryLookup:
    definition: MeasurementDefinition
    latest: bool


class MeasurementRegistry:

    def __init__(
        self,
    ):
        self._definitions: dict[
            tuple[str, str],
            MeasurementDefinition,
        ] = {}
        self._latest_versions: dict[str, str] = {}
        self._evaluators: dict[str, MeasurementEvaluator] = {}

    def register(
        self,
        definition: MeasurementDefinition,
    ):
        key = (
            definition.id,
            definition.version,
        )

        if key in self._definitions:
            raise ValueError(
                "measurement definition version already registered"
            )

        self._definitions[key] = definition

        current_latest = self._latest_versions.get(
            definition.id
        )

        if (
            current_latest is None
            or definition.version > current_latest
        ):
            self._latest_versions[
                definition.id
            ] = definition.version

    def get(
        self,
        definition_id: str,
        version: str | None = None,
    ) -> MeasurementDefinition:
        if version is None:
            version = self._latest_versions[
                definition_id
            ]

        return self._definitions[
            (
                definition_id,
                version,
            )
        ]

    def lookup(
        self,
        definition_id: str,
        version: str | None = None,
    ) -> RegistryLookup:
        definition = self.get(
            definition_id,
            version,
        )

        return RegistryLookup(
            definition=definition,
            latest=(
                self._latest_versions[
                    definition_id
                ]
                == definition.version
            ),
        )

    def by_concept(
        self,
        concept_id: str,
    ) -> list[MeasurementDefinition]:
        return [
            definition
            for definition in self._definitions.values()
            if definition.concept_id == concept_id
        ]

    def all(
        self,
    ) -> list[MeasurementDefinition]:
        return list(
            self._definitions.values()
        )

    def register_evaluator(
        self,
        evaluator: MeasurementEvaluator,
    ) -> None:
        self._evaluators[evaluator.metric_name] = evaluator

    def get_active_evaluators(
        self,
    ) -> list[MeasurementEvaluator]:
        return list(self._evaluators.values())


