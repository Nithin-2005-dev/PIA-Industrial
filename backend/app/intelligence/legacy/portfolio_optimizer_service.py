from .portfolio_item import (
    PortfolioItem,
)


class PortfolioOptimizerService:

    def optimize(
        self,
        interventions,
        costs,
        limit: int = 10,
    ):

        items = []

        for intervention in interventions:

            cost = next(
                (
                    item
                    for item in costs
                    if (
                        item.action
                        ==
                        intervention.action
                    )
                ),
                None,
            )

            if cost is None:
                continue

            roi = (
                intervention.expected_health_gain
                /
                cost.estimated_cost
            )

            items.append(
                PortfolioItem(
                    module_ref=(
                        intervention.module_ref
                    ),
                    action=(
                        intervention.action
                    ),
                    expected_health_gain=(
                        intervention
                        .expected_health_gain
                    ),
                    estimated_cost=(
                        cost.estimated_cost
                    ),
                    roi=roi,
                    rank=0,
                )
            )

        items.sort(
            key=lambda item: (
                item.roi
            ),
            reverse=True,
        )

        return [
            PortfolioItem(
                module_ref=item.module_ref,
                action=item.action,
                expected_health_gain=(
                    item.expected_health_gain
                ),
                estimated_cost=(
                    item.estimated_cost
                ),
                roi=item.roi,
                rank=index + 1,
            )
            for index, item in enumerate(
                items[:limit]
            )
        ]