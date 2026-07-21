import time
import dataclasses
import json
import uuid

from .models import ExecutionState, ExecutionStatus, AnswerConfidence, CognitiveAnswer, VerificationResult, StageResult, ExecutiveResponse, Intent
from .planner import PlanningEngine
from .executor import CapabilityPlanner, Executor
from .reflection import ReflectionEngine
from .policy import PolicyEngine
from .events import get_event_bus
from .answer_builder import AnswerBuilder
from .synthesizer import AdaptiveSynthesizer
from .decomposer import GoalDecomposer
from .tool_search import ToolSearchEngine, KeywordSearchEngine
from .invariants import InvariantChecker
from .models import PreconditionFailure, CapabilityResult, RepositoryMemory
from .validation import CapabilityValidator
from .semantic_parser import SemanticQueryParser
from .retriever import CapabilityRetriever
from .entity_resolver import EntityResolver
from .repository_knowledge import RepositoryKnowledge
from .adapter import PlatformResultAdapter
from .goal_builder import GoalGraphBuilder

class AgentOrchestrator:
    """
    The main execution loop for the Agentic Runtime (M58).
    Pipeline: SemanticParser -> CapabilityRetriever -> Planner -> Executor -> AnswerBuilder -> Synthesizer
    """
    def __init__(
        self,
        planner: PlanningEngine,
        executor: Executor,
        capability_planner: CapabilityPlanner,
        reflection_engine: ReflectionEngine,
        policy_engine: PolicyEngine,
        answer_builder: AnswerBuilder,
        synthesizer: AdaptiveSynthesizer,
        semantic_parser: SemanticQueryParser,
        retriever: CapabilityRetriever,
        entity_resolver: EntityResolver,
        registry,
        provider_manager
    ):
        self.semantic_parser = semantic_parser
        self.retriever = retriever
        self.entity_resolver = entity_resolver
        self.planner = planner
        self.executor = executor
        self.capability_planner = capability_planner
        self.reflection_engine = reflection_engine
        self.policy_engine = policy_engine
        self.answer_builder = answer_builder
        self.synthesizer = synthesizer
        self.registry = registry
        self.provider = provider_manager
        self.event_bus = get_event_bus()
        self.invariant_checker = InvariantChecker()
        self.goal_graph_builder = GoalGraphBuilder()
        
        from .pipelines.base import PipelineRegistry
        from .pipelines.informational import InformationalPipeline
        from .pipelines.decision import DecisionPipeline
        from .pipeline_planner import PipelinePlanner
        
        self.pipeline_registry = PipelineRegistry()
        self.pipeline_registry.register(InformationalPipeline(self.planner, self.executor, self.provider))
        self.pipeline_registry.register(DecisionPipeline(self.planner, self.executor, self.provider))
        self.pipeline_planner = PipelinePlanner(self.pipeline_registry)

    def run(self, state: ExecutionState) -> ExecutionState:
        iteration = 0
        stage_results = list(state.stage_results)
        
        def add_stage(name, status, exp_in, exp_out, act_out, dur, diag, reason=None):
            sr = StageResult(
                stage_id=f"{state.query_id}_{len(stage_results)}",
                stage_name=name,
                status=status,
                expected_input=exp_in,
                expected_output=exp_out,
                actual_output=act_out,
                duration_ms=dur,
                diagnostics=diag,
                reason=reason
            )
            stage_results.append(sr)
            return sr
            
        def abort_with_error(stage_name, reason, diagnostics, status=ExecutionStatus.RUNTIME_FAILURE):
            self._print_health_matrix(stage_results)
            exec_resp = ExecutiveResponse(
                executive_summary="Repository query could not be executed.",
                technical_summary=f"Diagnostic Error at [{stage_name}]:\nReason: {reason}\nDiagnostics:\n{json.dumps(diagnostics, indent=2, default=str)}",
                actionable_recommendations=["Improve semantic routing or capability retrieval."],
                supporting_evidence=[], confidence=0.0, risks=[], alternative_strategies=[]
            )
            return dataclasses.replace(state, status=status, executive_response=exec_resp, stage_results=tuple(stage_results))
        
        # 1. Semantic Parse
        self.event_bus.publish("SemanticParsingStarted", "orchestrator")
        t0 = time.monotonic()
        semantic_query = self.semantic_parser.parse(state.goal.query, intent=state.classification.intent)
        dur = (time.monotonic() - t0) * 1000
        
        if not semantic_query.topics and not semantic_query.keywords:
            add_stage("Semantic Parser", "FAIL", "User Query", "SemanticQuery", "UNKNOWN", dur, {"Topics": "UNKNOWN"}, "Parser returned no topics or keywords")
            return abort_with_error("Semantic Parser", "Parser returned no topics or keywords", {}, ExecutionStatus.RUNTIME_FAILURE)
            
        add_stage("Semantic Parser", "PASS", "User Query", "SemanticQuery", f"Topics: {semantic_query.topics}, Keywords: {semantic_query.keywords}", dur, {})
        state = dataclasses.replace(state, semantic_query=semantic_query)

        # 2. Goal Graph
        self.event_bus.publish("GoalGraphStarted", "orchestrator")
        t0 = time.monotonic()
        goal_graph = self.goal_graph_builder.build(semantic_query)
        dur = (time.monotonic() - t0) * 1000
        if not goal_graph.nodes:
            add_stage("Goal Graph", "FAIL", "SemanticQuery", "GoalGraph", "0 goals", dur, {}, "No executable goals extracted")
            return abort_with_error("Goal Graph", "No executable goals extracted from semantic query", {}, ExecutionStatus.RUNTIME_FAILURE)
        add_stage("Goal Graph", "PASS", "SemanticQuery", "GoalGraph", f"{len(goal_graph.nodes)} goals", dur, {"Hash": goal_graph.hash()})
        state = dataclasses.replace(state, goal_graph=goal_graph)
        
        # 3. Repository Knowledge wrapper
        adapter = PlatformResultAdapter(state.platform_result)
        repo_knowledge = RepositoryKnowledge(adapter)
        
        # 4. Entity Resolution
        self.event_bus.publish("EntityResolution", "orchestrator")
        semantic_query = self.entity_resolver.resolve(semantic_query, repo_knowledge)
        goal_graph = self.goal_graph_builder.build(semantic_query)
        state = dataclasses.replace(state, semantic_query=semantic_query, goal_graph=goal_graph)
        
        # 5. Capability Retrieval
        self.event_bus.publish("CapabilityRetrieval", "orchestrator")
        t0 = time.monotonic()
        candidates = self.retriever.retrieve(semantic_query, repo_knowledge)
        dur = (time.monotonic() - t0) * 1000
        
        diags = {"Candidates": len(candidates), "Details": [c.diagnostics for c in candidates if hasattr(c, 'diagnostics')]}
        if not candidates:
            add_stage("Capability Retrieval", "FAIL", "SemanticQuery", "CapabilityCandidates", "0 candidates", dur, diags, "No candidates found")
            return abort_with_error("Capability Retrieval", "No capability matched query", diags, ExecutionStatus.CAPABILITY_MISSING)
            
        add_stage("Capability Retrieval", "PASS", "SemanticQuery", "CapabilityCandidates", f"{len(candidates)} candidates", dur, diags)
        state = dataclasses.replace(state, candidate_set=candidates)
        
        # 6. Pipeline Planning
        self.event_bus.publish("PipelinePlanning", "orchestrator")
        t0 = time.monotonic()
        
        pipeline = self.pipeline_planner.select_pipeline(state.semantic_query, state.goal_graph)
        cost_estimate = self.pipeline_planner.estimate_cost(pipeline, state.goal_graph)
        
        dur = (time.monotonic() - t0) * 1000
        add_stage(
            "Pipeline Planner", "PASS", "SemanticQuery, GoalGraph", "CognitivePipeline",
            f"Selected {pipeline.strategy.id} (Complexity: {pipeline.strategy.complexity.value})", dur,
            {"Estimated Cost": cost_estimate.estimated_cost}
        )
        
        # 7. Pipeline Execution
        self.event_bus.publish("PipelineExecutionStarted", "orchestrator", pipeline=pipeline.strategy.id)
        t0 = time.monotonic()
        
        try:
            state = pipeline.plan(state)
            state = pipeline.execute(state)
            state = pipeline.present(state)
            
            dur = (time.monotonic() - t0) * 1000
            add_stage("Pipeline Execution", "PASS", "ExecutionState", "ExecutionState", f"Executed {pipeline.strategy.id}", dur, {})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return abort_with_error(f"Pipeline {pipeline.strategy.id}", str(e), {}, ExecutionStatus.RUNTIME_FAILURE)
            
        self.invariant_checker.validate(state)
        self._print_health_matrix(stage_results)
        
        self.event_bus.publish("AnswerFinished", "orchestrator", confidence=state.confidence.overall if state.confidence else 1.0)
        
        return dataclasses.replace(state, status=ExecutionStatus.SUCCESS, stage_results=tuple(stage_results))

    def _print_health_matrix(self, stage_results):
        print("\n")
        print("="*60)
        print("                   RUNTIME HEALTH MATRIX                    ")
        print("="*60)
        total_time = 0.0
        for sr in stage_results:
            color = "\033[92m" if sr.status == "PASS" else "\033[91m"
            reset = "\033[0m"
            print(f"{sr.stage_name:<25} {color}[{sr.status}]{reset} {sr.duration_ms:>10.1f}ms")
            if sr.status == "FAIL":
                print(f"   Reason: {sr.reason}")
            total_time += sr.duration_ms
        print("-" * 60)
        print(f"{'Total':<25} {'':>6} {total_time:>10.1f}ms")
        print("=" * 60)
        print("\n")
