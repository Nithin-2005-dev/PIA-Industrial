from dataclasses import replace
from uuid import NAMESPACE_URL, uuid5

from app.knowledge.evidence.confidence import EvidenceConfidenceEngine
from app.knowledge.evidence.core import EvidenceContext
from app.knowledge.evidence.core import EvidencePackage
from app.knowledge.evidence.domain import BenchmarkContext
from app.knowledge.evidence.domain import Evidence
from app.knowledge.evidence.domain import EvidenceLifecycle
from app.knowledge.evidence.domain import EvidenceLineage
from app.knowledge.evidence.domain import EvidenceMeasurementRef
from app.knowledge.evidence.domain import EvidencePriority
from app.knowledge.evidence.domain import EvidenceProvenance
from app.knowledge.evidence.domain import EvidenceStatus
from app.knowledge.evidence.domain import EvidenceTraceability
from app.knowledge.evidence.domain import HistoricalContext
from app.knowledge.evidence.domain import TimeWindow
from app.knowledge.evidence.knowledge import EvidenceKnowledgeBase
from app.knowledge.evidence.knowledge import EvidenceDefinition
from app.knowledge.evidence.ontology import EvidenceOntology
from app.knowledge.evidence.validation import EvidenceValidationPipeline
from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import ValidationStatus


