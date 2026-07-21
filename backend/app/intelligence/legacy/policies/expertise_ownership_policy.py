from app.intelligence.legacy.ownership_estimate import (
    OwnershipEstimate,
)

from app.intelligence.legacy.ownership_level import (
    OwnershipLevel,
)

from app.query.query_result import QueryResult

from .ownership_policy import (
    OwnershipPolicy,
)


class ExpertiseOwnershipPolicy(
    OwnershipPolicy
):

    def calculate(
        self,
        experts: list[QueryResult],
    ) -> list[OwnershipEstimate]:

        import math

        if not experts:
            return []

        # Use log normalization to prevent winner-takes-all collapsing
        total_score = sum(
            math.log1p(max(0, expert.effective_score))
            for expert in experts
        )

        if total_score == 0:
            return []

        ownership = []

        for expert in experts:

            ownership_percentage = (
                math.log1p(max(0, expert.effective_score))
                / total_score
            )

            # Softer thresholds due to log smoothing
            if ownership_percentage >= 0.40:
                level = OwnershipLevel.PRIMARY
            elif ownership_percentage >= 0.15:
                level = OwnershipLevel.SECONDARY
            else:
                level = OwnershipLevel.CONTRIBUTOR

            ownership.append(
                OwnershipEstimate(
                    owner_ref=(
                        expert.estimate
                        .developer_ref
                    ),
                    module_ref=(
                        expert.estimate
                        .module_ref
                    ),
                    ownership_percentage=(
                        ownership_percentage
                    ),
                    effective_score=(
                        expert.effective_score
                    ),
                    ownership_level=level,
                )
            )

        ownership.sort(
            key=lambda estimate: (
                estimate.ownership_percentage
            ),
            reverse=True,
        )

        return ownership