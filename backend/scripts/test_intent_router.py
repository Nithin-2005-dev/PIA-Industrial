import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.kernel.provider import MockLLMProvider
from app.kernel.router import IntentRouter
from app.kernel.models import Intent, CognitiveTopic

def main():
    print("=====================================================")
    print(" Intent Router Deterministic Tests (M57.2)")
    print("=====================================================")

    provider = MockLLMProvider()
    router = IntentRouter(provider)

    test_matrix = [
        ("hello", Intent.GENERAL_CHAT),
        ("hi", Intent.GENERAL_CHAT),
        ("thanks", Intent.GENERAL_CHAT),
        ("thank you", Intent.GENERAL_CHAT),
        ("who are you", Intent.GENERAL_CHAT),
        ("what models do you use", Intent.SYSTEM_PLATFORM),
        ("help", Intent.SYSTEM_PLATFORM),
        ("what repository is loaded", Intent.SYSTEM_RUNTIME),
        ("show planner", Intent.SYSTEM_RUNTIME),
        ("summarize repository", Intent.REPOSITORY_QUERY),
        ("forecast next month", Intent.REPOSITORY_QUERY),
        ("analyze kubernetes", Intent.REPOSITORY_QUERY),
        ("compare forecast and simulation", Intent.REPOSITORY_QUERY),
        ("explain graph theory", Intent.HYBRID_QUERY),
        ("what is git", Intent.HYBRID_QUERY),
        ("explain DFS", Intent.HYBRID_QUERY),
    ]

    passed = 0
    failed = 0

    for query, expected_intent in test_matrix:
        result = router.route(query)
        if result.intent == expected_intent:
            print(f"[PASS] '{query}' -> {result.intent.name} (Conf: {result.confidence})")
            passed += 1
        else:
            print(f"[FAIL] '{query}' -> Expected {expected_intent.name}, got {result.intent.name}")
            failed += 1

    print("\n=====================================================")
    print(f" TESTS COMPLETE: {passed} Passed, {failed} Failed")
    print("=====================================================")
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
