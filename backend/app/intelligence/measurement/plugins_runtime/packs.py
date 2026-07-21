from dataclasses import dataclass

from app.intelligence.measurement.domain import MeasurementDefinition


@dataclass(frozen=True)
class MeasurementPack:
    id: str
    name: str
    domain: str
    version: str
    definitions: tuple[MeasurementDefinition, ...]
    enabled_by_default: bool = False


class MeasurementMarketplace:

    def __init__(
        self,
    ):
        self._packs = {}
        self._tenant_installs = {}

    def publish(
        self,
        pack: MeasurementPack,
    ):
        self._packs[
            pack.id
        ] = pack

    def install(
        self,
        tenant_id: str,
        pack_id: str,
    ):
        if pack_id not in self._packs:
            raise KeyError(
                "unknown measurement pack"
            )

        self._tenant_installs.setdefault(
            tenant_id,
            set(),
        ).add(
            pack_id
        )

    def installed(
        self,
        tenant_id: str,
    ) -> list[MeasurementPack]:
        return [
            self._packs[
                pack_id
            ]
            for pack_id in self._tenant_installs.get(
                tenant_id,
                set(),
            )
        ]


