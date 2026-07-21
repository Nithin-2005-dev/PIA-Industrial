from app.intelligence.measurement.scientific.accuracy_profiles import AccuracyProfileRegistry
from app.intelligence.measurement.benchmarks.benchmark import BenchmarkEngine
from app.intelligence.measurement.benchmarks.benchmark_datasets import BenchmarkDatasetRegistry
from app.intelligence.measurement.scientific.confidence_calibration import ConfidenceCalibrationModel
from app.intelligence.measurement.scientific.confidence_calibration import ConfidenceObservation
from app.intelligence.measurement.domain import Measurement
from app.knowledge.evidence.knowledge.measurement_knowledge import SoftwareMeasurementKnowledgeBase
from app.intelligence.measurement.scientific.scientific_validation import ScientificValidationEngine
from app.intelligence.measurement.scientific.scientific_validation import ScientificValidationReport
from app.intelligence.measurement.scientific.standards import StandardsCatalog


class ScientificMeasurementApi:
    """
    Read API for scientific validation, calibration and interpretation.
    """

    def __init__(
        self,
        validation_engine: ScientificValidationEngine,
        benchmark_registry: BenchmarkDatasetRegistry,
        knowledge_base: SoftwareMeasurementKnowledgeBase,
        accuracy_profiles: AccuracyProfileRegistry,
        standards_catalog: StandardsCatalog,
    ):
        self._validation_engine = validation_engine
        self._benchmark_registry = benchmark_registry
        self._knowledge_base = knowledge_base
        self._accuracy_profiles = accuracy_profiles
        self._standards_catalog = standards_catalog
        self._benchmark_engine = BenchmarkEngine()
        self._calibration = ConfidenceCalibrationModel()

    def validation_report(
        self,
        measurement: Measurement,
    ) -> ScientificValidationReport:
        return self._validation_engine.validate_measurement(
            measurement
        )

    def benchmark_lookup(
        self,
        measurement_id: str,
    ):
        return self._benchmark_registry.for_measurement(
            measurement_id
        )

    def benchmark_comparison(
        self,
        measurement: Measurement,
    ):
        datasets = self.benchmark_lookup(
            measurement.definition.id
        )

        if not datasets:
            return None

        return self._benchmark_engine.compare(
            measurement.value,
            list(datasets[0].values),
            datasets[0].scope.value,
        )

    def confidence_explanation(
        self,
        measurement: Measurement,
        observations: list[ConfidenceObservation],
    ):
        return self._calibration.calibrate(
            measurement.definition.id,
            measurement.confidence,
            observations,
        )

    def uncertainty_explanation(
        self,
        measurement: Measurement,
    ):
        return measurement.uncertainty

    def interpretation(
        self,
        measurement_id: str,
    ):
        knowledge = self._knowledge_base.get(
            measurement_id
        )

        if knowledge is None:
            return None

        return knowledge.interpretation_guide

    def standards_lookup(
        self,
        topic: str,
    ):
        return self._standards_catalog.for_topic(
            topic
        )

    def research_references(
        self,
        measurement_id: str,
    ):
        knowledge = self._knowledge_base.get(
            measurement_id
        )

        if knowledge is None:
            return ()

        return knowledge.research_references

    def accuracy_profile(
        self,
        measurement_id: str,
    ):
        return self._accuracy_profiles.get(
            measurement_id
        )


