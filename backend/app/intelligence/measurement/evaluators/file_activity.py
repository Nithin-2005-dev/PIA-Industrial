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


class FileActivityEvaluator(MeasurementEvaluator):

    @property
    def metric_name(self) -> str:
        return "file_activity"

    @property
    def logic_version(self) -> str:
        return "v1.0.0"

    _REGISTRY = DefaultMeasurementCatalog.build()

    FILE_CHURN = _REGISTRY.get("file_churn")
    FILE_TOUCH_COUNT = _REGISTRY.get("file_touch_count")
    FILE_ADDITION_RATIO = _REGISTRY.get("file_addition_ratio")
    FILE_IS_TEST = _REGISTRY.get("file_is_test")
    FILE_IS_DOCUMENTATION = _REGISTRY.get("file_is_documentation")

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
        files = artifact_files(observation)
        measurements = []

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

        config = MeasurementConfig()

        for file in files:
            path = file.path
            status = getattr(file, "status", "modified")
            additions = getattr(file, "additions", 0)
            deletions = getattr(file, "deletions", 0)
            raw_changes = additions + deletions
            
            weight = config.get_file_weight(path, status)
            if weight == 0.0:
                continue
                
            effective_churn = raw_changes * weight
            if effective_churn < config.MIN_CHURN_THRESHOLD:
                continue
                
            fractional_churn = effective_churn / N

            for i, actor in enumerate(collaborators):
                role = "primary" if i == 0 else "co-author"
                meta = {"coverage": 1.0, "developer": actor, "role": role}

                # File churn
                if self.FILE_CHURN:
                    measurements.append(self._measurement(self.FILE_CHURN, fractional_churn, observation, context, path, meta))

                # Touch count
                if self.FILE_TOUCH_COUNT:
                    measurements.append(self._measurement(self.FILE_TOUCH_COUNT, 1.0, observation, context, path, meta))

                # Addition ratio
                if self.FILE_ADDITION_RATIO and raw_changes > 0:
                    measurements.append(self._measurement(self.FILE_ADDITION_RATIO, float(additions) / float(raw_changes), observation, context, path, meta))

                # Is test
                if self.FILE_IS_TEST:
                    is_test = 1.0 if re.search(r'test|spec|mock|fixture', path, re.IGNORECASE) else 0.0
                    measurements.append(self._measurement(self.FILE_IS_TEST, is_test, observation, context, path, meta))

                # Is documentation
                if self.FILE_IS_DOCUMENTATION:
                    is_doc = 1.0 if re.search(r'\.md|\.rst|\.txt|docs/|wiki/', path, re.IGNORECASE) else 0.0
                    measurements.append(self._measurement(self.FILE_IS_DOCUMENTATION, is_doc, observation, context, path, meta))

        return measurements

    def _measurement(
        self,
        definition: MeasurementDefinition,
        value: float,
        observation: Observation,
        context: MeasurementContext,
        target_entity: str,
        metadata: dict,
    ) -> Measurement:
        method = MeasurementMethod(
            name="file_activity_evaluator",
            version="1.0",
            algorithm=definition.id,
        )

        return Measurement(
            id=stable_measurement_id(
                observation.observation_id,
                definition.id,
                f"{definition.version}:{target_entity}:{metadata.get('developer', 'unknown')}",
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
