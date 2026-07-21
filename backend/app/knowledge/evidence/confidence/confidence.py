from dataclasses import dataclass
from datetime import datetime
from datetime import timezone

from app.knowledge.evidence.domain import EvidenceMeasurementRef
from app.knowledge.evidence.knowledge.definitions import EvidenceDefinition


@dataclass(frozen=True)
class EvidenceConfidenceScore:
    value: float
    uncertainty: float
    quality: float
    strength: float
    factors: dict[str, float]
    explanation: str


class EvidenceConfidenceEngine:

    def __init__(self, category_half_lives_days: dict[str, int] | None = None):
        self._category_half_lives_days = category_half_lives_days or {
            "developer": 90,
            "architecture": 365,
            "ownership": 365,
            "maintainability": 180,
            "testing": 180,
            "documentation": 365,
        }

    def aggregate(
        self,
        definition: EvidenceDefinition,
        supporting_measurements: tuple[EvidenceMeasurementRef, ...],
        validation_factor: float = 1.0,
    ) -> EvidenceConfidenceScore:
        if not supporting_measurements:
            return EvidenceConfidenceScore(
                value=0.0,
                uncertainty=1.0,
                quality=0.0,
                strength=0.0,
                factors={},
                explanation="No supporting measurements were available.",
            )

        measurement_confidence = sum(
            measurement.confidence
            for measurement in supporting_measurements
        ) / len(
            supporting_measurements
        )

        relative_uncertainties = []
        for measurement in supporting_measurements:
            relative_uncertainties.append(
                (
                    max(
                        0.0,
                        measurement.uncertainty_variance,
                    )
                    ** 0.5
                )
                / (
                    abs(
                        measurement.value
                    )
                    + 1.0
                )
            )

        average_uncertainty = sum(
            relative_uncertainties
        ) / len(
            relative_uncertainties
        )

        uncertainty_factor = max(
            0.0,
            min(
                1.0,
                1.0 - average_uncertainty,
            ),
        )

        quality = sum(
            measurement.quality_score
            for measurement in supporting_measurements
        ) / len(
            supporting_measurements
        )

        source_count = len(
            {
                measurement.source_system
                for measurement in supporting_measurements
            }
        )
        source_diversity = min(
            1.0,
            0.5 + (source_count * 0.25),
        )

        entity_count = len(
            {
                entity_id
                for measurement in supporting_measurements
                for entity_id in measurement.entity_ids
            }
        )
        cross_source_agreement = min(
            1.0,
            0.7 + (entity_count * 0.05),
        )

        benchmark_quality = float(
            definition.metadata.get(
                "benchmark_quality",
                1.0,
            )
        )
        historical_consistency = float(
            definition.metadata.get(
                "historical_consistency",
                1.0,
            )
        )

        now = datetime.now(timezone.utc)
        ages_in_days = []
        for m in supporting_measurements:
            try:
                if isinstance(m.timestamp, str):
                    ts_str = m.timestamp.replace("Z", "+00:00")
                    dt = datetime.fromisoformat(ts_str)
                else:
                    dt = m.timestamp
                # Ensure it's timezone aware
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                age = (now - dt).days
                ages_in_days.append(max(0.0, float(age)))
            except (ValueError, AttributeError, TypeError):
                ages_in_days.append(0.0)

        average_age = sum(ages_in_days) / len(ages_in_days)
        half_life = self._category_half_lives_days.get(definition.category, 365)
        
        # Exponential decay: 0.5 ^ (time / half_life)
        temporal_decay = 0.5 ** (average_age / half_life)

        factors = {
            "measurement_confidence": measurement_confidence,
            "measurement_uncertainty": uncertainty_factor,
            "source_diversity": source_diversity,
            "evidence_rule_reliability": definition.rule_reliability,
            "benchmark_quality": benchmark_quality,
            "historical_consistency": historical_consistency,
            "cross_source_agreement": cross_source_agreement,
            "temporal_decay": temporal_decay,
            "validation_results": validation_factor,
        }

        value = 1.0
        for factor in factors.values():
            value *= max(
                0.0,
                min(
                    1.0,
                    factor,
                ),
            )

        value = max(
            0.0,
            min(
                1.0,
                value,
            ),
        )
        strength = value * quality * (
            1.0 + definition.severity.rank()
        ) / 5.0

        return EvidenceConfidenceScore(
            value=value,
            uncertainty=1.0 - uncertainty_factor,
            quality=quality,
            strength=strength,
            factors=factors,
            explanation=(
                "confidence = product(measurement confidence, "
                "uncertainty factor, source diversity, rule reliability, "
                "benchmark quality, historical consistency, agreement, "
                "temporal decay, validation factor)"
            ),
        )
