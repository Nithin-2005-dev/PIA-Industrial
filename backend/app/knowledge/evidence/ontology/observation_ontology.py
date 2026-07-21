from dataclasses import dataclass
from enum import Enum

from app.ingestion.observation.domain import ObservationCategory


class ObservationRelationship(Enum):
    PRODUCED_BY = "produced_by"
    BELONGS_TO = "belongs_to"
    REFERENCES = "references"
    AFFECTS = "affects"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    GENERATES = "generates"
    RELATED_TO = "related_to"


@dataclass(frozen=True)
class ObservationConcept:
    id: str
    category: ObservationCategory
    name: str
    description: str


@dataclass(frozen=True)
class ObservationOntologyEdge:
    source_id: str
    target_id: str
    relationship: ObservationRelationship


class ObservationOntology:

    def __init__(
        self,
        concepts: tuple[ObservationConcept, ...] = (),
        edges: tuple[ObservationOntologyEdge, ...] = (),
    ):
        self._concepts = {
            concept.id: concept
            for concept in concepts
        }
        self._edges = list(
            edges
        )

    @classmethod
    def default(
        cls,
    ) -> "ObservationOntology":
        concepts = tuple(
            ObservationConcept(
                id=category.value,
                category=category,
                name=category.value.replace(
                    "_",
                    " ",
                ).title(),
                description=(
                    "Vendor-independent observation category for "
                    f"{category.value} facts."
                ),
            )
            for category in ObservationCategory
        )
        return cls(
            concepts=concepts,
            edges=(
                ObservationOntologyEdge(
                    source_id="code_review",
                    target_id="source_control",
                    relationship=ObservationRelationship.REFERENCES,
                ),
                ObservationOntologyEdge(
                    source_id="ci_cd",
                    target_id="source_control",
                    relationship=ObservationRelationship.FOLLOWS,
                ),
                ObservationOntologyEdge(
                    source_id="deployment",
                    target_id="ci_cd",
                    relationship=ObservationRelationship.FOLLOWS,
                ),
            ),
        )

    def register_concept(
        self,
        concept: ObservationConcept,
    ) -> None:
        self._concepts[
            concept.id
        ] = concept

    def register_edge(
        self,
        edge: ObservationOntologyEdge,
    ) -> None:
        self._edges.append(
            edge
        )

    def has_category(
        self,
        category: ObservationCategory,
    ) -> bool:
        return category.value in self._concepts

    def edges(
        self,
    ) -> tuple[ObservationOntologyEdge, ...]:
        return tuple(
            self._edges
        )

