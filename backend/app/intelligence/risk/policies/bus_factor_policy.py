from abc import ABC, abstractmethod

from app.intelligence.legacy.ownership_estimate import (
    OwnershipEstimate,
)

from app.intelligence.risk.bus_factor import (
    BusFactor,
)


class BusFactorPolicy(ABC):

    @abstractmethod
    def calculate(
        self,
        ownership: list[OwnershipEstimate],
    ) -> BusFactor:
        pass