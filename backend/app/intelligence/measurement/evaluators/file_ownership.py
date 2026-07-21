"""FileOwnershipEvaluator — per-file ownership concentration.

Produces per-file measurements indicating author touches.
The downstream aggregation layer computes the true ownership score
as the fraction of a file's touches attributable to its majority author.

Purpose:
    Identify knowledge silos and key-person dependencies at the file level.
Mathematical Basis:
    Emits 1.0 per touch. Aggregated via sum/mean to yield ownership concentration ratio [0.0, 1.0].
Assumptions:
    Author identity maps correctly. Touches imply knowledge retention.
Inputs:
    Observation (Commits)
Outputs:
    Measurements (file_ownership_score)
Limitations:
    Does not account for reading or code review, only authoring.
Expected Accuracy:
    High (90%+), though may misclassify trivial refactors as ownership.
"""

import re
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
from app.intelligence.measurement.evaluators.common import artifact_files
from app.intelligence.measurement.core.measurement_config import MeasurementConfig
from app.ingestion.observation.domain import Observation


class FileOwnershipEvaluator(MeasurementEvaluator):

    @property
    def metric_name(self) -> str:
        return "file_ownership"

    @property
    def logic_version(self) -> str:
        return "v1.0.0"
    """
    Emits `file_ownership_score` based on effective absolute churn for each (file, author) pair
    in the commit. The evidence synthesis engine uses this to compute
    the ownership concentration across commits.

    Mathematical basis:
        For each file, ownership_score = sum(effective_churn_by_author) / total_effective_churn
        By emitting absolute churn fractionally distributed to collaborators, we appropriately
        reward cleanup/refactoring while mitigating the Janitor and Silo fallacies.
    """

    _REGISTRY = DefaultMeasurementCatalog.build()
    FILE_OWNERSHIP_SCORE = _REGISTRY.get("file_ownership_score")



    def _extract_co_authors(self, message: str) -> list[str]:
        if not message:
            return []
        pattern = re.compile(r'(?mi)^Co-authored-by:\s*.*?\s*<(.*?)>')
        return pattern.findall(message)

    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        if not self.FILE_OWNERSHIP_SCORE:
            return []

        files = artifact_files(observation)
        if not files:
            return []

        if not observation.actors:
            return []
            
        primary_dev = observation.actors[0].id
        
        message = getattr(observation.facts, "message", "")
        co_author_emails = self._extract_co_authors(message)
        
        collaborators = [primary_dev]
        for email in co_author_emails:
            collaborators.append(email)
            
        collaborators = list(dict.fromkeys(collaborators))
        N = len(collaborators)

        measurements = []
        config = MeasurementConfig()
        
        for file in files:
            weight = config.get_file_weight(file.path, file.status)
            if weight == 0.0:
                continue
                
            absolute_churn = getattr(file, "additions", 0) + getattr(file, "deletions", 0)
            if absolute_churn == 0:
                continue
                
            effective_ownership_score = (absolute_churn * weight) / N
            if effective_ownership_score <= 0:
                continue

            for i, actor_id in enumerate(collaborators):
                role = "primary" if i == 0 else "co-author"
                measurements.append(
                    self._m(
                        self.FILE_OWNERSHIP_SCORE,
                        effective_ownership_score,
                        observation,
                        context,
                        file.path,
                        {"author": actor_id, "coverage": 1.0, "role": role},
                    )
                )

        return measurements

    def _m(
        self,
        definition: MeasurementDefinition,
        value: float,
        observation: Observation,
        context: MeasurementContext,
        target_entity: str,
        metadata: dict,
    ) -> Measurement:
        method = MeasurementMethod(
            name="file_ownership_evaluator",
            version="1.0",
            algorithm=definition.id,
        )
        return Measurement(
            id=stable_measurement_id(
                observation.observation_id,
                definition.id,
                f"{definition.version}:{target_entity}",
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
                source_entity_ids=tuple(target.id for target in observation.targets),
                transformations=("observation.facts", method.name),
                tenant_id=context.tenant_id,
                target_entity=target_entity,
                target_entity_type="module",
                measurement_scope="commit",
            ),
            timestamp=context.timestamp,
            version=definition.version,
            traceability=MeasurementTrace(
                pipeline_version=context.pipeline_version,
                evaluator=method.name,
            ),
            metadata=metadata,
        )
