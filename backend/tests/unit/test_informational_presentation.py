import pytest
from app.kernel.models import (
    ExecutionState, CognitiveGoal, CognitiveSession, CommunicationMode, IntentClassification, Intent,
    CapabilityResult, TopContributorReport, RepositoryMemory, PromptContext, RuntimeVersion
)
from app.kernel.pipelines.informational import InformationalPipeline
from app.kernel.provider_manager import ProviderManager
from app.kernel.models import AgentPolicy

class EchoProvider:
    def generate(self, *args, **kwargs):
        class MockResponse:
            content = f"ECHO: {args}"
        return MockResponse()

def test_informational_presentation_top_contributor():
    # Setup the provider and pipeline
    provider_mgr = ProviderManager([EchoProvider()], AgentPolicy())
    # We can pass None for planner and executor since we only test present()
    pipeline = InformationalPipeline(planner=None, executor=None, provider=provider_mgr)
    
    # Create the TopContributor DTO
    contributors = [{"name": "hoxyq", "commits": 9}]
    report = TopContributorReport(contributors=contributors, confidence=1.0)
    
    # Create a mock capability result containing the report
    result = CapabilityResult(
        capability_id="cap_top_contributors",
        status="SUCCESS",
        confidence=1.0,
        summary="Found top contributors", # This should NOT be used directly anymore
        evidence_ids=[],
        raw_output={},
        normalized_output={},
        warnings=[],
        recommendations=[],
        metadata={},
        execution_time_ms=10.0,
        report=report
    )
    
    # Create an observation wrapping the result
    class MockObservation:
        def __init__(self, output):
            self.output = output
            
    observations = [MockObservation(result)]
    
    repo_memory = RepositoryMemory(observations=tuple(observations))
    
    goal = CognitiveGoal(
        query="Who is the top contributor?",
        classification=IntentClassification(intent=Intent.GENERAL_CHAT, confidence=1.0, requires_repository=True, topics=[], reason="test")
    )
    
    state = ExecutionState(
        goal=goal,
        classification=goal.classification,
        platform_result=None,
        runtime_version=RuntimeVersion("v1", "v1", "v1", "v1"),
        repository_memory=repo_memory
    )
    
    # Call present
    final_state = pipeline.present(state)
    
    # Assert
    final_answer = final_state.executive_response.executive_summary
    
    # The final answer from the LLM (which echoes the prompt) MUST contain the structured data
    assert "hoxyq" in final_answer, "The Presentation Layer failed to pass the contributor name 'hoxyq' to the LLM."
    assert "9" in final_answer, "The Presentation Layer failed to pass the commits '9' to the LLM."
