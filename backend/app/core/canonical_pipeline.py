from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from app.core.api.contracts import RuntimePipelineInput
from app.core.api.contracts import RuntimePipelineResult
from app.core.api.contracts import RuntimeStageExecution
from app.core.event_bus import PlatformEvent


@dataclass(frozen=True, slots=True)
class CanonicalStageBinding:
    module: str
    stage: object
    input_contract: str
    output_contract: str


class CanonicalPlatformPipeline:
    def __init__(
        self,
        built_runtime,
    ):
        self._built = built_runtime

    def run(
        self,
        request: RuntimePipelineInput,
    ) -> RuntimePipelineResult:
        from scripts.platform_showcase.context import PlatformContext

        context = PlatformContext(
            repository=request.repository,
            branch=request.branch,
            commit_limit=request.commits,
            github_token=request.github_token,
            tenant_id=request.tenant_id,
            output_directory=request.output_directory or Path("outputs/showcase"),
            since_commit=request.since_commit,
            runtime=self._built.runtime,
            service_provider=self._built.provider,
        )

        bindings = self._bindings_by_runtime_order()
        completed: list[RuntimeStageExecution] = []
        errors: list[str] = []

        # Publish the full runtime execution plan into context metrics BEFORE
        # any stage executes.  PipelineValidationStage reads these so its
        # "Actual Execution Path" output is always derived from the real
        # runtime schedule — never from a hand-maintained list.
        context.metrics["execution_order"] = tuple(
            binding.module for binding in bindings
        )
        context.metrics["execution_stage_names"] = tuple(
            binding.stage.name for binding in bindings
        )

        self._built.runtime.event_bus.publish(
            PlatformEvent(
                type="runtime.pipeline.started",
                payload={
                    "repository": request.repository,
                    "branch": request.branch,
                    "commits": request.commits,
                },
            )
        )

        for binding in bindings:
            started = time.perf_counter()
            stage_name = binding.stage.name
            self._built.runtime.event_bus.publish(
                PlatformEvent(
                    type="runtime.stage.started",
                    payload={
                        "module": binding.module,
                        "stage": stage_name,
                    },
                )
            )
            try:
                binding.stage.run(context)
                duration = time.perf_counter() - started
                completed.append(
                    RuntimeStageExecution(
                        name=stage_name,
                        module=binding.module,
                        version=self._built.runtime.modules.get(
                            binding.module
                        ).version,
                        input_contract=binding.input_contract,
                        output_contract=binding.output_contract,
                        duration=duration,
                        metadata=dict(context.metrics),
                    )
                )
                self._built.runtime.event_bus.publish(
                    PlatformEvent(
                        type="runtime.stage.completed",
                        payload={
                            "module": binding.module,
                            "stage": stage_name,
                            "duration": duration,
                        },
                    )
                )
            except Exception as exc:
                duration = time.perf_counter() - started
                message = f"{stage_name}: {exc}"
                errors.append(message)
                completed.append(
                    RuntimeStageExecution(
                        name=stage_name,
                        module=binding.module,
                        version=self._built.runtime.modules.get(
                            binding.module
                        ).version,
                        input_contract=binding.input_contract,
                        output_contract=binding.output_contract,
                        duration=duration,
                        metadata=dict(context.metrics),
                        errors=(str(exc),),
                    )
                )
                self._built.runtime.event_bus.publish(
                    PlatformEvent(
                        type="runtime.stage.failed",
                        payload={
                            "module": binding.module,
                            "stage": stage_name,
                            "error": str(exc),
                        },
                    )
                )
                break

        # Automatic snapshot persistence on successful execution
        if not errors:
            try:
                from app.intelligence.temporal_engine import TemporalEngine
                engine = self._built.provider.resolve(TemporalEngine)
                snapshot = engine.create_snapshot(context)
                engine.repository.save(snapshot)
            except Exception as e:
                # Snapshot persistence is best-effort
                context.metrics["snapshot_error"] = str(e)

        self._built.runtime.event_bus.publish(
            PlatformEvent(
                type="runtime.pipeline.completed",
                payload={
                    "repository": request.repository,
                    "completed_stages": len(completed),
                    "errors": tuple(errors),
                },
            )
        )

        return RuntimePipelineResult(
            context=context,
            completed_stages=tuple(completed),
            execution_order=tuple(binding.module for binding in bindings),
            errors=tuple(errors),
        )

    def branch(
        self,
        baseline_context: Any,
        scenario: Any,
    ) -> Any:
        """
        Executes a branched pipeline for a simulation scenario.
        Starts execution from 'intelligence' onwards.
        Returns a ScenarioContext containing the ScenarioExecutionResult.
        """
        from app.intelligence.counterfactual.models import ScenarioContext, ScenarioExecutionResult
        import time
        import copy
        from app.core.event_bus import PlatformEvent

        # 1. Clone context
        import dataclasses
        if dataclasses.is_dataclass(baseline_context):
            cloned = copy.copy(baseline_context)
        else:
            cloned = copy.copy(baseline_context)

        # Deep copy graph
        if hasattr(cloned, "knowledge_graph") and cloned.knowledge_graph is not None:
            if hasattr(cloned.knowledge_graph, "copy"):
                cloned.knowledge_graph = cloned.knowledge_graph.copy()
            else:
                cloned.knowledge_graph = copy.deepcopy(cloned.knowledge_graph)
                
        # Shallow copy lists and dicts
        if hasattr(cloned, "expertise_models"):
            cloned.expertise_models = list(cloned.expertise_models)
        if hasattr(cloned, "metrics"):
            cloned.metrics = copy.deepcopy(cloned.metrics)

        # 2. Apply interventions
        for intervention in scenario.interventions:
            intervention.apply(cloned)

        # 3. Execute downstream stages
        bindings = self._bindings_by_runtime_order(runtime_override=baseline_context.runtime)
        
        # Determine earliest restart stage dynamically based on interventions
        restart_stages = [intervention.restart_stage() for intervention in scenario.interventions if hasattr(intervention, 'restart_stage')]
        if not restart_stages:
            restart_stages = ["knowledge"]  # fallback

        start_idx = len(bindings)
        for target_stage in restart_stages:
            for i, binding in enumerate(bindings):
                if binding.module == target_stage and i < start_idx:
                    start_idx = i
                    break
                    
        # Fallback if no matching binding found
        if start_idx == len(bindings):
            for i, binding in enumerate(bindings):
                if binding.module == "intelligence":
                    start_idx = i
                    break
                
        errors = []
        for binding in bindings[start_idx:]:
            # We don't want to run the SummaryStage for branches, as it outputs to console and ends the showcase
            if binding.stage.__class__.__name__ == "SummaryStage":
                continue
            if binding.stage.__class__.__name__ == "ExecutiveDashboardStage":
                continue
            if binding.stage.__class__.__name__ == "PipelineValidationStage":
                continue
            if binding.module == "simulation" or binding.stage.__class__.__name__ == "SimulationStage":
                continue

            try:
                binding.stage.run(cloned)
            except Exception as exc:
                errors.append(f"{binding.stage.name}: {exc}")
                break

        # 4. Package results
        result = ScenarioExecutionResult(
            org_intelligence=getattr(cloned, "org_intelligence", None),
            reasoning_results=getattr(cloned, "reasoning_results", ()),
            decisions=getattr(cloned, "decisions", ()),
            metrics=getattr(cloned, "metrics", {}),
        )

        return ScenarioContext(
            scenario=scenario,
            baseline_context=baseline_context,
            cloned_context=cloned,
            execution_result=result,
        )

    def _bindings_by_runtime_order(
        self,
        runtime_override=None,
    ) -> list[CanonicalStageBinding]:
        from scripts.platform_showcase.stages.stage01_initialize import InitializeStage
        from scripts.platform_showcase.stages.stage02_collection import CollectionStage
        from scripts.platform_showcase.stages.stage03_observation import ObservationStage
        from scripts.platform_showcase.stages.stage04_measurement import MeasurementStage
        from scripts.platform_showcase.stages.stage05_evidence import EvidenceStage
        from scripts.platform_showcase.stages.stage06_repository import ExpertiseStage
        from scripts.platform_showcase.stages.stage07_knowledge import KnowledgeStage
        from scripts.platform_showcase.stages.stage07b_graph import KnowledgeGraphStage
        from scripts.platform_showcase.stages.stage07c_temporal import TemporalIntelligenceStage
        from scripts.platform_showcase.stages.stage07d_forecast import ForecastingStage
        from scripts.platform_showcase.stages.stage07e_simulation import SimulationStage
        from scripts.platform_showcase.stages.stage08_org_intelligence import OrganizationIntelligenceStage
        from scripts.platform_showcase.stages.stage09_reasoning import ReasoningStage
        from scripts.platform_showcase.stages.stage10_decision import DecisionStage
        from scripts.platform_showcase.stages.stage10b_optimization import PortfolioOptimizationStage
        from scripts.platform_showcase.stages.stage10c_causal import CausalIntelligenceStage
        from scripts.platform_showcase.stages.stage11_executive import ExecutiveDashboardStage
        from scripts.platform_showcase.stages.stage12_validation import PipelineValidationStage
        from scripts.platform_showcase.stages.stage13_summary import SummaryStage

        by_module = {
            "observation": (
                CanonicalStageBinding(
                    "observation",
                    InitializeStage(),
                    "RuntimePipelineInput",
                    "PlatformContext.metadata",
                ),
                CanonicalStageBinding(
                    "observation",
                    CollectionStage(),
                    "RuntimePipelineInput",
                    "PlatformContext.observations",
                ),
                CanonicalStageBinding(
                    "observation",
                    ObservationStage(),
                    "PlatformContext.observations",
                    "PlatformContext.metrics.observation_health",
                ),
            ),
            "measurement": (
                CanonicalStageBinding(
                    "measurement",
                    MeasurementStage(),
                    "PlatformContext.observations",
                    "PlatformContext.measurements",
                ),
            ),
            "evidence": (
                CanonicalStageBinding(
                    "evidence",
                    EvidenceStage(),
                    "PlatformContext.measurements",
                    "PlatformContext.evidence_package",
                ),
            ),
            "estimation": (
                CanonicalStageBinding(
                    "estimation",
                    ExpertiseStage(),
                    "PlatformContext.evidence_package",
                    "PlatformContext.expertise_models",
                ),
            ),
            "knowledge": (
                CanonicalStageBinding(
                    "knowledge",
                    KnowledgeStage(),
                    "PlatformContext.expertise_models",
                    "PlatformContext.knowledge",
                ),
            ),
            "graph": (
                CanonicalStageBinding(
                    "graph",
                    KnowledgeGraphStage(),
                    "PlatformContext.knowledge",
                    "PlatformContext.knowledge_graph",
                ),
            ),
            "temporal": (
                CanonicalStageBinding(
                    "temporal",
                    TemporalIntelligenceStage(),
                    "PlatformContext.knowledge_graph",
                    "PlatformContext.historical_context",
                ),
            ),
            "forecasting": (
                CanonicalStageBinding(
                    "forecasting",
                    ForecastingStage(),
                    "PlatformContext.historical_context",
                    "PlatformContext.forecast_context",
                ),
            ),
            "simulation": (
                CanonicalStageBinding(
                    "simulation",
                    SimulationStage(),
                    "PlatformContext.forecast_context",
                    "PlatformContext.simulation_context",
                ),
            ),
            "intelligence": (
                CanonicalStageBinding(
                    "intelligence",
                    OrganizationIntelligenceStage(),
                    "PlatformContext.forecast_context",
                    "PlatformContext.org_intelligence",
                ),
            ),
            "causal": (
                CanonicalStageBinding(
                    "causal",
                    CausalIntelligenceStage(),
                    "PlatformContext.org_intelligence + forecast_context + simulation_context",
                    "PlatformContext.causal_context",
                ),
            ),
            "agent": (
                CanonicalStageBinding(
                    "agent",
                    ReasoningStage(),
                    "PlatformContext.knowledge + PlatformContext.org_intelligence",
                    "PlatformContext.reasoning_results",
                ),
            ),
            "decision": (
                CanonicalStageBinding(
                    "decision",
                    DecisionStage(),
                    "PlatformContext.reasoning_results",
                    "PlatformContext.decisions",
                ),
                CanonicalStageBinding(
                    "decision",
                    PortfolioOptimizationStage(),
                    "PlatformContext.decisions",
                    "PlatformContext.metrics.optimization_portfolio",
                ),
            ),
            "executive": (
                CanonicalStageBinding(
                    "executive",
                    ExecutiveDashboardStage(),
                    "PlatformContext.decisions",
                    "PlatformContext.metrics.executive",
                ),
                CanonicalStageBinding(
                    "executive",
                    PipelineValidationStage(),
                    "PlatformContext",
                    "PlatformContext.metrics.validation",
                ),
                CanonicalStageBinding(
                    "executive",
                    SummaryStage(),
                    "PlatformContext",
                    "RuntimePipelineResult",
                ),
            ),
        }

        bindings: list[CanonicalStageBinding] = []
        runtime = runtime_override or self._built.runtime
        for module in runtime.modules.startup_order():
            bindings.extend(by_module.get(module, ()))
        return bindings
