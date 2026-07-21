from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum
from typing import Any
from typing import Callable
from uuid import uuid4

from app.core.common import utc_now


class EventPriority(IntEnum):
    LOW = 10
    NORMAL = 50
    HIGH = 100


@dataclass(frozen=True)
class PlatformEvent:
    type: str
    payload: Any
    version: str = "1.0"
    priority: EventPriority = EventPriority.NORMAL
    event_id: str = ""
    correlation_id: str | None = None
    trace_id: str | None = None
    occurred_at: object | None = None

    def normalized(
        self,
    ) -> "PlatformEvent":
        return PlatformEvent(
            type=self.type,
            payload=self.payload,
            version=self.version,
            priority=self.priority,
            event_id=self.event_id or str(uuid4()),
            correlation_id=self.correlation_id,
            trace_id=self.trace_id,
            occurred_at=self.occurred_at or utc_now(),
        )


@dataclass(frozen=True)
class DeadLetter:
    event: PlatformEvent
    error: str


class EventBus:
    def __init__(
        self,
    ):
        self._subscribers: dict[str, list[Callable[[PlatformEvent], None]]] = (
            defaultdict(list)
        )
        self._history: list[PlatformEvent] = []
        self._dead_letters: list[DeadLetter] = []

    def subscribe(
        self,
        event_type: str,
        handler: Callable[[PlatformEvent], None],
    ) -> None:
        self._subscribers[event_type].append(handler)

    def publish(
        self,
        event: PlatformEvent,
    ) -> PlatformEvent:
        normalized = event.normalized()
        self._history.append(normalized)
        handlers = [
            *self._subscribers.get("*", []),
            *self._subscribers.get(normalized.type, []),
        ]
        for handler in handlers:
            try:
                handler(normalized)
            except Exception as exc:
                self._dead_letters.append(
                    DeadLetter(
                        event=normalized,
                        error=str(exc),
                    )
                )
        return normalized

    def publish_many(
        self,
        events: list[PlatformEvent],
    ) -> tuple[PlatformEvent, ...]:
        ordered = sorted(
            events,
            key=lambda event: int(event.priority),
            reverse=True,
        )
        return tuple(
            self.publish(event)
            for event in ordered
        )

    def replay(
        self,
        event_type: str | None = None,
    ) -> tuple[PlatformEvent, ...]:
        return tuple(
            event
            for event in self._history
            if event_type is None or event.type == event_type
        )

    def dead_letters(
        self,
    ) -> tuple[DeadLetter, ...]:
        return tuple(self._dead_letters)

