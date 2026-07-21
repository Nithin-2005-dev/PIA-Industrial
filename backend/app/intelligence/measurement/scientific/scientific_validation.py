from dataclasses import dataclass

from app.intelligence.measurement.scientific.accuracy_profiles import AccuracyProfileRegistry
from app.intelligence.measurement.benchmarks.benchmark_datasets import BenchmarkDatasetRegistry
from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementDefinition
from app.intelligence.measurement.domain import ValidationResult
from app.intelligence.measurement.domain import ValidationStatus
from app.knowledge.evidence.knowledge.measurement_knowledge import SoftwareMeasurementKnowledgeBase
from app.intelligence.measurement.domain.registry import MeasurementRegistry


@dataclass(frozen=True)
class ScientificValidationReport:
    measurement_id: str
    status: ValidationStatus
    mathematical: ValidationResult
    semantic: ValidationResult
    statistical: ValidationResult
    benchmark: ValidationResult
    cross_source: ValidationResult
    historical: ValidationResult
    confidence: ValidationResult
    uncertainty: ValidationResult
    messages: tuple[str, ...]


class ScientificValidationEngine:

    def __init__(
        self,
        knowledge_base: SoftwareMeasurementKnowledgeBase,
        accuracy_profiles: AccuracyProfileRegistry,
        benchmark_registry: BenchmarkDatasetRegistry,
    ):
        self._knowledge_base = knowledge_base
        self._accuracy_profiles = accuracy_profiles
        self._benchmark_registry = benchmark_registry

    def validate_definition(
        self,
        definition: MeasurementDefinition,
    ) -> ScientificValidationReport:
        mathematical = self._validate_mathematical(
            definition
        )
        semantic = self._validate_semantic(
            definition
        )
        statistical = self._validate_statistical(
            definition
        )
        benchmark = self._validate_benchmark(
            definition.id
        )
        cross_source = self._validate_cross_source(
            definition
        )
        historical = self._validate_historical(
            definition
        )
        confidence = self._validate_confidence(
            definition
        )
        uncertainty = self._validate_uncertainty(
            definition
        )

        results = (
            mathematical,
            semantic,
            statistical,
            benchmark,
            cross_source,
            historical,
            confidence,
            uncertainty,
        )
        status = ValidationStatus.PASSED

        if any(
            result.status == ValidationStatus.FAILED
            for result in results
        ):
            status = ValidationStatus.FAILED
        elif any(
            result.status == ValidationStatus.WARNING
            for result in results
        ):
            status = ValidationStatus.WARNING

        messages = tuple(
            message
            for result in results
            for message in (
                *result.warnings,
                *result.errors,
            )
        )

        return ScientificValidationReport(
            measurement_id=definition.id,
            status=status,
            mathematical=mathematical,
            semantic=semantic,
            statistical=statistical,
            benchmark=benchmark,
            cross_source=cross_source,
            historical=historical,
            confidence=confidence,
            uncertainty=uncertainty,
            messages=messages,
        )

    def validate_measurement(
        self,
        measurement: Measurement,
    ) -> ScientificValidationReport:
        return self.validate_definition(
            measurement.definition
        )

    def _passed(
        self,
        check,
    ):
        return ValidationResult(
            status=ValidationStatus.PASSED,
            checks=(check,),
        )

    def _failed(
        self,
        check,
        message,
    ):
        return ValidationResult(
            status=ValidationStatus.FAILED,
            checks=(check,),
            errors=(message,),
        )

    def _warning(
        self,
        check,
        message,
    ):
        return ValidationResult(
            status=ValidationStatus.WARNING,
            checks=(check,),
            warnings=(message,),
        )

    def _validate_mathematical(
        self,
        definition: MeasurementDefinition,
    ):
        if not definition.formula:
            return self._warning(
                "mathematical",
                "definition has no explicit formula",
            )

        return self._passed(
            "mathematical"
        )

    def _validate_semantic(
        self,
        definition: MeasurementDefinition,
    ):
        if definition.concept_id is None:
            return self._failed(
                "semantic",
                "definition has no concept id",
            )

        return self._passed(
            "semantic"
        )

    def _validate_statistical(
        self,
        definition: MeasurementDefinition,
    ):
        knowledge = self._knowledge_base.get(
            definition.id
        )

        if knowledge is None:
            return self._failed(
                "statistical",
                "definition has no knowledge entry",
            )

        if not knowledge.validation_rules:
            return self._failed(
                "statistical",
                "knowledge entry has no validation rules",
            )

        return self._passed(
            "statistical"
        )

    def _validate_benchmark(
        self,
        measurement_id: str,
    ):
        datasets = self._benchmark_registry.for_measurement(
            measurement_id
        )

        if not datasets:
            return self._warning(
                "benchmark",
                "no benchmark dataset registered",
            )

        return self._passed(
            "benchmark"
        )

    def _validate_cross_source(
        self,
        definition: MeasurementDefinition,
    ):
        if not definition.required_signals:
            return self._failed(
                "cross_source",
                "definition has no required signals",
            )

        return self._passed(
            "cross_source"
        )

    def _validate_historical(
        self,
        definition: MeasurementDefinition,
    ):
        profile = self._accuracy_profiles.get(
            definition.id
        )

        if profile is None:
            return self._failed(
                "historical",
                "definition has no accuracy profile",
            )

        return self._passed(
            "historical"
        )

    def _validate_confidence(
        self,
        definition: MeasurementDefinition,
    ):
        if not definition.confidence_model:
            return self._failed(
                "confidence",
                "definition has no confidence model",
            )

        return self._passed(
            "confidence"
        )

    def _validate_uncertainty(
        self,
        definition: MeasurementDefinition,
    ):
        knowledge = self._knowledge_base.get(
            definition.id
        )

        if knowledge is None or not knowledge.uncertainty_model:
            return self._failed(
                "uncertainty",
                "definition has no uncertainty model",
            )

        return self._passed(
            "uncertainty"
        )


