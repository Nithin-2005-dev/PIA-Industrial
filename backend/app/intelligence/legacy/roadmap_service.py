from .roadmap import (
    Roadmap,
)


class RoadmapService:

    def create(
        self,
        quarter_plans,
        recommendations,
    ):

        if not recommendations:

            summary = (
                "No recommendations available."
            )

        else:

            top = recommendations[0]

            q1_focus = "None"

            if quarter_plans:

                q1_focus = ", ".join(
                    item.action
                    for item
                    in quarter_plans[0].items
                )

            summary = (
                f"Top Priority: "
                f"{top.action}\n"
                f"Expected Gain: "
                f"{top.expected_health_gain:.2f}\n"
                f"Highest ROI: "
                f"{top.roi:.2f}\n"
                f"Q1 Focus: "
                f"{q1_focus}"
            )

        return Roadmap(
            quarter_plans=(
                quarter_plans
            ),
            recommendations=(
                recommendations
            ),
            executive_summary=(
                summary
            ),
        )