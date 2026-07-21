from app.intelligence.expertise.transfer_plan import (
    TransferPlan,
)

from ..simple_priority_policy import (
    SimplePriorityPolicy,
)

from .transfer_policy import (
    TransferPolicy,
)


class SimpleTransferPolicy(
    TransferPolicy
):

    def __init__(self):

        self._priority_policy = (
            SimplePriorityPolicy()
        )

    def recommend(
        self,
        ownerships,
        successors,
        concentration_reports,
    ):

        ownership_by_module = {}

        for ownership in ownerships:

            module_id = (
                ownership.module_ref.id
            )

            existing = (
                ownership_by_module.get(
                    module_id
                )
            )

            if (
                existing is None
                or
                ownership.ownership_percentage
                >
                existing.ownership_percentage
            ):
                ownership_by_module[
                    module_id
                ] = ownership

        successor_by_module = {}

        for successor in successors:

            module_id = (
                successor.module_ref.id
            )

            if (
                module_id
                not in successor_by_module
            ):
                successor_by_module[
                    module_id
                ] = successor

        plans = []

        for report in (
            concentration_reports
        ):

            if (
                report.concentration_level
                != "HIGH"
            ):
                continue

            module_id = (
                report.module_ref.id
            )

            owner = (
                ownership_by_module.get(
                    module_id
                )
            )

            successor = (
                successor_by_module.get(
                    module_id
                )
            )

            if (
                owner is None
                or successor is None
            ):
                continue

            bus_factor = 1

            priority = (
                self._priority_policy.score(
                    report.concentration_score,
                    bus_factor,
                )
            )

            plans.append(
                TransferPlan(
                    module_ref=(
                        report.module_ref
                    ),
                    mentor_ref=(
                        owner.owner_ref
                    ),
                    learner_ref=(
                        successor
                        .developer_ref
                    ),
                    priority_score=(
                        priority
                    ),
                    reason=(
                        "High concentration risk"
                    ),
                    bus_factor=(
                        bus_factor
                    ),
                    concentration_score=(
                        report.concentration_score
                    ),
                )
            )

        plans.sort(
            key=lambda plan: (
                plan.priority_score
            ),
            reverse=True,
        )

        return plans