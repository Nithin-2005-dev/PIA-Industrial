from dataclasses import dataclass

from app.domain.entity_ref import EntityRef


@dataclass(frozen=True)
class SuccessorCandidate:
    """
    Recommended future owner
    for a module.
    """

    developer_ref: EntityRef

    module_ref: EntityRef

    score: float

    rank: int