from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EventQuery:
    """
    Immutable description of an event collection request.

    It specifies WHAT events should be collected,
    not HOW they are collected.
    """


    identifier: str

    filters: Mapping[str, Any] = field(default_factory=dict)