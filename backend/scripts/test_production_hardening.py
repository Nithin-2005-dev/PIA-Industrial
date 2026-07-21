from pathlib import Path
import sys

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)

from app.decision import DecisionOptimizationEngine
from app.forecasting.validation import ForecastValidationService
from app.graph import GraphService
from app.measurement.scientific_engine import ScientificMeasurementEngine
from app.observation.ingestion import ObservationIngestionEngine
from app.platform import PlatformRuntime
from app.platform import ProductionHardeningService
from app.platform import default_platform_modules


def main():
    runtime = PlatformRuntime.create()
    for module in default_platform_modules():
        runtime.register_module(module)
    built = runtime.build()
    built.initialize()
    built.start()

    hardening = built.provider.resolve(
        ProductionHardeningService
    )
    report = hardening.audit(
        built,
        required_services=(
            ObservationIngestionEngine,
            ScientificMeasurementEngine,
            GraphService,
            ForecastValidationService,
            DecisionOptimizationEngine,
        ),
    )
    assert report.ready
    assert not report.failures()
    assert any(
        check.name == "event_bus_dead_letters"
        for check in report.checks
    )

    built.shutdown()
    stopped_report = hardening.audit(
        built,
        required_services=(
            ObservationIngestionEngine,
        ),
    )
    assert not stopped_report.ready
    assert stopped_report.failures()

    print("production_hardening_ok")


if __name__ == "__main__":
    main()

