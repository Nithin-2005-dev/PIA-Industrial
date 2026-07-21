from app.query.expertise_query_service import (
    ExpertiseQueryService,
)

from .ownership_estimate import (
    OwnershipEstimate,
)

from .policies.ownership_policy import (
    OwnershipPolicy,
)


class OwnershipService:

    def __init__(
        self,
        query_service: ExpertiseQueryService,
        policy: OwnershipPolicy,
    ):
        self._query_service = query_service
        self._policy = policy

    def owners_of(
        self,
        module_id: str,
    ) -> list[OwnershipEstimate]:

        experts = (
            self._query_service
            .module_experts(
                module_id
            )
        )

        return (
            self._policy.calculate(
                experts
            )
        )