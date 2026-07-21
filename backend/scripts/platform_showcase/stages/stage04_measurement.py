"""Stage 04 - run the canonical measurement engine."""

from __future__ import annotations

import statistics
import time
from collections import Counter
from datetime import UTC, datetime

from app.measurement.core.engine import MeasurementEngine
from app.measurement.domain import MeasurementContext

from ..context import PlatformContext
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


class MeasurementStage(PipelineStage):
    name = "Observation to Measurement"

    def execute(self, context: PlatformContext) -> None:
        if not context.observations:
            warning("No observations available")
            return

        started = time.perf_counter()
        engine = context.resolve(MeasurementEngine)
        measurement_context = MeasurementContext(
            timestamp=datetime.now(UTC),
            tenant_id=context.tenant_id,
            source_reliability={"github": 0.85, "GitHub": 0.85},
            metadata={"repository": context.repository},
        )
        measurements = engine.measure_observations(
            context.observations,
            measurement_context,
        )

        context.measurements = measurements
        context.metrics["measurements"] = len(measurements)
        context.metrics["measurement_seconds"] = time.perf_counter() - started
        context.metrics["valid_measurements"] = sum(
            1 for item in measurements if item.validation_status.value in {"passed", "warning"}
        )

        section("Measurement Registry")
        definitions = {item.definition.id: item.definition for item in measurements}
        metric("Definitions Observed", len(definitions))
        metric("Measurements", len(measurements))
        metric("Measurement Time", f"{context.metrics['measurement_seconds']:.3f}s")
        ranking(
            "Definitions",
            [
                f"{definition.id:<32} {definition.unit.value:<12} {definition.version}"
                for definition in definitions.values()
            ],
        )

        self._evaluators(measurements)
        self._validation(measurements)
        self._confidence(measurements)
        self._quality(measurements)
        self._uncertainty(measurements)
        self._normalization(measurements)
        self._calibration(measurements)
        self._benchmarks(measurements)
        self._statistics(measurements)
        self._samples(measurements)
        success("Measurement layer produced canonical measurements")

    def _evaluators(self, measurements) -> None:
        methods = Counter(item.measurement_method.name for item in measurements)
        ranking("Evaluators", [f"{name:<34} {count}" for name, count in methods.items()])

    def _validation(self, measurements) -> None:
        statuses = Counter(item.validation_status.value for item in measurements)
        validators = Counter()
        for item in measurements:
            validators.update(item.traceability.validator_ids)

        section("Validation")
        metric("Passed", statuses.get("passed", 0))
        metric("Warnings", statuses.get("warning", 0))
        metric("Failed", statuses.get("failed", 0))
        ranking("Validation Checks", [f"{name:<34} {count}" for name, count in validators.items()])

    def _confidence(self, measurements) -> None:
        values = [item.confidence for item in measurements]
        section("Confidence")
        metric("Average", f"{statistics.mean(values):.3f}" if values else "0.000")
        metric("Minimum", f"{min(values):.3f}" if values else "0.000")
        metric("Maximum", f"{max(values):.3f}" if values else "0.000")

        breakdowns = [item.confidence_breakdown for item in measurements if item.confidence_breakdown]
        if breakdowns:
            metric(
                "Average Coverage",
                f"{statistics.mean(item.coverage for item in breakdowns):.3f}",
            )
            metric(
                "Average Source Reliability",
                f"{statistics.mean(item.source_reliability for item in breakdowns):.3f}",
            )

    def _quality(self, measurements) -> None:
        values = [item.quality_score for item in measurements]
        section("Quality")
        metric("Average", f"{statistics.mean(values):.3f}" if values else "0.000")
        metric("Minimum", f"{min(values):.3f}" if values else "0.000")
        metric("Maximum", f"{max(values):.3f}" if values else "0.000")

    def _uncertainty(self, measurements) -> None:
        values = [item.uncertainty.variance for item in measurements]
        section("Uncertainty")
        metric("Average Variance", f"{statistics.mean(values):.3f}" if values else "0.000")
        metric("Minimum Variance", f"{min(values):.3f}" if values else "0.000")
        metric("Maximum Variance", f"{max(values):.3f}" if values else "0.000")

    def _normalization(self, measurements) -> None:
        methods = Counter(item.normalization_method.name for item in measurements)
        transforms = Counter()
        for item in measurements:
            transforms.update(item.provenance.transformations)

        ranking("Normalization Methods", [f"{name:<34} {count}" for name, count in methods.items()])
        ranking("Normalization and Derivation Steps", [f"{name:<34} {count}" for name, count in transforms.items()])

    def _calibration(self, measurements) -> None:
        factors = [float(item.metadata.get("calibration_factor", 1.0)) for item in measurements]
        section("Calibration")
        metric("Average Factor", f"{statistics.mean(factors):.3f}" if factors else "1.000")
        metric("Minimum Factor", f"{min(factors):.3f}" if factors else "1.000")
        metric("Maximum Factor", f"{max(factors):.3f}" if factors else "1.000")

    def _benchmarks(self, measurements) -> None:
        references = Counter()
        for item in measurements:
            for reference in item.definition.references:
                label = reference.identifier or reference.title
                references[label] += 1
        ranking("Benchmarks and Standards", [f"{name:<34} {count}" for name, count in references.items()])

    def _statistics(self, measurements) -> None:
        values = [item.value for item in measurements]
        section("Scientific Statistics")
        metric("Mean Value", f"{statistics.mean(values):.3f}" if values else "0.000")
        metric("Median Value", f"{statistics.median(values):.3f}" if values else "0.000")
        metric(
            "Standard Deviation",
            f"{statistics.stdev(values):.3f}" if len(values) > 1 else "0.000",
        )

    def _samples(self, measurements) -> None:
        ranking(
            "Sample Measurements",
            [
                (
                    f"{item.definition.id:<32} value={item.value:.3f} "
                    f"confidence={item.confidence:.3f} quality={item.quality_score:.3f}"
                )
                for item in measurements[:8]
            ],
        )
