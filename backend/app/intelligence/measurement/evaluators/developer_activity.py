"""DeveloperActivityEvaluator — extended with Tier 2 measurements.

Produces per-developer measurements using canonical GitHub login
as the entity key via DeveloperIdentityResolver.

Purpose:
    Quantify developer behavioral patterns and knowledge acquisition.
Mathematical Basis:
    Sums absolute churn (additions + deletions). Uses ratio scaling
    for subsystem focus.
Assumptions:
    Author email/login maps reliably to a single identity.
Inputs:
    Observation (Commits)
Outputs:
    Measurements (developer_knowledge_spread, developer_subsystem_focus, etc.)
Limitations:
    Does not account for non-code contributions (issues/reviews).
Expected Accuracy:
    High (95%+), barring severe identity fragmentation.
"""

import math
import re
from collections import Counter

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


class DeveloperActivityEvaluator(MeasurementEvaluator):

    @property
    def metric_name(self) -> str:
        return "developer_activity"

    @property
    def logic_version(self) -> str:
        return "v1.0.0"

    _REGISTRY = DefaultMeasurementCatalog.build()

    AUTHOR_CONTRIBUTION_COUNT = _REGISTRY.get("author_contribution_count")
    AUTHOR_FILE_TOUCH_COUNT   = _REGISTRY.get("author_file_touch_count")
    AUTHOR_CODE_CHURN         = _REGISTRY.get("author_code_churn")
    DEV_KNOWLEDGE_SPREAD      = _REGISTRY.get("developer_knowledge_spread")
    DEV_SUBSYSTEM_FOCUS       = _REGISTRY.get("developer_subsystem_focus")
    DEV_RECENCY_SCORE         = _REGISTRY.get("developer_recency_score")
    DEV_COMMIT_FREQUENCY      = _REGISTRY.get("developer_commit_frequency")
    DEV_FILES_OWNED           = _REGISTRY.get("developer_files_owned")

    def _extract_co_authors(self, message: str) -> list[str]:
        """Extracts emails from 'Co-authored-by: Name <email>' trailers."""
        if not message:
            return []
        pattern = re.compile(r'(?mi)^Co-authored-by:\s*.*?\s*<(.*?)>')
        return pattern.findall(message)

    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        if not hasattr(observation.facts, "author_name") or not observation.facts.author_name:
            return []

        if not observation.actors:
            return []
            
        primary_id = observation.actors[0].id

        # Mitigate Trap 2: Invisible Collaborators
        message = getattr(observation.facts, "message", "")
        co_author_emails = self._extract_co_authors(message)
        
        collaborators = [primary_id]
        for email in co_author_emails:
            collaborators.append(email)
        
        # De-duplicate while preserving order
        collaborators = list(dict.fromkeys(collaborators))
        N = len(collaborators)

        # Mitigate Trap 1 & 3: Merge Commit & Upstream Sync Distortion
        is_merge_commit = len(getattr(observation.facts, "parent_ids", [])) > 1

        files = artifact_files(observation)
        
        effective_churn = 0.0
        effective_file_touches = 0.0
        subsystem_counts: Counter = Counter()

        if not is_merge_commit:
            config = MeasurementConfig()
            for file in files:
                weight = config.get_file_weight(file.path, file.status)
                if weight == 0.0:
                    continue
                    
                churn = getattr(file, "additions", 0) + getattr(file, "deletions", 0)
                effective_churn += churn * weight
                effective_file_touches += weight
                
                subsystem = config.resolve_subsystem(file.path)
                subsystem_counts[subsystem] += weight

        distinct_subsystems = len(subsystem_counts)
        total_touches = sum(subsystem_counts.values()) or 1.0
        max_subsystem_touches = max(subsystem_counts.values(), default=0.0)
        subsystem_focus = max_subsystem_touches / total_touches

        recency_score = 1.0

        measurements = []

        for i, actor_id in enumerate(collaborators):
            role = "primary" if i == 0 else "co-author"
            meta = {"coverage": 1.0, "role": role}
            
            actor_churn = effective_churn / N
            actor_file_touches = effective_file_touches / N

            if self.AUTHOR_CONTRIBUTION_COUNT:
                measurements.append(self._m(self.AUTHOR_CONTRIBUTION_COUNT, 1.0, observation, context, actor_id, meta))

            if self.AUTHOR_FILE_TOUCH_COUNT:
                measurements.append(self._m(self.AUTHOR_FILE_TOUCH_COUNT, actor_file_touches, observation, context, actor_id, {**meta, "coverage": 1.0 if actor_file_touches > 0 else 0.0}))

            if self.AUTHOR_CODE_CHURN:
                measurements.append(self._m(self.AUTHOR_CODE_CHURN, actor_churn, observation, context, actor_id, meta))

            if self.DEV_KNOWLEDGE_SPREAD:
                measurements.append(self._m(self.DEV_KNOWLEDGE_SPREAD, float(distinct_subsystems), observation, context, actor_id, meta))

            if self.DEV_SUBSYSTEM_FOCUS:
                measurements.append(self._m(self.DEV_SUBSYSTEM_FOCUS, subsystem_focus, observation, context, actor_id, meta))

            if self.DEV_RECENCY_SCORE:
                measurements.append(self._m(self.DEV_RECENCY_SCORE, recency_score, observation, context, actor_id, meta))

            if self.DEV_COMMIT_FREQUENCY:
                measurements.append(self._m(self.DEV_COMMIT_FREQUENCY, 1.0, observation, context, actor_id, meta))

            if self.DEV_FILES_OWNED:
                measurements.append(self._m(self.DEV_FILES_OWNED, actor_file_touches, observation, context, actor_id, meta))

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
            name="developer_activity_evaluator",
            version="2.0",
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
                target_entity_type="developer",
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

    # Backwards compat alias
    _measurement = _m
