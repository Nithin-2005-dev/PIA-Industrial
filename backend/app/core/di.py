from __future__ import annotations

import inspect
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Callable

from app.core.common import DependencyResolutionError


class ServiceScope(str, Enum):
    SINGLETON = "singleton"
    SCOPED = "scoped"
    TRANSIENT = "transient"


@dataclass(frozen=True)
class ServiceDescriptor:
    key: Any
    provider: Callable[["ServiceProvider"], Any] | type
    scope: ServiceScope = ServiceScope.SINGLETON
    lazy: bool = True


class ServiceCollection:
    def __init__(
        self,
    ):
        self._descriptors: dict[Any, ServiceDescriptor] = {}

    def add(
        self,
        key: Any,
        provider: Callable[["ServiceProvider"], Any] | type | None = None,
        scope: ServiceScope = ServiceScope.SINGLETON,
        lazy: bool = True,
    ) -> "ServiceCollection":
        self._descriptors[key] = ServiceDescriptor(
            key=key,
            provider=provider or key,
            scope=scope,
            lazy=lazy,
        )
        return self

    def add_instance(
        self,
        key: Any,
        instance: Any,
    ) -> "ServiceCollection":
        self._descriptors[key] = ServiceDescriptor(
            key=key,
            provider=lambda _: instance,
            scope=ServiceScope.SINGLETON,
            lazy=False,
        )
        return self

    def build_provider(
        self,
    ) -> "ServiceProvider":
        return ServiceProvider(
            self._descriptors,
        )


class ServiceProvider:
    def __init__(
        self,
        descriptors: dict[Any, ServiceDescriptor],
        parent: "ServiceProvider | None" = None,
    ):
        self._descriptors = dict(descriptors)
        self._parent = parent
        self._singletons: dict[Any, Any] = (
            parent._singletons
            if parent is not None
            else {}
        )
        self._scoped: dict[Any, Any] = {}

    def create_scope(
        self,
    ) -> "ServiceProvider":
        return ServiceProvider(
            self._descriptors,
            parent=self,
        )

    def resolve(
        self,
        key: Any,
    ) -> Any:
        descriptor = self._descriptors.get(key)
        if descriptor is None:
            raise DependencyResolutionError(
                f"Service is not registered: {key}",
                code="service_not_registered",
            )

        if descriptor.scope == ServiceScope.SINGLETON:
            if key not in self._singletons:
                self._singletons[key] = self._create(descriptor)
            return self._singletons[key]

        if descriptor.scope == ServiceScope.SCOPED:
            if key not in self._scoped:
                self._scoped[key] = self._create(descriptor)
            return self._scoped[key]

        return self._create(descriptor)

    def _create(
        self,
        descriptor: ServiceDescriptor,
    ) -> Any:
        provider = descriptor.provider
        if inspect.isclass(provider):
            return self._construct(provider)
        return provider(self)

    def _construct(
        self,
        cls: type,
    ) -> Any:
        signature = inspect.signature(cls.__init__)
        kwargs = {}
        for name, parameter in signature.parameters.items():
            if name == "self":
                continue
            if parameter.default is not inspect.Parameter.empty:
                continue
            annotation = parameter.annotation
            if annotation is inspect.Parameter.empty:
                raise DependencyResolutionError(
                    (
                        "Constructor injection requires type annotations "
                        f"for {cls.__name__}.{name}"
                    ),
                    code="missing_constructor_annotation",
                )
            kwargs[name] = self.resolve(annotation)
        return cls(**kwargs)

