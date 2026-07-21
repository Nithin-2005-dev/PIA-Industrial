from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class Intervention:
    """
    Recommended organizational action.
    """

    module_ref: EntityRef

    action: str

    priority: float

    reason: str