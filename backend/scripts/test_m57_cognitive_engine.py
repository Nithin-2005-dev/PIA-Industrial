import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.kernel.runtime import CognitiveRuntime
from app.kernel.provider import MockLLMProvider
from app.kernel.models import RepositorySession

def run_tests():
    print("=====================================================")
    print(" M57 Cognitive Engine Regression Tests")
    print("=====================================================")
    
    provider = MockLLMProvider()
    runtime = CognitiveRuntime(provider=provider)
    session = runtime.create_session()
    
    repo_session = RepositorySession(repository="facebook/react", commit_window=100)
    session.set_repository(repo_session)

    class DummyPlatformResult:
        repository = "facebook/react"
        commits = 100

    platform_result = DummyPlatformResult()

    # Test 1: General Chat
    print("[1] Testing GENERAL_CHAT intent...")
    state = runtime.answer(platform_result, "Hello there!", session)
    assert state.classification.intent.value == "general_chat"
    assert "Conversational bypass" in state.executive_response.technical_summary
    print("    -> PASS")

    # Test 2: System Query
    print("[2] Testing SYSTEM_PLATFORM intent...")
    state = runtime.answer(platform_result, "what models do you use", session)
    assert state.classification.intent.value == "system_platform"
    assert "Platform: PIA" in state.executive_response.executive_summary
    print("    -> PASS")

    # Test 3: Repository Query (Triggers Full Pipeline & Observability)
    print("[3] Testing REPOSITORY_QUERY with Reflection Loop & Tracing...")
    state = runtime.answer(platform_result, "Who is the top contributor?", session)
    assert state.classification.intent.value == "repository_query"
    assert len(state.reasoning_trace) > 5  # Ensure observability works
    
    has_planner_trace = any("planner" in t.stage for t in state.reasoning_trace)
    assert has_planner_trace, "Missing planner trace"
    print("    -> PASS")
    
    # Test 4: Repository Resolution
    print("[4] Testing Repository Resolution Injection...")
    assert "facebook/react" in state.prompt_context.system_prompt
    print("    -> PASS")

    # Test 5: Adaptive Communication Mode
    print("[5] Testing Adaptive Communication (STUDENT mode)...")
    state = runtime.answer(platform_result, "Explain like I'm new how a graph works", session)
    # The heuristic should detect STUDENT mode
    assert any("student" in t.decision for t in state.reasoning_trace if t.stage == "synthesizer")
    print("    -> PASS")

    print("=====================================================")
    print(" ALL TESTS PASSED")
    print("=====================================================")

if __name__ == "__main__":
    run_tests()
