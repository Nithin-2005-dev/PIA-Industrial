from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.forecasting.forecast import (
    Forecast,
)

from app.forecasting.forecast_severity_service import (
    ForecastSeverityService,
)


def main():

    forecasts = [

        Forecast(
            module_ref=EntityRef(
                id="payments.py",
                type=EntityType.FILE,
            ),
            current_health=40,
            predicted_health=10,
            horizon=3,
            slope=-10,
            risk_level="CRITICAL",
        ),

        Forecast(
            module_ref=EntityRef(
                id="auth.py",
                type=EntityType.FILE,
            ),
            current_health=80,
            predicted_health=68,
            horizon=3,
            slope=-4,
            risk_level="WARNING",
        ),

        Forecast(
            module_ref=EntityRef(
                id="analytics.py",
                type=EntityType.FILE,
            ),
            current_health=90,
            predicted_health=99,
            horizon=3,
            slope=3,
            risk_level="SAFE",
        ),
    ]

    severities = (
        ForecastSeverityService()
        .ranking(
            forecasts
        )
    )

    print(
        "\n=== FORECAST SEVERITY ===\n"
    )

    for index, severity in enumerate(
        severities,
        start=1,
    ):

        print(
            f"Rank #{index}"
        )

        print(
            f"Module: "
            f"{severity.module_ref.id}"
        )

        print(
            f"Severity Score: "
            f"{severity.severity_score:.2%}"
        )

        print(
            f"Severity Level: "
            f"{severity.severity_level}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()