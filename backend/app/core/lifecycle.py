from __future__ import annotations

from app.core.module import ModuleRegistry
from app.core.module import ModuleState


class LifecycleManager:
    def __init__(
        self,
        registry: ModuleRegistry,
    ):
        self._registry = registry

    def initialize(
        self,
        context,
    ) -> None:
        for name in self._registry.startup_order():
            module = self._registry.get(name)
            module.initialize(context)
            self._registry.set_state(
                name,
                ModuleState.INITIALIZED,
            )

    def start(
        self,
    ) -> None:
        for name in self._registry.startup_order():
            module = self._registry.get(name)
            module.start()
            self._registry.set_state(
                name,
                ModuleState.STARTED,
            )

    def pause(
        self,
    ) -> None:
        for name in self._registry.shutdown_order():
            self._registry.get(name).pause()
            self._registry.set_state(
                name,
                ModuleState.PAUSED,
            )

    def resume(
        self,
    ) -> None:
        for name in self._registry.startup_order():
            self._registry.get(name).resume()
            self._registry.set_state(
                name,
                ModuleState.STARTED,
            )

    def stop(
        self,
    ) -> None:
        for name in self._registry.shutdown_order():
            self._registry.get(name).stop()
            self._registry.set_state(
                name,
                ModuleState.STOPPED,
            )

    def shutdown(
        self,
    ) -> None:
        for name in self._registry.shutdown_order():
            self._registry.get(name).shutdown()
            self._registry.set_state(
                name,
                ModuleState.SHUTDOWN,
            )

