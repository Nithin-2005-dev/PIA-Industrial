from __future__ import annotations

from datetime import datetime
from typing import Protocol

from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementContext
from app.intelligence.measurement.domain import MeasurementMethod
from app.intelligence.measurement.domain import MeasurementProvenance
from app.intelligence.measurement.domain import MeasurementTrace
from app.intelligence.measurement.domain import MeasurementUncertainty
from app.intelligence.measurement.domain import NormalizationMethod
from app.intelligence.measurement.domain import ValidationStatus
from app.intelligence.measurement.core.ids import stable_measurement_id
from app.intelligence.measurement.scientific_engine.registry import ScientificMeasurementRegistry
from app.ingestion.observation.domain import BuildFacts
from app.ingestion.observation.domain import CommitFacts
from app.ingestion.observation.domain import DeploymentFacts
from app.ingestion.observation.domain import DocumentationFacts
from app.ingestion.observation.domain import IssueFacts
from app.ingestion.observation.domain import Observation
from app.ingestion.observation.domain import ObservationType
from app.ingestion.observation.domain import PullRequestFacts
from app.ingestion.observation.domain import ReviewFacts
from app.ingestion.observation.domain import TestFacts


class MeasurementProvider(Protocol):
    name: str
    version: str
    supported_types: tuple[ObservationType, ...]

    def measure(
        self,
        observation: Observation,
        context: MeasurementContext,
        registry: ScientificMeasurementRegistry,
    ) -> tuple[Measurement, ...]:
        ...


class MeasurementProviderRegistry:
    def __init__(
        self,
        providers: tuple[MeasurementProvider, ...] = (),
    ):
        self._providers: dict[str, MeasurementProvider] = {}
        for provider in providers:
            self.register(provider)

    def register(
        self,
        provider: MeasurementProvider,
    ) -> None:
        self._providers[provider.name] = provider

    def all(
        self,
    ) -> tuple[MeasurementProvider, ...]:
        return tuple(self._providers.values())


class BaseMeasurementProvider:
    name = "base"
    version = "1.0"
    supported_types: tuple[ObservationType, ...] = ()

    def _measurement(
        self,
        observation: Observation,
        context: MeasurementContext,
        registry: ScientificMeasurementRegistry,
        measurement_id: str,
        value: float,
        precision: float = 1.0,
        metadata: dict | None = None,
    ) -> Measurement:
        definition = registry.get(measurement_id)
        measurement_definition = definition.to_measurement_definition()
        timestamp = context.timestamp or observation.timestamp
        return Measurement(
            id=stable_measurement_id(
                observation.observation_id,
                self.name,
                measurement_id,
                self.version,
            ),
            definition=measurement_definition,
            unit=definition.unit,
            value=float(value),
            confidence=0.95,
            uncertainty=MeasurementUncertainty(
                lower_bound=float(value) - precision,
                upper_bound=float(value) + precision,
                variance=precision * precision,
                method="deterministic_precision_bound",
            ),
            quality_score=0.95,
            measurement_method=MeasurementMethod(
                name=self.name,
                version=self.version,
                algorithm="pure_observation_feature_extraction",
            ),
            normalization_method=NormalizationMethod(
                name="identity",
                version="1.0",
                source_unit=definition.unit,
                target_unit=definition.unit,
            ),
            provenance=MeasurementProvenance(
                source_system=observation.source_platform,
                adapter=observation.source_adapter,
                source_observation_id=observation.observation_id,
                source_entity_ids=tuple(
                    target.id
                    for target in observation.targets
                ),
                tenant_id=observation.context.tenant_id,
                target_entity=(
                    observation.targets[0].id
                    if observation.targets
                    else None
                ),
                target_entity_type=(
                    observation.targets[0].type.value
                    if observation.targets
                    else None
                ),
            ),
            timestamp=timestamp if isinstance(timestamp, datetime) else observation.timestamp,
            version=definition.version,
            traceability=MeasurementTrace(
                pipeline_version=context.pipeline_version,
                evaluator=self.name,
                lineage_node_id=stable_measurement_id(
                    "lineage",
                    observation.observation_id,
                    measurement_id,
                ),
            ),
            validation_status=ValidationStatus.NOT_RUN,
            metadata={
                "actor_ids": tuple(
                    actor.id
                    for actor in observation.actors
                ),
                "precision": precision,
                "provider": self.name,
                **(metadata or {}),
            },
        )


class StructuralMeasurementProvider(BaseMeasurementProvider):
    name = "structural"
    supported_types = (ObservationType.COMMIT,)

    def measure(
        self,
        observation: Observation,
        context: MeasurementContext,
        registry: ScientificMeasurementRegistry,
    ) -> tuple[Measurement, ...]:
        if not isinstance(observation.facts, CommitFacts):
            return ()
        facts = observation.facts
        directories = {
            "/".join(file.path.replace("\\", "/").split("/")[:-1])
            for file in facts.files
        }
        directories.discard("")
        return (
            self._measurement(observation, context, registry, "lines_added", facts.total_additions),
            self._measurement(observation, context, registry, "lines_deleted", facts.total_deletions),
            self._measurement(observation, context, registry, "files_modified", len(facts.files)),
            self._measurement(observation, context, registry, "directories_changed", len(directories)),
        )


