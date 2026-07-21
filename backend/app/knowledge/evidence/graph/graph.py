from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.knowledge.evidence.domain import Evidence
from app.knowledge.evidence.ontology import EvidenceRelationship


@dataclass(frozen=True)
class EvidenceGraphNode:
    id: str
    type: str
    label: str


@dataclass(frozen=True)
class EvidenceGraphEdge:
    source_id: str
    target_id: str
    relationship: EvidenceRelationship
    origin_id: str | None = None


class IEvidenceGraphStore(ABC):

    @abstractmethod
    def add_evidence(self, evidence: Evidence) -> None:
        ...

    @abstractmethod
    def remove_evidence(self, evidence_id: str) -> None:
        ...

    @abstractmethod
    def add_relationship(
        self, source_id: str, target_id: str, relationship: EvidenceRelationship, origin_id: str | None = None
    ) -> None:
        ...

    @abstractmethod
    def nodes(self) -> tuple[EvidenceGraphNode, ...]:
        ...

    @abstractmethod
    def edges(self) -> tuple[EvidenceGraphEdge, ...]:
        ...

    @abstractmethod
    def neighbors(self, node_id: str) -> tuple[EvidenceGraphNode, ...]:
        ...

    @abstractmethod
    def lineage(self, evidence_id: str) -> tuple[EvidenceGraphEdge, ...]:
        ...

    @abstractmethod
    def impact_analysis(self, measurement_id: str) -> tuple[EvidenceGraphNode, ...]:
        ...


class LocalMemoryGraphStore(IEvidenceGraphStore):

    def __init__(
        self,
    ):
        self._nodes: dict[str, EvidenceGraphNode] = {}
        self._edges: list[EvidenceGraphEdge] = []

    def add_evidence(
        self,
        evidence: Evidence,
    ) -> None:
        self._nodes[evidence.evidence_id] = EvidenceGraphNode(
            id=evidence.evidence_id,
            type="evidence",
            label=evidence.name,
        )

        for measurement in evidence.supporting_measurements:
            self._nodes[measurement.id] = EvidenceGraphNode(
                id=measurement.id,
                type="measurement",
                label=measurement.name,
            )
            self._edges.append(
                EvidenceGraphEdge(
                    source_id=measurement.id,
                    target_id=evidence.evidence_id,
                    relationship=EvidenceRelationship.SUPPORTS,
                )
            )

        concept_id = f"expertise:{evidence.category}"
        self._nodes[concept_id] = EvidenceGraphNode(
            id=concept_id,
            type="expertise_concept",
            label=evidence.category,
        )
        self._edges.append(
            EvidenceGraphEdge(
                source_id=evidence.evidence_id,
                target_id=concept_id,
                relationship=EvidenceRelationship.EXPLAINS,
            )
        )

    def remove_evidence(self, evidence_id: str) -> None:
        if evidence_id in self._nodes:
            del self._nodes[evidence_id]
        
        self._edges = [
            edge for edge in self._edges
            if edge.source_id != evidence_id and edge.target_id != evidence_id and edge.origin_id != evidence_id
        ]

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship: EvidenceRelationship,
        origin_id: str | None = None,
    ) -> None:
        self._edges.append(
            EvidenceGraphEdge(
                source_id=source_id,
                target_id=target_id,
                relationship=relationship,
                origin_id=origin_id,
            )
        )

    def nodes(
        self,
    ) -> tuple[EvidenceGraphNode, ...]:
        return tuple(self._nodes.values())

    def edges(
        self,
    ) -> tuple[EvidenceGraphEdge, ...]:
        return tuple(self._edges)

    def neighbors(
        self,
        node_id: str,
    ) -> tuple[EvidenceGraphNode, ...]:
        ids = {
            edge.target_id for edge in self._edges if edge.source_id == node_id
        }.union(
            {edge.source_id for edge in self._edges if edge.target_id == node_id}
        )
        return tuple(
            self._nodes[item_id] for item_id in ids if item_id in self._nodes
        )

    def lineage(
        self,
        evidence_id: str,
    ) -> tuple[EvidenceGraphEdge, ...]:
        return tuple(
            edge
            for edge in self._edges
            if edge.target_id == evidence_id or edge.source_id == evidence_id
        )

    def impact_analysis(
        self,
        measurement_id: str,
    ) -> tuple[EvidenceGraphNode, ...]:
        impacted_ids = {
            edge.target_id for edge in self._edges if edge.source_id == measurement_id
        }
        return tuple(
            self._nodes[node_id] for node_id in impacted_ids if node_id in self._nodes
        )


class Neo4jGraphStore(IEvidenceGraphStore):

    def __init__(self):
        raise NotImplementedError(
            "Enterprise graph database required for PageRank scaling"
        )

    def add_evidence(self, evidence: Evidence) -> None:
        pass

    def remove_evidence(self, evidence_id: str) -> None:
        pass

    def add_relationship(
        self, source_id: str, target_id: str, relationship: EvidenceRelationship, origin_id: str | None = None
    ) -> None:
        pass

    def nodes(self) -> tuple[EvidenceGraphNode, ...]:
        pass

    def edges(self) -> tuple[EvidenceGraphEdge, ...]:
        pass

    def neighbors(self, node_id: str) -> tuple[EvidenceGraphNode, ...]:
        pass

    def lineage(self, evidence_id: str) -> tuple[EvidenceGraphEdge, ...]:
        pass

    def impact_analysis(self, measurement_id: str) -> tuple[EvidenceGraphNode, ...]:
        pass
