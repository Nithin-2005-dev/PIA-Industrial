from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GraphNode:
    """
    Generic graph node.
    """

    id: str

    type: str

    attributes: dict[str, Any] | None = None
