from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Callable

from app.core.common import ConfigurationError


@dataclass(frozen=True)
class FeatureFlag:
    name: str
    enabled: bool


class Configuration:
    def __init__(
        self,
        values: dict[str, Any] | None = None,
        profile: str = "default",
    ):
        self._values = values or {}
        self.profile = profile

    def get(
        self,
        path: str,
        default: Any = None,
    ) -> Any:
        current: Any = self._values
        for part in path.split("."):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def require(
        self,
        path: str,
    ) -> Any:
        value = self.get(path)
        if value is None:
            raise ConfigurationError(
                f"Missing configuration value: {path}",
                code="missing_configuration",
            )
        return value

    def with_overrides(
        self,
        overrides: dict[str, Any],
    ) -> "Configuration":
        merged = self._merge(
            dict(self._values),
            overrides,
        )
        return Configuration(
            merged,
            profile=self.profile,
        )

    def feature_enabled(
        self,
        name: str,
    ) -> bool:
        return bool(
            self.get(
                f"features.{name}",
                False,
            )
        )

    def validate(
        self,
        required_paths: tuple[str, ...],
    ) -> None:
        for path in required_paths:
            self.require(path)

    def _merge(
        self,
        base: dict[str, Any],
        overrides: dict[str, Any],
    ) -> dict[str, Any]:
        for key, value in overrides.items():
            if isinstance(value, dict) and isinstance(
                base.get(key),
                dict,
            ):
                base[key] = self._merge(
                    base[key],
                    value,
                )
            else:
                base[key] = value
        return base


class ConfigurationProvider:
    def __init__(
        self,
        configuration: Configuration,
    ):
        self._configuration = configuration
        self._subscribers: list[Callable[[Configuration], None]] = []

    def current(
        self,
    ) -> Configuration:
        return self._configuration

    def override(
        self,
        values: dict[str, Any],
    ) -> Configuration:
        self._configuration = self._configuration.with_overrides(values)
        for subscriber in self._subscribers:
            subscriber(self._configuration)
        return self._configuration

    def subscribe(
        self,
        callback: Callable[[Configuration], None],
    ) -> None:
        self._subscribers.append(callback)

