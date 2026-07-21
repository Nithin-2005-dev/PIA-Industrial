import math

from app.history.health_trend import (
    HealthTrend,
)

from .forecast import (
    Forecast,
)

from .forecast_policy import (
    ForecastPolicy,
)


class LinearForecastPolicy(
    ForecastPolicy
):

    def forecast(
        self,
        trend: HealthTrend,
        horizon: int,
    ):

        predicted_health = (
            trend.current_score
            +
            (
                trend.slope
                * horizon
            )
        )

        predicted_health = max(
            0,
            min(
                100,
                predicted_health,
            ),
        )

        if predicted_health >= 75:
            risk = "SAFE"
        elif predicted_health >= 50:
            risk = "WARNING"
        else:
            risk = "CRITICAL"

        # M56.1 Statistical Confidence Formulation (CV + Horizon decay)
        mean_health = max(1e-5, trend.current_score)
        cv = math.sqrt(trend.variance) / mean_health
        base_confidence = min(1.0, trend.sample_size / 30.0)
        
        # Exponential penalty based on CV and prediction horizon
        confidence = base_confidence * math.exp(-0.5 * cv) * math.exp(-0.01 * horizon)
        confidence = max(0.01, min(1.0, confidence))

        return Forecast(
            module_ref=(
                trend.module_ref
            ),
            current_health=(
                trend.current_score
            ),
            predicted_health=(
                predicted_health
            ),
            horizon=horizon,
            slope=trend.slope,
            risk_level=risk,
            confidence=confidence,
        )