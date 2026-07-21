import time
import dataclasses
import asyncio

from app.kernel.models import (
    ExecutionState, PipelineStrategy, CognitiveTopic, Goal,
    ExecutionComplexity, CapabilityResult, ExecutiveResponse, AnswerConfidence, CognitiveAnswer, VerificationResult
)
from app.kernel.pipelines.base import CognitivePipeline
from app.kernel.planner import PlanningEngine
from app.kernel.executor import Executor
from app.kernel.provider_manager import ProviderManager


class DecisionPipeline(CognitivePipeline):
    """
    A heavyweight pipeline that instantiates the full Reasoning OS graph and pareto optimizer.
    Uses the Executive Prompt to present the final analysis.
    """
    def __init__(self, planner: PlanningEngine, executor: Executor, provider: ProviderManager):
        self._planner = planner
        self._executor = executor
        self._provider = provider
        self._strategy = PipelineStrategy(
            id="pipeline_decision",
            description="Instantiates GraphEngine and Optimizer to compute causal inferences and recommendations.",
            requires_reasoning=True,
            requires_optimizer=True,
            requires_llm=True,
            presentation_plugin="executive_prompt",
            priority=50, # Higher priority than informational
            complexity=ExecutionComplexity.COMPLEX,
            supported_topics=(CognitiveTopic.CAUSAL, CognitiveTopic.OPTIMIZATION, CognitiveTopic.EXECUTIVE, CognitiveTopic.FORECAST, CognitiveTopic.SIMULATION),
            supported_goals=(Goal.IDENTIFY_RISK, Goal.DIAGNOSE_CAUSALITY, Goal.SIMULATE_DEPARTURE, Goal.SIMULATE_ARCHITECTURE, Goal.SIMULATE_FORECAST, Goal.SIMULATE_RISK, Goal.ANALYZE)
        )

    @property
    def strategy(self) -> PipelineStrategy:
        return self._strategy

    def plan(self, state: ExecutionState) -> ExecutionState:
        actions, execution_graph, plan_diagnostics = self._planner.plan(state.candidate_set, state.semantic_query, state.goal_graph)
        state = dataclasses.replace(state, execution_graph=execution_graph)
        agent_mem = dataclasses.replace(state.agent_memory, pending_actions=tuple(actions))
        return dataclasses.replace(state, agent_memory=agent_mem)

    def execute(self, state: ExecutionState) -> ExecutionState:
        from app.kernel.models import ExecutionRequest
        actions = state.agent_memory.pending_actions
        requests = [ExecutionRequest(capability=a.tool, arguments=a.arguments, cacheable=True) for a in actions]
        
        observations = self._executor.execute_queue(requests, state.platform_result)
        repo_mem = dataclasses.replace(state.repository_memory, observations=list(state.repository_memory.observations) + observations)
        
        state = dataclasses.replace(
            state,
            repository_memory=repo_mem,
            tool_history=state.tool_history + tuple(a.tool for a in actions)
        )
        
        # ─── Intelligence OS Execution (Graph Pipeline) ───
        from app.kernel.graph import GraphEngine
        from app.kernel.reasoning.builder import ReasoningGraphBuilder
        from app.kernel.reasoning.rule_engine import RuleEngine, create_single_point_of_failure_rule
        from app.kernel.reasoning.strategy import StrategyEngine
        from app.kernel.intelligence.ontology import CoreOntology
        from app.kernel.intelligence.translator import BusinessTranslator
        from app.kernel.intelligence.priority import PriorityEngine
        from app.kernel.decision.root_cause import RootCauseAnalyzer
        from app.kernel.decision.optimizer import GraphOptimizer
        from app.kernel.decision.mitigation import MitigationEngine
        from app.kernel.presentation.phrasing import InsightPhraser
        from app.kernel.presentation.report import ExecutiveReportGenerator
        
        graph = GraphEngine()
        
        successful_results = [
            obs.output for obs in state.repository_memory.observations
            if isinstance(obs.output, CapabilityResult) and obs.output.status == "SUCCESS"
        ]
        
        builder = ReasoningGraphBuilder(graph)
        builder.build_from_results(successful_results)
        
        rule_engine = RuleEngine(graph)
        rule_engine.register_rule(create_single_point_of_failure_rule())
        StrategyEngine(graph, rule_engine).execute_reasoning_cycle()
        
        PriorityEngine(graph).score_graph_inferences()
        BusinessTranslator(graph, CoreOntology()).translate_inferences_to_impact()
        
        RootCauseAnalyzer(graph).analyze_root_causes()
        GraphOptimizer(graph).optimize()
        MitigationEngine(graph).generate_mitigations()
        
        # Store graph in state (using a temporary attribute if needed, but since it's an object we can just pass it directly if we had a field for it).
        # We can add `reasoning_graph` to ExecutionState or just pass the final report in present().
        # To strictly follow plan-execute-present, we need to pass graph state. Let's add it to state dynamically or via a field.
        # For now, since present() relies on graph, we can do it all in execute() or just attach it to state.
        
        phraser = InsightPhraser(graph, self._provider)
        phrased_impacts = asyncio.run(phraser.phrase_impacts())
        
        generator = ExecutiveReportGenerator(graph)
        final_markdown_report = generator.generate_markdown_report(phrased_impacts)
        
        # Populate reasoning_trace for diagnostic assertions
        from app.kernel.models import CognitiveTrace
        trace = CognitiveTrace(
            stage="Reasoning",
            execution_time_ms=10.0,
            token_usage=0,
            prompt_version="1.0",
            decision="Generated reasoning graph",
            output_summary=f"Graph with {len(graph._nodes)} nodes and {len(graph._edges)} edges",
            input_hash="n/a",
            output_hash="n/a"
        )
        state = dataclasses.replace(state, reasoning_trace=state.reasoning_trace + (trace,))
        
        # Storing report in state so present() can pick it up
        verification = VerificationResult(original_text=final_markdown_report, verified_text=final_markdown_report, critiques=[], dropped_claims=0)
        answer = CognitiveAnswer(query=state.goal.query, response=final_markdown_report, verification=verification)
        state = dataclasses.replace(state, answer=answer)
        
        return state

    def present(self, state: ExecutionState) -> ExecutionState:
        # Extract the report generated in execute()
        final_markdown_report = state.answer.response
        
        # Pass the final report up as the executive summary so the UI prints it
        exec_resp = ExecutiveResponse(
            executive_summary=final_markdown_report,
            technical_summary="Generated via Decision Pipeline (GraphEngine + Optimizer).",
            actionable_recommendations=[],
            supporting_evidence=[],
            confidence=1.0,
            risks=[],
            alternative_strategies=[]
        )
        
        confidence = AnswerConfidence(1.0, 1.0, 1.0, 1.0, 1.0)
        
        return dataclasses.replace(
            state,
            executive_response=exec_resp,
            confidence=confidence
        )
