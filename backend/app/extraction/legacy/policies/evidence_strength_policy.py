from abc import ABC, abstractmethod

from app.domain.event import Event


class EvidenceStrengthPolicy(ABC):
    """
    Computes contribution magnitude
    from an observed Event.
    """

    @abstractmethod
    def strength(
        self,
        event: Event,
    ) -> float:
        pass