from .policies.transfer_policy import (
    TransferPolicy,
)


class TransferService:

    def __init__(
        self,
        policy: TransferPolicy,
    ):
        self._policy = policy

    def plans(
        self,
        ownerships,
        successors,
        concentration_reports,
    ):

        return (
            self._policy.recommend(
                ownerships,
                successors,
                concentration_reports,
            )
        )