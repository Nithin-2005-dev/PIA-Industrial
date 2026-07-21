from abc import ABC, abstractmethod

from app.intelligence.legacy.ownership_estimate import (
    OwnershipEstimate,
)

from app.intelligence.legacy.successor_candidate import (
    SuccessorCandidate,
)


class SuccessorPolicy(ABC):

    @abstractmethod
    def recommend(
        self,
        ownership: list[OwnershipEstimate],
        limit: int,
    ) -> list[SuccessorCandidate]:
        pass