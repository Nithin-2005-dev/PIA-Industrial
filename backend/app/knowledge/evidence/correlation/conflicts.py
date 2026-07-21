from dataclasses import dataclass

from app.knowledge.evidence.domain import Evidence
from app.knowledge.evidence.ontology import EvidenceOntology
from app.knowledge.evidence.ontology import EvidenceRelationship


@dataclass(frozen=True)
class EvidenceContradictionReport:
    source_evidence_id: str
    target_evidence_id: str
    confidence_reduction: float
    explanation: str
    recommended_follow_up_measurements: tuple[str, ...]


class EvidenceConflictEngine:

    def __init__(
        self,
        ontology: EvidenceOntology,
    ):
        self._ontology = ontology

    def detect(
        self,
        evidence: tuple[Evidence, ...],
    ) -> tuple[EvidenceContradictionReport, ...]:
        reports = []

        for source in evidence:
            for edge in self._ontology.relationships_from(
                source.category
            ):
                if edge.relationship != EvidenceRelationship.CONTRADICTS:
                    continue

                for target in evidence:
                    if (
                        source.evidence_id != target.evidence_id
                        and target.category == edge.target_id
                    ):
                        reports.append(
                            EvidenceContradictionReport(
                                source_evidence_id=source.evidence_id,
                                target_evidence_id=target.evidence_id,
                                confidence_reduction=(
                                    1.0 - edge.confidence
                                )
                                * 0.25,
                                explanation=(
                                    "Ontology marks these evidence categories "
                                    "as contradictory; review source "
                                    "measurements before expert reasoning."
                                ),
                                recommended_follow_up_measurements=(
                                    "runtime_validation",
                                    "historical_replay",
                                    "benchmark_recheck",
                                ),
                            )
                        )

        return tuple(
            reports
        )

