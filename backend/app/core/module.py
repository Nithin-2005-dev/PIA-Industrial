from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from app.core.common import ModuleError
from app.core.di import ServiceCollection


class ModuleState(str, Enum):
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    STARTED = "started"
    PAUSED = "paused"
    STOPPED = "stopped"
    SHUTDOWN = "shutdown"


class PlatformModule(Protocol):
    name: str
    version: str
    dependencies: tuple[str, ...]
    capabilities: tuple[str, ...]

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        ...

    def initialize(
        self,
        context,
    ) -> None:
        ...

    def start(
        self,
    ) -> None:
        ...

    def pause(
        self,
    ) -> None:
        ...

    def resume(
        self,
    ) -> None:
        ...

    def stop(
        self,
    ) -> None:
        ...

    def shutdown(
        self,
    ) -> None:
        ...


class BaseModule:
    name = "module"
    version = "1.0"
    dependencies: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        return None

    def initialize(
        self,
        context,
    ) -> None:
        return None

    def start(
        self,
    ) -> None:
        return None

    def pause(
        self,
    ) -> None:
        return None

    def resume(
        self,
    ) -> None:
        return None

    def stop(
        self,
    ) -> None:
        return None

    def shutdown(
        self,
    ) -> None:
        return None


@dataclass(frozen=True)
class ModuleDescriptor:
    name: str
    version: str
    dependencies: tuple[str, ...]
    capabilities: tuple[str, ...]


class ModuleRegistry:
    def __init__(
        self,
    ):
        self._modules: dict[str, PlatformModule] = {}
        self._states: dict[str, ModuleState] = {}
        self._capabilities: dict[str, set[str]] = {}

    def register(
        self,
        module: PlatformModule,
    ) -> None:
        if module.name in self._modules:
            raise ModuleError(
                f"Module already registered: {module.name}",
                code="module_already_registered",
            )
        self._modules[module.name] = module
        self._states[module.name] = ModuleState.REGISTERED
        for capability in module.capabilities:
            self._capabilities.setdefault(
                capability,
                set(),
            ).add(module.name)

    def discover(
        self,
    ) -> tuple[ModuleDescriptor, ...]:
        return tuple(
            ModuleDescriptor(
                name=module.name,
                version=module.version,
                dependencies=module.dependencies,
                capabilities=module.capabilities,
            )
            for module in self._modules.values()
        )

    def modules(
        self,
    ) -> tuple[PlatformModule, ...]:
        return tuple(self._modules.values())

    def has(
        self,
        name: str,
    ) -> bool:
        return name in self._modules

    def get(
        self,
        name: str,
    ) -> PlatformModule:
        return self._modules[name]

    def state(
        self,
        name: str,
    ) -> ModuleState:
        return self._states[name]

    def set_state(
        self,
        name: str,
        state: ModuleState,
    ) -> None:
        self._states[name] = state

    def providers_for(
        self,
        capability: str,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                self._capabilities.get(
                    capability,
                    set(),
                )
            )
        )

    def startup_order(
        self,
    ) -> tuple[str, ...]:
        temporary: set[str] = set()
        permanent: set[str] = set()
        order: list[str] = []

        def visit(name: str) -> None:
            if name in permanent:
                return
            if name in temporary:
                raise ModuleError(
                    f"Cyclic module dependency: {name}",
                    code="cyclic_module_dependency",
                )
            if name not in self._modules:
                raise ModuleError(
                    f"Missing module dependency: {name}",
                    code="missing_module_dependency",
                )
            temporary.add(name)
            for dependency in self._modules[name].dependencies:
                visit(dependency)
            temporary.remove(name)
            permanent.add(name)
            order.append(name)

        for name in self._modules:
            visit(name)

        return tuple(order)

    def shutdown_order(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            reversed(
                self.startup_order()
            )
        )
