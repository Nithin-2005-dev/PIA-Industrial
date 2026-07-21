from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.core.common import utc_now
from app.core.module import ModuleRegistry


class HealthStatus(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True)
class HealthReport:
    name: str
    status: HealthStatus
    version: str
    dependencies: tuple[str, ...]
    metrics: dict[str, float]
    resource_usage: dict[str, float]
    checked_at: object
    details: dict[str, Any]


class HealthRegistry:
    def __init__(
        self,
        module_registry: ModuleRegistry,
    ):
        self._module_registry = module_registry
        self._metrics: dict[str, dict[str, float]] = {}
        self._resources: dict[str, dict[str, float]] = {}

    def record_metric(
        self,
        module_name: str,
        metric: str,
        value: float,
    ) -> None:
        self._metrics.setdefault(
            module_name,
            {},
        )[metric] = value

    def record_resource(
        self,
        module_name: str,
        resource: str,
        value: float,
    ) -> None:
        self._resources.setdefault(
            module_name,
            {},
        )[resource] = value

    def report(
        self,
        module_name: str,
    ) -> HealthReport:
        module = self._module_registry.get(module_name)
        state = self._module_registry.state(module_name)
        status = (
            HealthStatus.HEALTHY
            if state.value in {"started", "initialized"}
            else HealthStatus.DEGRADED
        )
        return HealthReport(
            name=module.name,
            status=status,
            version=module.version,
            dependencies=module.dependencies,
            metrics=self._metrics.get(
                module_name,
                {},
            ),
            resource_usage=self._resources.get(
                module_name,
                {},
            ),
            checked_at=utc_now(),
            details={
                "state": state.value,
                "capabilities": module.capabilities,
            },
        )

    def all_reports(
        self,
    ) -> tuple[HealthReport, ...]:
        return tuple(
            self.report(descriptor.name)
            for descriptor in self._module_registry.discover()
        )

