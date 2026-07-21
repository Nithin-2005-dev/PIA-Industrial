from datetime import timedelta
from pathlib import Path
import sys

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)

from app.measurement.core.engine import MeasurementEngine
from app.platform import BaseModule
from app.platform import Configuration
from app.platform import EventBus
from app.platform import EventPriority
from app.platform import PipelineContext
from app.platform import PipelineEngine
from app.platform import PipelineStage
from app.platform import PipelineStageKind
from app.platform import PlatformEvent
from app.platform import PlatformRuntime
from app.platform import PluginKind
from app.platform import RetryPolicy
from app.platform import ServiceScope
from app.platform import TraceContext
from app.platform import ValidationIssue
from app.platform import ValidationResult
from app.platform import default_platform_modules


class Repository:
    def __init__(
        self,
    ):
        self.value = "repository"


class UsesRepository:
    def __init__(
        self,
        repository: Repository,
    ):
        self.repository = repository


class ModuleA(BaseModule):
    name = "module-a"
    version = "1.0"
    capabilities = ("cap.a",)

    def __init__(
        self,
        calls,
    ):
        self.calls = calls

    def configure_services(
        self,
        services,
    ):
        services.add(
            Repository,
            Repository,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            UsesRepository,
            UsesRepository,
            scope=ServiceScope.TRANSIENT,
        )

    def initialize(
        self,
        context,
    ):
        self.calls.append("a.initialize")

    def start(
        self,
    ):
        self.calls.append("a.start")

    def pause(
        self,
    ):
        self.calls.append("a.pause")

    def resume(
        self,
    ):
        self.calls.append("a.resume")

    def stop(
        self,
    ):
        self.calls.append("a.stop")

    def shutdown(
        self,
    ):
        self.calls.append("a.shutdown")


class ModuleB(BaseModule):
    name = "module-b"
    version = "1.0"
    dependencies = ("module-a",)
    capabilities = ("cap.b",)

    def __init__(
        self,
        calls,
    ):
        self.calls = calls

    def initialize(
        self,
        context,
    ):
        self.calls.append("b.initialize")

    def start(
        self,
    ):
        self.calls.append("b.start")

    def pause(
        self,
    ):
        self.calls.append("b.pause")

    def resume(
        self,
    ):
        self.calls.append("b.resume")

    def stop(
        self,
    ):
        self.calls.append("b.stop")

    def shutdown(
        self,
    ):
        self.calls.append("b.shutdown")


class DemoPlugin:
    id = "demo-measurement-provider"
    name = "Demo Measurement Provider"
    version = "1.0"
    kind = PluginKind.MEASUREMENT_PROVIDER
    capabilities = ("measurement.provider",)

    def create(
        self,
        context,
    ):
        return {
            "created": True,
            "profile": context.runtime.configuration.current().profile,
        }


