from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.forecasting.forecast_service import (
    ForecastService,
)

from app.forecasting.linear_forecast_policy import (
    LinearForecastPolicy,
)

from app.history.health_trend import (
    HealthTrend,
)

from app.history.trend_direction import (
    TrendDirection,
)


def main():

    trends = [

        HealthTrend(
            module_ref=EntityRef(
                id="payments.py",
                type=EntityType.FILE,
            ),
            previous_score=70,
            current_score=40,
            delta=-30,
            slope=-10,
            direction=(
                TrendDirection.DECLINING
            ),
        ),

        HealthTrend(
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
        ),

        HealthTrend(
            module_ref=EntityRef(
                id="analytics.py",
                type=EntityType.FILE,
            ),
            previous_score=81,
            current_score=90,
            delta=9,
            slope=3,
            direction=(
                TrendDirection.IMPROVING
            ),
        ),
    ]

    service = ForecastService(
        LinearForecastPolicy()
    )

    rankings = (
        service.rank(
            trends,
            horizon=3,
        )
    )

    print(
        "\n=== FORECAST RISKS ===\n"
    )

    for item in rankings:

        forecast = item.forecast

        print(
            f"Rank #{item.rank}"
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

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()