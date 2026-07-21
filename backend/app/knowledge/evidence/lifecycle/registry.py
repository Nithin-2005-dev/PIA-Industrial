from app.knowledge.evidence.domain import EvidenceLifecycle
from app.knowledge.evidence.knowledge import EvidenceDefinition


class VersionedEvidenceDefinitionRegistry:

    def __init__(
        self,
    ):
        self._definitions: dict[
            tuple[str, str],
            EvidenceDefinition,
        ] = {}

    def register(
        self,
        definition: EvidenceDefinition,
    ) -> None:
        version = definition.version_history[-1]
        self._definitions[
            (
                definition.id,
                version,
            )
        ] = definition

    def latest(
        self,
        definition_id: str,
    ) -> EvidenceDefinition:
        candidates = [
            definition
            for (
                current_id,
                _
            ), definition in self._definitions.items()
            if current_id == definition_id
            and definition.lifecycle
            not in {
                EvidenceLifecycle.DEPRECATED,
                EvidenceLifecycle.ARCHIVED,
            }
        ]
        if not candidates:
            raise KeyError(
                definition_id
            )
        return candidates[-1]

    def get(
        self,
        definition_id: str,
        version: str,
    ) -> EvidenceDefinition:
        return self._definitions[
            (
                definition_id,
                version,
            )
        ]

