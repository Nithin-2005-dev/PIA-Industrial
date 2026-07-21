from dataclasses import dataclass
from dataclasses import replace

from app.intelligence.measurement.benchmarks.benchmark import BenchmarkEngine
from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementContext
from app.intelligence.measurement.core.fusion import ProbabilisticFusionEngine
from app.intelligence.measurement.analytics.outliers import OutlierDetectionEngine
from app.intelligence.measurement.core.validation import ValidationResult
from app.intelligence.measurement.core.validation import ValidationStatus


@dataclass(frozen=True)
class CrossSourceDisagreement:
    definition_id: str
    measurement_ids: tuple[str, ...]
    disagreement_score: float


@dataclass(frozen=True)
class MeasurementAccuracyReport:
    measurements: tuple[Measurement, ...]
    fused_measurements: tuple[Measurement, ...]
    disagreements: tuple[CrossSourceDisagreement, ...]
    validations: tuple[ValidationResult, ...]


class EnterpriseAccuracyPipeline:
    """
    Batch integrity pipeline before measurements are handed to evidence.
    """

    def __init__(
        self,
    ):
        self._outliers = OutlierDetectionEngine()
        self._fusion = ProbabilisticFusionEngine()
        self._benchmarks = BenchmarkEngine()

    def process(
        self,
        measurements: list[Measurement],
        context: MeasurementContext,
    ) -> MeasurementAccuracyReport:
        unique = self._remove_duplicates(
            measurements
        )
        quality_checked = [
            self._annotate_signal_quality(
                measurement,
                context,
            )
            for measurement in unique
        ]
        outlier_checked = self._annotate_outliers(
            quality_checked
        )
        missing_checked = [
            self._annotate_missing_data(
                measurement
            )
            for measurement in outlier_checked
        ]
        benchmarked = [
            self._annotate_benchmark(
                measurement,
                context,
            )
            for measurement in missing_checked
        ]

        fused, disagreements = self._cross_source_verify(
            benchmarked
        )

        validations = tuple(
            self._integrity_validation(
                measurement
            )
            for measurement in [
                *benchmarked,
                *fused,
            ]
        )

        return MeasurementAccuracyReport(
            measurements=tuple(benchmarked),
            fused_measurements=tuple(fused),
            disagreements=tuple(disagreements),
            validations=validations,
        )

    def _remove_duplicates(
        self,
        measurements: list[Measurement],
    ) -> list[Measurement]:
        seen = set()
        unique = []

        for measurement in measurements:
            if measurement.id in seen:
                continue

            seen.add(
                measurement.id
            )
            unique.append(
                measurement
            )

        return unique

    def _annotate_signal_quality(
        self,
        measurement: Measurement,
        context: MeasurementContext,
    ) -> Measurement:
        reliability = context.source_reliability.get(
            measurement.provenance.source_system,
            0.75,
        )
        coverage = float(
            measurement.metadata.get(
                "coverage",
                1.0,
            )
        )
        signal_quality = max(
            0.0,
            min(
                1.0,
                reliability * coverage,
            ),
        )

        return replace(
            measurement,
            metadata={
                **measurement.metadata,
                "signal_quality": signal_quality,
            },
        )

    def _annotate_outliers(
        self,
        measurements: list[Measurement],
    ) -> list[Measurement]:
        result = list(
            measurements
        )

        by_definition = {}

        for index, measurement in enumerate(
            measurements
        ):
            by_definition.setdefault(
                measurement.definition.id,
                [],
            ).append(
                (
                    index,
                    measurement.value,
                )
            )

        for values in by_definition.values():
            indices = [
                item[0]
                for item in values
            ]
            numeric = [
                item[1]
                for item in values
            ]
            outliers = self._outliers.mad_outliers(
                numeric
            )

            for outlier_index in outliers:
                measurement_index = indices[
                    outlier_index
                ]
                measurement = result[
                    measurement_index
                ]
                result[
                    measurement_index
                ] = replace(
                    measurement,
                    metadata={
                        **measurement.metadata,
                        "outlier": True,
                    },
                )

        return result

    def _annotate_missing_data(
        self,
        measurement: Measurement,
    ) -> Measurement:
        coverage = float(
            measurement.metadata.get(
                "coverage",
                1.0,
            )
        )

        return replace(
            measurement,
            metadata={
                **measurement.metadata,
                "missing_data_estimated": coverage < 1.0,
            },
        )

    def _annotate_benchmark(
        self,
        measurement: Measurement,
        context: MeasurementContext,
    ) -> Measurement:
        benchmarks = context.metadata.get(
            "benchmarks",
            {},
        )
        cohort_values = benchmarks.get(
            measurement.definition.id
        )

        if not cohort_values:
            return measurement

        benchmark = self._benchmarks.compare(
            measurement.value,
            cohort_values,
            "context",
        )

        return replace(
            measurement,
            metadata={
                **measurement.metadata,
                "benchmark_percentile": benchmark.percentile,
                "benchmark_label": benchmark.label,
                "benchmark_cohort": benchmark.cohort,
            },
        )

    def _cross_source_verify(
        self,
        measurements: list[Measurement],
    ):
        by_definition = {}

        for measurement in measurements:
            by_definition.setdefault(
                measurement.definition.id,
                [],
            ).append(
                measurement
            )

        fused = []
        disagreements = []

        for definition_id, group in by_definition.items():
            sources = {
                measurement.provenance.source_system
                for measurement in group
            }

            if len(group) < 2 or len(sources) < 2:
                continue

            fused_measurement = self._fusion.fuse(
                group
            )
            fused.append(
                fused_measurement
            )

            disagreement = 1.0 - float(
                fused_measurement.metadata.get(
                    "agreement",
                    1.0,
                )
            )

            if disagreement > 0.2:
                disagreements.append(
                    CrossSourceDisagreement(
                        definition_id=definition_id,
                        measurement_ids=tuple(
                            measurement.id
                            for measurement in group
                        ),
                        disagreement_score=disagreement,
                    )
                )

        return fused, disagreements

    def _integrity_validation(
        self,
        measurement: Measurement,
    ) -> ValidationResult:
        errors = []

        if measurement.validation_status == ValidationStatus.FAILED:
            errors.append(
                "measurement failed upstream validation"
            )

        if measurement.confidence <= 0:
            errors.append(
                "measurement confidence is zero"
            )

        if errors:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                checks=("enterprise_accuracy",),
                errors=tuple(errors),
            )

        return ValidationResult(
            status=ValidationStatus.PASSED,
            checks=("enterprise_accuracy",),
        )


