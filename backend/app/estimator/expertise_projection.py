from app.domain.evidence import Evidence
from app.domain.expertise_estimate import ExpertiseEstimate

from .estimation_context import EstimationContext
from .expertise_estimate_factory import (
    ExpertiseEstimateFactory,
)
from .expertise_estimator import ExpertiseEstimator
from .expertise_key import ExpertiseKey


class ExpertiseProjection:

    def __init__(
        self,
        estimator: ExpertiseEstimator,
    ):
        self._estimator = estimator

        self._estimates: dict[
            ExpertiseKey,
            ExpertiseEstimate,
        ] = {}

    def apply(
        self,
        evidence: Evidence,
        context: EstimationContext,
    ) -> ExpertiseEstimate:

        key = ExpertiseKey(
            developer_id=evidence.subject_ref.id,
            module_id=evidence.object_ref.id,
        )

        current = self._estimates.get(key)

        if current is None:

            current = (
                ExpertiseEstimateFactory.create(
                    developer_ref=evidence.subject_ref,
                    module_ref=evidence.object_ref,
                    current_time=context.current_time,
                )
            )

        updated = self._estimator.estimate(
            current=current,
            evidence=evidence,
            context=context,
        )

        self._estimates[key] = updated

        return updated

    def all_estimates(
        self,
    ) -> list[ExpertiseEstimate]:

        return list(
            self._estimates.values()
        )