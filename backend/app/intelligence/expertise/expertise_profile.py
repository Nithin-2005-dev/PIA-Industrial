from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class ExpertiseProfile:
    """
    Repository-wide expertise profile
    for a developer.
    """

    developer_ref: EntityRef

    module_count: int

    covered_modules: list[str]

    total_expertise: float

    average_expertise: float