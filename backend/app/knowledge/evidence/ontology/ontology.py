from dataclasses import dataclass
from enum import Enum


class EvidenceRelationship(Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    STRENGTHENS = "strengthens"
    WEAKENS = "weakens"
    DEPENDS_ON = "depends_on"
    DERIVED_FROM = "derived_from"
    EXPLAINS = "explains"
    CAUSED_BY = "caused_by"
    RELATED_TO = "related_to"
    IMPACTS = "impacts"
    AUTHORED = "authored"
    INTRODUCED_BUG_IN = "introduced_bug_in"
    CAUSED_INCIDENT = "caused_incident"


@dataclass(frozen=True)
class EvidenceConcept:
    id: str
    name: str
    description: str
    parent_id: str | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidenceOntologyEdge:
    source_id: str
    target_id: str
    relationship: EvidenceRelationship
    confidence: float = 1.0
    explanation: str = ""


class EvidenceOntology:

    def __init__(
        self,
        concepts: tuple[EvidenceConcept, ...] = (),
        edges: tuple[EvidenceOntologyEdge, ...] = (),
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
    ) -> "EvidenceOntology":
        concepts = tuple(
            EvidenceConcept(
                id=concept_id,
                name=name,
                description=description,
            )
            for concept_id, name, description in (
                (
                    "architecture",
                    "Architecture",
                    "Evidence about structural design and modularity.",
                ),
                (
                    "maintainability",
                    "Maintainability",
                    "Evidence about cost and safety of future change.",
                ),
                (
                    "performance",
                    "Performance",
                    "Evidence about latency, throughput, or efficiency.",
                ),
                (
                    "reliability",
                    "Reliability",
                    "Evidence about fault tolerance and service stability.",
                ),
                (
                    "security",
                    "Security",
                    "Evidence about exposure and control effectiveness.",
                ),
                (
                    "technical_debt",
                    "Technical Debt",
                    "Evidence about accumulated remediation burden.",
                ),
                (
                    "developer_productivity",
                    "Developer Productivity",
                    "Evidence about developer flow and delivery friction.",
                ),
                (
                    "testing",
                    "Testing",
                    "Evidence about verification depth and risk coverage.",
                ),
                (
                    "infrastructure",
                    "Infrastructure",
                    "Evidence about deployment and platform foundations.",
                ),
                (
                    "cloud",
                    "Cloud",
                    "Evidence about cloud architecture and operations.",
                ),
                (
                    "runtime",
                    "Runtime",
                    "Evidence about running system behavior.",
                ),
                (
                    "ai_engineering",
                    "AI Engineering",
                    "Evidence about ML/AI delivery and governance.",
                ),
                (
                    "documentation",
                    "Documentation",
                    "Evidence about knowledge capture and discoverability.",
                ),
                (
                    "business_risk",
                    "Business Risk",
                    "Evidence about business continuity and value risk.",
                ),
                (
                    "operational_risk",
                    "Operational Risk",
                    "Evidence about incident and support exposure.",
                ),
                (
                    "compliance",
                    "Compliance",
                    "Evidence about control, policy, and audit posture.",
                ),
                (
                    "developer",
                    "Developer Intelligence",
                    "Evidence about developer behavior and impact.",
                ),
                (
                    "ownership",
                    "Ownership",
                    "Evidence about code ownership and knowledge distribution.",
                ),
            )
        )

        return cls(
            concepts=concepts,
            edges=(
                EvidenceOntologyEdge(
                    source_id="technical_debt",
                    target_id="maintainability",
                    relationship=EvidenceRelationship.IMPACTS,
                    confidence=0.9,
                ),
                EvidenceOntologyEdge(
                    source_id="testing",
                    target_id="reliability",
                    relationship=EvidenceRelationship.SUPPORTS,
                    confidence=0.8,
                ),
                EvidenceOntologyEdge(
                    source_id="security",
                    target_id="business_risk",
                    relationship=EvidenceRelationship.IMPACTS,
                    confidence=0.85,
                ),
            ),
        )

    def register_concept(
        self,
        concept: EvidenceConcept,
    ) -> None:
        self._concepts[
            concept.id
        ] = concept

    def register_edge(
        self,
        edge: EvidenceOntologyEdge,
    ) -> None:
        self._edges.append(
            edge
        )

    def get(
        self,
        concept_id: str,
    ) -> EvidenceConcept:
        return self._concepts[
            concept_id
        ]

    def has_concept(
        self,
        concept_id: str,
    ) -> bool:
        return concept_id in self._concepts

    def concepts(
        self,
    ) -> tuple[EvidenceConcept, ...]:
        return tuple(
            self._concepts.values()
        )

    def edges(
        self,
    ) -> tuple[EvidenceOntologyEdge, ...]:
        return tuple(
            self._edges
        )

    def relationships_from(
        self,
        concept_id: str,
    ) -> tuple[EvidenceOntologyEdge, ...]:
        return tuple(
            edge
            for edge in self._edges
            if edge.source_id == concept_id
        )

