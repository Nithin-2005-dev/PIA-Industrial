from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.domain.evidence import Evidence

from .estimation_context import EstimationContext

T = TypeVar("T")


class LatentStateEstimator(ABC, Generic[T]):
    """
    Generic interface for latent state estimation.

    Transforms:
        Current Estimate + Evidence + Context

    into:
        New Estimate
    """

    @abstractmethod
    def estimate(
        self,
        current: T,
        evidence: Evidence,
        context: EstimationContext,
    ) -> T:
        pass