import re
from app.intelligence.measurement.core.ids import stable_measurement_id
from app.intelligence.measurement.core.interfaces import MeasurementEvaluator
from app.intelligence.measurement.core.measurement_config import MeasurementConfig
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
from app.intelligence.measurement.evaluators.common import entropy
from app.intelligence.measurement.evaluators.common import files_changed
from app.ingestion.observation.domain import Observation


class ChangeComplexityEvaluator(MeasurementEvaluator):

    @property
    def metric_name(self) -> str:
        return "change_complexity"

    @property
    def logic_version(self) -> str:
        return "v1.0.0"

    _REGISTRY = DefaultMeasurementCatalog.build()

    CODE_CHURN = _REGISTRY.get("code_churn")
    FILES_CHANGED = _REGISTRY.get("files_changed")
    PATCH_COMPLEXITY_DELTA = _REGISTRY.get("patch_complexity_delta")
    CHANGE_DISTRIBUTION_ENTROPY = _REGISTRY.get(
        "change_distribution_entropy"
    )



    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        files = artifact_files(
            observation
        )

        effective_churn = 0.0
        effective_file_count = 0.0
        effective_complexity_delta = 0.0
        weighted_changes = []

        config = MeasurementConfig()

        for file in files:
            weight = config.get_file_weight(file.path, file.status)
            if weight == 0.0:
                continue

            churn = float(file.additions + file.deletions)
            effective_churn += churn * weight
            effective_file_count += weight
            effective_complexity_delta += self._calculate_mccabe_delta(file.patch) * weight
            weighted_changes.append(float(file.changes) * weight)

        distribution_entropy = entropy(weighted_changes)

        return [
            self._measurement(
                self.CODE_CHURN,
                effective_churn,
                observation,
                context,
                {
                    "coverage": 1.0,
                },
            ),
            self._measurement(
                self.FILES_CHANGED,
                effective_file_count,
                observation,
                context,
                {
                    "coverage": 1.0 if effective_file_count > 0 else 0.5,
                },
            ),
            self._measurement(
                self.PATCH_COMPLEXITY_DELTA,
                effective_complexity_delta,
                observation,
                context,
                {
                    "coverage": self._patch_coverage(
                        files
                    ),
                },
            ),
            self._measurement(
                self.CHANGE_DISTRIBUTION_ENTROPY,
                distribution_entropy,
                observation,
                context,
                {
                    "coverage": 1.0 if files else 0.4,
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
            name="change_complexity_evaluator",
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



    def _calculate_mccabe_delta(self, patch: str | None) -> float:
        if not patch:
            return 0.0
            
        try:
            # 1. Sanitize: strip string literals and single-line comments
            sanitized = re.sub(r'".*?"|\'.*?\'', '', patch)
            sanitized = re.sub(r'(#|//).*', '', sanitized)
            
            score = 0.0
            for line in sanitized.splitlines():
                if line.startswith('+++') or line.startswith('---'):
                    continue
                if not (line.startswith('+') or line.startswith('-')):
                    continue
                    
                # Scan for branching keywords
                matches = re.findall(r'\b(if|elif|else if|for|while|case|catch)\b', line)
                score += len(matches)
                
                # Scan for logical operators
                matches = re.findall(r'(&&|\|\||\?)', line)
                score += len(matches)
                
            return float(score)
        except Exception:
            return 0.0

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
