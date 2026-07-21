from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.history.health_trend import (
    HealthTrend,
)

from app.history.trend_direction import (
    TrendDirection,
)

from app.forecasting.linear_forecast_policy import (
    LinearForecastPolicy,
)


def main():

    trend = HealthTrend(
        module_ref=EntityRef(
            id="auth.py",
            type=EntityType.FILE,
        ),
        previous_score=92,
        current_score=80,
        delta=-12,
        slope=-4,
        direction=(
            TrendDirection.DECLINING
        ),
    )

    forecast = (
        LinearForecastPolicy()
        .forecast(
            trend,
            horizon=3,
        )
    )

    print(
        "\n=== FORECAST ===\n"
    )

    print(
        f"Module: "
        f"{forecast.module_ref.id}"
    )

    print(
        f"Current Health: "
        f"{forecast.current_health:.2f}"
    )

    print(
        f"Predicted Health: "
        f"{forecast.predicted_health:.2f}"
    )

    print(
        f"Slope: "
        f"{forecast.slope:.2f}"
    )

    print(
        f"Horizon: "
        f"{forecast.horizon}"
    )

    print(
        f"Risk: "
        f"{forecast.risk_level}"
    )


if __name__ == "__main__":
    main()