from dataclasses import dataclass
from enum import Enum

from app.knowledge.evidence.domain import Evidence
from app.knowledge.evidence.ontology import EvidenceOntology
from app.knowledge.evidence.ontology import EvidenceRelationship


class EvidenceCorrelationType(Enum):
    SEMANTIC = "semantic"
    STATISTICAL = "statistical"
    GRAPH = "graph"
    TEMPORAL = "temporal"
    DEPENDENCY = "dependency"
    BENCHMARK = "benchmark"
    HISTORICAL = "historical"


@dataclass(frozen=True)
class EvidenceCorrelation:
    source_evidence_id: str
    target_evidence_id: str
    correlation_type: EvidenceCorrelationType
    relationship: EvidenceRelationship
    strength: float
    explanation: str
    implies_causation: bool = False


class EvidenceCorrelationEngine:

    def __init__(
        self,
        ontology: EvidenceOntology,
    ):
        self._ontology = ontology

    def correlate(
        self,
        evidence: tuple[Evidence, ...],
    ) -> tuple[EvidenceCorrelation, ...]:
        from collections import defaultdict
        correlations = []

        category_index = defaultdict(list)
        measurement_index = defaultdict(list)

        for item in evidence:
            category_index[item.category].append(item)
            for measurement_id in item.lineage.source_measurement_ids:
                measurement_index[measurement_id].append(item)

        # 1. SEMANTIC & GRAPH (Category-based)
        for category, sources in category_index.items():
            # SEMANTIC
            if len(sources) > 1:
                for i, source in enumerate(sources):
                    for target in sources[i + 1:]:
                        correlations.append(
                            EvidenceCorrelation(
                                source_evidence_id=source.evidence_id,
                                target_evidence_id=target.evidence_id,
                                correlation_type=EvidenceCorrelationType.SEMANTIC,
                                relationship=EvidenceRelationship.RELATED_TO,
                                strength=min(source.confidence, target.confidence),
                                explanation="Evidence items share an ontology category. This is correlation, not causation."
                            )
                        )

            # GRAPH
            for edge in self._ontology.relationships_from(category):
                targets = category_index.get(edge.target_id, [])
                for source in sources:
                    for target in targets:
                        correlations.append(
                            EvidenceCorrelation(
                                source_evidence_id=source.evidence_id,
                                target_evidence_id=target.evidence_id,
                                correlation_type=EvidenceCorrelationType.GRAPH,
                                relationship=edge.relationship,
                                strength=edge.confidence,
                                explanation=edge.explanation or "Ontology graph relates these concepts."
                            )
                        )

        # 2. DEPENDENCY (Measurement-based)
        dependency_map = defaultdict(set)
        for measurement_id, items in measurement_index.items():
            if len(items) > 1:
                for i, source in enumerate(items):
                    for target in items[i + 1:]:
                        if source.evidence_id < target.evidence_id:
                            key = (source, target)
                        else:
                            key = (target, source)
                        dependency_map[key].add(measurement_id)

        for (source, target), overlap in dependency_map.items():
            source_measurements = set(source.lineage.source_measurement_ids)
            target_measurements = set(target.lineage.source_measurement_ids)
            union_len = max(1, len(source_measurements.union(target_measurements)))
            correlations.append(
                EvidenceCorrelation(
                    source_evidence_id=source.evidence_id,
                    target_evidence_id=target.evidence_id,
                    correlation_type=EvidenceCorrelationType.DEPENDENCY,
                    relationship=EvidenceRelationship.DERIVED_FROM,
                    strength=min(1.0, len(overlap) / union_len),
                    explanation="Evidence items share source measurements. Shared provenance does not imply causation."
                )
            )

        return tuple(correlations)

