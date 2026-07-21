from app.intelligence.measurement.domain import SoftwareSignal
from app.intelligence.measurement.domain import ValidationResult
from app.intelligence.measurement.domain import ValidationStatus
from app.kernel.classifiers.mapping import MappingResolution
from app.kernel.classifiers.signal_classifier import SignalClassification
from app.kernel.classifiers.signals import SignalDefinition


class SignalDefinitionValidator:

    def validate_value(
        self,
        signal: SoftwareSignal,
        definition: SignalDefinition,
    ) -> ValidationResult:
        errors = []

        if signal.unit != definition.unit:
            errors.append(
                "signal unit does not match registered definition"
            )

        expected = definition.expected_range

        if (
            expected is not None
            and isinstance(signal.value, int | float)
        ):
            if (
                expected.minimum is not None
                and signal.value < expected.minimum
            ):
                errors.append(
                    "signal value below expected range"
                )

            if (
                expected.maximum is not None
                and signal.value > expected.maximum
            ):
                errors.append(
                    "signal value above expected range"
                )

        if errors:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                checks=("signal_definition",),
                errors=tuple(errors),
            )

        return ValidationResult(
            status=ValidationStatus.PASSED,
            checks=("signal_definition",),
        )


class SemanticMappingValidator:

    def validate(
        self,
        classification: SignalClassification,
        resolution: MappingResolution,
    ) -> ValidationResult:
        errors = []

        if classification.requires_human_approval:
            errors.append(
                "mapping requires human approval"
            )

        if not resolution.definitions:
            errors.append(
                "mapping resolved no measurement definitions"
            )

        for definition in resolution.definitions:
            if (
                definition.concept_id is not None
                and resolution.mappings
                and definition.concept_id
                != resolution.mappings[0].concept_id
            ):
                errors.append(
                    "mapping concept does not match measurement definition"
                )

        if errors:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                checks=("semantic_mapping",),
                errors=tuple(errors),
            )

        return ValidationResult(
            status=ValidationStatus.PASSED,
            checks=("semantic_mapping",),
        )


