from math import isfinite

from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import ValidationResult
from app.intelligence.measurement.domain import ValidationStatus
from app.intelligence.measurement.core.interfaces import MeasurementValidator


class FiniteValueValidator(MeasurementValidator):

    def validate(
        self,
        measurement: Measurement,
    ) -> ValidationResult:
        if isfinite(
            measurement.value
        ):
            return ValidationResult(
                status=ValidationStatus.PASSED,
                checks=("finite_value",),
            )

        return ValidationResult(
            status=ValidationStatus.FAILED,
            checks=("finite_value",),
            errors=("measurement value is not finite",),
        )


class UnitValidator(MeasurementValidator):

    def validate(
        self,
        measurement: Measurement,
    ) -> ValidationResult:
        if measurement.unit == measurement.definition.unit:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                checks=("unit_matches_definition",),
            )

        return ValidationResult(
            status=ValidationStatus.FAILED,
            checks=("unit_matches_definition",),
            errors=(
                "measurement unit does not match definition unit",
            ),
        )


class RangeValidator(MeasurementValidator):

    def validate(
        self,
        measurement: Measurement,
    ) -> ValidationResult:
        minimum = measurement.definition.minimum
        maximum = measurement.definition.maximum

        warnings = []

        if (
            minimum is not None
            and measurement.value < minimum
        ):
            warnings.append(
                "measurement value is below definition minimum"
            )

        if (
            maximum is not None
            and measurement.value > maximum
        ):
            warnings.append(
                "measurement value is above definition maximum"
            )

        if warnings:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                checks=("range",),
                warnings=tuple(warnings),
            )

        return ValidationResult(
            status=ValidationStatus.PASSED,
            checks=("range",),
        )


def merge_validation_results(
    results: list[ValidationResult],
) -> ValidationResult:
    checks = []
    warnings = []
    errors = []
    status = ValidationStatus.PASSED

    for result in results:
        checks.extend(result.checks)
        warnings.extend(result.warnings)
        errors.extend(result.errors)

        if result.status == ValidationStatus.FAILED:
            status = ValidationStatus.FAILED
        elif (
            result.status == ValidationStatus.WARNING
            and status != ValidationStatus.FAILED
        ):
            status = ValidationStatus.WARNING

    return ValidationResult(
        status=status,
        checks=tuple(checks),
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


