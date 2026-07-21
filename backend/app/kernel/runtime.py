import dataclasses
import time
import uuid
from typing import Any

from .models import (
    ExecutionState, CognitiveGoal, CognitiveSession,
    CognitiveAnswer, ExecutiveResponse, VerificationResult,
    PromptContext, AnswerConfidence, CognitiveTrace,
    Intent, CommunicationMode, _hash, ExecutionStatus,
    AgentPolicy, WorkspaceSession, RuntimeVersion
)
from .registry import CapabilityRegistry
from .provider import LLMProvider
from .provider_manager import ProviderManager
from .planner import PlanningEngine
from .executor import Executor, CapabilityPlanner
from .reflection import ReflectionEngine
from .policy import PolicyEngine
from .answer_builder import AnswerBuilder
from .synthesizer import AdaptiveSynthesizer
from .router import IntentRouter
from .events import get_event_bus
from .semantic_parser import SemanticQueryParser
from .retriever import CapabilityRetriever
from .entity_resolver import EntityResolver


class RuntimeStartupValidationError(Exception):
    pass

class CognitiveRuntime:
    """
    On-demand entry point for the Cognitive Intelligence Layer.
    All pipeline stages consume and produce immutable ExecutionState objects.
    """
    def __init__(self, provider_manager: ProviderManager, agent_policy: AgentPolicy):
        self.provider = provider_manager
        self.policy_engine = PolicyEngine(agent_policy)

        self.registry = CapabilityRegistry()
        self.planner = PlanningEngine(self.registry)
        self.executor = Executor(self.registry)
        self.capability_planner = CapabilityPlanner(self.registry)
        self.reflection_engine = ReflectionEngine(self.provider)
        self.answer_builder = AnswerBuilder()
        self.synthesizer = AdaptiveSynthesizer(self.provider)
        self.router = IntentRouter(self.provider)
        self.event_bus = get_event_bus()
        
        # M57.15 Semantic Pipeline
        self.semantic_parser = SemanticQueryParser(self.provider)
        self.retriever = CapabilityRetriever(self.registry)
        self.entity_resolver = EntityResolver()
        
        # Late import orchestrator to avoid circular dependencies if any
        from .orchestrator import AgentOrchestrator
        self.orchestrator = AgentOrchestrator(
            planner=self.planner,
            executor=self.executor,
            capability_planner=self.capability_planner,
            reflection_engine=self.reflection_engine,
            policy_engine=self.policy_engine,
            answer_builder=self.answer_builder,
            synthesizer=self.synthesizer,
            semantic_parser=self.semantic_parser,
            retriever=self.retriever,
            entity_resolver=self.entity_resolver,
            registry=self.registry,
            provider_manager=self.provider
        )
        
        self._validate_startup()

    def _validate_startup(self) -> None:
        from .adapter import PlatformResultAdapter
        implemented = [c for c in self.registry.get_all() if c.contract.implemented.name == "IMPLEMENTED"]
        
        method_map = {
            "cap_top_contributors": "organization",
            "cap_ownership": "ownership",
            "cap_bus_factor": "organization",
            "cap_health": "health",
            "cap_forecast": "forecast",
            "cap_simulation": "simulation",
            "cap_dev_departure_simulation": "simulation",
            "cap_ownership_simulation": "simulation",
            "cap_architecture_simulation": "simulation",
            "cap_forecast_simulation": "simulation",
            "cap_risk_simulation": "simulation",
            "cap_causal_analysis": "causal",
            "cap_knowledge_graph": "knowledge_graph",
        }
        
        print("\nCapability Coverage\n")
        for cap in implemented:
            if cap.contract.id not in method_map:
                raise RuntimeStartupValidationError(f"Capability {cap.name} (id: {cap.contract.id}) is missing executor mapping.")
            
            adapter_method = method_map[cap.contract.id]
            if not hasattr(PlatformResultAdapter, adapter_method):
                raise RuntimeStartupValidationError(f"Adapter is missing method '{adapter_method}' required by {cap.name}.")
                
            if not cap.contract.output_type:
                raise RuntimeStartupValidationError(f"Capability {cap.name} is missing a schema in contract.outputs.")
                
            print(f"{cap.name:<20} OK")
            
        print(f"\nImplemented : {len(implemented)}")
        print(f"Validated   : {len(implemented)}")
        print(f"Coverage    : 100%\n")

    def create_session(self) -> CognitiveSession:
        return CognitiveSession(session_id=str(uuid.uuid4()))

    def answer(
        self,
        platform_result: Any,
        question: str,
        session: CognitiveSession = None
    ) -> ExecutionState:
        """
        Executes the cognitive pipeline conditionally based on intent routing.
        Returns an immutable ExecutionState.
        """
        if session is None:
            session = self.create_session()

        mode = session.communication_mode

        trace = []

        # ─── Stage 0: Intent Routing ───────────────────────────────────────
        t0 = time.monotonic()
        classification = self.router.route(question)
        goal = CognitiveGoal(query=question, classification=classification)
        intent = classification.intent

        state = ExecutionState(
            goal=goal,
            classification=classification,
            platform_result=platform_result,
            runtime_version=RuntimeVersion(
                runtime_version="M57.11",
                prompt_version="planner_v4",
                policy_version="provider_v2",
                benchmark_version="2026.07"
            )
        )
        
        # ─── Fast Path: General Chat ───────────────────────────────────────
        if intent == Intent.GENERAL_CHAT:
            response = self.provider.generate(f"System: You are a helpful AI engineering assistant.\nUser: {question}")
            
            content = response.content
            if "[ALL_PROVIDERS_FAILED]" in content:
                content = "I'm currently unable to connect to my AI providers. Please check your API keys or quota limits."
            
            # Create a mock answer
            verification = VerificationResult(original_text=content, verified_text=content, critiques=[], dropped_claims=0)
            ans = CognitiveAnswer(query=question, response=content, verification=verification)
            exec_resp = ExecutiveResponse(
                executive_summary=ans.response, technical_summary="Conversational bypass.",
                actionable_recommendations=[], supporting_evidence=[], confidence=1.0, risks=[], alternative_strategies=[]
            )
            return dataclasses.replace(state, answer=ans, executive_response=exec_resp)

        # ─── Full Pipeline with Agent Loop ────────────────────────────
        t1 = time.monotonic()
        
        # Build initial prompt context (stubbed for now, full context inside planner)
        prompt_context = PromptContext(system_prompt="", user_query=question, artifacts=[], intent=intent, workspace_session=session.workspace_session)
        state = dataclasses.replace(state, prompt_context=prompt_context)
        
        # Run agent loop
        state = self.orchestrator.run(state)
        
        return state
