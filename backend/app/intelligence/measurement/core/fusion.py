from dataclasses import replace

from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementTrace
from app.intelligence.measurement.domain import MeasurementUncertainty
from app.intelligence.measurement.core.ids import stable_measurement_id


class MultiSourceFusionEngine:

    def fuse(
        self,
        measurements: list[Measurement],
    ) -> Measurement:
        if not measurements:
            raise ValueError(
                "cannot fuse empty measurement set"
            )

        first = measurements[0]

        total_weight = sum(
            max(
                measurement.confidence,
                0.001,
            )
            for measurement in measurements
        )

        value = sum(
            measurement.value
            * max(
                measurement.confidence,
                0.001,
            )
            for measurement in measurements
        ) / total_weight

        agreement = self._agreement(
            [
                measurement.value
                for measurement in measurements
            ],
            value,
        )

        confidence = min(
            1.0,
            (
                sum(
                    measurement.confidence
                    for measurement in measurements
                )
                / len(
                    measurements
                )
            )
            * agreement,
        )

        width = max(
            abs(
                measurement.value - value
            )
            for measurement in measurements
        )

        dependencies = tuple(
            measurement.id
            for measurement in measurements
        )

        return replace(
            first,
            id=stable_measurement_id(
                "fused",
                first.definition.id,
                *dependencies,
            ),
            value=value,
            confidence=confidence,
            uncertainty=MeasurementUncertainty(
                lower_bound=value - width,
                upper_bound=value + width,
                variance=width * width,
                method="confidence_weighted_fusion",
            ),
            quality_score=min(
                1.0,
                confidence * agreement,
            ),
            provenance=replace(
                first.provenance,
                source_signal_ids=dependencies,
                transformations=(
                    *first.provenance.transformations,
                    "multi_source_fusion",
                ),
            ),
            traceability=MeasurementTrace(
                pipeline_version=(
                    first.traceability.pipeline_version
                ),
                dependency_ids=dependencies,
                evaluator="multi_source_fusion",
            ),
            dependencies=dependencies,
            metadata={
                **first.metadata,
                "agreement": agreement,
                "source_count": len(
                    measurements
                ),
            },
        )

    def _agreement(
        self,
        values: list[float],
        center: float,
    ) -> float:
        scale = max(
            abs(
                center
            ),
            1.0,
        )

        mean_error = sum(
            abs(
                value - center
            )
            for value in values
        ) / len(
            values
        )

        return max(
            0.0,
            1.0 - min(
                1.0,
                mean_error / scale,
            ),
        )


class ProbabilisticFusionEngine:
    """
    Reliability-weighted Bayesian-style fusion for measurements of one
    concept. This keeps deterministic source measurements intact while
    producing a posterior-like fused value and uncertainty interval.
    """

    def fuse(
        self,
        measurements: list[Measurement],
    ) -> Measurement:
        if not measurements:
            raise ValueError(
                "cannot fuse empty measurement set"
            )

        first = measurements[0]

        precisions = []

        for measurement in measurements:
            variance = max(
                measurement.uncertainty.variance,
                0.0001,
            )
            precisions.append(
                max(
                    measurement.confidence,
                    0.001,
                )
                / variance
            )

        total_precision = sum(
            precisions
        )

        value = sum(
            measurement.value * precisions[index]
            for index, measurement in enumerate(
                measurements
            )
        ) / total_precision

        posterior_variance = 1.0 / total_precision
        width = posterior_variance ** 0.5

        agreement = MultiSourceFusionEngine()._agreement(
            [
                measurement.value
                for measurement in measurements
            ],
            value,
        )

        confidence = min(
            1.0,
            agreement
            * sum(
                measurement.confidence
                for measurement in measurements
            )
            / len(
                measurements
            ),
        )

        dependencies = tuple(
            measurement.id
            for measurement in measurements
        )

        return replace(
            first,
            id=stable_measurement_id(
                "probabilistic_fused",
                first.definition.id,
                *dependencies,
            ),
            value=value,
            confidence=confidence,
            uncertainty=MeasurementUncertainty(
                lower_bound=value - width,
                upper_bound=value + width,
                variance=posterior_variance,
                method="precision_weighted_bayesian_fusion",
                parameters={
                    "agreement": agreement,
                    "source_count": len(
                        measurements
                    ),
                },
            ),
            quality_score=min(
                1.0,
                confidence * agreement,
            ),
            provenance=replace(
                first.provenance,
                source_signal_ids=dependencies,
                transformations=(
                    *first.provenance.transformations,
                    "probabilistic_fusion",
                ),
            ),
            traceability=MeasurementTrace(
                pipeline_version=(
                    first.traceability.pipeline_version
                ),
                dependency_ids=dependencies,
                evaluator="probabilistic_fusion",
            ),
            dependencies=dependencies,
            metadata={
                **first.metadata,
                "agreement": agreement,
                "fusion": "precision_weighted_bayesian",
                "source_count": len(
                    measurements
                ),
            },
        )


