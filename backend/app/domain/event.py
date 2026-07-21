from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from .entity_ref import EntityRef
from .event_type import EventType


@dataclass(frozen=True)
class Event:
    """
    Immutable fact that occurred in the external world.

    Events are append-only and form the source of truth
    for the entire intelligence engine.
    """

    id: UUID

    type: EventType

    actor_ref: EntityRef

    target_refs: tuple[EntityRef, ...]

    occurred_at: datetime

    payload: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)