def main():
    runtime = PlatformRuntime.create(
        Configuration(
            {
                "platform": {
                    "name": "pia",
                },
                "features": {
                    "plugins": True,
                },
            },
            profile="test",
        )
    )

    calls = []
    runtime.register_module(
        ModuleB(calls)
    )
    runtime.register_module(
        ModuleA(calls)
    )

    assert runtime.modules.startup_order() == (
        "module-a",
        "module-b",
    )
    assert runtime.modules.shutdown_order() == (
        "module-b",
        "module-a",
    )
    assert runtime.modules.providers_for("cap.a") == (
        "module-a",
    )

    built = runtime.build()
    built.initialize()
    built.start()
    built.lifecycle.pause()
    built.lifecycle.resume()
    built.shutdown()

    assert calls == [
        "a.initialize",
        "b.initialize",
        "a.start",
        "b.start",
        "b.pause",
        "a.pause",
        "a.resume",
        "b.resume",
        "b.stop",
        "a.stop",
        "b.shutdown",
        "a.shutdown",
    ]

    consumer = built.provider.resolve(UsesRepository)
    assert consumer.repository.value == "repository"

    events = []
    bus = EventBus()
    bus.subscribe(
        "demo.created",
        events.append,
    )
    bus.subscribe(
        "demo.created",
        lambda event: (_ for _ in ()).throw(
            RuntimeError("boom")
        ),
    )
    published = bus.publish_many(
        [
            PlatformEvent(
                type="demo.created",
                payload={
                    "id": "normal",
                },
                priority=EventPriority.NORMAL,
            ),
            PlatformEvent(
                type="demo.created",
                payload={
                    "id": "high",
                },
                priority=EventPriority.HIGH,
            ),
        ]
    )

    assert published[0].payload["id"] == "high"
    assert len(events) == 2
    assert len(bus.replay("demo.created")) == 2
    assert len(bus.dead_letters()) == 2

    run = PipelineEngine().run(
        [
            1,
            2,
            3,
        ],
        [
            PipelineStage(
                name="validate",
                kind=PipelineStageKind.VALIDATION,
                handler=lambda value, _: (
                    ValidationResult.passed()
                    if value
                    else ValidationResult.failed(
                        ValidationIssue(
                            "value",
                            "empty",
                        )
                    )
                ),
            ),
            PipelineStage(
                name="double",
                kind=PipelineStageKind.TRANSFORMATION,
                parallel=True,
                handler=lambda value, _: value * 2,
            ),
            PipelineStage(
                name="sum",
                kind=PipelineStageKind.AGGREGATION,
                handler=lambda value, _: sum(value),
                retry_policy=RetryPolicy(
                    attempts=2
                ),
            ),
        ],
        PipelineContext(
            correlation_id="corr",
            trace_id="trace",
        ),
    )

    assert run.output == 12
    assert run.completed_stages == (
        "validate",
        "double",
        "sum",
    )
    assert not run.errors

    config_changes = []
    runtime.configuration.subscribe(config_changes.append)
    runtime.configuration.override(
        {
            "features": {
                "experimental": True,
            }
        }
    )

    assert runtime.configuration.current().require("platform.name") == "pia"
    assert runtime.configuration.current().feature_enabled("experimental")
    assert config_changes

    scheduled = []
    runtime.scheduler.schedule_once(
        "job-1",
        lambda: scheduled.append("job-1"),
        delay=timedelta(),
    )
    assert runtime.scheduler.run_due() == ("job-1",)
    assert scheduled == ["job-1"]

    context = TraceContext.new()
    runtime.logger.log(
        "info",
        "platform runtime smoke test",
        context,
        subsystem="platform",
    )
    runtime.metrics.time(
        "noop",
        lambda: "ok",
    )
    runtime.audit_log.append(
        "test_action",
        "test",
        "platform",
    )

    assert runtime.logger.records()[0].correlation_id == context.correlation_id
    assert runtime.metrics.metrics()
    assert runtime.audit_log.records()

    runtime.plugins.register(
        DemoPlugin()
    )
    assert runtime.plugins.list(PluginKind.MEASUREMENT_PROVIDER)
    assert runtime.plugins.create(
        "demo-measurement-provider",
        built,
    )["created"]

    health = built.health.report("module-a")
    assert health.name == "module-a"
    assert health.version == "1.0"

    default_runtime = PlatformRuntime.create()
    for module in default_platform_modules():
        default_runtime.register_module(module)
    default_built = default_runtime.build()
    default_built.initialize()
    default_built.start()

    assert default_runtime.modules.startup_order() == (
        "observation",
        "measurement",
        "evidence",
        "estimation",
        "knowledge",
        "graph",
        "intelligence",
        "forecasting",
        "simulation",
        "agent",
        "decision",
        "executive",
    )
    assert default_runtime.modules.providers_for(
        "measurement.engine"
    ) == ("measurement",)
    assert isinstance(
        default_built.provider.resolve(MeasurementEngine),
        MeasurementEngine,
    )
    assert all(
        report.status.value == "healthy"
        for report in default_built.health.all_reports()
    )

    default_built.shutdown()

    print(
        "\n=== PLATFORM RUNTIME ===\n"
    )
    print(
        "M38 Core Platform Infrastructure passed."
    )


if __name__ == "__main__":
    main()
