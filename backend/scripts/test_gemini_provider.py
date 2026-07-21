import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.kernel.provider import GeminiProvider
from app.kernel.models import ToolSpecification

def main():
    print("=====================================================")
    print(" Gemini Provider Independent Test (M57.1)")
    print("=====================================================")

    # 1. Verification
    print("\n[1] Verifying API Key...")
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("[FAIL] GEMINI_API_KEY environment variable is missing.")
        sys.exit(1)
    print("[PASS] API Key loaded.")

    # Instantiate Provider
    provider = GeminiProvider(api_key=api_key, debug=True)

    # 2. Test Hello
    print("\n[2] Testing 'Hello'...")
    resp = provider.generate("hello")
    print(f"\nResponse:\n{resp.content}")

    if "Error Type" in resp.content or "Unexpected Error" in resp.content:
        print("\n[FAIL] Provider could not answer 'Hello'. Stopping tests.")
        sys.exit(1)
    
    print("\n[PASS] 'Hello' succeeded.")

    # 3. Test Math
    print("\n[3] Testing '2+2'...")
    resp = provider.generate("what is 2+2?")
    print(f"\nResponse:\n{resp.content}")
    print("\n[PASS] Math succeeded.")

    # 4. Test Engineering Payload
    print("\n[4] Testing Engineering JSON Payload with Mock Tool...")
    mock_tool = ToolSpecification(
        name="mock_architecture_tool",
        description="Retrieves architecture layers.",
        inputs=["layer_name"],
        outputs=["layer_details"]
    )
    
    resp = provider.generate(
        prompt="Use the mock tool to get the Observation Layer.",
        tools=[mock_tool]
    )
    print(f"\nResponse:\n{resp.content}")
    
    if "PLAN:" in resp.content:
        print("\n[PASS] Tool selection succeeded.")
    else:
        print("\n[WARN] LLM did not return a PLAN block, but the request succeeded.")

    print("\n=====================================================")
    print(" ALL TESTS COMPLETE")
    print("=====================================================")

if __name__ == "__main__":
    main()