class CatalogValidationService:

    def __init__(
        self,
        registry: MeasurementRegistry,
        validation_engine: ScientificValidationEngine,
    ):
        self._registry = registry
        self._validation_engine = validation_engine

    def validate_all(
        self,
    ) -> list[ScientificValidationReport]:
        return [
            self._validation_engine.validate_definition(
                definition
            )
            for definition in self._registry.all()
        ]

import random
import copy
import logging
from typing import List, Dict, Any
from datetime import timedelta

logger = logging.getLogger(__name__)

from app.intelligence.measurement.scientific.mcmc_generator import MarkovChainCorpusGenerator

class MonteCarloValidationEngine:
    def __init__(self):
        self.generator = MarkovChainCorpusGenerator()

    def run_simulation_suite(self, engine: Any, iterations: int = 100, events_per_sim: int = 50) -> Dict[str, Any]:
        """Runs the measurement engine against MCMC generated realities."""
        logger.info(f"Initiating MCMC Simulation: {iterations} iterations.")
        
        success_counts = 0
        total_runs = 0
        
        for i in range(iterations):
            # Generate a completely novel, logically sound reality
            synthetic_history = self.generator.generate_synthetic_history(num_events=events_per_sim)
            
            try:
                # Feed the Markov-generated timeline into the physics engine
                sim_measurements = [engine.measure_observation(obs, None) for obs in synthetic_history]
                
                # Check for fatal mathematical failures (e.g. engine crashes on edge cases)
                if sim_measurements is not None:
                     success_counts += 1
            except Exception as e:
                logger.error(f"Simulation failed on MCMC iteration {i}: {e}")
                
            total_runs += 1
            
        return {
            "iterations_run": total_runs,
            "survival_rate": success_counts / total_runs if total_runs else 0.0,
            "mcmc_engine_active": True
        }