class EvidenceSynthesisEngine:

    def __init__(
        self,
        knowledge_base: EvidenceKnowledgeBase | None = None,
        ontology: EvidenceOntology | None = None,
        confidence_engine: EvidenceConfidenceEngine | None = None,
        validation_pipeline: EvidenceValidationPipeline | None = None,
    ):
        self._knowledge_base = (
            knowledge_base
            or EvidenceKnowledgeBase.default()
        )
        self._ontology = (
            ontology
            or EvidenceOntology.default()
        )
        self._confidence_engine = (
            confidence_engine
            or EvidenceConfidenceEngine()
        )
        self._validation_pipeline = (
            validation_pipeline
            or EvidenceValidationPipeline(
                self._ontology
            )
        )

    def synthesize(
        self,
        measurements: list[Measurement],
        context: EvidenceContext | None = None,
    ) -> EvidencePackage:
        if context is None:
            context = EvidenceContext()

        valid_measurements = [
            measurement
            for measurement in measurements
            if measurement.validation_status
            in {
                ValidationStatus.PASSED,
                ValidationStatus.WARNING,
            }
        ]

        # Fact Extraction: Group by target_entity
        from collections import defaultdict
        measurements_by_entity = defaultdict(dict)
        
        for measurement in valid_measurements:
            target_entity = measurement.provenance.target_entity or "global"
            target_entity_type = measurement.provenance.target_entity_type or "unknown"
            
            # Store tuple of (target_entity, target_entity_type)
            measurements_by_entity[(target_entity, target_entity_type)][measurement.definition.id] = (
                EvidenceMeasurementRef.from_measurement(measurement)
            )

        evidence_items = []
        rejected_count = len(measurements) - len(valid_measurements)

        for (target_entity, target_entity_type), entity_measurements in measurements_by_entity.items():
            for definition in self._knowledge_base.all():
                candidate = self._synthesize_definition(
                    definition,
                    entity_measurements,
                    context,
                    target_entity,
                    target_entity_type,
                )

                if candidate is None:
                    continue

                validated = self._validation_pipeline.validate(
                    candidate
                )
                if validated.is_valid_for_expertise():
                    evidence_items.append(
                        validated
                    )
                else:
                    for r in validated.validation_results:
                        if r.status.value == "failed":
                            print(f"[Evidence Rejection] {candidate.name}: {r.name} - {r.errors}")
                    rejected_count += 1

        return EvidencePackage(
            tenant_id=context.tenant_id,
            generated_at=context.timestamp,
            pipeline_version=context.pipeline_version,
            evidence=tuple(
                evidence_items
            ),
            rejected_count=rejected_count,
            audit_events=(
                "measurement_intake_validated",
                "evidence_facts_extracted",
                "evidence_rules_evaluated",
                "evidence_validation_completed",
            ),
            metadata={
                "input_measurements": len(
                    measurements
                ),
                "validated_measurements": len(
                    valid_measurements
                ),
            },
        )

    def _synthesize_definition(
        self,
        definition: EvidenceDefinition,
        measurements_by_definition: dict[str, EvidenceMeasurementRef],
        context: EvidenceContext,
        target_entity: str,
        target_entity_type: str,
    ) -> Evidence | None:
        required_present = all(
            measurement_id in measurements_by_definition
            for measurement_id in definition.required_measurements
        )
        if not required_present:
            return None

        matched_rules = [
            rule
            for rule in definition.triggering_conditions
            if rule.measurement_id in measurements_by_definition
            and rule.matches(
                measurements_by_definition[
                    rule.measurement_id
                ]
            )
        ]

        required_rule_ids = {
            rule.measurement_id
            for rule in definition.triggering_conditions
            if rule.measurement_id in definition.required_measurements
        }
        matched_required_ids = {
            rule.measurement_id
            for rule in matched_rules
            if rule.measurement_id in definition.required_measurements
        }
        if not required_rule_ids.issubset(
            matched_required_ids
        ):
            return None

        support_ids = (
            definition.required_measurements
            + definition.optional_measurements
        )
        supporting = tuple(
            measurements_by_definition[
                measurement_id
            ]
            for measurement_id in support_ids
            if measurement_id in measurements_by_definition
        )

        confidence = self._confidence_engine.aggregate(
            definition,
            supporting,
        )

        evidence_id = str(
            uuid5(
                NAMESPACE_URL,
                "|".join(
                    (
                        context.tenant_id or "global",
                        definition.id,
                        definition.version_history[-1],
                        *sorted(
                            measurement.id
                            for measurement in supporting
                        ),
                    )
                ),
            )
        )

        priority = self._priority_for(
            definition,
            confidence.value,
        )

        first_timestamp = min(
            measurement.timestamp
            for measurement in supporting
        )
        last_timestamp = max(
            measurement.timestamp
            for measurement in supporting
        )

        evidence = Evidence(
            evidence_id=evidence_id,
            name=definition.name,
            category=definition.category,
            description=definition.description,
            severity=definition.severity,
            priority=priority,
            status=EvidenceStatus.DRAFT,
            confidence=confidence.value,
            uncertainty=confidence.uncertainty,
            quality=confidence.quality,
            strength=confidence.strength,
            supporting_measurements=supporting,
            contradicting_measurements=(),
            benchmark_context=BenchmarkContext(
                quality=float(
                    definition.metadata.get(
                        "benchmark_quality",
                        1.0,
                    )
                )
            ),
            historical_context=HistoricalContext(
                consistency=float(
                    definition.metadata.get(
                        "historical_consistency",
                        1.0,
                    )
                )
            ),
            time_window=TimeWindow(
                started_at=first_timestamp,
                ended_at=last_timestamp,
            ),
            provenance=EvidenceProvenance(
                source_layer="Measurement Operating System",
                generated_by="EvidenceSynthesisEngine",
                tenant_id=context.tenant_id,
                measurement_ids=tuple(
                    measurement.id
                    for measurement in supporting
                ),
                evidence_definition_id=definition.id,
                pipeline_version=context.pipeline_version,
            ),
            lineage=EvidenceLineage(
                source_measurement_ids=tuple(
                    measurement.id
                    for measurement in supporting
                ),
                derived_from=(
                    definition.id,
                ),
                graph_node_id=evidence_id,
            ),
            traceability=EvidenceTraceability(
                synthesis_rule_ids=tuple(
                    rule.id
                    for rule in matched_rules
                ),
                confidence_factors=confidence.factors,
                explanation=confidence.explanation,
            ),
            assumptions=definition.assumptions,
            limitations=definition.known_limitations,
            validation_results=(),
            version=definition.version_history[-1],
            lifecycle=definition.lifecycle,
            metadata={
                "target_entity": target_entity,
                "target_entity_type": target_entity_type,
                "semantic_meaning": definition.semantic_meaning,
                "required_measurements": (
                    definition.required_measurements
                ),
                "optional_measurements": (
                    definition.optional_measurements
                ),
                "interpretation": definition.interpretation,
                "business_interpretation": (
                    definition.business_interpretation
                ),
                "standards_references": (
                    definition.standards_references
                ),
                "confidence_strategy": (
                    definition.confidence_strategy
                ),
            },
        )

        if definition.lifecycle == EvidenceLifecycle.EXPERIMENTAL:
            return replace(
                evidence,
                metadata={
                    **evidence.metadata,
                    "experimental": True,
                },
            )

        return evidence

    def _priority_for(
        self,
        definition: EvidenceDefinition,
        confidence: float,
    ) -> EvidencePriority:
        if (
            definition.severity.rank() >= 4
            and confidence >= 0.75
        ):
            return EvidencePriority.URGENT
        if (
            definition.severity.rank() >= 3
            and confidence >= 0.5
        ):
            return EvidencePriority.HIGH
        if confidence >= 0.4:
            return EvidencePriority.MEDIUM
        return EvidencePriority.LOW

