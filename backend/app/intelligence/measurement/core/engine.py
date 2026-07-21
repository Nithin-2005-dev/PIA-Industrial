from dataclasses import replace
from datetime import UTC, datetime

from app.intelligence.measurement.core.confidence import DefaultConfidenceEstimator
from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementContext
from app.intelligence.measurement.domain import ValidationStatus
from app.intelligence.measurement.domain.registry import MeasurementRegistry
from app.intelligence.measurement.core.interfaces import ConfidenceEstimator
from app.intelligence.measurement.core.interfaces import MeasurementEvaluator
from app.intelligence.measurement.core.interfaces import MeasurementNormalizer
from app.intelligence.measurement.core.interfaces import MeasurementValidator
from app.intelligence.measurement.core.interfaces import QualityScorer
from app.intelligence.measurement.core.normalization import BoundedScoreNormalizer
from app.intelligence.measurement.core.normalization import IdentityNormalizer
from app.intelligence.measurement.core.normalization import UnitConversionNormalizer
from app.intelligence.measurement.core.normalization_pipeline import NormalizationPipeline
from app.intelligence.measurement.core.quality import DefaultQualityScorer
from app.intelligence.measurement.core.validation import FiniteValueValidator
from app.intelligence.measurement.core.validation import RangeValidator
from app.intelligence.measurement.core.validation import UnitValidator
from app.intelligence.measurement.core.validation import merge_validation_results
from app.ingestion.observation.domain import Observation
from app.ingestion.observation.integration.event_compat import event_to_observation

import logging
logger = logging.getLogger(__name__)

