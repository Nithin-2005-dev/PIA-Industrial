import math
from collections import defaultdict
from math import log1p

from app.intelligence.measurement.core.ids import stable_measurement_id
from app.intelligence.measurement.core.interfaces import MeasurementEvaluator
from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementContext
from app.intelligence.measurement.domain import MeasurementDefinition
from app.intelligence.measurement.domain import MeasurementMethod
from app.intelligence.measurement.domain import MeasurementProvenance
from app.intelligence.measurement.domain import MeasurementTrace
from app.intelligence.measurement.domain import MeasurementUncertainty
from app.intelligence.measurement.domain import NormalizationMethod
from app.intelligence.measurement.domain.catalog import DefaultMeasurementCatalog
from app.intelligence.measurement.evaluators.common import additions
from app.intelligence.measurement.evaluators.common import artifact_files
from app.intelligence.measurement.evaluators.common import deletions
from app.intelligence.measurement.evaluators.common import files_changed
from app.intelligence.measurement.evaluators.common import total_changes
from app.intelligence.measurement.core.measurement_config import MeasurementConfig
from app.ingestion.observation.domain import Observation


class ChangeImpactEvaluator(MeasurementEvaluator):

    @property
    def metric_name(self) -> str:
        return "change_impact"

    @property
    def logic_version(self) -> str:
        return "v1.0.0"

    _REGISTRY = DefaultMeasurementCatalog.build()

    CHANGE_SURFACE_AREA = _REGISTRY.get("change_surface_area")
    REVIEW_ATTENTION_NEED = _REGISTRY.get("review_attention_need")

    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        files = artifact_files(
            observation
        )

        churn = total_changes(
            observation
        )

        filtered_paths = []
        config = MeasurementConfig()
        for file in files:
            weight = config.get_file_weight(file.path, file.status, context="impact")
            if weight > 0.0:
                filtered_paths.append(file.path)
                
        entropy = self._calculate_directory_entropy(filtered_paths)
        
        total_blast_radius = 0.0
        for path in filtered_paths:
            depth_multiplier = config.get_depth_multiplier(path)
            total_blast_radius += (1.0 * depth_multiplier)
            
        surface_area = total_blast_radius * (1.0 + entropy)

        deletion_ratio = 0.0

        line_total = additions(
            observation
        ) + deletions(
            observation
        )

        if line_total > 0:
            deletion_ratio = deletions(
                observation
            ) / line_total

        patch_coverage = self._patch_coverage(
            files
        )

        attention = min(
            100.0,
            surface_area
            * 0.65
            + deletion_ratio * 20.0
            + (1.0 - patch_coverage) * 15.0,
        )

        return [
            self._measurement(
                self.CHANGE_SURFACE_AREA,
                surface_area,
                observation,
                context,
                {
                    "coverage": 1.0 if churn > 0 else 0.4,
                },
            ),
            self._measurement(
                self.REVIEW_ATTENTION_NEED,
                attention,
                observation,
                context,
                {
                    "coverage": max(
                        0.35,
                        patch_coverage,
                    ),
                    "missing_penalty": (
                        1.0 - patch_coverage
                    )
                    * 0.25,
                },
            ),
        ]

    def _measurement(
        self,
        definition: MeasurementDefinition,
        value: float,
        observation: Observation,
        context: MeasurementContext,
        metadata,
    ) -> Measurement:
        method = MeasurementMethod(
            name="change_impact_evaluator",
            version="1.0",
            algorithm=definition.id,
        )

        return Measurement(
            id=stable_measurement_id(
                observation.observation_id,
                definition.id,
                definition.version,
            ),
            definition=definition,
            unit=definition.unit,
            value=value,
            confidence=0.0,
            uncertainty=MeasurementUncertainty(
                lower_bound=value,
                upper_bound=value,
                variance=0.0,
            ),
            quality_score=0.0,
            measurement_method=method,
            normalization_method=NormalizationMethod(
                name="not_normalized",
                version="1.0",
                source_unit=definition.unit,
                target_unit=definition.unit,
            ),
            provenance=MeasurementProvenance(
                source_system=observation.source_platform,
                adapter=observation.source_adapter,
                source_event_id=observation.observation_id,
                source_observation_id=observation.observation_id,
                source_entity_ids=tuple(
                    target.id
                    for target in observation.targets
                ),
                transformations=(
                    "observation.facts",
                    method.name,
                ),
                tenant_id=context.tenant_id,
            ),
            timestamp=context.timestamp,
            version=definition.version,
            traceability=MeasurementTrace(
                pipeline_version=context.pipeline_version,
                evaluator=method.name,
            ),
            metadata=metadata,
        )

    def _patch_coverage(
        self,
        files,
    ) -> float:
        if not files:
            return 0.0

        files_with_patch = sum(
            1
            for file in files
            if file.patch
        )

        return files_with_patch / len(
            files
        )



    def _calculate_directory_entropy(self, file_paths: list[str]) -> float:
        """Calculates Shannon Entropy across root directories to measure coupling risk."""
        if not file_paths:
            return 0.0
            
        # Count how many files were touched in each top-level directory
        # e.g., 'backend/app/main.py' -> root is 'backend/app'
        dir_counts = defaultdict(int)
        for path in file_paths:
            parts = path.split('/')
            # Group by the first two levels to represent a 'subsystem' (adjust as needed)
            subsystem = "/".join(parts[:2]) if len(parts) > 1 else parts[0]
            dir_counts[subsystem] += 1
            
        total_files = len(file_paths)
        entropy = 0.0
        
        for count in dir_counts.values():
            probability = count / total_files
            entropy -= probability * math.log2(probability)
            
        return entropy # 0.0 means all files in one folder. Higher means highly scattered.