class ReviewMeasurementProvider(BaseMeasurementProvider):
    name = "review"
    supported_types = (
        ObservationType.PULL_REQUEST,
        ObservationType.REVIEW,
    )

    def measure(
        self,
        observation: Observation,
        context: MeasurementContext,
        registry: ScientificMeasurementRegistry,
    ) -> tuple[Measurement, ...]:
        facts = observation.facts
        if isinstance(facts, PullRequestFacts):
            latency = 0.0
            end = facts.merged_at or facts.closed_at or facts.updated_at
            if end is not None:
                latency = max(0.0, (end - facts.created_at).total_seconds())
            return (
                self._measurement(observation, context, registry, "review_latency_seconds", latency, precision=0.001),
            )
        if isinstance(facts, ReviewFacts):
            return (
                self._measurement(observation, context, registry, "review_count", 1),
                self._measurement(observation, context, registry, "comment_count", facts.comment_count),
            )
        return ()


class RepositoryMeasurementProvider(BaseMeasurementProvider):
    name = "repository"
    supported_types = (ObservationType.ISSUE,)

    def measure(
        self,
        observation: Observation,
        context: MeasurementContext,
        registry: ScientificMeasurementRegistry,
    ) -> tuple[Measurement, ...]:
        if not isinstance(observation.facts, IssueFacts):
            return ()
        facts = observation.facts
        resolution = 0.0
        if facts.closed_at is not None:
            resolution = max(0.0, (facts.closed_at - facts.created_at).total_seconds())
        return (
            self._measurement(observation, context, registry, "issue_resolution_seconds", resolution, precision=0.001),
            self._measurement(observation, context, registry, "label_count", len(facts.labels)),
        )


class EngineeringMeasurementProvider(BaseMeasurementProvider):
    name = "engineering"
    supported_types = (
        ObservationType.BUILD,
        ObservationType.TEST,
        ObservationType.DEPLOYMENT,
    )

    def measure(
        self,
        observation: Observation,
        context: MeasurementContext,
        registry: ScientificMeasurementRegistry,
    ) -> tuple[Measurement, ...]:
        facts = observation.facts
        if isinstance(facts, BuildFacts):
            return (
                self._measurement(observation, context, registry, "build_duration_seconds", facts.duration_seconds or 0.0, precision=0.001),
            )
        if isinstance(facts, TestFacts):
            return (
                self._measurement(observation, context, registry, "test_failures", facts.failed),
            )
        if isinstance(facts, DeploymentFacts):
            return (
                self._measurement(observation, context, registry, "deployment_duration_seconds", 0.0, precision=0.001),
            )
        return ()


class DocumentationMeasurementProvider(BaseMeasurementProvider):
    name = "documentation"
    supported_types = (ObservationType.DOCUMENTATION,)

    def measure(
        self,
        observation: Observation,
        context: MeasurementContext,
        registry: ScientificMeasurementRegistry,
    ) -> tuple[Measurement, ...]:
        if not isinstance(observation.facts, DocumentationFacts):
            return ()
        depth = len(
            [
                part
                for part in observation.facts.path.replace("\\", "/").split("/")
                if part
            ]
        )
        return (
            self._measurement(observation, context, registry, "document_path_depth", depth),
        )


class StaticAnalysisMeasurementProvider(BaseMeasurementProvider):
    name = "static_analysis"
    supported_types = (ObservationType.COMMIT,)

    def measure(
        self,
        observation: Observation,
        context: MeasurementContext,
        registry: ScientificMeasurementRegistry,
    ) -> tuple[Measurement, ...]:
        if not isinstance(observation.facts, CommitFacts):
            return ()
        facts = observation.facts
        files = facts.files
        file_count = max(1, len(files))
        total_changed = facts.total_changes or sum(
            file.changes
            for file in files
        )
        test_files = [
            file
            for file in files
            if self._is_test_path(file.path)
        ]
        largest_file_delta = max(
            (
                file.changes
                for file in files
            ),
            default=0,
        )
        patch_complexity = sum(
            self._patch_complexity(file.patch)
            for file in files
        ) + len(files)
        churn_ratio = (
            (
                facts.total_additions
                + facts.total_deletions
            )
            / max(1.0, float(total_changed))
        )

        return (
            self._measurement(
                observation,
                context,
                registry,
                "code_churn_ratio",
                min(1.0, churn_ratio),
                precision=0.001,
            ),
            self._measurement(
                observation,
                context,
                registry,
                "test_file_touch_ratio",
                len(test_files) / file_count,
                precision=0.001,
            ),
            self._measurement(
                observation,
                context,
                registry,
                "largest_file_delta",
                largest_file_delta,
            ),
            self._measurement(
                observation,
                context,
                registry,
                "patch_complexity_score",
                patch_complexity,
            ),
        )

    def _is_test_path(
        self,
        path: str,
    ) -> bool:
        normalized = path.replace("\\", "/").lower()
        return (
            "/test/" in normalized
            or "/tests/" in normalized
            or normalized.startswith("test_")
            or normalized.endswith("_test.py")
            or normalized.endswith(".test.ts")
            or normalized.endswith(".spec.ts")
        )

    def _patch_complexity(
        self,
        patch: str | None,
    ) -> int:
        if not patch:
            return 0
        keywords = (
            " if ",
            " elif ",
            " for ",
            " while ",
            " case ",
            " catch ",
            "&&",
            "||",
            "?",
        )
        lowered = f" {patch.lower()} "
        return sum(
            lowered.count(keyword)
            for keyword in keywords
        )


def default_measurement_providers(
) -> tuple[MeasurementProvider, ...]:
    return (
        StructuralMeasurementProvider(),
        StaticAnalysisMeasurementProvider(),
        ReviewMeasurementProvider(),
        RepositoryMeasurementProvider(),
        EngineeringMeasurementProvider(),
        DocumentationMeasurementProvider(),
    )
