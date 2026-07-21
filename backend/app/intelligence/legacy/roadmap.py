from dataclasses import dataclass

from .quarter_plan import (
    QuarterPlan,
)

from .executive_recommendation import (
    ExecutiveRecommendation,
)


@dataclass(frozen=True)
class Roadmap:
    """
    Strategic roadmap for leadership.
    """

    quarter_plans: list[QuarterPlan]

    recommendations: list[
        ExecutiveRecommendation
    ]

    executive_summary: str