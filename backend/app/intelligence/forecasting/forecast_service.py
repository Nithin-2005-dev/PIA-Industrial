from .forecast_risk import (
    ForecastRisk,
)


class ForecastService:

    def __init__(
        self,
        policy,
    ):
        self._policy = policy

    def forecast_all(
        self,
        trends,
        horizon: int,
    ):

        return [

            self._policy.forecast(
                trend,
                horizon,
            )

            for trend in trends
        ]

    def rank(
        self,
        trends,
        horizon: int,
        limit: int = 10,
    ):

        forecasts = (
            self.forecast_all(
                trends,
                horizon,
            )
        )

        forecasts.sort(
            key=lambda forecast: (
                forecast.predicted_health
            )
        )

        return [

            ForecastRisk(
                forecast=forecast,
                rank=index + 1,
            )

            for index, forecast in enumerate(
                forecasts[:limit]
            )
        ]