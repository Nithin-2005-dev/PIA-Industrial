from .transfer_priority_policy import (
    TransferPriorityPolicy,
)


class SimplePriorityPolicy(
    TransferPriorityPolicy
):

    def score(
        self,
        concentration_score: float,
        bus_factor: int,
    ) -> float:

        concentration_component = (
            concentration_score * 100
        )

        bus_factor_penalty = max(
            0,
            (3 - bus_factor) * 10,
        )

        return (
            concentration_component
            + bus_factor_penalty
        )