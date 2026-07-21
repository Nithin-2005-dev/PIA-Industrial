"""Tests for M61 — Industrial Knowledge Graph Population and Queries."""
from __future__ import annotations

import pytest

from app.domain.industrial.relationships import IndustrialRelationship
from app.extraction.entities.entity_resolver import ResolvedEntity
from app.knowledge.graph.builders.industrial_graph_builder import IndustrialGraphBuilder
from app.knowledge.graph.industrial_graph_manager import IndustrialGraphManager


class TestIndustrialGraphManager:
    def test_populate_from_entities(self):
        builder = IndustrialGraphBuilder()
        manager = IndustrialGraphManager(builder)

        # Mock some resolved entities
        entities = (
            ResolvedEntity("equipment_tag", "P-101", ("P-101",), 0.95, ("regex",)),
            ResolvedEntity("work_order_id", "WO-123", ("WO-123",), 0.98, ("regex",)),
            ResolvedEntity("failure_mode", "bearing_degradation", ("bearing degradation",), 0.8, ("dictionary",)),
        )

        manager.populate_from_entities(entities, "DOC-001")
        graph = manager.build_graph()

        # Check nodes are created
        node_ids = {n.id for n in graph.nodes}
        assert "P-101" in node_ids
        assert "WO-123" in node_ids
        assert "fm_bearing_degradation" in node_ids

        # Check edges back to document
        edges = graph.edges
        assert any(e.source_id == "DOC-001" and e.target_id == "P-101" and e.relationship == IndustrialRelationship.DOCUMENTS.value for e in edges)
        assert any(e.source_id == "DOC-001" and e.target_id == "WO-123" and e.relationship == IndustrialRelationship.DOCUMENTS.value for e in edges)

    def test_get_asset_neighborhood(self):
        builder = IndustrialGraphBuilder()
        manager = IndustrialGraphManager(builder)

        # Create asset and link things
        from app.domain.industrial.document import Document, DocumentType, DocumentFormat
        import datetime
        doc = Document(
            document_id="DOC-001",
            name="Test.pdf",
            document_type=DocumentType.INSPECTION_REPORT,
            document_format=DocumentFormat.PDF,
            file_hash="123",
            file_path="test.pdf",
            file_size_bytes=100,
            ingested_at=datetime.datetime.now(),
        )
        builder.add_document(doc)

        entities = (
            ResolvedEntity("equipment_tag", "P-101", ("P-101",), 0.95, ("regex",)),
        )
        manager.populate_from_entities(entities, "DOC-001")
        
        # Add a work order linking to asset manually
        from app.domain.industrial.document import MaintenanceWorkOrder
        wo = MaintenanceWorkOrder(work_order_id="WO-999", title="Test WO", asset_id="P-101")
        builder.add_work_order(wo, document_id="DOC-002")

        neighborhood = manager.get_asset_neighborhood("P-101")
        
        # DOC-001 is a document linked via DOCUMENTS
        assert any(item["id"] == "DOC-001" for item in neighborhood["documents"])
        
        # WO-999 is a work order linked via APPLIES_TO
        assert any(item["id"] == "WO-999" for item in neighborhood["work_orders"])

    def test_get_failure_chain(self):
        builder = IndustrialGraphBuilder()
        manager = IndustrialGraphManager(builder)

        from app.domain.industrial.failure import FailureEvent, FailureMode, FailureCause

        # Build failure chain manually using domain models
        fm = FailureMode(id="fm_1", name="Vibration")
        fc = FailureCause(id="fc_1", name="Misalignment")
        builder.add_failure_mode(fm)
        builder.add_failure_cause(fc)

        fe = FailureEvent(
            id="fe_1",
            description="High vibration event",
            asset_id="P-101",
            failure_mode_id="fm_1",
            failure_cause_id="fc_1",
            source_document_id="DOC-003",
        )
        builder.add_failure_event(fe)

        chain = manager.get_failure_chain("fe_1")
        assert chain["failure_mode"] == "fm_1"
        assert chain["failure_cause"] == "fc_1"
        assert chain["asset_id"] == "P-101"
