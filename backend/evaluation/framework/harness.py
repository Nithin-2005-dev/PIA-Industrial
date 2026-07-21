from app.kernel.runtime import CognitiveRuntime
from tests.mocks.mock_provider import MockLLMProvider
from app.kernel.models import WorkspaceSession
from evaluation.framework.manifest import BenchmarkManifest
from evaluation.benchmarks.suites import ALL_SUITES
from evaluation.framework.assertions import AssertionEngine
from evaluation.framework.metrics import MetricsEngine, LayerMetrics, CoverageMetrics
from evaluation.framework.reporters import JSONReporter
from evaluation.framework.dataset_validator import DatasetValidator
import app.core.core_modules

from app.core.runtime import PlatformRuntime
from app.infrastructure.github.adapter import GitHubAdapter
from app.infrastructure.github.source import OfflineSnapshotSource

class MockContext:
    def __init__(self):
        self.org_intelligence = []
        self.knowledge_graph = None
        self.forecast_context = None
        self.causal_context = None
        self.simulation_context = None
        self.historical_context = None
        self.expertise_models = []
        self.knowledge = None
        self.measurements = []
        self.observations = []
        self.decisions = []
        self.evidence_package = None

class MockPlatformResult:
    def __init__(self, repository: str, commits: int):
        self.repository = repository
        self.commits = commits
        self.context = MockContext()

from app.kernel.provider_manager import ProviderManager
from app.kernel.models import AgentPolicy
import time

class EvaluationHarness:
    def __init__(self, manifest_path: str = "evaluation/benchmark.yaml"):
        self.manifest = BenchmarkManifest.load(manifest_path)
        mock_responses = {
            "semantic": '{"entities": [{"value": "contributor", "type": "domain"}], "relationships": []}',
            "intent": '{"intent": "REPOSITORY_QUERY", "confidence": 0.99, "reason": "test"}',
            "Who is the top contributor?": '{"intent": "REPOSITORY_QUERY", "confidence": 0.99, "reason": "test"}'
        }
        mock = MockLLMProvider(fixed_responses=mock_responses)
        self.provider = ProviderManager([mock], AgentPolicy())
        self.runtime = CognitiveRuntime(provider_manager=self.provider, agent_policy=AgentPolicy())
        
    def _run_cognitive_iterations(self, platform_result, query_text: str, session: WorkspaceSession, iterations: int = 10):
        states = []
        for _ in range(iterations):
            states.append(self.runtime.answer(platform_result, query_text, session))
        return states

    def run_suite(self):
        print(f"Starting Evaluation Harness (Manifest v{self.manifest.version})")
        print(f"Target: {self.manifest.dataset.repository} ({self.manifest.dataset.size})")
        
        repo_slug = self.manifest.dataset.repository.replace("/", "_")
        dataset_path = f"evaluation/datasets/v1/{repo_slug}"
        
        # 1. Dataset Validation
        dataset_valid = DatasetValidator.validate(dataset_path)
        real_platform_result = None
        if dataset_valid:
            print("Dataset Validation Passed. Running Real Platform Pipeline...")
            
            # Monkeypatch GitHubAdapter to use OfflineSnapshotSource
            class OfflineGitHubAdapterFactory:
                def create(self, token: str):
                    return GitHubAdapter(source=OfflineSnapshotSource(dataset_path))
            app.core.core_modules.GitHubAdapterFactory = OfflineGitHubAdapterFactory
            
            platform = PlatformRuntime.create()
            real_platform_result = platform.run(
                repository=self.manifest.dataset.repository, 
                commits=self.manifest.dataset.size,
                github_token="offline_dummy_token"
            )
        else:
            print("Dataset Validation Failed. Proceeding with Mock Only.")
            
        if real_platform_result and real_platform_result.errors:
            print(f"PIPELINE ERRORS: {real_platform_result.errors}")
            
        # [Validation] Run Operational Store Validation
        from evaluation.framework.validators.store_validator import StoreValidator
        print("Running Operational Store Validation...")
        store_passed, store_report = StoreValidator.validate()
        if not store_passed:
            print(store_report)
            print("Store Validation FAILED. Benchmark aborted.")
            return {"error": "Store Validation Failed"}
        print("Operational Store Validation Passed.")

        mock_platform_result = MockPlatformResult(repository=self.manifest.dataset.repository, commits=self.manifest.dataset.size)
        
        session = self.runtime.create_session()
        session.set_repository(WorkspaceSession(repository=self.manifest.dataset.repository, commit_window=self.manifest.dataset.size))
        
        results = {}
        
        for suite_name in self.manifest.enabled_suites:
            if suite_name not in ALL_SUITES:
                continue
                
            suite_queries = ALL_SUITES[suite_name]
            suite_results = []
            
            for query in suite_queries:
                print(f"  -> Executing Query: {query.question}")
                
                # Mock Runs
                mock_states = self._run_cognitive_iterations(mock_platform_result, query.question, session, iterations=10)
                mock_metrics = MetricsEngine.extract_metrics(mock_states[-1])
                mock_coverage = MetricsEngine.extract_coverage(mock_states[-1])
                mock_assertions = AssertionEngine.evaluate_facts(mock_states[-1], query.expected_facts)
                
                # Real Runs
                if real_platform_result:
                    real_states = self._run_cognitive_iterations(real_platform_result, query.question, session, iterations=10)
                    
                    if real_states[-1].status.name != "SUCCESS":
                        print(f"PIPELINE FAILED with status {real_states[-1].status.name} and reason {real_states[-1].failure_reason}")
                        if real_states[-1].executive_response:
                            print(f"TECHNICAL SUMMARY: {real_states[-1].executive_response.technical_summary}")
                        
                    real_metrics = MetricsEngine.extract_metrics(real_states[-1])
                    real_coverage = MetricsEngine.extract_coverage(real_states[-1])
                    real_assertions = AssertionEngine.evaluate_facts(real_states[-1], query.expected_facts)
                else:
                    real_metrics, real_coverage, real_assertions = None, None, None
                
                suite_results.append({
                    "id": query.id,
                    "question": query.question,
                    "mock": {
                        "assertions": mock_assertions,
                        "metrics": mock_metrics.model_dump(),
                        "coverage": mock_coverage.model_dump(),
                    },
                    "real": {
                        "assertions": real_assertions,
                        "metrics": real_metrics.model_dump() if real_metrics else None,
                        "coverage": real_coverage.model_dump() if real_coverage else None,
                    } if real_platform_result else None
                })
                
            results[suite_name] = suite_results
            
        print("Evaluation complete.")
        return results

if __name__ == "__main__":
    harness = EvaluationHarness()
    harness.run_suite()
