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

from app.forecasting.future_risk_pipeline_service import (
    FutureRiskPipelineService,
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

    forecast_pipeline = ForecastPipelineService(
        HistoryService(
            health_projection
        ),
        ForecastService(
            LinearForecastPolicy()
        ),
    )

    pipeline = FutureRiskPipelineService(
        forecast_pipeline
    )

    risks = pipeline.risks(
        horizon=3
    )

    ranking = pipeline.ranking(
        horizon=3
    )

    severities = pipeline.severities(
        horizon=3
    )

    severity_ranking = (
        pipeline.severity_ranking(
            horizon=3
        )
    )

    risk = risks[0]

    severity = severities[0]

    assert risk.module_ref.id == "payments.py"
    assert risk.current_health == 40
    assert risk.predicted_health == 0
    assert risk.risk_score == 40
    assert ranking[0].module_ref.id == "payments.py"
    assert severity.severity_score == 1.0
    assert severity.severity_level == "EXTREME"
    assert (
        severity_ranking[0]
        .module_ref
        .id
        == "payments.py"
    )

    print(
        "\n=== FUTURE RISK PIPELINE ===\n"
    )

    print(
        f"Module: "
        f"{risk.module_ref.id}"
    )

    print(
        f"Current: "
        f"{risk.current_health:.2f}"
    )

    print(
        f"Predicted: "
        f"{risk.predicted_health:.2f}"
    )

    print(
        f"Risk Score: "
        f"{risk.risk_score:.2f}"
    )

    print(
        f"Severity: "
        f"{severity.severity_level}"
    )


if __name__ == "__main__":
    main()
