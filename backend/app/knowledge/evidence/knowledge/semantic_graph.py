from dataclasses import dataclass
from enum import Enum


class ConceptRelationship(Enum):
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    OPPOSES = "opposes"
    DERIVED_FROM = "derived_from"
    CAUSES = "causes"
    CORRELATES_WITH = "correlates_with"


@dataclass(frozen=True)
class SemanticMeasurementEdge:
    source_concept_id: str
    target_concept_id: str
    relationship: ConceptRelationship
    confidence: float = 1.0
    rationale: str | None = None


class SemanticMeasurementGraph:

    def __init__(
        self,
    ):
        self._edges: list[SemanticMeasurementEdge] = []

    def add(
        self,
        edge: SemanticMeasurementEdge,
    ):
        self._edges.append(
            edge
        )

    def neighbors(
        self,
        concept_id: str,
        relationship: ConceptRelationship | None = None,
    ) -> list[SemanticMeasurementEdge]:
        return [
            edge
            for edge in self._edges
            if edge.source_concept_id == concept_id
            and (
                relationship is None
                or edge.relationship == relationship
            )
        ]

    def path(
        self,
        source_concept_id: str,
        target_concept_id: str,
    ) -> list[SemanticMeasurementEdge]:
        frontier = [
            (
                source_concept_id,
                [],
            )
        ]
        visited = set()

        while frontier:
            concept_id, path = frontier.pop(0)

            if concept_id in visited:
                continue

            visited.add(
                concept_id
            )

            for edge in self.neighbors(
                concept_id
            ):
                next_path = [
                    *path,
                    edge,
                ]

                if edge.target_concept_id == target_concept_id:
                    return next_path

                frontier.append(
                    (
                        edge.target_concept_id,
                        next_path,
                    )
                )

        return []


