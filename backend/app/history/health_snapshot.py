from dataclasses import dataclass
from datetime import datetime

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class HealthSnapshot:
    """
    Health score at a point in time.
    """

    module_ref: EntityRef

    health_score: float

    recorded_at: datetime