from dataclasses import dataclass

from .portfolio_item import (
    PortfolioItem,
)


@dataclass(frozen=True)
class QuarterPlan:
    """
    Planned initiatives for a quarter.
    """

    quarter: int

    items: list[PortfolioItem]

    total_expected_gain: float

    total_cost: float