from dataclasses import replace

from app.intelligence.measurement.domain import ConfidenceBreakdown
from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementContext
from app.intelligence.measurement.domain import MeasurementUncertainty
from app.intelligence.measurement.core.interfaces import ConfidenceEstimator


class DefaultConfidenceEstimator(ConfidenceEstimator):

    def estimate(
        self,
        measurement: Measurement,
        context: MeasurementContext,
    ) -> Measurement:
        source_reliability = context.source_reliability.get(
            measurement.provenance.source_system,
            0.75,
        )

        coverage = float(
            measurement.metadata.get(
                "coverage",
                1.0,
            )
        )

        agreement = float(
            measurement.metadata.get(
                "agreement",
                1.0,
            )
        )

        missing_penalty = float(
            measurement.metadata.get(
                "missing_penalty",
                0.0,
            )
        )

        freshness = float(
            measurement.metadata.get(
                "freshness",
                1.0,
            )
        )

        historical_stability = float(
            measurement.metadata.get(
                "historical_stability",
                1.0,
            )
        )

        breakdown = ConfidenceBreakdown(
            source_reliability=source_reliability,
            coverage=coverage,
            agreement=agreement,
            freshness=freshness,
            historical_stability=historical_stability,
            missing_data=missing_penalty,
        )

        confidence = breakdown.value()

        absolute_value = abs(
            measurement.value
        )

        error_width = (
            max(
                absolute_value,
                1.0,
            )
            * (1.0 - confidence)
        )

        uncertainty = MeasurementUncertainty(
            lower_bound=measurement.value - error_width,
            upper_bound=measurement.value + error_width,
            variance=error_width * error_width,
            parameters={
                "source_reliability": source_reliability,
                "coverage": coverage,
                "agreement": agreement,
                "missing_penalty": missing_penalty,
            },
        )

        return replace(
            measurement,
            confidence=confidence,
            uncertainty=uncertainty,
            confidence_breakdown=breakdown,
        )


