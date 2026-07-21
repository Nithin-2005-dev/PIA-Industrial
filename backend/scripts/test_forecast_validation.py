from datetime import UTC
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.forecasting.linear_forecast_policy import LinearForecastPolicy
from app.forecasting.validation import ForecastValidationService
from app.history.health_history import HealthHistory
from app.history.health_snapshot import HealthSnapshot
from app.history.trend_analyzer import TrendAnalyzer
from app.platform import PlatformRuntime
from app.platform import default_platform_modules


def _history(
) -> HealthHistory:
    module_ref = EntityRef(
        id="backend/app/platform/runtime.py",
        type=EntityType.FILE,
    )
    return HealthHistory(
        module_ref=module_ref,
        snapshots=[
            HealthSnapshot(
                module_ref=module_ref,
                health_score=90,
                recorded_at=datetime(2026, 7, 1, tzinfo=UTC),
            ),
            HealthSnapshot(
                module_ref=module_ref,
                health_score=85,
                recorded_at=datetime(2026, 7, 2, tzinfo=UTC),
            ),
            HealthSnapshot(
                module_ref=module_ref,
                health_score=80,
                recorded_at=datetime(2026, 7, 3, tzinfo=UTC),
            ),
            HealthSnapshot(
                module_ref=module_ref,
                health_score=74,
                recorded_at=datetime(2026, 7, 4, tzinfo=UTC),
            ),
        ],
    )


def main():
    history = _history()
    policy = LinearForecastPolicy()
    trend = TrendAnalyzer().analyze(
        HealthHistory(
            module_ref=history.module_ref,
            snapshots=history.snapshots[:3],
        )
    )
    forecast = policy.forecast(
        trend,
        horizon=1,
    )
    validation = ForecastValidationService(
        tolerance=2.0,
    ).validate(
        forecast,
        history.snapshots[-1],
    )
    assert validation.module_id == history.module_ref.id
    assert validation.predicted_health == 75
    assert validation.actual_health == 74
    assert validation.absolute_error == 1
    assert validation.within_tolerance

    report = ForecastValidationService(
        tolerance=2.0,
    ).backtest(
        history,
        policy,
        horizon=1,
    )
    assert report.sample_count == 2
    assert report.mean_absolute_error >= 0
    assert report.root_mean_squared_error >= report.mean_absolute_error
    assert 0.0 <= report.within_tolerance_rate <= 1.0
    assert len(report.results) == report.sample_count

    platform = PlatformRuntime.create()
    for module in default_platform_modules():
        platform.register_module(module)
    built = platform.build()
    built.initialize()
    assert isinstance(
        built.provider.resolve(ForecastValidationService),
        ForecastValidationService,
    )
    built.shutdown()

    print("forecast_validation_ok")


if __name__ == "__main__":
    main()

