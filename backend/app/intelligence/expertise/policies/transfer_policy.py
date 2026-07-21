from abc import ABC, abstractmethod

from app.intelligence.expertise.transfer_plan import (
    TransferPlan,
)


class TransferPolicy(
    ABC
):

    @abstractmethod
    def recommend(
        self,
        ownerships,
        successors,
        concentration_reports,
    ) -> list[TransferPlan]:
        pass