from .forecast_pipeline_service import (
    ForecastPipelineService,
)

from .forecast_severity_service import (
    ForecastSeverityService,
)

from .future_risk_service import (
    FutureRiskService,
)


class FutureRiskPipelineService:

    def __init__(
        self,
        forecast_pipeline_service: ForecastPipelineService,
    ):
        self._forecast_pipeline = (
            forecast_pipeline_service
        )

        self._future_risk_service = (
            FutureRiskService()
        )

        self._severity_service = (
            ForecastSeverityService()
        )

    def risks(
        self,
        horizon: int,
    ):

        forecasts = (
            self._forecast_pipeline
            .forecasts(
                horizon
            )
        )

        return (
            self._future_risk_service
            .analyze(
                forecasts
            )
        )

    def ranking(
        self,
        horizon: int,
        limit: int = 10,
    ):

        forecasts = (
            self._forecast_pipeline
            .forecasts(
                horizon
            )
        )

        return (
            self._future_risk_service
            .ranking(
                forecasts,
                limit,
            )
        )

    def severities(
        self,
        horizon: int,
    ):

        forecasts = (
            self._forecast_pipeline
            .forecasts(
                horizon
            )
        )

        return (
            self._severity_service
            .analyze(
                forecasts
            )
        )

    def severity_ranking(
        self,
        horizon: int,
        limit: int = 10,
    ):

        forecasts = (
            self._forecast_pipeline
            .forecasts(
                horizon
            )
        )

        return (
            self._severity_service
            .ranking(
                forecasts,
                limit,
            )
        )
