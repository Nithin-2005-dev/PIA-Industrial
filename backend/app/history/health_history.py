from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)

from .health_snapshot import (
    HealthSnapshot,
)


@dataclass(frozen=True)
class HealthHistory:
    """
    Historical health
    measurements for a module.
    """

    module_ref: EntityRef

    snapshots: list[HealthSnapshot]