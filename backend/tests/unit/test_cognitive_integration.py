import pytest
import os
import json
from dataclasses import asdict
from app.kernel.runtime import CognitiveRuntime
from app.kernel.provider_manager import ProviderManager
from app.kernel.models import AgentPolicy, WorkspaceSession, CommunicationMode
from tests.mocks.mock_provider import MockLLMProvider
from app.core.api.contracts import RuntimePipelineResult
from tests.unit.test_platform_adapter import MockRuntimeContext, MockPlatformResult

def get_golden_file_path(snapshot_id: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "golden", f"{snapshot_id}.json")

def test_full_pipeline_integration():
    """
    Tests the end-to-end flow from PlatformResult -> Adapter -> Executor 
    -> CapabilityResult -> Verifier -> AnswerBuilder.
    Ensures deterministic data is untouched.
    """
    mock_provider = MockLLMProvider()
    runtime = CognitiveRuntime(ProviderManager([mock_provider], AgentPolicy()), AgentPolicy())
    session = runtime.create_session()
    
    repo_session = WorkspaceSession(
        repository="facebook/react",
        commit_window=500,
        metadata={"platform": "github"}
    )
    session.set_repository(repo_session)
    session.communication_mode = CommunicationMode("auto")

    # Mock PlatformResult to simulate what the executor receives
    class TestPlatformResult(MockPlatformResult):
        def __init__(self):
            super().__init__()
            self.context.org_intelligence = {
                "top_contributors": ["real_dev_1", "real_dev_2"],
                "bus_factor": 1,
                "health_score": 90,
                "technical_debt": "low",
                "ownership_gini": 0.82
            }
            self.context.forecast_context = {"risk": "low"}
            self.context.causal_context = {"root_cause": "test"}
            self.context.simulation_context = {"impact": "none"}
            self.context.knowledge_graph = {"nodes": 1, "edges": 1}
            self.context.repository = "facebook/react"
            self.context.branch = "main"
            self.context.commit_limit = 500

    platform_result = TestPlatformResult()
    
    # Send a query that triggers the mock provider to select TopContributorsTool
    state = runtime.answer(
        platform_result=platform_result,
        question="Who is the top contributor?",
        session=session
    )
    
    # 1. Assert successful execution
    assert state.status.name == "SUCCESS"
    
    # 2. Check that the observation contains real deterministic data
    assert len(state.repository_memory.observations) > 0
    obs = state.repository_memory.observations[0]
    
    assert obs.output.raw_output is not None
    assert obs.output.normalized_output is not None
    
    # Ensure no mock placeholder values are present
    assert "Dev A" not in json.dumps(obs.output.raw_output)
    
    # 3. Check provenance chain
    assert obs.output.provenance is not None
    assert obs.output.provenance.adapter_version == "v1"
    assert obs.output.provenance.source_snapshot == "facebook/react"
    assert obs.output.provenance.source_commit_window == 500
    
    # 4. Golden snapshot validation
    snapshot_id = f"facebook-react-main-500-v1"
    golden_path = get_golden_file_path(snapshot_id)
    
    output_data = {
        "repository": "facebook/react",
        "branch": "main",
        "commit_window": 500,
        "runtime_version": "M57.13",
        "adapter_version": "v1",
        "snapshot_id": snapshot_id,
        "data": obs.output.raw_output
    }
    
    if not os.path.exists(golden_path):
        # Create it if it doesn't exist
        with open(golden_path, "w") as f:
            json.dump(output_data, f, indent=2)
    else:
        # Assert against golden file
        with open(golden_path, "r") as f:
            golden_data = json.load(f)
        assert golden_data["data"] == output_data["data"]
