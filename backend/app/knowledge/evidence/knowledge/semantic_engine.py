from __future__ import annotations

from app.knowledge.evidence.core import EvidenceContext
from app.knowledge.evidence.core import EvidencePackage
from app.knowledge.evidence.knowledge import EvidenceKnowledgeBase
from app.knowledge.evidence.knowledge.semantic_definitions import m41_semantic_evidence_definitions
from app.knowledge.evidence.synthesis.engine import EvidenceSynthesisEngine
from app.intelligence.measurement.domain import Measurement


class SemanticEvidenceEngine:
    def __init__(
        self,
        synthesis_engine: EvidenceSynthesisEngine | None = None,
    ):
        self._synthesis = synthesis_engine or EvidenceSynthesisEngine(
            knowledge_base=EvidenceKnowledgeBase(
                m41_semantic_evidence_definitions()
            )
        )

    def synthesize(
        self,
        measurements: list[Measurement],
        context: EvidenceContext | None = None,
    ) -> EvidencePackage:
        return self._synthesis.synthesize(
            measurements,
            context,
        )

