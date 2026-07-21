from app.intelligence.temporal.models import HistoricalContext
from .factory import TimeSeriesFactory
from .models import ForecastContext, ForecastModel, ForecastSeries


class ForecastRegistry:
    def __init__(self):
        self._models: list[ForecastModel] = []

    def register(self, model: ForecastModel) -> None:
        self._models.append(model)

    def get_model_for(self, metric_name: str) -> ForecastModel | None:
        """
        Returns the first registered model that supports the given metric name.
        Models registered earlier have higher priority.
        """
        for model in self._models:
            if model.supports(metric_name):
                return model
        return None


class ForecastEngine:
    def __init__(
        self,
        registry: ForecastRegistry,
        factory: type[TimeSeriesFactory] = TimeSeriesFactory,
    ):
        self._registry = registry
        self._factory = factory

    def build_forecast_context(
        self,
        history: HistoricalContext,
        horizons: tuple[int, ...] = (7, 30, 90),
    ) -> ForecastContext:
        """
        Derives generic TimeSeries from history, selects models via the registry,
        and computes forecasts for all supported metrics.
        """
        context = ForecastContext()

        if not history.has_history:
            # Cannot forecast without history
            return context

        time_series_map = self._factory.build_all(history)

        for metric_name, series in time_series_map.items():
            model = self._registry.get_model_for(metric_name)
            if model:
                forecast_series = model.forecast(series, horizons=horizons)
                if forecast_series:
                    context.metrics[metric_name] = forecast_series

        return context
