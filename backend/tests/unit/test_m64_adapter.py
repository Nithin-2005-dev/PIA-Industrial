"""Tests for Phase 0 - Industrial Observation Adapter."""
from __future__ import annotations

import datetime

from app.domain.industrial.document import Document, DocumentChunk, DocumentFormat, DocumentType
from app.extraction.entities.entity_resolver import ResolvedEntity
from app.ingestion.observation.adapters.industrial_adapter import IndustrialObservationAdapter
from app.ingestion.observation.domain import ObservationType


class TestIndustrialObservationAdapter:
    def test_adapt_document(self):
        adapter = IndustrialObservationAdapter()
        
        doc = Document(
            document_id="DOC-123",
            name="test.pdf",
            document_type=DocumentType.INSPECTION_REPORT,
            document_format=DocumentFormat.PDF,
            file_hash="hash",
            file_path="test.pdf",
            file_size_bytes=100,
            ingested_at=datetime.datetime.now(datetime.UTC),
        )
        
        chunks = (
            DocumentChunk("c1", "DOC-123", "bearing failure on P-101"),
        )
        
        entities = (
            ResolvedEntity("equipment_tag", "P-101", ("P-101",), 0.9, ("regex",)),
            ResolvedEntity("failure_mode", "bearing_failure", ("bearing failure",), 0.9, ("dict",)),
            ResolvedEntity("work_order_id", "WO-999", ("WO-999",), 0.9, ("regex",)),
        )
        
        observations = adapter.adapt_document(doc, chunks, entities)
        
        assert len(observations) == 3
        
        obs_types = {obs.observation_type for obs in observations}
        assert ObservationType.DOCUMENT_INGESTION in obs_types
        assert ObservationType.FAILURE in obs_types
        assert ObservationType.WORK_ORDER in obs_types
        
        # Check properties of Document Ingestion
        ingest = next(o for o in observations if o.observation_type == ObservationType.DOCUMENT_INGESTION)
        assert ingest.facts.chunk_count == 1
        assert ingest.facts.entity_count == 3
        assert ingest.context.metadata["document_id"] == "DOC-123"
