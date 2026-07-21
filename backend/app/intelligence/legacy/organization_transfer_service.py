from .organization_transfer import (
    OrganizationTransfer,
)


class OrganizationTransferService:

    def __init__(
        self,
        intelligence_context,
    ):
        self._intelligence = (
            intelligence_context
        )

    def top_opportunities(
        self,
        limit: int = 10,
    ):

        estimates = (
            self._intelligence
            .projection
            .all_estimates()
        )

        ownerships = []

        module_ids = {
            estimate.module_ref.id
            for estimate in estimates
        }

        for module_id in module_ids:

            ownerships.extend(
                self._intelligence
                .ownership_service
                .owners_of(
                    module_id
                )
            )

        concentration_reports = (
            self._intelligence
            .concentration_service
            .analyze(
                estimates
            )
        )

        successors = []

        for module_id in module_ids:

            recommendations = (
                self._intelligence
                .successor_service
                .recommend(
                    module_id,
                    limit=3,
                )
            )

            successors.extend(
                recommendations
            )

        plans = (
            self._intelligence
            .transfer_service
            .plans(
                ownerships,
                successors,
                concentration_reports,
            )
        )

        plans.sort(
            key=lambda plan: (
                plan.priority_score
            ),
            reverse=True,
        )

        return [
            OrganizationTransfer(
                module_ref=(
                    plan.module_ref
                ),
                mentor_ref=(
                    plan.mentor_ref
                ),
                learner_ref=(
                    plan.learner_ref
                ),
                priority_score=(
                    plan.priority_score
                ),
                rank=index + 1,
            )
            for index, plan in enumerate(
                plans[:limit]
            )
        ]