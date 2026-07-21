from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Generic
from typing import TypeVar


T = TypeVar("T")


def utc_now() -> datetime:
    return datetime.now(UTC)


class PlatformError(Exception):
    def __init__(
        self,
        message: str,
        code: str = "platform_error",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.details = details or {}


class ConfigurationError(PlatformError):
    pass


class DependencyResolutionError(PlatformError):
    pass


class LifecycleError(PlatformError):
    pass


class ModuleError(PlatformError):
    pass


class PipelineError(PlatformError):
    pass


class PluginError(PlatformError):
    pass


class ResultStatus(str, Enum):
    OK = "ok"
    ERROR = "error"


@dataclass(frozen=True)
class Result(Generic[T]):
    status: ResultStatus
    value: T | None = None
    error: PlatformError | None = None

    @classmethod
    def ok(
        cls,
        value: T | None = None,
    ) -> "Result[T]":
        return cls(
            status=ResultStatus.OK,
            value=value,
        )

    @classmethod
    def fail(
        cls,
        error: PlatformError,
    ) -> "Result[T]":
        return cls(
            status=ResultStatus.ERROR,
            error=error,
        )

    def unwrap(
        self,
    ) -> T:
        if self.error is not None:
            raise self.error
        return self.value  # type: ignore[return-value]


@dataclass(frozen=True)
class ValidationIssue:
    field: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    issues: tuple[ValidationIssue, ...] = ()

    @classmethod
    def passed(
        cls,
    ) -> "ValidationResult":
        return cls(
            valid=True,
        )

    @classmethod
    def failed(
        cls,
        *issues: ValidationIssue,
    ) -> "ValidationResult":
        return cls(
            valid=False,
            issues=tuple(issues),
        )


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 1
    retry_on: tuple[type[Exception], ...] = (Exception,)

    def run(
        self,
        operation,
    ):
        last_error: Exception | None = None
        for _ in range(max(1, self.attempts)):
            try:
                return operation()
            except self.retry_on as exc:
                last_error = exc
        if last_error is not None:
            raise last_error


class SimpleCache:
    def __init__(
        self,
    ):
        self._values: dict[str, Any] = {}

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._values.get(
            key,
            default,
        )

    def put(
        self,
        key: str,
        value: Any,
    ) -> None:
        self._values[key] = value

    def clear(
        self,
    ) -> None:
        self._values.clear()

