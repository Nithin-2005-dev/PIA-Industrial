from dataclasses import dataclass

from app.domain.expertise_estimate import (
    ExpertiseEstimate,
)


@dataclass(frozen=True)
class QueryResult:
    """
    Result returned by query services.

    effective_score is a ranking score
    derived from expertise magnitude
    and confidence.
    """

    estimate: ExpertiseEstimate

    effective_score: float