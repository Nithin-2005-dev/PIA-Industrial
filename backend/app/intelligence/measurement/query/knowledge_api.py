from app.intelligence.measurement.benchmarks.benchmark_datasets import BenchmarkDataset
from app.intelligence.measurement.benchmarks.benchmark_datasets import BenchmarkDatasetRegistry
from app.kernel.classifiers.mapping import MappingResolution
from app.kernel.classifiers.mapping import SignalMeasurementMapping
from app.kernel.classifiers.mapping import SignalMeasurementMappingRegistry
from app.knowledge.evidence.knowledge.measurement_knowledge import MeasurementDefinitionKnowledge
from app.knowledge.evidence.knowledge.measurement_knowledge import SoftwareMeasurementKnowledgeBase
from app.intelligence.measurement.domain.registry import MeasurementRegistry
from app.kernel.classifiers.signal_ontology import SignalOntology
from app.kernel.classifiers.signal_ontology import SignalOntologyEdge
from app.kernel.classifiers.signals import SignalDefinition
from app.kernel.classifiers.signals import SignalRegistry
from app.intelligence.measurement.scientific.standards import StandardReference
from app.intelligence.measurement.scientific.standards import StandardsCatalog


class MeasurementKnowledgeApi:
    """
    Abstraction-first read API for M33 knowledge objects.
    """

    def __init__(
        self,
        signal_registry: SignalRegistry,
        measurement_registry: MeasurementRegistry,
        mapping_registry: SignalMeasurementMappingRegistry,
        signal_ontology: SignalOntology,
        measurement_knowledge: SoftwareMeasurementKnowledgeBase,
        benchmark_registry: BenchmarkDatasetRegistry,
        standards_catalog: StandardsCatalog,
    ):
        self._signal_registry = signal_registry
        self._measurement_registry = measurement_registry
        self._mapping_registry = mapping_registry
        self._signal_ontology = signal_ontology
        self._measurement_knowledge = measurement_knowledge
        self._benchmark_registry = benchmark_registry
        self._standards_catalog = standards_catalog

    def signal_definition(
        self,
        signal_id: str,
    ) -> SignalDefinition:
        return self._signal_registry.get(
            signal_id
        )

    def measurement_definition(
        self,
        measurement_id: str,
    ):
        return self._measurement_registry.get(
            measurement_id
        )

    def mappings_for_signal(
        self,
        signal_id: str,
    ) -> list[SignalMeasurementMapping]:
        return self._mapping_registry.for_signal(
            signal_id
        )

    def explain_mapping(
        self,
        mapping: SignalMeasurementMapping,
    ) -> dict:
        return {
            "id": mapping.id,
            "version": mapping.version,
            "signals": mapping.signal_ids,
            "concept": mapping.concept_id,
            "measurements": mapping.measurement_definition_ids,
            "evaluator": mapping.evaluator,
            "cardinality": mapping.cardinality.value,
            "confidence": mapping.confidence,
            "explanation": mapping.explanation,
            "trace": mapping.trace,
        }

    def ontology_relationships(
        self,
        signal_id: str,
    ) -> list[SignalOntologyEdge]:
        return self._signal_ontology.relationships(
            signal_id
        )

    def measurement_knowledge(
        self,
        measurement_id: str,
    ) -> MeasurementDefinitionKnowledge | None:
        return self._measurement_knowledge.get(
            measurement_id
        )

    def benchmark_metadata(
        self,
        measurement_id: str,
    ) -> list[BenchmarkDataset]:
        return self._benchmark_registry.for_measurement(
            measurement_id
        )

    def standards_references(
        self,
    ) -> list[StandardReference]:
        return self._standards_catalog.all()


