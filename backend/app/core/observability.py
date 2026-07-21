from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any
from uuid import uuid4

from app.core.common import utc_now


@dataclass(frozen=True)
class TraceContext:
    correlation_id: str
    trace_id: str

    @classmethod
    def new(
        cls,
    ) -> "TraceContext":
        return cls(
            correlation_id=str(uuid4()),
            trace_id=str(uuid4()),
        )


@dataclass(frozen=True)
class LogRecord:
    level: str
    message: str
    timestamp: object
    correlation_id: str | None
    trace_id: str | None
    fields: dict[str, Any]


class StructuredLogger:
    def __init__(
        self,
    ):
        self._records: list[LogRecord] = []

    def log(
        self,
        level: str,
        message: str,
        context: TraceContext | None = None,
        **fields,
    ) -> None:
        self._records.append(
            LogRecord(
                level=level,
                message=message,
                timestamp=utc_now(),
                correlation_id=(
                    context.correlation_id
                    if context is not None
                    else None
                ),
                trace_id=(
                    context.trace_id
                    if context is not None
                    else None
                ),
                fields=fields,
            )
        )

    def info(
        self,
        message: str,
        context: TraceContext | None = None,
        **fields,
    ) -> None:
        self.log("INFO", message, context, **fields)

    def warning(
        self,
        message: str,
        context: TraceContext | None = None,
        **fields,
    ) -> None:
        self.log("WARNING", message, context, **fields)

    def error(
        self,
        message: str,
        context: TraceContext | None = None,
        **fields,
    ) -> None:
        self.log("ERROR", message, context, **fields)

    def debug(
        self,
        message: str,
        context: TraceContext | None = None,
        **fields,
    ) -> None:
        self.log("DEBUG", message, context, **fields)

    def records(
        self,
    ) -> tuple[LogRecord, ...]:
        return tuple(self._records)


@dataclass(frozen=True)
class PerformanceMetric:
    name: str
    duration_ms: float
    timestamp: object


class MetricsRecorder:
    def __init__(
        self,
    ):
        self._metrics: list[PerformanceMetric] = []

    def time(
        self,
        name: str,
        operation,
    ):
        started = perf_counter()
        result = operation()
        self._metrics.append(
            PerformanceMetric(
                name=name,
                duration_ms=(perf_counter() - started) * 1000,
                timestamp=utc_now(),
            )
        )
        return result

    def metrics(
        self,
    ) -> tuple[PerformanceMetric, ...]:
        return tuple(self._metrics)


@dataclass(frozen=True)
class AuditRecord:
    action: str
    actor: str
    target: str
    timestamp: object
    metadata: dict[str, Any]


class AuditLog:
    def __init__(
        self,
    ):
        self._records: list[AuditRecord] = []

    def append(
        self,
        action: str,
        actor: str,
        target: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._records.append(
            AuditRecord(
                action=action,
                actor=actor,
                target=target,
                timestamp=utc_now(),
                metadata=metadata or {},
            )
        )

    def records(
        self,
    ) -> tuple[AuditRecord, ...]:
        return tuple(self._records)

