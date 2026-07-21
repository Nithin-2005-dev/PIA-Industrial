import uuid
import sys
from app.kernel.models import CognitiveGoal, IntentClassification, Intent, ExecutionState, WorkspaceSession, AgentPolicy, PromptContext
from app.kernel.registry import CapabilityRegistry
from app.kernel.orchestrator import AgentOrchestrator
from app.kernel.semantic_parser import SemanticQueryParser
from app.kernel.retriever import CapabilityRetriever
from app.kernel.planner import PlanningEngine
from app.kernel.executor import CapabilityPlanner, Executor
from app.kernel.reflection import ReflectionEngine
from app.kernel.policy import PolicyEngine
from app.kernel.answer_builder import AnswerBuilder
from app.kernel.synthesizer import AdaptiveSynthesizer
from app.kernel.entity_resolver import EntityResolver
from app.kernel.provider import LLMProvider, LLMResponse

class DummyProvider(LLMProvider):
    def generate(self, prompt, **kwargs):
        print("Fallback LLM invoked!")
        return LLMResponse(content='{"topics": ["risk", "simulation"], "keywords": ["risk", "simulation"], "confidence": 0.8}')
    def stream(self, prompt, **kwargs):
        pass

provider = DummyProvider()
semantic_parser = SemanticQueryParser(provider)
default_registry = CapabilityRegistry()
retriever = CapabilityRetriever(default_registry)
planner = PlanningEngine(default_registry)
executor = Executor(default_registry)
capability_planner = CapabilityPlanner(default_registry)
reflection_engine = ReflectionEngine(provider)
policy_engine = PolicyEngine(AgentPolicy())
answer_builder = AnswerBuilder()
synthesizer = AdaptiveSynthesizer(provider)
entity_resolver = EntityResolver()

orchestrator = AgentOrchestrator(
    planner=planner,
    executor=executor,
    capability_planner=capability_planner,
    reflection_engine=reflection_engine,
    policy_engine=policy_engine,
    answer_builder=answer_builder,
    synthesizer=synthesizer,
    semantic_parser=semantic_parser,
    retriever=retriever,
    entity_resolver=entity_resolver,
    registry=default_registry
)

# Dummy PlatformResult
class MockContext:
    org_intelligence = {}
    forecast_context = {}
    causal_context = {}
    simulation_context = {}
    knowledge_graph = {}

class MockPlatformResult:
    def __init__(self):
        self.context = MockContext()

state = ExecutionState(
    goal=CognitiveGoal(query="run a risk simulation"),
    classification=IntentClassification(intent=Intent.REPOSITORY_QUERY, confidence=1.0, reason="", requires_repository=True),
    platform_result=MockPlatformResult(),
    prompt_context=PromptContext(system_prompt="", user_query="", artifacts=[], workspace_session=WorkspaceSession("test/repo")),
    query_id=str(uuid.uuid4())
)

print("Running orchestrator...")
final_state = orchestrator.run(state)

print(f"\nFinal Status: {final_state.status}")
print(f"Executive Response:\n{final_state.executive_response.technical_summary if final_state.executive_response else 'None'}")
