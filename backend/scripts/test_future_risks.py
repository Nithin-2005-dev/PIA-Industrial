from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.forecasting.forecast import (
    Forecast,
)

from app.forecasting.future_risk_service import (
    FutureRiskService,
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

    risks = (
        FutureRiskService()
        .ranking(
            forecasts
        )
    )

    print(
        "\n=== FUTURE RISKS ===\n"
    )

    for index, risk in enumerate(
        risks,
        start=1,
    ):

        print(
            f"Rank #{index}"
        )

        print(
            f"Module: "
            f"{risk.module_ref.id}"
        )

        print(
            f"Current Health: "
            f"{risk.current_health:.2f}"
        )

        print(
            f"Predicted Health: "
            f"{risk.predicted_health:.2f}"
        )

        print(
            f"Risk Score: "
            f"{risk.risk_score:.2f}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()