from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Protocol

from app.core.common import PluginError


class PluginKind(str, Enum):
    MEASUREMENT_PROVIDER = "measurement_provider"
    EXTRACTOR = "extractor"
    SIMULATOR = "simulator"
    FORECASTING_MODEL = "forecasting_model"
    RISK_MODEL = "risk_model"
    AGENT_TOOL = "agent_tool"


class PlatformPlugin(Protocol):
    id: str
    name: str
    version: str
    kind: PluginKind
    capabilities: tuple[str, ...]

    def create(
        self,
        context,
    ) -> Any:
        ...


@dataclass(frozen=True)
class PluginDescriptor:
    id: str
    name: str
    version: str
    kind: PluginKind
    capabilities: tuple[str, ...]


class PluginRegistry:
    def __init__(
        self,
    ):
        self._plugins: dict[str, PlatformPlugin] = {}
        self._by_kind: dict[PluginKind, set[str]] = {}

    def register(
        self,
        plugin: PlatformPlugin,
    ) -> None:
        if plugin.id in self._plugins:
            raise PluginError(
                f"Plugin already registered: {plugin.id}",
                code="plugin_already_registered",
            )
        self._plugins[plugin.id] = plugin
        self._by_kind.setdefault(
            plugin.kind,
            set(),
        ).add(plugin.id)

    def list(
        self,
        kind: PluginKind | None = None,
    ) -> tuple[PluginDescriptor, ...]:
        ids = (
            self._by_kind.get(
                kind,
                set(),
            )
            if kind is not None
            else set(self._plugins)
        )
        return tuple(
            PluginDescriptor(
                id=plugin.id,
                name=plugin.name,
                version=plugin.version,
                kind=plugin.kind,
                capabilities=plugin.capabilities,
            )
            for plugin in (
                self._plugins[plugin_id]
                for plugin_id in sorted(ids)
            )
        )

    def create(
        self,
        plugin_id: str,
        context,
    ) -> Any:
        return self._plugins[plugin_id].create(context)

