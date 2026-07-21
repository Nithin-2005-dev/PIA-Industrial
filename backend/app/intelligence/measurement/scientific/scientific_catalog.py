from dataclasses import dataclass

from app.intelligence.measurement.scientific.accuracy_profiles import AccuracyProfileRegistry
from app.intelligence.measurement.scientific.accuracy_profiles import MeasurementAccuracyProfile
from app.intelligence.measurement.domain import ExpectedRange
from app.intelligence.measurement.domain import MeasurementDefinition
from app.intelligence.measurement.domain import MeasurementReference
from app.intelligence.measurement.domain import MeasurementUnit
from app.knowledge.evidence.knowledge.measurement_knowledge import MeasurementDefinitionKnowledge
from app.knowledge.evidence.knowledge.measurement_knowledge import SoftwareMeasurementKnowledgeBase
from app.intelligence.measurement.domain.registry import MeasurementRegistry


@dataclass(frozen=True)
class ScientificMeasurementSpec:
    id: str
    name: str
    domain: str
    unit: MeasurementUnit
    scientific_definition: str
    business_definition: str
    formula: str
    required_signals: tuple[str, ...]
    dependencies: tuple[str, ...] = ()
    expected_minimum: float | None = None
    expected_maximum: float | None = None
    validation_rules: tuple[str, ...] = (
        "schema",
        "semantic",
        "statistical",
        "benchmark",
        "historical_consistency",
    )
    assumptions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    standards: tuple[str, ...] = ()
    research: tuple[str, ...] = ()


