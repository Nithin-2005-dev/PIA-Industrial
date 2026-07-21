from dataclasses import dataclass
from app.domain.entity_ref import EntityRef

@dataclass(frozen=True)
class ReviewerRecommendation:
    """
    Recommendation produced by PIA
    for reviewing a change set.
    """

    reviewer_ref: EntityRef

    score: float

    covered_files: int