class MeasurementEngine:
    """
    Deterministic measurement pipeline.

    The engine consumes immutable canonical observations and
    produces immutable, normalized, validated measurements.
    """

    def __init__(
        self,
        registry: MeasurementRegistry,
        normalizers: list[MeasurementNormalizer],
        validators: list[MeasurementValidator],
        confidence_estimator: ConfidenceEstimator,
        quality_scorer: QualityScorer,
        normalization_pipeline: NormalizationPipeline | None = None,
    ):
        from app.intelligence.measurement.core.fusion import MultiSourceFusionEngine

        self._registry = registry
        self._normalizers = normalizers
        self._validators = validators
        self._confidence_estimator = confidence_estimator
        self._quality_scorer = quality_scorer
        self._normalization_pipeline = (
            normalization_pipeline
            or NormalizationPipeline.default()
        )
        self._fusion_engine = MultiSourceFusionEngine()

    @classmethod
    def default(
        cls,
    ):
        from app.intelligence.measurement.evaluators.complexity import ChangeComplexityEvaluator
        from app.intelligence.measurement.evaluators.impact import ChangeImpactEvaluator
        from app.intelligence.measurement.evaluators.developer_activity import DeveloperActivityEvaluator
        from app.intelligence.measurement.evaluators.file_activity import FileActivityEvaluator
        from app.intelligence.measurement.evaluators.file_ownership import FileOwnershipEvaluator
        from app.intelligence.measurement.evaluators.subsystem_activity import SubsystemActivityEvaluator
        
        registry = MeasurementRegistry()
        registry.register_evaluator(ChangeComplexityEvaluator())
        registry.register_evaluator(ChangeImpactEvaluator())
        registry.register_evaluator(DeveloperActivityEvaluator())
        registry.register_evaluator(FileActivityEvaluator())
        registry.register_evaluator(SubsystemActivityEvaluator())
        registry.register_evaluator(FileOwnershipEvaluator())
        
        return cls(
            registry=registry,
            normalizers=[
                UnitConversionNormalizer(),
                BoundedScoreNormalizer(),
                IdentityNormalizer(),
            ],
            validators=[
                FiniteValueValidator(),
                UnitValidator(),
                RangeValidator(),
            ],
            confidence_estimator=DefaultConfidenceEstimator(),
            quality_scorer=DefaultQualityScorer(),
            normalization_pipeline=NormalizationPipeline.default(),
        )

    def measure_observation(
        self,
        observation: Observation,
        context: MeasurementContext | None = None,
    ) -> list[Measurement]:
        if context is None:
            context = MeasurementContext(
                timestamp=datetime.now(
                    UTC,
                )
            )

        finalized_measurements = []

        active_evaluators = self._registry.get_active_evaluators()
        if not active_evaluators:
            logger.warning("MeasurementEngine processed observation but no evaluators are registered.")
            return []

        for evaluator in active_evaluators:
            try:
                for measurement in evaluator.evaluate(
                    observation,
                    context,
                ):
                    # Inject logic version into measurement here
                    measurement = replace(measurement, version=evaluator.logic_version)
                    
                    finalized_measurements.append(
                        self._finalize(
                            measurement,
                            context,
                        )
                    )
            except Exception as e:
                # Isolate failures so one broken evaluator doesn't crash the whole pipeline
                logger.error(f"Evaluator {evaluator.metric_name} failed: {str(e)}")

        if not finalized_measurements:
            return []

        # Structural Grouping (NOT Temporal)
        # Group by the unique collision key: What metric is being applied to whom?
        from collections import defaultdict
        grouped_measurements = defaultdict(list)
        for m in finalized_measurements:
            collision_key = f"{m.definition.id}_{m.provenance.target_entity}"
            grouped_measurements[collision_key].append(m)
            
        # Resolve Conflicts using the Fusion Engine
        fused_measurements = []
        for collision_key, measurement_group in grouped_measurements.items():
            if len(measurement_group) == 1:
                fused_measurements.append(measurement_group[0])
            else:
                fused_result = self._fusion_engine.fuse(measurement_group)
                fused_measurements.append(fused_result)

        return fused_measurements

    def measure_observations(
        self,
        observations: list[Observation],
        context: MeasurementContext | None = None,
    ) -> list[Measurement]:
        measurements = []

        for observation in observations:
            measurements.extend(
                self.measure_observation(
                    observation,
                    context,
                )
            )

        # Increment 1: Perform mathematical calibration over the measurement population
        from app.intelligence.measurement.core.calibration.engine import StatisticalCalibrationEngine
        calibration_engine = StatisticalCalibrationEngine()
        return list(calibration_engine.calibrate(measurements))

    def measure_event(
        self,
        event,
        context: MeasurementContext | None = None,
    ) -> list[Measurement]:
        """
        Deprecated compatibility bridge.

        Measurement's canonical contract is `Observation`. Legacy callers that
        still hold `app.domain.event.Event` are translated before evaluation.
        """
        return self.measure_observation(
            event_to_observation(event),
            context,
        )

    def measure_events(
        self,
        events: list,
        context: MeasurementContext | None = None,
    ) -> list[Measurement]:
        return self.measure_observations(
            [
                event_to_observation(event)
                for event in events
            ],
            context,
        )

    def _finalize(
        self,
        measurement: Measurement,
        context: MeasurementContext,
    ) -> Measurement:
        pipeline_measurement, stage_names = (
            self._normalization_pipeline.apply(
                measurement
            )
        )

        normalized = self._normalize(
            replace(
                pipeline_measurement,
                provenance=replace(
                    pipeline_measurement.provenance,
                    transformations=(
                        *pipeline_measurement
                        .provenance
                        .transformations,
                        *stage_names,
                    ),
                ),
            )
        )

        validation = merge_validation_results(
            [
                validator.validate(
                    normalized
                )
                for validator in self._validators
            ]
        )

        with_validation = replace(
            normalized,
            validation_status=validation.status,
        )

        if validation.status == ValidationStatus.FAILED:
            return self._quality_scorer.score(
                with_validation,
                validation,
                context,
            )

        with_confidence = (
            self._confidence_estimator
            .estimate(
                with_validation,
                context,
            )
        )

        return self._quality_scorer.score(
            with_confidence,
            validation,
            context,
        )

    def _normalize(
        self,
        measurement: Measurement,
    ) -> Measurement:
        for normalizer in self._normalizers:
            if normalizer.supports(
                measurement
            ):
                normalized = normalizer.normalize(
                    measurement
                )

                return replace(
                    normalized,
                    traceability=replace(
                        normalized.traceability,
                        normalizer=(
                            normalized
                            .normalization_method
                            .name
                        ),
                    ),
                )

        return measurement


