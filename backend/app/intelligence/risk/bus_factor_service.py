from app.intelligence.legacy.ownership_service import (
    OwnershipService,
)

from .bus_factor import BusFactor

from .policies.bus_factor_policy import (
    BusFactorPolicy,
)


class BusFactorService:

    def __init__(
        self,
        ownership_service: OwnershipService,
        policy: BusFactorPolicy,
    ):
        self._ownership_service = (
            ownership_service
        )

        self._policy = policy

    def analyze(
        self,
        module_id: str,
    ) -> BusFactor:

        ownership = (
            self._ownership_service
            .owners_of(module_id)
        )

        return (
            self._policy.calculate(
                ownership
            )
        )