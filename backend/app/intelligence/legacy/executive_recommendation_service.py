from .executive_recommendation import (
    ExecutiveRecommendation,
)


class ExecutiveRecommendationService:

    def recommend(
        self,
        portfolio_items,
        limit: int = 10,
    ):

        recommendations = []

        for index, item in enumerate(
            portfolio_items[:limit],
            start=1,
        ):

            reason = (
                f"Highest ROI intervention "
                f"for {item.module_ref.id}"
            )

            recommendations.append(
                ExecutiveRecommendation(
                    module_ref=(
                        item.module_ref
                    ),
                    action=(
                        item.action
                    ),
                    reason=reason,
                    expected_health_gain=(
                        item.expected_health_gain
                    ),
                    estimated_cost=(
                        item.estimated_cost
                    ),
                    roi=item.roi,
                    priority=index,
                )
            )

        return recommendations