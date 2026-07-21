from app.intelligence.legacy.ownership_service import (
    OwnershipService,
)

from .policies.successor_policy import (
    SuccessorPolicy,
)


class SuccessorService:

    def __init__(
        self,
        ownership_service: OwnershipService,
        policy: SuccessorPolicy,
    ):
        self._ownership_service = (
            ownership_service
        )

        self._policy = policy

    def recommend(
        self,
        module_id: str,
        limit: int = 3,
    ):

        ownership = (
            self._ownership_service
            .owners_of(module_id)
        )

        return (
            self._policy.recommend(
                ownership,
                limit,
            )
        )