"""SubsystemActivityEvaluator — extended with Tier 2 measurements.

Uses SubsystemResolver to map file paths to canonical subsystem names.
Produces per-subsystem measurements covering churn, contributors,
file concentration, coupling, and volatility.

Purpose:
    Assess structural risk, knowledge distribution, and volatility at the subsystem level.
Mathematical Basis:
    Gini coefficient for file concentration. Simple sums and ratios for coupling/churn.
Assumptions:
    SubsystemResolver accurately groups files into logical architecture domains.
Inputs:
    Observation (Commits)
Outputs:
    Measurements (subsystem_churn_rate, subsystem_file_concentration, etc.)
Limitations:
    Coupling score is currently bound to single-commit co-changes.
Expected Accuracy:
    High for churn and contributors; moderate for coupling due to single-commit constraint.
"""

import math
import re
from collections import defaultdict
from typing import Any

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


def _gini(values: list[float]) -> float:
    """Compute the Gini coefficient of a list of non-negative values."""
    if not values or sum(values) == 0:
        return 0.0
    n = len(values)
    sorted_vals = sorted(values)
    cumulative = sum((i + 1) * v for i, v in enumerate(sorted_vals))
    total = sum(sorted_vals)
    return (2 * cumulative) / (n * total) - (n + 1) / n


class SubsystemActivityEvaluator(MeasurementEvaluator):

    @property
    def metric_name(self) -> str:
        return "subsystem_activity"

    @property
    def logic_version(self) -> str:
        return "v1.0.0"

    _REGISTRY = DefaultMeasurementCatalog.build()

    DIRECTORY_CHURN         = _REGISTRY.get("directory_churn")
    DIRECTORY_FILE_COUNT    = _REGISTRY.get("directory_file_count")
    SUBSYSTEM_CHURN_RATE    = _REGISTRY.get("subsystem_churn_rate")
    SUBSYSTEM_CONTRIBUTOR   = _REGISTRY.get("subsystem_contributor_count")
    SUBSYSTEM_CONCENTRATION = _REGISTRY.get("subsystem_file_concentration")
    SUBSYSTEM_COUPLING      = _REGISTRY.get("subsystem_coupling_score")
    SUBSYSTEM_VOLATILITY    = _REGISTRY.get("subsystem_volatility")

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

        subsystem_churn:   defaultdict[str, float]      = defaultdict(float)
        subsystem_files:   defaultdict[str, set]        = defaultdict(set)
        subsystem_file_churn: defaultdict[str, list]    = defaultdict(list)

        config = MeasurementConfig()

        for file in files:
            weight = config.get_file_weight(file.path, file.status)
            if weight == 0.0:
                continue
                
            subsystem = config.resolve_subsystem(file.path)
            raw_changes = getattr(file, "additions", 0) + getattr(file, "deletions", 0)
            changes = raw_changes * weight
            
            subsystem_churn[subsystem]  += changes
            subsystem_files[subsystem].add(file.path)
            subsystem_file_churn[subsystem].append(float(changes))

        all_subsystems = set(subsystem_churn) | set(subsystem_files)

        for subsystem in all_subsystems:
            churn      = float(subsystem_churn.get(subsystem, 0.0))
            file_set   = subsystem_files.get(subsystem, set())
            file_churn = subsystem_file_churn.get(subsystem, [])
            file_count = float(len(file_set))
            
            fractional_churn = churn / N
            fractional_file_count = file_count / N
            
            gini = _gini(file_churn) if file_churn else 0.0
            total_files_in_commit = len(files) or 1
            coupling = min(file_count / total_files_in_commit, 1.0)

            for i, actor in enumerate(collaborators):
                role = "primary" if i == 0 else "co-author"
                meta = {"coverage": 1.0, "developer": actor, "role": role}

                if self.DIRECTORY_CHURN:
                    measurements.append(self._m(self.DIRECTORY_CHURN, fractional_churn, observation, context, subsystem, meta))

                if self.DIRECTORY_FILE_COUNT:
                    measurements.append(self._m(self.DIRECTORY_FILE_COUNT, fractional_file_count, observation, context, subsystem, meta))

                if self.SUBSYSTEM_CHURN_RATE:
                    measurements.append(self._m(self.SUBSYSTEM_CHURN_RATE, fractional_churn, observation, context, subsystem, meta))

                if self.SUBSYSTEM_CONTRIBUTOR:
                    measurements.append(self._m(self.SUBSYSTEM_CONTRIBUTOR, 1.0, observation, context, subsystem, meta))

                if self.SUBSYSTEM_CONCENTRATION and file_churn:
                    measurements.append(self._m(self.SUBSYSTEM_CONCENTRATION, gini, observation, context, subsystem, meta))

                if self.SUBSYSTEM_COUPLING:
                    measurements.append(self._m(self.SUBSYSTEM_COUPLING, coupling, observation, context, subsystem, meta))

                if self.SUBSYSTEM_VOLATILITY:
                    measurements.append(self._m(self.SUBSYSTEM_VOLATILITY, fractional_churn, observation, context, subsystem, meta))

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
            name="subsystem_activity_evaluator",
            version="2.0",
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
                target_entity_type="subsystem",
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
