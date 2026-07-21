import datetime
import math
from typing import Any

from .models import (
    ForecastConfidence,
    ForecastExplanation,
    ForecastPoint,
    ForecastProvenance,
    ForecastSeries,
    ForecastUncertainty,
    PredictionInterval,
    TimeSeries,
)


class ConstantBaselineModel:
    @property
    def name(self) -> str:
        return "ConstantBaseline"

    @property
    def version(self) -> str:
        return "1.0.0"

    def supports(self, metric_name: str) -> bool:
        # Fallback model supports everything
        return True

    def forecast(
        self,
        series: TimeSeries[float],
        horizons: tuple[int, ...] = (7, 30, 90),
    ) -> ForecastSeries[float] | None:
        if series.is_empty:
            return None

        current = series.current
        
        predictions = []
        for horizon in horizons:
            proj_date = f"T+{horizon}d"
            predictions.append(
                ForecastPoint(
                    horizon_days=horizon,
                    projected_date=proj_date,
                    predicted_value=current,
                    interval=PredictionInterval(lower_bound=current, upper_bound=current),
                )
            )

        return ForecastSeries(
            metric_name=series.metric_name,
            current_value=current,
            predictions=tuple(predictions),
            confidence=ForecastConfidence(score=0.1),
            uncertainty=ForecastUncertainty(variance=0.0),
            explanation=ForecastExplanation(
                rationale="Constant baseline projection",
                assumptions=("Metric remains completely static",),
            ),
            provenance=ForecastProvenance(
                model_name=self.name,
                model_version=self.version,
                training_window_size=1,
                history_length=series.history_length,
            ),
        )


class LinearTrendModel:
    @property
    def name(self) -> str:
        return "LinearTrend"

    @property
    def version(self) -> str:
        return "1.0.0"

    def supports(self, metric_name: str) -> bool:
        return metric_name in (
            "bus_factor",
            "knowledge_growth",
            "coverage",
            "health",
            "expertise",
        )

    def forecast(
        self,
        series: TimeSeries[float],
        horizons: tuple[int, ...] = (7, 30, 90),
    ) -> ForecastSeries[float] | None:
        if series.history_length < 2:
            return None

        y = [p.value for p in series.points]
        x = list(range(len(y)))
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_x2 = sum(xi * xi for xi in x)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))

        denominator = (n * sum_x2 - sum_x * sum_x)
        if denominator == 0:
            slope = 0.0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            
        intercept = (sum_y - slope * sum_x) / n

        # Calculate variance/uncertainty based on residuals
        residuals = [yi - (slope * xi + intercept) for xi, yi in zip(x, y)]
        variance = sum(r * r for r in residuals) / n

        predictions = []
        for horizon in horizons:
            proj_date = f"T+{horizon}d"
            
            # Since our x-axis is just snapshot index, we map horizon days to indices roughly.
            # Assuming 1 snapshot per day for this simple model, x_proj = n - 1 + horizon.
            # In a real model, we'd map timestamps to precise float days.
            x_proj = n - 1 + horizon
            y_proj = slope * x_proj + intercept
            
            # Uncertainty grows over time
            std_dev = math.sqrt(variance) * (1.0 + horizon / 30.0)
            
            predictions.append(
                ForecastPoint(
                    horizon_days=horizon,
                    projected_date=proj_date,
                    predicted_value=y_proj,
                    interval=PredictionInterval(
                        lower_bound=y_proj - 1.96 * std_dev,
                        upper_bound=y_proj + 1.96 * std_dev,
                    ),
                )
            )

        # M56.1 Statistical Confidence Formulation (CV + Horizon decay)
        mean_y = abs(sum_y/n)
        cv = math.sqrt(variance) / (mean_y + 1e-5) # Coefficient of Variation
        base_conf = min(1.0, n / 10.0) # Penalty for very short histories
        # exp(-alpha * CV) * exp(-beta * horizon) -> we apply decay per point later, but this is the baseline confidence of the series
        confidence_score = base_conf * math.exp(-0.5 * cv)

        return ForecastSeries(
            metric_name=series.metric_name,
            current_value=series.current,
            predictions=tuple(predictions),
            confidence=ForecastConfidence(score=min(1.0, confidence_score)),
            uncertainty=ForecastUncertainty(variance=variance),
            explanation=ForecastExplanation(
                rationale="Linear regression fit over historical points.",
                assumptions=("Trend is linear", "1 snapshot ≈ 1 day"),
            ),
            provenance=ForecastProvenance(
                model_name=self.name,
                model_version=self.version,
                training_window_size=n,
                history_length=n,
            ),
        )


class MovingAverageModel:
    @property
    def name(self) -> str:
        return "MovingAverage"

    @property
    def version(self) -> str:
        return "1.0.0"

    def supports(self, metric_name: str) -> bool:
        return metric_name in (
            "knowledge_risk",
            "ownership_concentration",
            "observations",
        )

    def forecast(
        self,
        series: TimeSeries[float],
        horizons: tuple[int, ...] = (7, 30, 90),
    ) -> ForecastSeries[float] | None:
        if series.history_length < 1:
            return None
            
        window = min(5, series.history_length)
        recent_points = [p.value for p in series.points[-window:]]
        ma = sum(recent_points) / len(recent_points)
        
        variance = sum((p - ma)**2 for p in recent_points) / len(recent_points)

        predictions = []
        for horizon in horizons:
            proj_date = f"T+{horizon}d"
            std_dev = math.sqrt(variance) * (1.0 + horizon / 30.0)
            predictions.append(
                ForecastPoint(
                    horizon_days=horizon,
                    projected_date=proj_date,
                    predicted_value=ma,
                    interval=PredictionInterval(
                        lower_bound=ma - 1.96 * std_dev,
                        upper_bound=ma + 1.96 * std_dev,
                    ),
                )
            )
        # M56.1 Statistical Confidence Formulation (CV + Horizon decay)
        mean_y = abs(ma)
        cv = math.sqrt(variance) / (mean_y + 1e-5) # Coefficient of Variation
        base_conf = min(1.0, series.history_length / 10.0)
        confidence_score = base_conf * math.exp(-0.5 * cv)

        return ForecastSeries(
            metric_name=series.metric_name,
            current_value=series.current,
            predictions=tuple(predictions),
            confidence=ForecastConfidence(score=confidence_score),
            uncertainty=ForecastUncertainty(variance=variance),
            explanation=ForecastExplanation(
                rationale=f"Moving average over last {window} snapshots.",
                assumptions=("Recent history is the best predictor of near future",),
            ),
            provenance=ForecastProvenance(
                model_name=self.name,
                model_version=self.version,
                training_window_size=window,
                history_length=series.history_length,
            ),
        )


