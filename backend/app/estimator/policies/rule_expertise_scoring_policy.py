from app.domain.evidence import Evidence
from app.domain.predicate_type import PredicateType

from .evidence_scoring_policy import EvidenceScoringPolicy


class RuleExpertiseScoringPolicy(EvidenceScoringPolicy):

    _SCORES = {
        PredicateType.MODIFIED: 1.0,
        PredicateType.REVIEWED: 2.0,
        PredicateType.FIXED: 5.0,
        PredicateType.CREATED: 3.0,
        PredicateType.MERGED: 1.0,
        PredicateType.COMMENTED: 0.2,
        PredicateType.TOUCHED: 0.5,
    }

    def score(self, evidence: Evidence) -> float:
        return self._SCORES.get(evidence.predicate, 0.0)