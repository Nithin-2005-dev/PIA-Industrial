from dataclasses import dataclass

from app.domain.entity_ref import EntityRef

from .ownership_level import OwnershipLevel


@dataclass(frozen=True)
class OwnershipEstimate:
    """
    Estimated ownership relationship
    between a developer and a module.
    """

    owner_ref: EntityRef

    module_ref: EntityRef

    ownership_percentage: float

    effective_score: float

    ownership_level: OwnershipLevel