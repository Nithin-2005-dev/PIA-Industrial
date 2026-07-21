from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from .entity_ref import EntityRef
from .predicate_type import PredicateType


@dataclass(frozen=True)
class Evidence:
    """
    Immutable interpretation extracted from an Event.

    One Event can generate multiple Evidence objects.
    """

    id: UUID

    source_event_id: UUID

    subject_ref: EntityRef

    predicate: PredicateType

    object_ref: EntityRef

    confidence: float

    metadata: dict[str, Any] = field(default_factory=dict)