class MomentumProjectionModel:
    @property
    def name(self) -> str:
        return "MomentumProjection"

    @property
    def version(self) -> str:
        return "1.0.0"

    def supports(self, metric_name: str) -> bool:
        return metric_name in (
            "expertise",
            "knowledge_growth",
        )

    def forecast(
        self,
        series: TimeSeries[float],
        horizons: tuple[int, ...] = (7, 30, 90),
    ) -> ForecastSeries[float] | None:
        if series.history_length < 3:
            return None
            
        y = [p.value for p in series.points]
        
        # Velocity = (current - prev)
        # Accel = (Velocity - prev_velocity)
        v1 = y[-2] - y[-3]
        v2 = y[-1] - y[-2]
        acceleration = v2 - v1
        
        # Dampening factor so acceleration doesn't blow up long horizons
        dampening = 0.9

        predictions = []
        current_val = y[-1]
        current_vel = v2
        
        for horizon in horizons:
            proj_date = f"T+{horizon}d"
            
            # Integrate over horizon days
            # Assuming 1 snapshot ≈ 1 day for this simple model
            proj_val = current_val
            proj_vel = current_vel
            
            for _ in range(horizon):
                proj_vel += acceleration
                proj_vel *= dampening
                proj_val += proj_vel
                
            std_dev = abs(proj_val * 0.1) * (horizon / 30.0)
                
            predictions.append(
                ForecastPoint(
                    horizon_days=horizon,
                    projected_date=proj_date,
                    predicted_value=proj_val,
                    interval=PredictionInterval(
                        lower_bound=proj_val - std_dev,
                        upper_bound=proj_val + std_dev,
                    ),
                )
            )

        variance = abs(acceleration)        # M56.1 Statistical Confidence Formulation (CV + Horizon decay)
        mean_y = abs(current_vel)
        cv = math.sqrt(variance) / (mean_y + 1e-5) # Coefficient of Variation
        base_conf = min(1.0, len(series.points) / 10.0)
        confidence_score = base_conf * math.exp(-0.5 * cv)

        return ForecastSeries(
            metric_name=series.metric_name,
            current_value=series.current,
            predictions=tuple(predictions),
            confidence=ForecastConfidence(score=confidence_score),
            uncertainty=ForecastUncertainty(variance=variance),
            explanation=ForecastExplanation(
                rationale="Kinematic projection using velocity and acceleration.",
                assumptions=("Inertia persists", "Acceleration dampens over time"),
            ),
            provenance=ForecastProvenance(
                model_name=self.name,
                model_version=self.version,
                training_window_size=3,
                history_length=series.history_length,
            ),
        )


class ExponentialSmoothingModel:
    @property
    def name(self) -> str:
        return "ExponentialSmoothing"

    @property
    def version(self) -> str:
        return "1.0.0"

    def supports(self, metric_name: str) -> bool:
        return True

    def forecast(
        self,
        series: TimeSeries[float],
        horizons: tuple[int, ...] = (7, 30, 90),
    ) -> ForecastSeries[float] | None:
        if series.history_length < 1:
            return None
            
        alpha = 0.3
        s = series.points[0].value
        for p in series.points[1:]:
            s = alpha * p.value + (1 - alpha) * s
            
        predictions = []
        for horizon in horizons:
            proj_date = f"T+{horizon}d"
            std_dev = abs(s * 0.05) * (1.0 + horizon / 30.0)
            
            predictions.append(
                ForecastPoint(
                    horizon_days=horizon,
                    projected_date=proj_date,
                    predicted_value=s,
                    interval=PredictionInterval(
                        lower_bound=s - 1.96 * std_dev,
                        upper_bound=s + 1.96 * std_dev,
                    ),
                )
            )

        variance = abs(series.current - s)        # M56.1 Statistical Confidence Formulation (CV + Horizon decay)
        mean_y = abs(s)
        cv = math.sqrt(variance) / (mean_y + 1e-5) # Coefficient of Variation
        base_conf = min(1.0, series.history_length / 10.0)
        confidence_score = base_conf * math.exp(-0.5 * cv)

        return ForecastSeries(
            metric_name=series.metric_name,
            current_value=series.current,
            predictions=tuple(predictions),
            confidence=ForecastConfidence(score=confidence_score),
            uncertainty=ForecastUncertainty(variance=variance),
            explanation=ForecastExplanation(
                rationale="Exponential smoothing (EMA).",
                assumptions=("Recent points have exponentially more weight",),
            ),
            provenance=ForecastProvenance(
                model_name=self.name,
                model_version=self.version,
                training_window_size=series.history_length,
                history_length=series.history_length,
            ),
        )
