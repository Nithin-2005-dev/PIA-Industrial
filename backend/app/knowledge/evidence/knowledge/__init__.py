from importlib import import_module

_EXPORTS = {
    "ConceptRelationship": "app.knowledge.evidence.knowledge.semantic_graph",
    "DefaultDomainPacks": "app.knowledge.evidence.knowledge.domain_packs",
    "DefaultSoftwareMeasurementKnowledge": "app.knowledge.evidence.knowledge.measurement_knowledge",
    "MeasurementDefinitionKnowledge": "app.knowledge.evidence.knowledge.measurement_knowledge",
    "EvidenceDefinition": "app.knowledge.evidence.knowledge.definitions",
    "EvidenceRule": "app.knowledge.evidence.knowledge.definitions",
    "EvidenceRuleOperator": "app.knowledge.evidence.knowledge.definitions",
    "EvidenceKnowledgeBase": "app.knowledge.evidence.knowledge.knowledge_base",
    "MeasurementKnowledgeBase": "app.knowledge.evidence.knowledge.knowledge_base",
    "MeasurementKnowledgeEntry": "app.knowledge.evidence.knowledge.knowledge_base",
    "SemanticMeasurementEdge": "app.knowledge.evidence.knowledge.semantic_graph",
    "SemanticMeasurementGraph": "app.knowledge.evidence.knowledge.semantic_graph",
    "SoftwareMeasurementKnowledgeBase": "app.knowledge.evidence.knowledge.measurement_knowledge",
    "StandardReference": "app.intelligence.measurement.scientific.standards",
    "StandardsCatalog": "app.intelligence.measurement.scientific.standards",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

