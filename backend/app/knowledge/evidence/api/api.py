from app.knowledge.evidence.core import EvidenceContext
from app.knowledge.evidence.core import EvidencePackage
from app.knowledge.evidence.domain import Evidence
from app.knowledge.evidence.graph import IEvidenceGraphStore
from app.knowledge.evidence.graph import LocalMemoryGraphStore
from app.knowledge.evidence.query import EqlEngine
from app.knowledge.evidence.query import EqlParser
from app.knowledge.evidence.ranking import EvidenceRankingEngine
from app.knowledge.evidence.synthesis import EvidenceSynthesisEngine
from app.intelligence.measurement.domain import Measurement


class EvidenceApi:

    def __init__(
        self,
        synthesis_engine: EvidenceSynthesisEngine | None = None,
        ranking_engine: EvidenceRankingEngine | None = None,
    ):
        self._synthesis_engine = (
            synthesis_engine
            or EvidenceSynthesisEngine()
        )
        self._ranking_engine = (
            ranking_engine
            or EvidenceRankingEngine()
        )
        self._packages: dict[str, EvidencePackage] = {}

    def generate(
        self,
        measurements: list[Measurement],
        context: EvidenceContext,
    ) -> EvidencePackage:
        package = self._synthesis_engine.synthesize(
            measurements,
            context,
        )
        self._packages[
            self._key(
                context.tenant_id
            )
        ] = package
        return package

    def lookup(
        self,
        evidence_id: str,
        tenant_id: str | None = None,
    ) -> Evidence:
        for evidence in self._package(
            tenant_id
        ).evidence:
            if evidence.evidence_id == evidence_id:
                return evidence
        raise KeyError(
            evidence_id
        )

    def search(
        self,
        eql: str,
        tenant_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, object]:
        query = EqlParser().parse(
            eql,
            tenant_id or "global"
        )
        results = EqlEngine().query(
            self._package(
                tenant_id
            ).evidence,
            query,
        )
        return {
            "total": len(results),
            "data": results[offset : offset + limit]
        }

    def explanation(
        self,
        evidence_id: str,
        tenant_id: str | None = None,
    ) -> dict[str, object]:
        evidence = self.lookup(
            evidence_id,
            tenant_id,
        )
        return {
            "id": evidence.evidence_id,
            "name": evidence.name,
            "confidence": evidence.confidence,
            "confidence_factors": (
                evidence.traceability.confidence_factors
            ),
            "explanation": evidence.traceability.explanation,
            "supporting_measurements": [
                measurement.definition_id
                for measurement in evidence.supporting_measurements
            ],
            "assumptions": evidence.assumptions,
            "limitations": evidence.limitations,
            "validation": [
                result.status.value
                for result in evidence.validation_results
            ],
        }

    def lineage(
        self,
        evidence_id: str,
        tenant_id: str | None = None,
    ) -> tuple[str, ...]:
        evidence = self.lookup(
            evidence_id,
            tenant_id,
        )
        return evidence.lineage.source_measurement_ids

    def graph(
        self,
        tenant_id: str | None = None,
    ) -> IEvidenceGraphStore:
        from app.knowledge.evidence.graph.builder import EvidenceGraphBuilder
        builder = EvidenceGraphBuilder(LocalMemoryGraphStore())
        return builder.build(self._package(tenant_id))

    def compare(
        self,
        left_id: str,
        right_id: str,
        tenant_id: str | None = None,
    ) -> dict[str, object]:
        left = self.lookup(
            left_id,
            tenant_id,
        )
        right = self.lookup(
            right_id,
            tenant_id,
        )
        return {
            "confidence_delta": left.confidence - right.confidence,
            "severity_delta": (
                left.severity.rank()
                - right.severity.rank()
            ),
            "shared_measurements": tuple(
                set(
                    left.lineage.source_measurement_ids
                ).intersection(
                    right.lineage.source_measurement_ids
                )
            ),
        }

    def export(
        self,
        tenant_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, object]:
        ranked = self._ranking_engine.rank(
            self._package(
                tenant_id
            ).evidence
        )
        return {
            "total": len(ranked),
            "data": tuple(
                {
                    "id": evidence.evidence_id,
                    "name": evidence.name,
                    "category": evidence.category,
                    "confidence": evidence.confidence,
                    "severity": evidence.severity.value,
                    "priority": evidence.priority.value,
                    "measurements": (
                        evidence.lineage.source_measurement_ids
                    ),
                }
                for evidence in ranked[offset : offset + limit]
            )
        }

    def _package(
        self,
        tenant_id: str | None,
    ) -> EvidencePackage:
        return self._packages[
            self._key(
                tenant_id
            )
        ]

    def _key(
        self,
        tenant_id: str | None,
    ) -> str:
        return tenant_id or "global"

