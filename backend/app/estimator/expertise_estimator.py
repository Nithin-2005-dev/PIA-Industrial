from app.domain.evidence import Evidence
from app.domain.expertise_estimate import ExpertiseEstimate

from .latent_state_estimator import LatentStateEstimator
from .policies.evidence_scoring_policy import (
    EvidenceScoringPolicy,
)
from .policies.decay_policy import (
    DecayPolicy,
)
from .estimation_context import EstimationContext


class ExpertiseEstimator(
    LatentStateEstimator[ExpertiseEstimate]
):

    def __init__(
        self,
        scoring_policy: EvidenceScoringPolicy,
        decay_policy: DecayPolicy,
    ):
        self._scoring_policy = (
            scoring_policy
        )

        self._decay_policy = (
            decay_policy
        )

    def estimate(
        self,
        current: ExpertiseEstimate,
        evidence: Evidence,
        context: EstimationContext,
    ) -> ExpertiseEstimate:

        strength = evidence.metadata.get(
            "strength",
            1.0,
        )

        contribution = (
            self._scoring_policy.score(
                evidence
            )
            * strength
            * evidence.confidence
            * context.learning_rate
        )

        decayed_score = (
            self._decay_policy.apply(
                score=current.raw_score,
                last_updated=current.updated_at,
                current_time=context.current_time,
            )
        )

        new_score = (
            decayed_score
            + contribution
        )

        new_confidence = min(
            1.0,
            current.confidence
            + (
                evidence.confidence
                * 0.1
            ),
        )

        return ExpertiseEstimate(
            developer_ref=current.developer_ref,
            module_ref=current.module_ref,
            raw_score=new_score,
            confidence=new_confidence,
            updated_at=context.current_time,
        )