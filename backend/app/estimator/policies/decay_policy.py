from abc import ABC, abstractmethod
from datetime import datetime


class DecayPolicy(ABC):
    """
    Controls how expertise changes
    as time passes.
    """

    @abstractmethod
    def apply(
        self,
        score: float,
        last_updated: datetime,
        current_time: datetime,
    ) -> float:
        pass