from dataclasses import dataclass
from dataclasses import fields
from datetime import UTC, datetime
from enum import Enum

from app.ingestion.observation.domain import Observation
from app.ingestion.observation.domain import ObservationLifecycle
from app.knowledge.evidence.ontology import ObservationOntology
from app.ingestion.observation.registry import ObservationRegistry


class ObservationValidationStatus(Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


@dataclass(frozen=True)
class ObservationValidationResult:
    status: ObservationValidationStatus
    checks: tuple[str, ...]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()


class ObservationValidationPipeline:

    def __init__(
        self,
        registry: ObservationRegistry | None = None,
        ontology: ObservationOntology | None = None,
    ):
        self._registry = registry or ObservationRegistry.default()
        self._ontology = ontology or ObservationOntology.default()
        self._seen_ids: set[str] = set()

    def validate(
        self,
        observation: Observation,
    ) -> ObservationValidationResult:
        checks = (
            "schema",
            "type",
            "timestamp",
            "duplicate",
            "malformed",
            "required",
            "source",
            "version",
            "ontology",
        )
        errors: list[str] = []
        warnings: list[str] = []

        if observation.observation_id in self._seen_ids:
            errors.append(
                "duplicate observation id"
            )

        if not self._ontology.has_category(
            observation.observation_category
        ):
            errors.append(
                "unknown observation category"
            )

        try:
            definition = self._registry.for_observation(
                observation.observation_type,
                observation.version,
            )
        except KeyError:
            errors.append(
                "observation definition is not registered"
            )
            definition = None

        if definition is not None:
            if observation.observation_category != definition.category:
                errors.append(
                    "observation category does not match registry"
                )

            if type(
                observation.facts
            ).__name__ != definition.schema:
                errors.append(
                    "observation facts schema does not match registry"
                )

            supported = set(
                definition.supported_adapters
            )
            if (
                observation.source_platform not in supported
                and observation.source_adapter not in supported
            ):
                errors.append(
                    "source adapter is not registered for observation type"
                )

            if definition.lifecycle in {
                ObservationLifecycle.DEPRECATED,
                ObservationLifecycle.ARCHIVED,
            }:
                errors.append(
                    "observation definition is not active"
                )

            errors.extend(
                self._required_field_errors(
                    observation,
                    definition.required_fields,
                )
            )

        timestamp = observation.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(
                tzinfo=UTC
            )

        if timestamp > datetime.now(
            UTC
        ):
            warnings.append(
                "observation timestamp is in the future"
            )

        if not observation.observation_id:
            errors.append(
                "observation id is required"
            )

        if not observation.trace_id:
            errors.append(
                "trace id is required"
            )

        if not observation.correlation_id:
            errors.append(
                "correlation id is required"
            )

        if not observation.source_platform:
            errors.append(
                "source platform is required"
            )

        if not observation.source_adapter:
            errors.append(
                "source adapter is required"
            )

        if observation.version != "1.0":
            errors.append(
                "unsupported observation version"
            )

        if errors:
            return ObservationValidationResult(
                status=ObservationValidationStatus.FAILED,
                checks=checks,
                warnings=tuple(
                    warnings
                ),
                errors=tuple(
                    errors
                ),
            )

        self._seen_ids.add(
            observation.observation_id
        )

        if warnings:
            return ObservationValidationResult(
                status=ObservationValidationStatus.WARNING,
                checks=checks,
                warnings=tuple(
                    warnings
                ),
            )

        return ObservationValidationResult(
            status=ObservationValidationStatus.PASSED,
            checks=checks,
        )

    def _required_field_errors(
        self,
        observation: Observation,
        required_fields: tuple[str, ...],
    ) -> tuple[str, ...]:
        fact_fields = {
            field.name
            for field in fields(
                observation.facts
            )
        }
        errors = []

        for required in required_fields:
            if required not in fact_fields:
                errors.append(
                    f"required field {required} is not in facts schema"
                )
                continue

            value = getattr(
                observation.facts,
                required,
            )
            if value is None or value == "":
                errors.append(
                    f"required field {required} is empty"
                )

        return tuple(
            errors
        )
