from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class OrganizationTransfer:

    module_ref: EntityRef

    mentor_ref: EntityRef

    learner_ref: EntityRef

    priority_score: float

    rank: int