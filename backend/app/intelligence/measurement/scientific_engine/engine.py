from __future__ import annotations

from datetime import UTC
from datetime import datetime

from app.intelligence.measurement.core.calibration.engine import StatisticalCalibrationEngine
from app.intelligence.measurement.core.confidence import DefaultConfidenceEstimator
from app.intelligence.measurement.core.quality import DefaultQualityScorer
from app.intelligence.measurement.core.validation import FiniteValueValidator
from app.intelligence.measurement.core.validation import RangeValidator
from app.intelligence.measurement.core.validation import UnitValidator
from app.intelligence.measurement.core.validation import merge_validation_results
from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementContext
from app.intelligence.measurement.domain import ValidationStatus
from app.intelligence.measurement.scientific_engine.benchmark import MeasurementBenchmark
from app.intelligence.measurement.scientific_engine.benchmark import MeasurementBenchmarkRecorder
from app.intelligence.measurement.scientific_engine.providers import MeasurementProviderRegistry
from app.intelligence.measurement.scientific_engine.providers import default_measurement_providers
from app.intelligence.measurement.scientific_engine.registry import ScientificMeasurementRegistry
from app.intelligence.measurement.scientific_engine.registry import default_scientific_measurements
from app.ingestion.observation.domain import Observation


class ScientificMeasurementEngine:
    def __init__(
        self,
        providers: MeasurementProviderRegistry | None = None,
        registry: ScientificMeasurementRegistry | None = None,
    ):
        self.providers = providers or MeasurementProviderRegistry(default_measurement_providers())
        self.registry = registry or ScientificMeasurementRegistry(default_scientific_measurements())
        self.validators = (
            FiniteValueValidator(),
            UnitValidator(),
            RangeValidator(),
        )
        self.confidence = DefaultConfidenceEstimator()
        self.quality = DefaultQualityScorer()
        self.calibration = StatisticalCalibrationEngine()
        self.benchmarks = MeasurementBenchmarkRecorder()
        self.last_benchmark = MeasurementBenchmark()

    def measure_observation(
        self,
        observation: Observation,
        context: MeasurementContext | None = None,
    ) -> tuple[Measurement, ...]:
        return tuple(
            self.measure_observations(
                [observation],
                context,
            )
        )

    def measure_observations(
        self,
        observations: list[Observation],
        context: MeasurementContext | None = None,
    ) -> tuple[Measurement, ...]:
        if context is None:
            context = MeasurementContext(
                timestamp=datetime.now(UTC),
                pipeline_version="sme.v1",
            )

        def run():
            raw = []
            for observation in observations:
                for provider in self.providers.all():
                    if observation.observation_type not in provider.supported_types:
                        continue
                    raw.extend(provider.measure(observation, context, self.registry))
            finalized = [
                self._finalize(measurement, context)
                for measurement in raw
            ]
            return tuple(self.calibration.calibrate(finalized))

        result, benchmark = self.benchmarks.record(run, len(observations))
        self.last_benchmark = benchmark
        return result

    def _finalize(
        self,
        measurement: Measurement,
        context: MeasurementContext,
    ) -> Measurement:
        validation = merge_validation_results(
            [
                validator.validate(measurement)
                for validator in self.validators
            ]
        )
        from dataclasses import replace

        with_validation = replace(
            measurement,
            validation_status=validation.status,
        )
        if validation.status == ValidationStatus.FAILED:
            return self.quality.score(with_validation, validation, context)
        with_confidence = self.confidence.estimate(with_validation, context)
        return self.quality.score(with_confidence, validation, context)

