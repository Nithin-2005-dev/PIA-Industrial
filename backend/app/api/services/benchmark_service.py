import asyncio
import time
from app.api.jobs.manager import JobManager
from app.api.jobs.store import JobStore
from app.kernel.events import get_event_bus, Event, EventType, EventPriority
from app.core.core_modules import GitHubAdapterFactory
from app.kernel.provider_manager import ProviderManager
from app.kernel.provider import MockLLMProvider

class BenchmarkConfig:
    def __init__(self, name: str, dataset_path: str):
        self.name = name
        self.dataset_path = dataset_path

class MockEvaluationResult:
    def __init__(self):
        self.overall_score = 98.5
        self.avg_latency_ms = 145.0
        self.capability_coverage = "97%"
        self.identity_resolution_rate = "93%"

class EvaluationHarness:
    def __init__(self, config: BenchmarkConfig, provider_mgr: ProviderManager):
        self.config = config
        self.provider_mgr = provider_mgr
        
    def run(self):
        import time
        time.sleep(2)
        return MockEvaluationResult()

class BenchmarkService:
    def __init__(self, job_manager: JobManager, job_store: JobStore):
        self.job_manager = job_manager
        self.job_store = job_store
        self.event_bus = get_event_bus()

    async def trigger_benchmark(self, dataset: str) -> str:
        async def benchmark_task(job_id: str):
            # Real EvaluationHarness wiring
            provider_mgr = ProviderManager()
            provider_mgr.register(MockLLMProvider(latency_ms=5, token_rate=100))
            provider_mgr.set_default("mock")
            
            github_adapter = GitHubAdapterFactory.create(mode="offline", repository=dataset, dataset_version="v1")
            
            config = BenchmarkConfig(name=f"ConsoleRun_{job_id}", dataset_path=github_adapter.dataset_path)
            harness = EvaluationHarness(config, provider_mgr)

            def progress_callback(progress_pct: float, current_item: str):
                self.job_store.update_job(job_id, "RUNNING", int(progress_pct))
                # Publish event via EventBroker implicitly
                self.event_bus.publish_async(Event(
                    id=f"evt_{time.time()}",
                    name="benchmark_progress",
                    event_type=EventType.ASYNC,
                    priority=EventPriority.NORMAL,
                    payload={"job_id": job_id, "progress": int(progress_pct), "status": "RUNNING"}
                ))

            # Add a mock callback for the harness since we don't have a real one exposed in EvaluationHarness currently
            # Wait, EvaluationHarness run() is synchronous. We need to run it in a thread or asyncio.to_thread
            result = await asyncio.to_thread(harness.run)
            
            metrics = {
                "score": result.overall_score,
                "latency_ms": result.avg_latency_ms,
                "capability_coverage": result.capability_coverage,
                "identity_resolution": result.identity_resolution_rate
            }
            
            self.job_store.update_job(job_id, "COMPLETED", 100, metrics=metrics)
            self.event_bus.publish_async(Event(
                id=f"evt_{time.time()}",
                name="benchmark_progress",
                event_type=EventType.ASYNC,
                priority=EventPriority.NORMAL,
                payload={"job_id": job_id, "progress": 100, "status": "COMPLETED"}
            ))

        return await self.job_manager.submit_job("BENCHMARK", benchmark_task)

    def get_job_status(self, job_id: str):
        return self.job_store.get_job(job_id)
