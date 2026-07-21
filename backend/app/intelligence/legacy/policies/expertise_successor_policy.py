from app.intelligence.legacy.successor_candidate import (
    SuccessorCandidate,
)

from .successor_policy import (
    SuccessorPolicy,
)


class ExpertiseSuccessorPolicy(
    SuccessorPolicy
):

    def recommend(
        self,
        ownership,
        limit: int,
    ):

        if not ownership:
            return []

        sorted_owners = sorted(
            ownership,
            key=lambda owner: (
                owner.ownership_percentage
            ),
            reverse=True,
        )

        remaining_owners = (
            sorted_owners[1:]
        )

        candidates = []

        for rank, owner in enumerate(
            remaining_owners,
            start=1,
        ):

            candidates.append(
                SuccessorCandidate(
                    developer_ref=(
                        owner.owner_ref
                    ),
                    module_ref=(
                        owner.module_ref
                    ),
                    score=(
                        owner.effective_score
                    ),
                    rank=rank,
                )
            )

        return candidates[:limit]