from dataclasses import dataclass
from datetime import datetime

from .entity_ref import EntityRef


@dataclass(frozen=True)
class ExpertiseEstimate:
    """
    Immutable snapshot representing the current estimated
    expertise relationship between a developer and a module.
    """

    developer_ref: EntityRef

    module_ref: EntityRef

    raw_score: float

    confidence: float

    updated_at: datetime