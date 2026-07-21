from abc import ABC
from abc import abstractmethod

from .forecast import Forecast


class ForecastPolicy(
    ABC
):

    @abstractmethod
    def forecast(
        self,
        trend,
        horizon: int,
    ) -> Forecast:
        pass