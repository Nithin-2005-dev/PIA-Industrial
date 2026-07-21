from dataclasses import dataclass

from app.knowledge.evidence.knowledge import EvidenceDefinition


@dataclass(frozen=True)
class EvidencePack:
    id: str
    name: str
    domain: str
    version: str
    definitions: tuple[EvidenceDefinition, ...]


class EvidencePluginRegistry:

    def __init__(
        self,
    ):
        self._packs: dict[str, EvidencePack] = {}
        self._tenant_installs: dict[str, set[str]] = {}

    def publish(
        self,
        pack: EvidencePack,
    ) -> None:
        self._packs[
            pack.id
        ] = pack

    def install(
        self,
        tenant_id: str,
        pack_id: str,
    ) -> None:
        if pack_id not in self._packs:
            raise KeyError(
                pack_id
            )
        self._tenant_installs.setdefault(
            tenant_id,
            set(),
        ).add(
            pack_id
        )

    def installed_definitions(
        self,
        tenant_id: str,
    ) -> tuple[EvidenceDefinition, ...]:
        definitions = []
        for pack_id in self._tenant_installs.get(
            tenant_id,
            set(),
        ):
            definitions.extend(
                self._packs[
                    pack_id
                ].definitions
            )
        return tuple(
            definitions
        )

