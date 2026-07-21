from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class OrganizationReadiness:

    module_ref: EntityRef

    readiness_score: float

    rank: int