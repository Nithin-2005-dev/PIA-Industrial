from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.module import ModuleState


@dataclass(frozen=True)
class ProductionCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ProductionReadinessReport:
    ready: bool
    checks: tuple[ProductionCheck, ...]

    def failures(
        self,
    ) -> tuple[ProductionCheck, ...]:
        return tuple(
            check
            for check in self.checks
            if not check.passed
        )


class ProductionHardeningService:
    def audit(
        self,
        built_runtime,
        required_services: tuple[Any, ...] = (),
    ) -> ProductionReadinessReport:
        checks: list[ProductionCheck] = []
        checks.extend(
            self._module_checks(built_runtime)
        )
        checks.extend(
            self._health_checks(built_runtime)
        )
        checks.extend(
            self._service_checks(
                built_runtime,
                required_services,
            )
        )
        checks.append(
            self._dead_letter_check(built_runtime)
        )
        return ProductionReadinessReport(
            ready=all(
                check.passed
                for check in checks
            ),
            checks=tuple(checks),
        )

    def _module_checks(
        self,
        built_runtime,
    ) -> tuple[ProductionCheck, ...]:
        checks = []
        for module in built_runtime.runtime.modules.modules():
            state = built_runtime.runtime.modules.state(
                module.name
            )
            checks.append(
                ProductionCheck(
                    name=f"module_state:{module.name}",
                    passed=state
                    in {
                        ModuleState.STARTED,
                        ModuleState.INITIALIZED,
                    },
                    detail=state.value,
                )
            )
        return tuple(checks)

    def _health_checks(
        self,
        built_runtime,
    ) -> tuple[ProductionCheck, ...]:
        checks = []
        for report in built_runtime.health.all_reports():
            checks.append(
                ProductionCheck(
                    name=f"health:{report.name}",
                    passed=report.status.value == "healthy",
                    detail=report.status.value,
                )
            )
        return tuple(checks)

    def _service_checks(
        self,
        built_runtime,
        required_services: tuple[Any, ...],
    ) -> tuple[ProductionCheck, ...]:
        checks = []
        for service in required_services:
            try:
                built_runtime.provider.resolve(service)
                checks.append(
                    ProductionCheck(
                        name=f"service:{self._name(service)}",
                        passed=True,
                        detail="resolved",
                    )
                )
            except Exception as exc:
                checks.append(
                    ProductionCheck(
                        name=f"service:{self._name(service)}",
                        passed=False,
                        detail=str(exc),
                    )
                )
        return tuple(checks)

    def _dead_letter_check(
        self,
        built_runtime,
    ) -> ProductionCheck:
        count = len(
            built_runtime.runtime.event_bus.dead_letters()
        )
        return ProductionCheck(
            name="event_bus_dead_letters",
            passed=count == 0,
            detail=str(count),
        )

    def _name(
        self,
        service,
    ) -> str:
        return getattr(
            service,
            "__name__",
            str(service),
        )

