from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Configuration
from app.core.config import ConfigurationProvider
from app.core.api.contracts import RuntimePipelineInput
from app.core.api.contracts import RuntimePipelineResult
from app.core.canonical_pipeline import CanonicalPlatformPipeline
from app.core.core_modules import default_platform_modules
from app.core.di import ServiceCollection
from app.core.event_bus import EventBus
from app.core.health import HealthRegistry
from app.core.lifecycle import LifecycleManager
from app.core.module import ModuleRegistry
from app.core.observability import AuditLog
from app.core.observability import MetricsRecorder
from app.core.observability import StructuredLogger
from app.core.plugin import PluginRegistry
from app.core.scheduler import Scheduler


@dataclass
class PlatformRuntime:
    modules: ModuleRegistry
    services: ServiceCollection
    event_bus: EventBus
    configuration: ConfigurationProvider
    scheduler: Scheduler
    plugins: PluginRegistry
    logger: StructuredLogger
    metrics: MetricsRecorder
    audit_log: AuditLog

    @classmethod
    def create(
        cls,
        configuration: Configuration | None = None,
    ) -> "PlatformRuntime":
        return cls(
            modules=ModuleRegistry(),
            services=ServiceCollection(),
            event_bus=EventBus(),
            configuration=ConfigurationProvider(
                configuration or Configuration()
            ),
            scheduler=Scheduler(),
            plugins=PluginRegistry(),
            logger=StructuredLogger(),
            metrics=MetricsRecorder(),
            audit_log=AuditLog(),
        )

    def register_module(
        self,
        module,
    ) -> None:
        self.modules.register(module)
        module.configure_services(self.services)
        self.audit_log.append(
            action="module_registered",
            actor="platform",
            target=module.name,
            metadata={
                "version": module.version,
                "capabilities": module.capabilities,
            },
        )

    def register_default_modules(
        self,
    ) -> None:
        for module in default_platform_modules():
            if not self.modules.has(module.name):
                self.register_module(module)

    def build(
        self,
    ) -> "BuiltPlatformRuntime":
        provider = self.services.build_provider()
        health = HealthRegistry(self.modules)
        lifecycle = LifecycleManager(self.modules)
        return BuiltPlatformRuntime(
            runtime=self,
            provider=provider,
            health=health,
            lifecycle=lifecycle,
        )

    def run(
        self,
        repository: str,
        commits: int = 100,
        branch: str = "main",
        github_token: str | None = None,
        tenant_id: str = "default",
        output_directory=None,
        since_commit: str | None = None,
    ) -> RuntimePipelineResult:
        self.register_default_modules()
        built = self.build()
        built.initialize()
        built.start()
        try:
            return CanonicalPlatformPipeline(built).run(
                RuntimePipelineInput(
                    repository=repository,
                    branch=branch,
                    commits=commits,
                    github_token=github_token,
                    tenant_id=tenant_id,
                    output_directory=output_directory,
                    since_commit=since_commit,
                )
            )
        finally:
            built.shutdown()

    def branch(self, baseline_context: Any, scenario: Any, built_runtime: BuiltPlatformRuntime | None = None) -> Any:
        """
        Creates a branched execution of the canonical pipeline for a simulation scenario.
        Delegates to CanonicalPlatformPipeline.branch().
        """
        from app.core.canonical_pipeline import CanonicalPlatformPipeline
        
        # If not provided, we can't reliably get the currently running built_runtime from PlatformRuntime alone, 
        # but the showcase passes it implicitly through the pipeline.
        return CanonicalPlatformPipeline(built_runtime).branch(baseline_context, scenario)


@dataclass
class BuiltPlatformRuntime:
    runtime: PlatformRuntime
    provider: object
    health: HealthRegistry
    lifecycle: LifecycleManager

    def initialize(
        self,
    ) -> None:
        self.lifecycle.initialize(self)

    def start(
        self,
    ) -> None:
        self.lifecycle.start()
        
        # Phase 32: Schedule Nightly Analysis Job safely off the real-time event bus
        try:
            from app.core.jobs.analysis_job import NightlyAnalysisJob
            analysis_job = self.provider.resolve(NightlyAnalysisJob)
            self.runtime.scheduler.schedule_cron(
                job_id="nightly_analysis_job",
                handler=analysis_job.run,
                cron="0 0 * * *"  # Run nightly at midnight
            )
            self.runtime.logger.info("NightlyAnalysisJob scheduled successfully via Cron.")
        except Exception as e:
            self.runtime.logger.error(f"Failed to schedule NightlyAnalysisJob: {e}")

    def shutdown(
        self,
    ) -> None:
        self.lifecycle.stop()
        self.lifecycle.shutdown()
