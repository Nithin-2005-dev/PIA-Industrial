from __future__ import annotations

from dataclasses import dataclass
from uuid import NAMESPACE_URL
from uuid import uuid5

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.domain.evidence import Evidence as EstimatorEvidence
from app.domain.predicate_type import PredicateType
from app.estimator.estimation_context import EstimationContext
from app.estimator.expertise_projection import ExpertiseProjection
from app.knowledge.evidence.core import EvidencePackage
from app.knowledge.evidence.domain import Evidence as SemanticEvidence


@dataclass(frozen=True)
class ExpertiseProjectionResult:
    applied_count: int
    skipped_count: int


class SemanticEvidenceExpertiseBridge:
    def to_estimator_evidence(
        self,
        evidence: SemanticEvidence,
    ) -> tuple[EstimatorEvidence, ...]:
        target_entity = evidence.metadata.get("target_entity")
        if not target_entity or target_entity == "global":
            return ()
        actor_ids = self._actor_ids(evidence)
        if not actor_ids:
            return ()

        predicate = self._predicate_for(evidence)
        strength = self._strength_for(evidence)
        object_ref = EntityRef(
            id=str(target_entity),
            type=self._entity_type(
                evidence.metadata.get("target_entity_type")
            ),
        )
        converted = []
        for actor_id in actor_ids:
            converted.append(
                EstimatorEvidence(
                    id=uuid5(
                        NAMESPACE_URL,
                        f"{evidence.evidence_id}|{actor_id}|expertise",
                    ),
                    source_event_id=uuid5(
                        NAMESPACE_URL,
                        evidence.evidence_id,
                    ),
                    subject_ref=EntityRef(
                        id=actor_id,
                        type=EntityType.DEVELOPER,
                    ),
                    predicate=predicate,
                    object_ref=object_ref,
                    confidence=evidence.confidence,
                    metadata={
                        "strength": strength,
                        "semantic_evidence_id": evidence.evidence_id,
                        "semantic_category": evidence.category,
                        "semantic_name": evidence.name,
                        "quality": evidence.quality,
                        "uncertainty": evidence.uncertainty,
                        "supporting_measurement_ids": tuple(
                            measurement.id
                            for measurement in evidence.supporting_measurements
                        ),
                    },
                )
            )
        return tuple(converted)

    def package_to_estimator_evidence(
        self,
        package: EvidencePackage,
    ) -> tuple[EstimatorEvidence, ...]:
        converted = []
        for evidence in package.for_expertise():
            converted.extend(
                self.to_estimator_evidence(evidence)
            )
        return tuple(converted)

    def _actor_ids(
        self,
        evidence: SemanticEvidence,
    ) -> tuple[str, ...]:
        actor_ids: list[str] = []
        for measurement in evidence.supporting_measurements:
            for actor_id in measurement.metadata.get("actor_ids", ()):
                if actor_id and actor_id not in actor_ids:
                    actor_ids.append(str(actor_id))
        return tuple(actor_ids)

    def _predicate_for(
        self,
        evidence: SemanticEvidence,
    ) -> PredicateType:
        definition_id = evidence.provenance.evidence_definition_id or ""
        if "review" in definition_id:
            return PredicateType.REVIEWED
        if "documentation" in definition_id:
            return PredicateType.CREATED
        if "build" in definition_id or "test" in definition_id:
            return PredicateType.TOUCHED
        if "merge" in definition_id:
            return PredicateType.MERGED
        return PredicateType.MODIFIED

    def _strength_for(
        self,
        evidence: SemanticEvidence,
    ) -> float:
        severity_multiplier = 1.0 + (
            evidence.severity.rank() * 0.15
        )
        return max(
            0.0,
            evidence.strength
            * evidence.quality
            * severity_multiplier
        )

    def _entity_type(
        self,
        value,
    ) -> EntityType:
        normalized = str(value or "FILE").upper()
        return EntityType.__members__.get(
            normalized,
            EntityType.FILE,
        )


class SemanticExpertiseProjectionPipeline:
    def __init__(
        self,
        bridge: SemanticEvidenceExpertiseBridge | None = None,
    ):
        self._bridge = bridge or SemanticEvidenceExpertiseBridge()

    def apply(
        self,
        package: EvidencePackage,
        projection: ExpertiseProjection,
        context: EstimationContext,
    ) -> ExpertiseProjectionResult:
        converted = []
        skipped = 0
        for semantic_evidence in package.for_expertise():
            evidence_items = self._bridge.to_estimator_evidence(
                semantic_evidence
            )
            if not evidence_items:
                skipped += 1
            converted.extend(evidence_items)
        applied = 0
        for evidence in converted:
            projection.apply(
                evidence,
                context,
            )
            applied += 1
        return ExpertiseProjectionResult(
            applied_count=applied,
            skipped_count=skipped,
        )
