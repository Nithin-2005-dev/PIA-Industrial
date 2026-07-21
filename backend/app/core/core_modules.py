from __future__ import annotations

from app.core.di import ServiceCollection
from app.core.di import ServiceScope
from app.core.module import BaseModule


class GitHubAdapterFactory:
    def create(
        self,
        token: str,
    ):
        from app.infrastructure.github.adapter import GitHubAdapter
        from app.infrastructure.github.source import LiveGitHubSource
        from app.core.secrets import MockSecretProvider

        secret_provider = MockSecretProvider({"GITHUB_TOKEN": token})
        return GitHubAdapter(
            source=LiveGitHubSource(secret_provider=secret_provider)
        )


class MeasurementPlatformModule(BaseModule):
    name = "measurement"
    version = "1.0"
    dependencies = ("observation",)
    capabilities = (
        "measurement.provider",
        "measurement.engine",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.intelligence.measurement.core.engine import MeasurementEngine
        from app.intelligence.measurement.scientific_engine import MeasurementAggregationEngine
        from app.intelligence.measurement.scientific_engine import MeasurementBenchmarkRecorder
        from app.intelligence.measurement.scientific_engine import MeasurementProviderRegistry
        from app.intelligence.measurement.scientific_engine import ScientificMeasurementEngine
        from app.intelligence.measurement.scientific_engine import ScientificMeasurementRegistry
        from app.intelligence.measurement.scientific_engine import ScientificStatistics
        from app.intelligence.measurement.scientific_engine import default_measurement_providers
        from app.intelligence.measurement.scientific_engine import default_scientific_measurements
        from app.core.storage import PlatformStorage

        services.add(
            MeasurementEngine,
            lambda _: MeasurementEngine.default(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ScientificMeasurementRegistry,
            lambda _: ScientificMeasurementRegistry(
                default_scientific_measurements()
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            MeasurementProviderRegistry,
            lambda _: MeasurementProviderRegistry(
                default_measurement_providers()
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ScientificMeasurementEngine,
            lambda provider: ScientificMeasurementEngine(
                providers=provider.resolve(MeasurementProviderRegistry),
                registry=provider.resolve(ScientificMeasurementRegistry),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            MeasurementAggregationEngine,
            MeasurementAggregationEngine,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ScientificStatistics,
            ScientificStatistics,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            MeasurementBenchmarkRecorder,
            MeasurementBenchmarkRecorder,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            PlatformStorage,
            PlatformStorage,
            scope=ServiceScope.SINGLETON,
        )


class ObservationPlatformModule(BaseModule):
    name = "observation"
    version = "1.0"
    dependencies = ()
    capabilities = (
        "observation.ingestion",
        "observation.adapter",
        "observation.replay",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.ingestion.observation.ingestion import AdapterRegistry
        from app.ingestion.observation.ingestion import CheckpointStore
        from app.ingestion.observation.ingestion import ObservationDeduplicator
        from app.ingestion.observation.ingestion import ObservationIngestionEngine
        from app.ingestion.observation.ingestion import ObservationIngestionStore
        from app.ingestion.observation.ingestion import ObservationMetrics
        from app.ingestion.observation.ingestion import ObservationNormalizer
        from app.ingestion.observation.ingestion import RateLimiter
        from app.ingestion.observation.ingestion import UnifiedIdentityResolver
        from app.ingestion.observation.validation import ObservationValidationPipeline
        from app.ingestion.observation.adapters import default_observation_adapters

        services.add(
            AdapterRegistry,
            lambda _: self._adapter_registry(
                AdapterRegistry(),
                default_observation_adapters(),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            UnifiedIdentityResolver,
            UnifiedIdentityResolver,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationNormalizer,
            lambda provider: ObservationNormalizer(
                provider.resolve(UnifiedIdentityResolver)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationValidationPipeline,
            ObservationValidationPipeline,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationIngestionStore,
            ObservationIngestionStore,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CheckpointStore,
            CheckpointStore,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationDeduplicator,
            ObservationDeduplicator,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            RateLimiter,
            RateLimiter,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationMetrics,
            ObservationMetrics,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationIngestionEngine,
            lambda provider: ObservationIngestionEngine(
                adapters=provider.resolve(AdapterRegistry),
                normalizer=provider.resolve(ObservationNormalizer),
                validator=provider.resolve(ObservationValidationPipeline),
                store=provider.resolve(ObservationIngestionStore),
                checkpoints=provider.resolve(CheckpointStore),
                deduplicator=provider.resolve(ObservationDeduplicator),
                rate_limiter=provider.resolve(RateLimiter),
                metrics=provider.resolve(ObservationMetrics),
            ),
            scope=ServiceScope.SINGLETON,
        )
        from app.ingestion.observation.ingestion.operational_adapter import OperationalStoreAdapterFactory
        services.add(
            GitHubAdapterFactory,
            lambda _: OperationalStoreAdapterFactory(),
            scope=ServiceScope.SINGLETON,
        )

    def _adapter_registry(
        self,
        registry,
        adapters,
    ):
        for adapter in adapters:
            registry.register(adapter)
        return registry


class EvidencePlatformModule(BaseModule):
    name = "evidence"
    version = "1.0"
    dependencies = ("measurement",)
    capabilities = (
        "evidence.synthesis",
        "evidence.validation",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.knowledge.evidence.synthesis.engine import EvidenceSynthesisEngine
        from app.knowledge.evidence.knowledge.semantic_engine import SemanticEvidenceEngine

        services.add(
            EvidenceSynthesisEngine,
            EvidenceSynthesisEngine,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SemanticEvidenceEngine,
            SemanticEvidenceEngine,
            scope=ServiceScope.SINGLETON,
        )


class EstimationPlatformModule(BaseModule):
    name = "estimation"
    version = "1.0"
    dependencies = ("evidence",)
    capabilities = (
        "estimation.expertise",
        "estimation.ownership",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.estimator.policies.exponential_decay_policy import ExponentialDecayPolicy
        from app.estimator.policies.rule_expertise_scoring_policy import RuleExpertiseScoringPolicy
        from app.estimator.semantic_pipeline import SemanticEvidenceExpertiseBridge
        from app.estimator.semantic_pipeline import SemanticExpertiseProjectionPipeline

        services.add(
            ExponentialDecayPolicy,
            lambda _: ExponentialDecayPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            RuleExpertiseScoringPolicy,
            lambda _: RuleExpertiseScoringPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SemanticEvidenceExpertiseBridge,
            lambda _: SemanticEvidenceExpertiseBridge(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SemanticExpertiseProjectionPipeline,
            lambda provider: SemanticExpertiseProjectionPipeline(
                provider.resolve(SemanticEvidenceExpertiseBridge)
            ),
            scope=ServiceScope.SINGLETON,
        )


class GraphPlatformModule(BaseModule):
    name = "graph"
    version = "1.0"
    dependencies = ("knowledge",)
    capabilities = (
        "graph.organization",
        "graph.knowledge",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.knowledge.graph.graph_service import GraphService
        from app.knowledge.graph.builders import KnowledgeGraphBuilder
        from app.knowledge.graph.organizational_graph import OrganizationalGraph

        services.add(
            KnowledgeGraphBuilder,
            lambda _: KnowledgeGraphBuilder(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            OrganizationalGraph,
            lambda _: OrganizationalGraph(
                nodes=[],
                edges=[],
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            GraphService,
            lambda provider: GraphService(
                provider.resolve(OrganizationalGraph)
            ),
            scope=ServiceScope.SINGLETON,
        )


class TemporalPlatformModule(BaseModule):
    name = "temporal"
    version = "1.0"
    dependencies = ("graph",)
    capabilities = (
        "temporal.snapshot",
        "temporal.history",
        "temporal.trend",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from pathlib import Path
        from app.intelligence.temporal.graph_diff import GraphDiffEngine
        from app.intelligence.temporal.snapshot_repository import SnapshotRepository
        from app.intelligence.temporal_engine import TemporalEngine

        services.add(
            SnapshotRepository,
            lambda _: SnapshotRepository(
                root=Path("outputs/showcase/history/snapshots")
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            GraphDiffEngine,
            lambda _: GraphDiffEngine(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            TemporalEngine,
            lambda provider: TemporalEngine(
                repository=provider.resolve(SnapshotRepository),
                graph_diff=provider.resolve(GraphDiffEngine),
            ),
            scope=ServiceScope.SINGLETON,
        )


class KnowledgePlatformModule(BaseModule):
    name = "knowledge"
    version = "1.0"
    dependencies = ("estimation",)
    capabilities = (
        "knowledge.model",
        "knowledge.contract",
    )


class ForecastingPlatformModule(BaseModule):
    name = "forecasting"
    version = "1.0"
    dependencies = ("temporal", "estimation",)
    capabilities = (
        "forecasting.model",
        "forecasting.pipeline",
        "forecast.engine",
        "forecast.models",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.intelligence.forecasting.forecast_service import ForecastService
        from app.intelligence.forecasting.validation import ForecastValidationService
        from app.intelligence.forecasting.linear_forecast_policy import LinearForecastPolicy

        from app.intelligence.forecasting.baseline_models import (
            ConstantBaselineModel,
            ExponentialSmoothingModel,
            LinearTrendModel,
            MomentumProjectionModel,
            MovingAverageModel,
        )
        from app.intelligence.forecasting.engine import ForecastEngine, ForecastRegistry
        from app.intelligence.forecasting.factory import TimeSeriesFactory

        # Register forecasting services
        services.add(
            LinearForecastPolicy,
            LinearForecastPolicy,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ForecastService,
            lambda provider: ForecastService(
                provider.resolve(LinearForecastPolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ForecastValidationService,
            lambda _: ForecastValidationService(),
            scope=ServiceScope.SINGLETON,
        )

        # Register baseline models
        services.add(LinearTrendModel, lambda _: LinearTrendModel(), scope=ServiceScope.SINGLETON)
        services.add(ExponentialSmoothingModel, lambda _: ExponentialSmoothingModel(), scope=ServiceScope.SINGLETON)
        services.add(MovingAverageModel, lambda _: MovingAverageModel(), scope=ServiceScope.SINGLETON)
        services.add(MomentumProjectionModel, lambda _: MomentumProjectionModel(), scope=ServiceScope.SINGLETON)
        services.add(ConstantBaselineModel, lambda _: ConstantBaselineModel(), scope=ServiceScope.SINGLETON)

        # Register and populate the Registry
        def build_registry(provider):
            registry = ForecastRegistry()
            # Register in priority order
            registry.register(provider.resolve(LinearTrendModel))
            registry.register(provider.resolve(MomentumProjectionModel))
            registry.register(provider.resolve(MovingAverageModel))
            registry.register(provider.resolve(ExponentialSmoothingModel))
            registry.register(provider.resolve(ConstantBaselineModel))
            return registry

        services.add(
            ForecastRegistry,
            build_registry,
            scope=ServiceScope.SINGLETON,
        )

        services.add(
            ForecastEngine,
            lambda provider: ForecastEngine(
                registry=provider.resolve(ForecastRegistry),
                factory=TimeSeriesFactory,
            ),
            scope=ServiceScope.SINGLETON,
        )


class SimulationPlatformModule(BaseModule):
    name = "simulation"
    version = "1.0"
    dependencies = (
        "forecasting",
    )
    capabilities = (
        "simulation.engine",
        "simulation.registry",
        "simulation.comparison",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.intelligence.counterfactual.engine import SimulationEngine, ScenarioComparisonEngine
        from app.intelligence.counterfactual.registry import SimulationRegistry

        services.add(
            SimulationEngine,
            lambda _: SimulationEngine(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ScenarioComparisonEngine,
            lambda _: ScenarioComparisonEngine(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SimulationRegistry,
            lambda _: SimulationRegistry(),
            scope=ServiceScope.SINGLETON,
        )


class AgentPlatformModule(BaseModule):
    name = "agent"
    version = "1.0"
    dependencies = (
        "graph",
        "simulation",
        "intelligence",
    )
    capabilities = (
        "agent.reasoning",
        "agent.tool",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        pass


class CausalPlatformModule(BaseModule):
    name = "causal"
    version = "1.0"
    dependencies = (
        "intelligence",
    )
    capabilities = (
        "causal.engine",
        "causal.explanation",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.intelligence.causal.ontology import CausalOntology
        from app.intelligence.causal.graph import CausalSemanticModelBuilder
        from app.intelligence.causal.rules import CausalRuleRegistry, default_rule_registry
        from app.intelligence.causal.rules import CausalRuleEngine
        from app.intelligence.causal.hypothesis import CausalHypothesisEngine
        from app.intelligence.causal.explanation import ExplanationEngine
        from app.intelligence.causal.engine import CausalEngine

        services.add(
            CausalOntology,
            lambda _: CausalOntology(),
            scope=ServiceScope.SINGLETON,
        )
        # NOTE: All 5 legacy RuleProviders have been retired and migrated to
        # ReasoningRule wrappers (kg-v1.0 / rg-v1.0). The CausalRuleRegistry
        # and CausalRuleEngine are retained here because CausalSemanticModelBuilder
        # and CausalEngine still depend on them for ontology traversal, hypothesis
        # generation, and explanation narratives — NOT for rule evaluation.
        services.add(
            CausalRuleRegistry,
            lambda _: default_rule_registry(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CausalRuleEngine,
            lambda provider: CausalRuleEngine(provider.resolve(CausalRuleRegistry)),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CausalSemanticModelBuilder,
            lambda provider: CausalSemanticModelBuilder(
                rule_engine=provider.resolve(CausalRuleEngine),
                ontology=provider.resolve(CausalOntology),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CausalHypothesisEngine,
            lambda provider: CausalHypothesisEngine(provider.resolve(CausalOntology)),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ExplanationEngine,
            lambda _: ExplanationEngine(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CausalEngine,
            lambda provider: CausalEngine(
                ontology=provider.resolve(CausalOntology),
                rule_registry=provider.resolve(CausalRuleRegistry),
            ),
            scope=ServiceScope.SINGLETON,
        )


class ExecutivePlatformModule(BaseModule):
    name = "executive"
    version = "1.0"
    dependencies = (
        "agent",
        "decision",
        "forecasting",
    )
    capabilities = (
        "executive.recommendation",
        "executive.roadmap",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.intelligence.legacy.executive_recommendation_service import ExecutiveRecommendationService
        from app.intelligence.legacy.roadmap_service import RoadmapService
        from app.core.hardening import ProductionHardeningService

        services.add(
            ExecutiveRecommendationService,
            ExecutiveRecommendationService,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            RoadmapService,
            RoadmapService,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ProductionHardeningService,
            lambda _: ProductionHardeningService(),
            scope=ServiceScope.SINGLETON,
        )


class DecisionPlatformModule(BaseModule):
    name = "decision"
    version = "1.0"
    dependencies = (
        "agent",
        "forecasting",
        "simulation",
    )
    capabilities = (
        "decision.optimization",
        "decision.portfolio",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.intelligence.decisions.optimization import DecisionOptimizationEngine

        services.add(
            DecisionOptimizationEngine,
            lambda _: DecisionOptimizationEngine(),
            scope=ServiceScope.SINGLETON,
        )


class IntelligencePlatformModule(BaseModule):
    name = "intelligence"
    version = "1.0"
    dependencies = (
        "forecasting",
        "simulation",
    )
    capabilities = (
        "intelligence.context",
        "intelligence.ownership",
        "intelligence.organization",
    )

    def __init__(
        self,
        projection=None,
        context=None,
    ):
        self._projection = projection
        self._context = context

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.bootstrap.intelligence_context import IntelligenceContext
        from app.concentration.concentration_service import ConcentrationService
        from app.concentration.policies.expertise_concentration_policy import ExpertiseConcentrationPolicy
        from app.coverage.coverage_service import CoverageService
        from app.coverage.policies.expertise_coverage_policy import ExpertiseCoveragePolicy
        from app.estimator.expertise_projection import ExpertiseProjection
        from app.intelligence.forecasting.forecast_pipeline_service import ForecastPipelineService
        from app.intelligence.forecasting.forecast_service import ForecastService
        from app.intelligence.forecasting.forecast_severity_service import ForecastSeverityService
        from app.intelligence.forecasting.future_risk_pipeline_service import FutureRiskPipelineService
        from app.intelligence.forecasting.linear_forecast_policy import LinearForecastPolicy
        from app.intelligence.assets.health_service import HealthService
        from app.intelligence.assets.policies.organizational_health_policy import OrganizationalHealthPolicy
        from app.history.health_projection import HealthProjection
        from app.history.history_service import HistoryService
        from app.intelligence.expertise.policies.simple_transfer_policy import SimpleTransferPolicy
        from app.intelligence.expertise.transfer_service import TransferService
        from app.intelligence.legacy.organization_dashboard_service import OrganizationDashboardService
        from app.intelligence.legacy.organization_health_service import OrganizationHealthService
        from app.intelligence.legacy.organization_readiness_service import OrganizationReadinessService
        from app.intelligence.legacy.organization_risk_service import OrganizationRiskService
        from app.intelligence.legacy.organization_transfer_service import OrganizationTransferService
        from app.intelligence.legacy.ownership_service import OwnershipService
        from app.intelligence.legacy.policies.expertise_ownership_policy import ExpertiseOwnershipPolicy
        from app.query.expertise_query_service import ExpertiseQueryService
        from app.intelligence.risk.bus_factor_service import BusFactorService
        from app.intelligence.risk.policies.ownership_bus_factor_policy import OwnershipBusFactorPolicy
        from app.intelligence.risk.knowledge_risk_service import KnowledgeRiskService
        from app.intelligence.risk.policies.knowledge_risk_policy import KnowledgeRiskPolicy
        from app.intelligence.risk.policies.bus_factor_risk_policy import BusFactorRiskPolicy
        from app.knowledge.evidence.ranking import RankingService
        from app.core.jobs.analysis_job import NightlyAnalysisJob
        from app.core.scheduler import Scheduler
        from app.knowledge.graph.graph_service import GraphService

        from app.intelligence.legacy.policies.expertise_successor_policy import ExpertiseSuccessorPolicy
        from app.intelligence.legacy.successor_service import SuccessorService

        if self._projection is not None:
            services.add_instance(
                ExpertiseProjection,
                self._projection,
            )
        if self._context is not None:
            services.add_instance(
                IntelligenceContext,
                self._context,
            )
        services.add(
            ExpertiseQueryService,
            lambda provider: ExpertiseQueryService(
                provider.resolve(ExpertiseProjection)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ExpertiseOwnershipPolicy,
            lambda _: ExpertiseOwnershipPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            OwnershipService,
            lambda provider: OwnershipService(
                provider.resolve(ExpertiseQueryService),
                provider.resolve(ExpertiseOwnershipPolicy),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ExpertiseSuccessorPolicy,
            lambda _: ExpertiseSuccessorPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SuccessorService,
            lambda provider: SuccessorService(
                provider.resolve(OwnershipService),
                provider.resolve(ExpertiseSuccessorPolicy),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ExpertiseCoveragePolicy,
            lambda _: ExpertiseCoveragePolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CoverageService,
            lambda provider: CoverageService(
                provider.resolve(ExpertiseCoveragePolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ExpertiseConcentrationPolicy,
            lambda _: ExpertiseConcentrationPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ConcentrationService,
            lambda provider: ConcentrationService(
                provider.resolve(ExpertiseConcentrationPolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            OwnershipBusFactorPolicy,
            lambda _: OwnershipBusFactorPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            BusFactorService,
            lambda provider: BusFactorService(
                provider.resolve(OwnershipService),
                provider.resolve(OwnershipBusFactorPolicy),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            OrganizationalHealthPolicy,
            lambda _: OrganizationalHealthPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            HealthService,
            lambda provider: HealthService(
                provider.resolve(OrganizationalHealthPolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            HealthProjection,
            HealthProjection,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            HistoryService,
            lambda provider: HistoryService(
                provider.resolve(HealthProjection)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            BusFactorRiskPolicy,
            lambda _: BusFactorRiskPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            KnowledgeRiskPolicy,
            lambda provider: provider.resolve(BusFactorRiskPolicy),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            KnowledgeRiskService,
            lambda provider: KnowledgeRiskService(
                provider.resolve(OwnershipService),
                provider.resolve(BusFactorService),
                provider.resolve(KnowledgeRiskPolicy),
                provider.resolve(GraphService),
            ),
            scope=ServiceScope.SINGLETON,
        )
        # Note: RankingService assumes graph_store exists in GraphService or similar.
        # It needs something implementing IEvidenceGraphStore. We'll pass the underlying graph.
        from app.knowledge.graph.organizational_graph import OrganizationalGraph
        services.add(
            RankingService,
            lambda provider: RankingService(provider.resolve(OrganizationalGraph)),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            NightlyAnalysisJob,
            lambda provider: NightlyAnalysisJob(
                ranking_service=provider.resolve(RankingService),
                knowledge_risk_service=provider.resolve(KnowledgeRiskService),
                graph_service=provider.resolve(GraphService),
            ),
            scope=ServiceScope.SINGLETON,
        )
        # Schedule the job!
        # In a real app we'd resolve Scheduler from the Runtime context, but since this is configure_services,
        # we can register a post-build action or just do it if scheduler is passed. Wait, `core_modules.py`
        # is just registering. To wire into Scheduler, maybe `runtime.py` is better?
        # Actually, let's just add it to DI, we can schedule it in the runtime or app entrypoint.
        # Wait, if I have to "wire `AnalysisJob` into the `Scheduler` in `app/platform/core_modules.py`", I will
        # do it here using a factory that resolves Scheduler, but Scheduler is created in runtime.py.
        # For now, let's just register NightlyAnalysisJob.
        services.add(
            LinearForecastPolicy,
            lambda _: LinearForecastPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ForecastService,
            lambda provider: ForecastService(
                provider.resolve(LinearForecastPolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ForecastPipelineService,
            lambda provider: ForecastPipelineService(
                provider.resolve(HistoryService),
                provider.resolve(ForecastService),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            FutureRiskPipelineService,
            lambda provider: FutureRiskPipelineService(
                provider.resolve(ForecastPipelineService)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SimpleTransferPolicy,
            lambda _: SimpleTransferPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            TransferService,
            lambda provider: TransferService(
                provider.resolve(SimpleTransferPolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )

        services.add(
            ForecastSeverityService,
            lambda _: ForecastSeverityService(),
            scope=ServiceScope.SINGLETON,
        )
        if self._context is not None:
            services.add(
                OrganizationRiskService,
                lambda provider: OrganizationRiskService(
                    provider.resolve(IntelligenceContext)
                ),
                scope=ServiceScope.SINGLETON,
            )
            services.add(
                OrganizationHealthService,
                lambda provider: OrganizationHealthService(
                    provider.resolve(IntelligenceContext)
                ),
                scope=ServiceScope.SINGLETON,
            )
            services.add(
                OrganizationReadinessService,
                lambda provider: OrganizationReadinessService(
                    provider.resolve(IntelligenceContext)
                ),
                scope=ServiceScope.SINGLETON,
            )
            services.add(
                OrganizationTransferService,
                lambda provider: OrganizationTransferService(
                    provider.resolve(IntelligenceContext)
                ),
                scope=ServiceScope.SINGLETON,
            )
            services.add(
                OrganizationDashboardService,
                lambda provider: OrganizationDashboardService(
                    provider.resolve(IntelligenceContext)
                ),
                scope=ServiceScope.SINGLETON,
            )


def default_platform_modules() -> tuple[BaseModule, ...]:
    return (
        ObservationPlatformModule(),
        MeasurementPlatformModule(),
        EvidencePlatformModule(),
        EstimationPlatformModule(),
        KnowledgePlatformModule(),
        GraphPlatformModule(),
        TemporalPlatformModule(),
        ForecastingPlatformModule(),
        SimulationPlatformModule(),
        IntelligencePlatformModule(),
        CausalPlatformModule(),
        AgentPlatformModule(),
        DecisionPlatformModule(),
        ExecutivePlatformModule(),
    )
