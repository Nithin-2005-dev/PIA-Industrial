import time
import dataclasses

from app.kernel.models import (
    ExecutionState, PipelineStrategy, CognitiveTopic, Goal,
    ExecutionComplexity, CapabilityResult, ExecutiveResponse, AnswerConfidence, CognitiveAnswer, VerificationResult
)
from app.kernel.pipelines.base import CognitivePipeline
from app.kernel.planner import PlanningEngine
from app.kernel.executor import Executor
from app.kernel.provider_manager import ProviderManager


class InformationalPipeline(CognitivePipeline):
    """
    A lightweight pipeline that bypasses the Reasoning OS.
    Executes capabilities and uses a Tiny Prompt to return a natural answer.
    """
    def __init__(self, planner: PlanningEngine, executor: Executor, provider: ProviderManager):
        self._planner = planner
        self._executor = executor
        self._provider = provider
        self._strategy = PipelineStrategy(
            id="pipeline_informational",
            description="Executes simple queries deterministically without advanced reasoning.",
            requires_reasoning=False,
            requires_optimizer=False,
            requires_llm=True,
            presentation_plugin="tiny_prompt",
            priority=10,
            complexity=ExecutionComplexity.SIMPLE,
            supported_topics=(CognitiveTopic.GENERAL_KNOWLEDGE, CognitiveTopic.REPOSITORY, CognitiveTopic.ORGANIZATION, CognitiveTopic.EXPERTISE),
            supported_goals=(Goal.FIND_PERSON, Goal.FIND_OWNER, Goal.FIND_CONTRIBUTOR, Goal.EXPLAIN, Goal.VISUALIZE_GRAPH, Goal.SUMMARIZE)
        )

    @property
    def strategy(self) -> PipelineStrategy:
        return self._strategy

    def plan(self, state: ExecutionState) -> ExecutionState:
        # Same initial planning as before for capability selection
        actions, execution_graph, plan_diagnostics = self._planner.plan(state.candidate_set, state.semantic_query, state.goal_graph)
        state = dataclasses.replace(state, execution_graph=execution_graph)
        
        # We store actions in state so execute() can use them. We can temporarily store them in tool_history.
        # Actually, let's just do it directly. We'll store them in a temporary attribute if needed, but since state is immutable, 
        # we can execute in execute() by re-planning or storing in state.
        # For simplicity, we can do everything in execute() or store it.
        # Let's add pending_actions to agent_memory.
        agent_mem = dataclasses.replace(state.agent_memory, pending_actions=tuple(actions))
        return dataclasses.replace(state, agent_memory=agent_mem)

    def execute(self, state: ExecutionState) -> ExecutionState:
        from app.kernel.models import ExecutionRequest
        actions = state.agent_memory.pending_actions
        requests = [ExecutionRequest(capability=a.tool, arguments=a.arguments, cacheable=True) for a in actions]
        
        observations = self._executor.execute_queue(requests, state.platform_result)
        repo_mem = dataclasses.replace(state.repository_memory, observations=list(state.repository_memory.observations) + observations)
        
        return dataclasses.replace(
            state,
            repository_memory=repo_mem,
            tool_history=state.tool_history + tuple(a.tool for a in actions)
        )

    def present(self, state: ExecutionState) -> ExecutionState:
        from app.kernel.presentation_mapper import InformationalPresentationMapper
        import json
        
        successful_results = [
            obs.output for obs in state.repository_memory.observations
            if isinstance(obs.output, CapabilityResult) and obs.output.status == "SUCCESS"
        ]
        
        # Tiny Prompt
        prompt = f"""
        User Query: "{state.goal.query}"
        
        Presentation Data:
        """
        for r in successful_results:
            if hasattr(r, 'report') and r.report:
                presentation_model = InformationalPresentationMapper.map_report(r.report)
                prompt += f"- {r.capability_id}: {json.dumps(presentation_model)}\n"
            else:
                prompt += f"- {r.capability_id}: {r.summary}\n"
            
        prompt += "\nProvide a concise, direct answer based ONLY on the Presentation Data above. Do not hallucinate. Do not extract facts from execution traces."
        
        response = self._provider.generate(prompt)
        content = response.content
        
        verification = VerificationResult(original_text=content, verified_text=content, critiques=[], dropped_claims=0)
        answer = CognitiveAnswer(query=state.goal.query, response=content, verification=verification)
        
        exec_resp = ExecutiveResponse(
            executive_summary=content,
            technical_summary="Generated via Informational Pipeline.",
            actionable_recommendations=[],
            supporting_evidence=[],
            confidence=1.0,
            risks=[],
            alternative_strategies=[]
        )
        
        confidence = AnswerConfidence(1.0, 1.0, 1.0, 1.0, 1.0)
        
        return dataclasses.replace(
            state,
            answer=answer,
            executive_response=exec_resp,
            confidence=confidence
        )
