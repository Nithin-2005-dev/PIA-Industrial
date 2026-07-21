from app.history.history_service import (
    HistoryService,
)

from .forecast_service import (
    ForecastService,
)


class ForecastPipelineService:

    def __init__(
        self,
        history_service: HistoryService,
        forecast_service: ForecastService,
    ):
        self._history_service = history_service

        self._forecast_service = (
            forecast_service
        )

    def forecasts(
        self,
        horizon: int,
    ):

        trends = (
            self._history_service
            .trends()
        )

        return (
            self._forecast_service
            .forecast_all(
                trends,
                horizon,
            )
        )

    def ranking(
        self,
        horizon: int,
        limit: int = 10,
    ):

        trends = (
            self._history_service
            .trends()
        )

        return (
            self._forecast_service
            .rank(
                trends,
                horizon,
                limit,
            )
        )
