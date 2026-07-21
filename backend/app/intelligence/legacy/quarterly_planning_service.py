from .quarter_plan import (
    QuarterPlan,
)


class QuarterlyPlanningService:

    def create_plan(
        self,
        portfolio_items,
        capacity_per_quarter: int = 2,
    ):

        plans = []

        quarter = 1

        for index in range(
            0,
            len(portfolio_items),
            capacity_per_quarter,
        ):

            batch = (
                portfolio_items[
                    index:
                    index
                    + capacity_per_quarter
                ]
            )

            total_gain = sum(
                item.expected_health_gain
                for item in batch
            )

            total_cost = sum(
                item.estimated_cost
                for item in batch
            )

            plans.append(
                QuarterPlan(
                    quarter=quarter,
                    items=batch,
                    total_expected_gain=(
                        total_gain
                    ),
                    total_cost=(
                        total_cost
                    ),
                )
            )

            quarter += 1

        return plans