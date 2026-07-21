from dataclasses import replace

from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementContext
from app.intelligence.measurement.domain import ValidationResult
from app.intelligence.measurement.domain import ValidationStatus
from app.intelligence.measurement.core.interfaces import QualityScorer


class DefaultQualityScorer(QualityScorer):

    def score(
        self,
        measurement: Measurement,
        validation: ValidationResult,
        context: MeasurementContext,
    ) -> Measurement:
        validation_score = 1.0

        if validation.status == ValidationStatus.WARNING:
            validation_score = 0.75
        elif validation.status == ValidationStatus.FAILED:
            validation_score = 0.0

        interval_width = (
            measurement.uncertainty.upper_bound
            - measurement.uncertainty.lower_bound
        )

        scale = max(
            abs(
                measurement.value
            ),
            1.0,
        )

        uncertainty_score = max(
            0.0,
            1.0 - min(
                1.0,
                interval_width / (2.0 * scale),
            ),
        )

        quality = (
            0.45 * measurement.confidence
            + 0.30 * uncertainty_score
            + 0.25 * validation_score
        )

        quality = max(
            0.0,
            min(
                1.0,
                quality,
            ),
        )

        return replace(
            measurement,
            quality_score=quality,
            validation_status=validation.status,
            traceability=replace(
                measurement.traceability,
                validator_ids=validation.checks,
            ),
        )


class RecomputeQualityGate:
    MAX_ALLOWED_DRIFT_PERCENTAGE = 5.0  # 500%
    
    @classmethod
    def check_divergence(cls, old_value: float, new_value: float) -> tuple[bool, float]:
        """
        Calculates drift. Returns (is_safe, percentage_drift).
        If drift exceeds MAX_ALLOWED_DRIFT_PERCENTAGE, it requires manual human approval.
        """
        if old_value == 0.0:
            if new_value == 0.0:
                return True, 0.0
            return False, float('inf') # Infinite drift from zero requires approval
            
        drift = abs(new_value - old_value) / abs(old_value)
        is_safe = drift <= cls.MAX_ALLOWED_DRIFT_PERCENTAGE
        return is_safe, drift


