from dataclasses import replace

from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementUnit
from app.intelligence.measurement.domain import NormalizationMethod
from app.intelligence.measurement.core.interfaces import MeasurementNormalizer


class IdentityNormalizer(MeasurementNormalizer):

    def supports(
        self,
        measurement: Measurement,
    ) -> bool:
        return True

    def normalize(
        self,
        measurement: Measurement,
    ) -> Measurement:
        method = NormalizationMethod(
            name="identity",
            version="1.0",
            source_unit=measurement.unit,
            target_unit=measurement.definition.unit,
        )

        return replace(
            measurement,
            normalization_method=method,
        )


class UnitConversionNormalizer(MeasurementNormalizer):

    def supports(
        self,
        measurement: Measurement,
    ) -> bool:
        return (
            measurement.unit,
            measurement.definition.unit,
        ) in {
            (
                MeasurementUnit.PERCENT,
                MeasurementUnit.RATIO,
            ),
            (
                MeasurementUnit.RATIO,
                MeasurementUnit.PERCENT,
            ),
        }

    def normalize(
        self,
        measurement: Measurement,
    ) -> Measurement:
        source_unit = measurement.unit
        target_unit = measurement.definition.unit
        value = measurement.value

        if (
            source_unit
            == MeasurementUnit.PERCENT
            and target_unit
            == MeasurementUnit.RATIO
        ):
            value = value / 100.0

        elif (
            source_unit
            == MeasurementUnit.RATIO
            and target_unit
            == MeasurementUnit.PERCENT
        ):
            value = value * 100.0

        return replace(
            measurement,
            unit=target_unit,
            value=value,
            normalization_method=NormalizationMethod(
                name="unit_conversion",
                version="1.0",
                source_unit=source_unit,
                target_unit=target_unit,
            ),
        )


class BoundedScoreNormalizer(MeasurementNormalizer):

    def supports(
        self,
        measurement: Measurement,
    ) -> bool:
        return (
            measurement.definition.unit
            == MeasurementUnit.SCORE
            and measurement.definition.minimum is not None
            and measurement.definition.maximum is not None
        )

    def normalize(
        self,
        measurement: Measurement,
    ) -> Measurement:
        minimum = measurement.definition.minimum
        maximum = measurement.definition.maximum

        if minimum is None or maximum is None:
            return measurement

        value = max(
            minimum,
            min(
                maximum,
                measurement.value,
            ),
        )

        return replace(
            measurement,
            value=value,
            unit=measurement.definition.unit,
            normalization_method=NormalizationMethod(
                name="bounded_score_clamp",
                version="1.0",
                source_unit=measurement.unit,
                target_unit=measurement.definition.unit,
                parameters={
                    "minimum": minimum,
                    "maximum": maximum,
                },
            ),
        )


