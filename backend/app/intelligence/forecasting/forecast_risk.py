from dataclasses import dataclass

from .forecast import Forecast


@dataclass(frozen=True)
class ForecastRisk:

    forecast: Forecast

    rank: int