class EnterpriseMeasurementCatalog:

    @classmethod
    def build_registry(
        cls,
    ) -> MeasurementRegistry:
        registry = MeasurementRegistry()

        for definition in cls.definitions():
            registry.register(
                definition
            )

        return registry

    @classmethod
    def build_knowledge_base(
        cls,
    ) -> SoftwareMeasurementKnowledgeBase:
        base = SoftwareMeasurementKnowledgeBase()

        for knowledge in cls.knowledge_entries():
            base.register(
                knowledge
            )

        return base

    @classmethod
    def build_accuracy_profiles(
        cls,
    ) -> AccuracyProfileRegistry:
        registry = AccuracyProfileRegistry()

        for spec in cls.specs():
            registry.register(
                MeasurementAccuracyProfile(
                    measurement_id=spec.id,
                    expected_error=0.1,
                    confidence_calibration=(
                        "empirical reliability curve by benchmark cohort"
                    ),
                    known_biases=(
                        "adapter sampling bias",
                        "repository structure bias",
                    ),
                    sensitivity="medium",
                    robustness="requires corroborating signals",
                    reliability=0.8,
                    minimum_required_signals=spec.required_signals,
                    recommended_interpretation=spec.business_definition,
                    failure_conditions=(
                        "missing required signals",
                        "unsupported repository topology",
                    ),
                )
            )

        return registry

    @classmethod
    def definitions(
        cls,
    ) -> list[MeasurementDefinition]:
        references = (
            MeasurementReference(
                title="ISO/IEC 15939",
                source="ISO/IEC",
                identifier="ISO-15939",
            ),
            MeasurementReference(
                title="ISO/IEC 25010",
                source="ISO/IEC",
                identifier="ISO-25010",
            ),
        )

        definitions = []

        for spec in cls.specs():
            definitions.append(
                MeasurementDefinition(
                    id=spec.id,
                    name=spec.name,
                    description=spec.business_definition,
                    unit=spec.unit,
                    version="1.0",
                    minimum=spec.expected_minimum,
                    maximum=spec.expected_maximum,
                    tags=(
                        spec.domain,
                        "enterprise_catalog",
                    ),
                    concept_id=spec.domain,
                    category=spec.domain,
                    expected_range=ExpectedRange(
                        minimum=spec.expected_minimum,
                        maximum=spec.expected_maximum,
                    ),
                    formula=spec.formula,
                    dependencies=spec.dependencies,
                    required_signals=spec.required_signals,
                    confidence_model=(
                        "source reliability x coverage x agreement "
                        "x historical stability"
                    ),
                    validator="scientific_validation_pipeline",
                    normalizer="domain_normalization_pipeline",
                    aggregation_strategy="domain_specific",
                    references=references,
                )
            )

        return definitions

    @classmethod
    def knowledge_entries(
        cls,
    ) -> list[MeasurementDefinitionKnowledge]:
        entries = []

        for spec in cls.specs():
            entries.append(
                MeasurementDefinitionKnowledge(
                    measurement_id=spec.id,
                    scientific_definition=spec.scientific_definition,
                    business_definition=spec.business_definition,
                    formula=spec.formula,
                    dependencies=spec.dependencies,
                    required_signals=spec.required_signals,
                    units=spec.unit.value,
                    expected_range=str(
                        (
                            spec.expected_minimum,
                            spec.expected_maximum,
                        )
                    ),
                    confidence_model=(
                        "calibrated empirical reliability model"
                    ),
                    uncertainty_model=(
                        "bounded interval with benchmark-calibrated "
                        "variance"
                    ),
                    validation_rules=spec.validation_rules,
                    normalization_strategy=(
                        "domain normalization with benchmark context"
                    ),
                    aggregation_strategy="domain-specific aggregation",
                    benchmark_strategy=(
                        "repository, language, organization and size cohorts"
                    ),
                    interpretation_guide=spec.business_definition,
                    assumptions=spec.assumptions,
                    known_limitations=spec.limitations,
                    standards_references=spec.standards,
                    research_references=spec.research,
                    version_history=("1.0 enterprise catalog definition",),
                )
            )

        return entries

    @classmethod
    def specs(
        cls,
    ) -> list[ScientificMeasurementSpec]:
        return [
            *cls._architecture(),
            *cls._code_quality(),
            *cls._git_analytics(),
            *cls._devops(),
            *cls._testing(),
            *cls._runtime(),
            *cls._security(),
            *cls._cloud(),
            *cls._ai_engineering(),
        ]

    @classmethod
    def _spec(
        cls,
        domain,
        name,
        unit=MeasurementUnit.SCORE,
        formula="domain_specific_formula",
        required_signals=("domain_signal",),
        minimum=0.0,
        maximum=100.0,
    ):
        measurement_id = (
            name
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
        )

        return ScientificMeasurementSpec(
            id=measurement_id,
            name=name,
            domain=domain,
            unit=unit,
            scientific_definition=(
                f"{name} quantifies the {domain.replace('_', ' ')} "
                "property using normalized software engineering signals."
            ),
            business_definition=(
                f"{name} helps teams understand {domain.replace('_', ' ')} "
                "risk, quality or performance."
            ),
            formula=formula,
            required_signals=required_signals,
            expected_minimum=minimum,
            expected_maximum=maximum,
            assumptions=(
                "required signals are collected consistently",
            ),
            limitations=(
                "interpretation depends on repository and organization context",
            ),
            standards=(
                "ISO-15939",
                "ISO-25010",
            ),
            research=(
                "Empirical Software Engineering",
                "Mining Software Repositories",
            ),
        )

    @classmethod
    def _architecture(cls):
        names = (
            "Coupling",
            "Cohesion",
            "Instability",
            "Package Cyclicity",
            "Layer Violations",
            "Dependency Density",
            "Architectural Drift",
            "Structural Entropy",
        )

        return [
            cls._spec(
                "architecture",
                name,
                MeasurementUnit.SCORE,
                required_signals=(
                    "dependency_graph",
                    "module_graph",
                ),
            )
            for name in names
        ]

    @classmethod
    def _code_quality(cls):
        names = (
            "Cyclomatic Complexity",
            "Cognitive Complexity",
            "Maintainability Index",
            "Duplication",
            "Readability",
            "Technical Debt",
            "Documentation Coverage",
            "Code Smells",
        )

        return [
            cls._spec(
                "code_quality",
                name,
                MeasurementUnit.SCORE,
                required_signals=(
                    "ast",
                    "static_analysis",
                ),
            )
            for name in names
        ]

    @classmethod
    def _git_analytics(cls):
        names = (
            "Code Churn",
            "Ownership",
            "Bus Factor",
            "Change Frequency",
            "Hotspots",
            "Review Latency",
            "Review Coverage",
            "Commit Risk",
        )

        return [
            cls._spec(
                "git_analytics",
                name,
                MeasurementUnit.SCORE,
                required_signals=(
                    "git_commits",
                    "pull_requests",
                ),
            )
            for name in names
        ]

    @classmethod
    def _devops(cls):
        names = (
            "Deployment Frequency",
            "Lead Time",
            "MTTR",
            "Change Failure Rate",
            "Build Stability",
            "Release Stability",
        )

        return [
            cls._spec(
                "devops",
                name,
                MeasurementUnit.SCORE,
                required_signals=(
                    "ci_cd",
                    "deployments",
                ),
            )
            for name in names
        ]

    @classmethod
    def _testing(cls):
        names = (
            "Coverage",
            "Mutation Score",
            "Test Stability",
            "Test Flakiness",
            "Test Effectiveness",
        )

        return [
            cls._spec(
                "testing",
                name,
                MeasurementUnit.SCORE,
                required_signals=(
                    "coverage",
                    "test_results",
                ),
            )
            for name in names
        ]

    @classmethod
    def _runtime(cls):
        names = (
            "Availability",
            "Error Rate",
            "Tail Latency",
            "Throughput",
            "Saturation",
            "Resource Efficiency",
        )

        return [
            cls._spec(
                "runtime",
                name,
                MeasurementUnit.SCORE,
                required_signals=(
                    "runtime_telemetry",
                    "logs",
                ),
            )
            for name in names
        ]

    @classmethod
    def _security(cls):
        names = (
            "Vulnerability Density",
            "Dependency Risk",
            "Secret Exposure",
            "Supply Chain Risk",
            "Security Debt",
        )

        return [
            cls._spec(
                "security",
                name,
                MeasurementUnit.SCORE,
                required_signals=(
                    "security_scanner",
                    "dependency_manifest",
                ),
            )
            for name in names
        ]

    @classmethod
    def _cloud(cls):
        names = (
            "Resource Utilization",
            "Cost Efficiency",
            "Scaling Efficiency",
            "Infrastructure Health",
        )

        return [
            cls._spec(
                "cloud",
                name,
                MeasurementUnit.SCORE,
                required_signals=(
                    "cloud_metrics",
                    "infrastructure_state",
                ),
            )
            for name in names
        ]

    @classmethod
    def _ai_engineering(cls):
        names = (
            "Prompt Stability",
            "Model Drift",
            "Evaluation Quality",
            "Token Efficiency",
            "Hallucination Risk Indicators",
        )

        return [
            cls._spec(
                "ai_engineering",
                name,
                MeasurementUnit.SCORE,
                required_signals=(
                    "llm_evaluations",
                    "model_telemetry",
                ),
            )
            for name in names
        ]


