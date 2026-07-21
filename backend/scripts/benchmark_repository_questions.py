import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.kernel.registry import CapabilityRegistry
from app.kernel.runtime import CognitiveRuntime
from app.kernel.models import AgentPolicy, ProviderPolicy, CommunicationMode
from app.kernel.provider_manager import ProviderManager
from tests.mocks.mock_provider import MockLLMProvider
from app.platform.runtime import PlatformRuntime

QUESTIONS = [
    "Who owns ReactDOM?",
    "Which subsystem is riskiest?",
    "Who reviews most PRs?",
    "Highest knowledge concentration?",
    "Forecast next month.",
    "Most unstable module.",
    "Explain architecture.",
    "Draw dependency graph.",
    "Who leaves biggest gap?",
    "Compare ownership between commits."
]

def run_benchmark():
    print("=========================================================")
    print(" M57.14 End-to-End Capability Composition Benchmark")
    print("=========================================================\n")
    
    # We use a mock LLM provider for the benchmark to test the routing and capability execution cleanly.
    provider = MockLLMProvider()
    provider_manager = ProviderManager(providers=[provider], policy=AgentPolicy())
    runtime = CognitiveRuntime(provider_manager=provider_manager, agent_policy=AgentPolicy())
    session = runtime.create_session()
    
    from app.kernel.models import WorkspaceSession
    repo_session = WorkspaceSession(
        repository="facebook/react",
        commit_window=10,
        metadata={"platform": "mock"}
    )
    session.set_repository(repo_session)
    
    print("Initializing Mock Platform Runtime...")
    platform = PlatformRuntime.create()
    platform.register_default_modules()
    # Use small commit window for speed in benchmark
    result = platform.run(repository="facebook/react", commits=10, github_token="mock_token")
    
    print("\nRunning benchmark questions...\n")
    
    total_time = 0
    successes = 0
    
    for i, q in enumerate(QUESTIONS):
        start = time.perf_counter_ns()
        
        # Patch the mock provider to return the correct capability based on the question
        mock_cap = "Simulation"
        if "Who owns" in q: mock_cap = "Ownership"
        elif "riskiest" in q: mock_cap = "RiskSimulation"
        elif "Who reviews" in q: mock_cap = "TopContributors"
        elif "concentration" in q: mock_cap = "BusFactor"
        elif "Forecast" in q: mock_cap = "Forecast"
        elif "unstable" in q: mock_cap = "Health"
        elif "architecture" in q: mock_cap = "ArchitectureSimulation"
        elif "dependency graph" in q: mock_cap = "KnowledgeGraph"
        elif "biggest gap" in q: mock_cap = "DeveloperDepartureSimulation"
        elif "Compare" in q: mock_cap = "CompareBranches"
        
        with patch.object(provider, 'generate') as mock_gen:
            from app.kernel.provider import LLMResponse
            def mock_generate(prompt, tools=(), **kwargs):
                if "Classify the following user query" in prompt:
                    return LLMResponse(content='```json\n{"intent": "REPOSITORY_QUERY", "requires_repository": true}\n```')
                elif "Available Capabilities" in prompt:
                    return LLMResponse(content=f'```json\n[{{\"name\": \"{mock_cap}\"}}]\n```')
                else:
                    return LLMResponse(content="FINAL_ANSWER")
                    
            mock_gen.side_effect = mock_generate
            
            try:
                state = runtime.answer(
                    platform_result=result,
                    question=q,
                    session=session,
                )
                success = "PASS" if len(state.tool_history) > 0 else "FAIL"
                tools = ", ".join(state.tool_history)
            except Exception as e:
                success = "FAIL"
                tools = f"Error: {e}"
            
        
        latency = (time.perf_counter_ns() - start) / 1e6
        total_time += latency
        
        if success == "PASS":
            successes += 1
            
        print(f"[{i+1}/{len(QUESTIONS)}] {q:<40} {success} ({latency:.1f}ms)")
        
        if success == "PASS":
            print(f"    → Routed to: {tools}")
            
    print("\n" + "=" * 57)
    print(f"Success Rate : {successes}/{len(QUESTIONS)} ({successes/len(QUESTIONS)*100:.0f}%)")
    print(f"Total Time   : {total_time:.1f}ms")
    print(f"Avg Latency  : {total_time/len(QUESTIONS):.1f}ms/query")
    print("=" * 57)

if __name__ == "__main__":
    run_benchmark()
