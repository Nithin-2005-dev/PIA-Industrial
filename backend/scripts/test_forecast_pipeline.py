from datetime import UTC
from datetime import datetime
from datetime import timedelta

from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.forecasting.forecast_pipeline_service import (
    ForecastPipelineService,
)

from app.forecasting.forecast_service import (
    ForecastService,
)

from app.forecasting.linear_forecast_policy import (
    LinearForecastPolicy,
)

from app.health.health_report import (
    HealthReport,
)

from app.history.health_projection import (
    HealthProjection,
)

from app.history.history_service import (
    HistoryService,
)


def module(name):

    return EntityRef(
        id=name,
        type=EntityType.FILE,
    )


def report(
    module_ref,
    health_score,
):

    return HealthReport(
        module_ref=module_ref,
        health_score=health_score,
        health_level="WARNING",
        coverage_score=50,
        concentration_score=0.75,
        bus_factor=2,
    )


def main():

    health_projection = HealthProjection()

    payments = module(
        "payments.py"
    )

    now = datetime.now(
        UTC
    )

    scores = [
        95,
        80,
        60,
        40,
    ]

    for index, score in enumerate(
        scores
    ):

        health_projection.apply(
            report(
                payments,
                score,
            ),
            now - timedelta(
                days=(
                    len(scores)
                    - index
                    - 1
                )
                * 30
            ),
        )

    pipeline = ForecastPipelineService(
        HistoryService(
            health_projection
        ),
        ForecastService(
            LinearForecastPolicy()
        ),
    )

    forecasts = pipeline.forecasts(
        horizon=3
    )

    ranking = pipeline.ranking(
        horizon=3
    )

    forecast = forecasts[0]

    assert forecast.module_ref.id == "payments.py"
    assert forecast.current_health == 40
    assert forecast.predicted_health == 0
    assert forecast.risk_level == "CRITICAL"
    assert ranking[0].forecast.module_ref.id == "payments.py"

    print(
        "\n=== FORECAST PIPELINE ===\n"
    )

    print(
        f"Module: "
        f"{forecast.module_ref.id}"
    )

    print(
        f"Current: "
        f"{forecast.current_health:.2f}"
    )

    print(
        f"Predicted: "
        f"{forecast.predicted_health:.2f}"
    )

    print(
        f"Risk: "
        f"{forecast.risk_level}"
    )


if __name__ == "__main__":
    main()
