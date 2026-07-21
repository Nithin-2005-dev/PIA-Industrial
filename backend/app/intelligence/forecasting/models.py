import datetime
from dataclasses import dataclass, field
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")

@dataclass(frozen=True)
class TimeSeriesPoint(Generic[T]):
    snapshot_id: str
    timestamp: str
    value: T


@dataclass(frozen=True)
class TimeSeries(Generic[T]):
    metric_name: str
    points: tuple[TimeSeriesPoint[T], ...]

    @property
    def is_empty(self) -> bool:
        return len(self.points) == 0

    @property
    def current(self) -> T | None:
        return self.points[-1].value if self.points else None

    @property
    def history_length(self) -> int:
        return len(self.points)


@dataclass(frozen=True)
class PredictionInterval:
    lower_bound: float
    upper_bound: float


@dataclass(frozen=True)
class ForecastConfidence:
    score: float  # 0.0 to 1.0


@dataclass(frozen=True)
class ForecastUncertainty:
    variance: float


@dataclass(frozen=True)
class ForecastExplanation:
    rationale: str
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class ForecastProvenance:
    model_name: str
    model_version: str
    training_window_size: int
    history_length: int


@dataclass(frozen=True)
class ForecastPoint(Generic[T]):
    horizon_days: int
    projected_date: str
    predicted_value: T
    interval: PredictionInterval


@dataclass(frozen=True)
class ForecastSeries(Generic[T]):
    metric_name: str
    current_value: T
    predictions: tuple[ForecastPoint[T], ...]
    confidence: ForecastConfidence
    uncertainty: ForecastUncertainty
    explanation: ForecastExplanation
    provenance: ForecastProvenance

    def get_forecast(self, horizon_days: int) -> ForecastPoint[T] | None:
        for point in self.predictions:
            if point.horizon_days == horizon_days:
                return point
        return None


@dataclass(frozen=True)
class ForecastContext:
    # A generic dictionary mapping metric names (e.g., "bus_factor", "knowledge_risk")
    # to their respective ForecastSeries.
    metrics: dict[str, ForecastSeries] = field(default_factory=dict)


class ForecastModel(Protocol):
    """
    Interface for pluggable predictive models.
    """
    
    @property
    def name(self) -> str:
        ...
        
    @property
    def version(self) -> str:
        ...

    def supports(self, metric_name: str) -> bool:
        """
        Check if this model has the capability to forecast a specific metric.
        """
        ...

    def forecast(
        self,
        series: TimeSeries[float],
        horizons: tuple[int, ...] = (7, 30, 90),
    ) -> ForecastSeries[float]:
        """
        Generate forecasts for the given time series over the specified horizons.
        """
        ...
