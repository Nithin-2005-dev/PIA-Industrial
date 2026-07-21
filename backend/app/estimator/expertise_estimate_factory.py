from datetime import datetime

from app.domain.entity_ref import EntityRef
from app.domain.expertise_estimate import ExpertiseEstimate


class ExpertiseEstimateFactory:

    @staticmethod
    def create(
        developer_ref: EntityRef,
        module_ref: EntityRef,
        current_time: datetime,
    ) -> ExpertiseEstimate:

        return ExpertiseEstimate(
            developer_ref=developer_ref,
            module_ref=module_ref,
            raw_score=0.0,
            confidence=0.0,
            updated_at=current_time,
        )