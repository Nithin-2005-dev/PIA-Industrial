from abc import ABC, abstractmethod


class TransferPriorityPolicy(
    ABC
):

    @abstractmethod
    def score(
        self,
        concentration_score: float,
        bus_factor: int,
    ) -> float:
        pass