from importlib import import_module

_EXPORTS = {
    "ClassificationSource": "app.kernel.classifiers.signal_classifier",
    "DefaultSignalCatalog": "app.kernel.classifiers.signals",
    "MappingCardinality": "app.kernel.classifiers.mapping",
    "MeasurementKnowledgeApi": "app.intelligence.measurement.query.knowledge_api",
    "SemanticMappingValidator": "app.kernel.classifiers.signal_validation",
    "SemanticSignalClassifier": "app.kernel.classifiers.signal_classifier",
    "SignalClassification": "app.kernel.classifiers.signal_classifier",
    "SignalDefinition": "app.kernel.classifiers.signals",
    "SignalDefinitionValidator": "app.kernel.classifiers.signal_validation",
    "SignalMeasurementMapping": "app.kernel.classifiers.mapping",
    "SignalMeasurementMappingRegistry": "app.kernel.classifiers.mapping",
    "SignalOntology": "app.kernel.classifiers.signal_ontology",
    "SignalOntologyEdge": "app.kernel.classifiers.signal_ontology",
    "SignalOntologyNode": "app.kernel.classifiers.signal_ontology",
    "SignalRegistry": "app.kernel.classifiers.signals",
    "SignalRelationship": "app.kernel.classifiers.signal_ontology",
    "SignalToMeasurementMapper": "app.kernel.classifiers.mapping",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

