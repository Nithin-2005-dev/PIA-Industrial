from importlib import import_module
import sys

_LEGACY_MODULE_ALIASES = {
    'accuracy': 'app.intelligence.measurement.core.accuracy',
    'active': 'app.intelligence.measurement.core.active',
    'audit': 'app.intelligence.measurement.core.audit',
    'composite': 'app.intelligence.measurement.core.composite',
    'confidence': 'app.intelligence.measurement.core.confidence',
    'engine': 'app.intelligence.measurement.core.engine',
    'execution': 'app.intelligence.measurement.core.execution',
    'formula': 'app.intelligence.measurement.core.formula',
    'fusion': 'app.intelligence.measurement.core.fusion',
    'ids': 'app.intelligence.measurement.core.ids',
    'interfaces': 'app.intelligence.measurement.core.interfaces',
    'normalization': 'app.intelligence.measurement.core.normalization',
    'normalization_pipeline': 'app.intelligence.measurement.core.normalization_pipeline',
    'quality': 'app.intelligence.measurement.core.quality',
    'recompute': 'app.intelligence.measurement.core.recompute',
    'store': 'app.intelligence.measurement.core.store',
    'streaming': 'app.intelligence.measurement.core.streaming',
    'validation': 'app.intelligence.measurement.core.validation',
    'catalog': 'app.intelligence.measurement.domain.catalog',
    'contracts': 'app.intelligence.measurement.domain.contracts',
    'ontology': 'app.intelligence.measurement.domain.ontology',
    'registry': 'app.intelligence.measurement.domain.registry',
    'signals': 'app.kernel.classifiers.signals',
    'signal_ontology': 'app.kernel.classifiers.signal_ontology',
    'signal_classifier': 'app.kernel.classifiers.signal_classifier',
    'mapping': 'app.kernel.classifiers.mapping',
    'signal_validation': 'app.kernel.classifiers.signal_validation',
    'scientific_api': 'app.intelligence.measurement.scientific.scientific_api',
    'scientific_catalog': 'app.intelligence.measurement.scientific.scientific_catalog',
    'scientific_validation': 'app.intelligence.measurement.scientific.scientific_validation',
    'accuracy_profiles': 'app.intelligence.measurement.scientific.accuracy_profiles',
    'confidence_calibration': 'app.intelligence.measurement.scientific.confidence_calibration',
    'test_corpus': 'app.intelligence.measurement.scientific.test_corpus',
    'standards': 'app.intelligence.measurement.scientific.standards',
    'benchmark': 'app.intelligence.measurement.benchmarks.benchmark',
    'benchmark_datasets': 'app.intelligence.measurement.benchmarks.benchmark_datasets',
    'statistical': 'app.intelligence.measurement.analytics.statistical',
    'statistical_pipeline': 'app.intelligence.measurement.analytics.statistical_pipeline',
    'graph': 'app.intelligence.measurement.analytics.graph',
    'time_series': 'app.intelligence.measurement.analytics.time_series',
    'drift': 'app.intelligence.measurement.analytics.drift',
    'outliers': 'app.intelligence.measurement.analytics.outliers',
    'compression': 'app.intelligence.measurement.analytics.compression',
    'mql': 'app.intelligence.measurement.query.mql',
    'lineage': 'app.intelligence.measurement.query.lineage',
    'lineage_query': 'app.intelligence.measurement.query.lineage_query',
    'knowledge_api': 'app.intelligence.measurement.query.knowledge_api',
    'packs': 'app.intelligence.measurement.plugins_runtime.packs',
    'plugins': 'app.intelligence.measurement.plugins_runtime.plugins',
    'ml': 'app.intelligence.measurement.plugins_runtime.ml',
    'dsl': 'app.intelligence.measurement.plugins_runtime.dsl',
}

for _legacy_name, _target_name in _LEGACY_MODULE_ALIASES.items():
    sys.modules[f'{__name__}.{_legacy_name}'] = import_module(_target_name)

from app.intelligence.measurement.core.accuracy import EnterpriseAccuracyPipeline
from app.intelligence.measurement.domain.catalog import DefaultMeasurementCatalog
from app.intelligence.measurement.domain.contracts import MeasurementContract, MeasurementLifecycle
from app.intelligence.measurement.domain import (
    Measurement,
    MeasurementContext,
    MeasurementConcept,
    MeasurementDefinition,
    MeasurementUnit,
)
from app.intelligence.measurement.core.engine import MeasurementEngine
from app.intelligence.measurement.core.execution import MeasurementExecutionPlanner
from app.kernel.classifiers.mapping import SignalToMeasurementMapper
from app.intelligence.measurement.domain.ontology import MeasurementOntology
from app.intelligence.measurement.domain.registry import MeasurementRegistry
from app.intelligence.measurement.scientific.scientific_api import ScientificMeasurementApi
from app.intelligence.measurement.scientific.scientific_catalog import EnterpriseMeasurementCatalog
from app.intelligence.measurement.scientific.scientific_validation import ScientificValidationEngine
from app.knowledge.evidence.knowledge.semantic_graph import SemanticMeasurementGraph
from app.kernel.classifiers.signal_classifier import SemanticSignalClassifier
from app.kernel.classifiers.signal_ontology import SignalOntology
from app.kernel.classifiers.signals import DefaultSignalCatalog, SignalRegistry

__all__ = [
    'DefaultMeasurementCatalog',
    'DefaultSignalCatalog',
    'EnterpriseAccuracyPipeline',
    'EnterpriseMeasurementCatalog',
    'Measurement',
    'MeasurementContract',
    'MeasurementConcept',
    'MeasurementContext',
    'MeasurementDefinition',
    'MeasurementEngine',
    'MeasurementExecutionPlanner',
    'MeasurementLifecycle',
    'MeasurementOntology',
    'MeasurementRegistry',
    'MeasurementUnit',
    'SemanticMeasurementGraph',
    'SemanticSignalClassifier',
    'SignalOntology',
    'SignalRegistry',
    'SignalToMeasurementMapper',
    'ScientificMeasurementApi',
    'ScientificValidationEngine',
]
