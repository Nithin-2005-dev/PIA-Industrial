from dataclasses import dataclass
from enum import Enum


class SignalRelationship(Enum):
    BELONGS_TO = "belongs_to"
    DERIVED_FROM = "derived_from"
    EQUIVALENT_TO = "equivalent_to"
    INFLUENCES = "influences"
    CONFLICTS_WITH = "conflicts_with"
    COMPLEMENTS = "complements"
    REQUIRES = "requires"


@dataclass(frozen=True)
class SignalOntologyNode:
    id: str
    display_name: str
    domain: str
    description: str


@dataclass(frozen=True)
class SignalOntologyEdge:
    source_id: str
    target_id: str
    relationship: SignalRelationship
    confidence: float = 1.0
    rationale: str | None = None


class SignalOntology:

    def __init__(
        self,
    ):
        self._nodes = {}
        self._edges: list[SignalOntologyEdge] = []

    @classmethod
    def default(
        cls,
    ):
        ontology = cls()

        for domain in (
            "source_control",
            "static_analysis",
            "runtime",
            "build_systems",
            "ci_cd",
            "cloud",
            "infrastructure",
            "security",
            "testing",
            "documentation",
            "databases",
            "ai_systems",
            "developer_collaboration",
            "project_management",
        ):
            ontology.add_node(
                SignalOntologyNode(
                    id=domain,
                    display_name=domain.replace(
                        "_",
                        " ",
                    ).title(),
                    domain=domain,
                    description=(
                        f"Signal domain for {domain.replace('_', ' ')}."
                    ),
                )
            )

        ontology.add_edge(
            SignalOntologyEdge(
                source_id="git.total_additions",
                target_id="source_control",
                relationship=SignalRelationship.BELONGS_TO,
            )
        )
        ontology.add_edge(
            SignalOntologyEdge(
                source_id="git.total_deletions",
                target_id="source_control",
                relationship=SignalRelationship.BELONGS_TO,
            )
        )
        ontology.add_edge(
            SignalOntologyEdge(
                source_id="static.patch",
                target_id="static_analysis",
                relationship=SignalRelationship.BELONGS_TO,
            )
        )

        return ontology

    def add_node(
        self,
        node: SignalOntologyNode,
    ):
        self._nodes[
            node.id
        ] = node

    def add_edge(
        self,
        edge: SignalOntologyEdge,
    ):
        self._edges.append(
            edge
        )

    def node(
        self,
        node_id: str,
    ) -> SignalOntologyNode | None:
        return self._nodes.get(
            node_id
        )

    def relationships(
        self,
        source_id: str,
    ) -> list[SignalOntologyEdge]:
        return [
            edge
            for edge in self._edges
            if edge.source_id == source_id
        ]

    def all_nodes(
        self,
    ) -> list[SignalOntologyNode]:
        return list(
            self._nodes.values()
        )


