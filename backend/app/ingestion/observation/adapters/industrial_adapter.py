"""Industrial Observation Adapter.

Bridges the Industrial Knowledge Extraction Pipeline (M60) with
the Canonical PIA Observation Pipeline. Converts extracted entities
and documents into deterministic Observation events.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entity_ref import EntityRef
from app.domain.industrial.document import Document, DocumentChunk
from app.extraction.entities.entity_resolver import ResolvedEntity
from app.ingestion.observation.domain import (
    CanonicalFacts,
    DocumentIngestionFacts,
    FailureEventFacts,
    InspectionFacts,
    MaintenanceActionFacts,
    Observation,
    ObservationCategory,
    ObservationContext,
    ObservationLifecycle,
    ObservationProvenance,
    ObservationType,
    ProcessingMode,
)

logger = logging.getLogger(__name__)


class IndustrialObservationAdapter:
    """Converts industrial extractions to Canonical Observations."""

    def __init__(self, source_platform: str = "pia_industrial_ingestion"):
        self._source_platform = source_platform

    def adapt_document(
        self,
        document: Document,
        chunks: tuple[DocumentChunk, ...],
        entities: tuple[ResolvedEntity, ...],
    ) -> tuple[Observation, ...]:
        """Convert a document and its extractions into Observations."""
        observations: list[Observation] = []
        correlation_id = str(uuid4())

        # 1. Document Ingestion Observation
        ingest_obs = self._create_ingestion_observation(document, chunks, entities, correlation_id)
        observations.append(ingest_obs)

        # 2. Extract Event Observations (Failures, Inspections, Maintenance)
        # In a real system, we might have multiple entities per event, but for now
        # we'll create an observation for each significant entity as an event.
        for entity in entities:
            if entity.entity_type == "failure_mode":
                obs = self._create_failure_observation(document, entity, correlation_id)
                observations.append(obs)
            elif entity.entity_type == "inspection_report_id":
                obs = self._create_inspection_observation(document, entity, correlation_id)
                observations.append(obs)
            elif entity.entity_type == "work_order_id":
                obs = self._create_maintenance_observation(document, entity, correlation_id)
                observations.append(obs)
            # equipment_tag alone doesn't trigger an event, it's just a target entity

        return tuple(observations)

    def _create_base_observation(
        self,
        obs_type: ObservationType,
        category: ObservationCategory,
        facts: CanonicalFacts,
        document_id: str,
        correlation_id: str,
        targets: tuple[EntityRef, ...] = (),
    ) -> Observation:
        """Create a standard Observation structure."""
        return Observation(
            observation_id=str(uuid4()),
            trace_id=str(uuid4()),
            correlation_id=correlation_id,
            timestamp=datetime.now(UTC),
            observation_type=obs_type,
            observation_category=category,
            source_platform=self._source_platform,
            source_adapter="industrial_adapter",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=targets,
            provenance=ObservationProvenance(
                source_platform=self._source_platform,
                source_adapter="industrial_adapter",
                source_record_id=document_id,
                fetched_at=datetime.now(UTC),
            ),
            context=ObservationContext(
                metadata={"document_id": document_id}
            ),
            facts=facts,
            processing_mode=ProcessingMode.LIVE,
        )

    def _create_ingestion_observation(
        self,
        document: Document,
        chunks: tuple[DocumentChunk, ...],
        entities: tuple[ResolvedEntity, ...],
        correlation_id: str,
    ) -> Observation:
        facts = DocumentIngestionFacts(
            document_id=document.document_id,
            document_name=document.name,
            document_type=document.document_type.value,
            document_format=document.document_format.value,
            file_hash=document.file_hash,
            page_count=0,  # Not fully tracked in M59 yet
            chunk_count=len(chunks),
            entity_count=len(entities),
            ingested_at=document.ingested_at or datetime.now(UTC),
        )
        return self._create_base_observation(
            obs_type=ObservationType.DOCUMENT_INGESTION,
            category=ObservationCategory.OPERATIONS,
            facts=facts,
            document_id=document.document_id,
            correlation_id=correlation_id,
            targets=(EntityRef(id=document.document_id, type="document"),)
        )

    def _create_failure_observation(
        self,
        document: Document,
        entity: ResolvedEntity,
        correlation_id: str,
    ) -> Observation:
        # Look for associated equipment tag in document to link as target
        facts = FailureEventFacts(
            failure_id=f"failure_{str(uuid4())[:8]}",
            failure_mode=entity.canonical_value,
            description=f"Failure mode {entity.canonical_value} detected in {document.name}",
            source_document_id=document.document_id,
        )
        return self._create_base_observation(
            obs_type=ObservationType.FAILURE,
            category=ObservationCategory.RELIABILITY,
            facts=facts,
            document_id=document.document_id,
            correlation_id=correlation_id,
        )

    def _create_inspection_observation(
        self,
        document: Document,
        entity: ResolvedEntity,
        correlation_id: str,
    ) -> Observation:
        facts = InspectionFacts(
            inspection_id=entity.canonical_value,
            result="DETECTED",
            source_document_id=document.document_id,
        )
        return self._create_base_observation(
            obs_type=ObservationType.INSPECTION_EVENT,
            category=ObservationCategory.INSPECTION,
            facts=facts,
            document_id=document.document_id,
            correlation_id=correlation_id,
            targets=(EntityRef(id=entity.canonical_value, type="inspection"),)
        )

    def _create_maintenance_observation(
        self,
        document: Document,
        entity: ResolvedEntity,
        correlation_id: str,
    ) -> Observation:
        facts = MaintenanceActionFacts(
            work_order_id=entity.canonical_value,
            status="OPEN",  # Defaulting, requires NLP to refine in M72
            source_document_id=document.document_id,
        )
        return self._create_base_observation(
            obs_type=ObservationType.WORK_ORDER,
            category=ObservationCategory.MAINTENANCE,
            facts=facts,
            document_id=document.document_id,
            correlation_id=correlation_id,
            targets=(EntityRef(id=entity.canonical_value, type="work_order"),)
        )
