from dataclasses import dataclass

from .entity_type import EntityType


@dataclass(frozen=True)
class EntityRef:
    """
    Immutable lightweight reference to a domain entity.

    This is not the entity itself, only a pointer.
    """

    id: str

    type: EntityType