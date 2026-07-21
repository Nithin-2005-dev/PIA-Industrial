import os
import sys

# Fake token
os.environ["GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN", "")

from app.kernel.runtime import CognitiveRuntime
from app.kernel.provider_manager import ProviderManager
from app.kernel.provider import MockLLMProvider
from app.kernel.models import AgentPolicy

# Create runtime
provider_manager = ProviderManager([MockLLMProvider()], AgentPolicy(max_iterations=1, require_confidence=0.0))
runtime = CognitiveRuntime(provider_manager, AgentPolicy(max_iterations=1, require_confidence=0.0))

# Mock platform result for testing
from app.kernel.adapter import PlatformResultAdapter
class MockPlatformResult:
    def __init__(self):
        self.repository = "expressjs/express"
        self.branch = "master"
        self.commit_limit = 20
        self.github_token = os.environ["GITHUB_TOKEN"]
        self.tenant_id = "test"
        
result = MockPlatformResult()

session = runtime.create_session()
state = runtime.answer(
    platform_result=result,
    question="Analyze knowledge risks",
    session=session
)

print(state.executive_response.executive_summary)
print("SUCCESS!")
