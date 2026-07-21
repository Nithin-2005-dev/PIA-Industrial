import pytest
from app.kernel.adapter import PlatformResultAdapter, MissingMeasurementException, PlatformCompatibilityException

class MockRuntimeContext:
    def __init__(self, missing=False):
        if missing:
            return # Empty context
        self.org_intelligence = {"test": 1}
        self.forecast_context = {"test": 2}
        self.causal_context = {"test": 3}
        self.simulation_context = {"test": 4}
        self.knowledge_graph = {"test": 5}
        self.repository = "test/repo"
        self.branch = "main"
        self.commit_limit = 100

class MockPlatformResult:
    def __init__(self, missing=False):
        if missing:
            self.context = None
        else:
            self.context = MockRuntimeContext()

def test_adapter_compatibility():
    # Should pass
    result = MockPlatformResult()
    adapter = PlatformResultAdapter(result)
    assert adapter.version == "v1"

    # Should fail if context is completely missing
    result_missing = MockPlatformResult(missing=True)
    with pytest.raises(PlatformCompatibilityException):
        PlatformResultAdapter(result_missing)
        
    # Should fail if a specific section is missing
    result_partial = MockPlatformResult()
    delattr(result_partial.context, "knowledge_graph")
    with pytest.raises(PlatformCompatibilityException):
        PlatformResultAdapter(result_partial)

def test_adapter_methods():
    result = MockPlatformResult()
    adapter = PlatformResultAdapter(result)

    assert adapter.organization() == {"test": 1}
    assert adapter.forecast() == {"test": 2}
    assert adapter.causal() == {"test": 3}
    assert adapter.simulation() == {"test": 4}
    assert adapter.knowledge_graph() == {"test": 5}
    
    summary = adapter.repository_summary()
    assert summary["repository"] == "test/repo"
    assert summary["branch"] == "main"
    assert summary["commit_window"] == 100

def test_adapter_missing_data_raises_exception():
    result = MockPlatformResult()
    adapter = PlatformResultAdapter(result)
    
    # Manually delete it after init to test the extraction methods
    adapter._context.org_intelligence = None
    with pytest.raises(MissingMeasurementException):
        adapter.organization()

def test_adapter_immutability():
    result = MockPlatformResult()
    adapter = PlatformResultAdapter(result)
    org_data = adapter.organization()
    
    # We test that the adapter does not mutate the RuntimePipelineResult.
    assert adapter._result is result
    assert result.context.org_intelligence == {"test": 1}
