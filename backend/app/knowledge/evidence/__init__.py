from importlib import import_module
import sys

_LEGACY_MODULE_ALIASES = {
    "conflicts": "app.knowledge.evidence.correlation.conflicts",
    "eql": "app.knowledge.evidence.query.eql",
    "knowledge_base": "app.knowledge.evidence.knowledge.knowledge_base",
}

for _legacy_name, _target_name in _LEGACY_MODULE_ALIASES.items():
    sys.modules[f"{__name__}.{_legacy_name}"] = import_module(
        _target_name
    )

from app.knowledge.evidence.api import EvidenceApi
from app.knowledge.evidence.correlation import EvidenceConflictEngine
from app.knowledge.evidence.correlation import EvidenceCorrelationEngine
from app.knowledge.evidence.core import EvidenceContext
from app.knowledge.evidence.core import EvidencePackage
from app.knowledge.evidence.domain import Evidence
from app.knowledge.evidence.domain import EvidenceLifecycle
from app.knowledge.evidence.domain import EvidencePriority
from app.knowledge.evidence.domain import EvidenceSeverity
from app.knowledge.evidence.graph import IEvidenceGraphStore
from app.knowledge.evidence.graph import LocalMemoryGraphStore
from app.knowledge.evidence.knowledge import EvidenceDefinition
from app.knowledge.evidence.knowledge import EvidenceKnowledgeBase
from app.knowledge.evidence.ontology import EvidenceOntology
from app.knowledge.evidence.query import EqlEngine
from app.knowledge.evidence.query import EqlParser
from app.knowledge.evidence.ranking import EvidenceRankingEngine
from app.knowledge.evidence.streaming import StreamingEvidenceEngine
from app.knowledge.evidence.synthesis import EvidenceSynthesisEngine

__all__ = [
    "EqlEngine",
    "EqlParser",
    "Evidence",
    "EvidenceApi",
    "EvidenceConflictEngine",
    "EvidenceContext",
    "EvidenceCorrelationEngine",
    "EvidenceDefinition",
    "IEvidenceGraphStore",
    "LocalMemoryGraphStore",
    "EvidenceKnowledgeBase",
    "EvidenceLifecycle",
    "EvidenceOntology",
    "EvidencePackage",
    "EvidencePriority",
    "EvidenceRankingEngine",
    "EvidenceSeverity",
    "EvidenceSynthesisEngine",
    "StreamingEvidenceEngine",
]
