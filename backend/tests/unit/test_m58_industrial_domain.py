"""Tests for M58 — Industrial Domain & Ontology.

Validates:
1. All industrial domain models are immutable (frozen dataclasses)
2. Industrial entity types are properly defined
3. Industrial ontology schema is valid
4. Industrial graph builder produces correct graphs
5. Existing software domain types are preserved
"""
from __future__ import annotations

import datetime
from uuid import uuid4

import pytest


# ---------------------------------------------------------------------------
# Test: Industrial Asset Models
# ---------------------------------------------------------------------------

class TestAssetModels:
    def test_asset_is_frozen(self):
        from app.domain.industrial.asset import Asset, AssetStatus, AssetCriticality
        asset = Asset(
            id="P-101",
            name="Cooling Water Pump",
            equipment_tag="P-101",
            asset_type="Centrifugal Pump",
            system_id="CWS-01",
            status=AssetStatus.OPERATIONAL,
            criticality=AssetCriticality.PRODUCTION_CRITICAL,
        )
        assert asset.equipment_tag == "P-101"
        with pytest.raises(AttributeError):
            asset.name = "Modified"  # type: ignore

    def test_plant_hierarchy(self):
        from app.domain.industrial.asset import Plant, System, Asset, Component
        plant = Plant(id="PLT-01", name="Main Plant", location="Houston, TX")
        system = System(id="CWS-01", name="Cooling Water System", plant_id="PLT-01")
        asset = Asset(id="P-101", name="CW Pump", equipment_tag="P-101", asset_type="Pump", system_id="CWS-01")
        component = Component(id="B-101", name="Drive-End Bearing", component_type="Bearing", asset_id="P-101")

        assert plant.id == "PLT-01"
        assert system.plant_id == "PLT-01"
        assert asset.system_id == "CWS-01"
        assert component.asset_id == "P-101"

    def test_operating_parameter_abnormal(self):
        from app.domain.industrial.asset import OperatingParameter
        param = OperatingParameter(
            id="vib-001",
            asset_id="P-101",
            parameter_name="vibration",
            value=8.5,
            unit="mm/s",
            normal_range_low=0.0,
            normal_range_high=7.0,
        )
        assert param.is_abnormal is True

        normal_param = OperatingParameter(
            id="vib-002",
            asset_id="P-101",
            parameter_name="vibration",
            value=3.2,
            unit="mm/s",
            normal_range_low=0.0,
            normal_range_high=7.0,
        )
        assert normal_param.is_abnormal is False

    def test_equipment_tag(self):
        from app.domain.industrial.asset import EquipmentTag
        tag = EquipmentTag(tag="P-101", asset_id="P-101", confidence=0.95)
        assert tag.tag == "P-101"


# ---------------------------------------------------------------------------
# Test: Industrial Document Models
# ---------------------------------------------------------------------------

class TestDocumentModels:
    def test_document_is_frozen(self):
        from app.domain.industrial.document import Document, DocumentType, DocumentFormat, DocumentStatus
        doc = Document(
            document_id="DOC-001",
            name="OEM Manual P-101",
            document_type=DocumentType.OEM_MANUAL,
            document_format=DocumentFormat.PDF,
            file_hash="abc123",
            status=DocumentStatus.PROCESSED,
        )
        assert doc.document_type == DocumentType.OEM_MANUAL
        with pytest.raises(AttributeError):
            doc.name = "Modified"  # type: ignore

    def test_document_provenance(self):
        from app.domain.industrial.document import DocumentProvenance
        prov = DocumentProvenance(
            document_id="DOC-001",
            document_name="OEM Manual",
            document_type="OEM_MANUAL",
            page_number=3,
            section="Section 4.2",
            chunk_id="chunk-001",
            source_text="Recommended bearing replacement every 5000 hours.",
            confidence=0.95,
        )
        assert prov.page_number == 3
        assert prov.confidence == 0.95

    def test_inspection_report(self):
        from app.domain.industrial.document import InspectionReport
        report = InspectionReport(
            report_id="IR-104",
            document_id="DOC-003",
            asset_id="P-101",
            equipment_tag="P-101",
            inspector="John Smith",
            findings=("High vibration on drive-end bearing",),
            recommendations=("Replace drive-end bearing within 30 days",),
            severity="HIGH",
        )
        assert len(report.findings) == 1
        assert "vibration" in report.findings[0].lower()

    def test_work_order(self):
        from app.domain.industrial.document import MaintenanceWorkOrder
        wo = MaintenanceWorkOrder(
            work_order_id="WO-291",
            asset_id="P-101",
            title="Replace Drive-End Bearing",
            work_type="corrective",
            priority="urgent",
            status="DEFERRED",
        )
        assert wo.status == "DEFERRED"


# ---------------------------------------------------------------------------
# Test: Industrial Failure Models
# ---------------------------------------------------------------------------

class TestFailureModels:
    def test_failure_event(self):
        from app.domain.industrial.failure import FailureEvent, FailureSeverity
        failure = FailureEvent(
            id="F-17",
            asset_id="P-101",
            equipment_tag="P-101",
            description="Drive-end bearing seizure causing pump shutdown",
            severity=FailureSeverity.MAJOR,
            downtime_hours=48.0,
        )
        assert failure.severity == FailureSeverity.MAJOR
        assert failure.downtime_hours == 48.0

    def test_failure_mode_and_cause(self):
        from app.domain.industrial.failure import FailureMode, FailureCause
        mode = FailureMode(
            id="FM-001",
            name="Bearing Seizure",
            category="Mechanical",
            typical_indicators=("High vibration", "Elevated temperature"),
        )
        cause = FailureCause(
            id="FC-001",
            name="Lubrication Degradation",
            category="Wear",
        )
        assert mode.name == "Bearing Seizure"
        assert cause.name == "Lubrication Degradation"

    def test_failure_pattern(self):
        from app.domain.industrial.failure import FailurePattern
        pattern = FailurePattern(
            id="FP-001",
            pattern_name="Recurring Bearing Failures in Centrifugal Pumps",
            affected_asset_ids=("P-101", "P-102"),
            occurrence_count=3,
            trend_direction="INCREASING",
            confidence=0.85,
        )
        assert pattern.occurrence_count == 3
        assert len(pattern.affected_asset_ids) == 2


# ---------------------------------------------------------------------------
# Test: Industrial Maintenance Models
# ---------------------------------------------------------------------------

class TestMaintenanceModels:
    def test_recommendation_overdue(self):
        from app.domain.industrial.maintenance import Recommendation, RecommendationStatus, MaintenancePriority
        rec = Recommendation(
            id="REC-001",
            asset_id="P-101",
            description="Replace drive-end bearing",
            priority=MaintenancePriority.URGENT,
            status=RecommendationStatus.OPEN,
            due_date=datetime.datetime(2024, 1, 1),
        )
        assert rec.is_overdue is True
        assert rec.is_deferred is False

    def test_recommendation_deferred(self):
        from app.domain.industrial.maintenance import Recommendation, RecommendationStatus
        rec = Recommendation(
            id="REC-002",
            status=RecommendationStatus.DEFERRED,
        )
        assert rec.is_deferred is True


# ---------------------------------------------------------------------------
# Test: Industrial Personnel Models
# ---------------------------------------------------------------------------

class TestPersonnelModels:
    def test_person(self):
        from app.domain.industrial.personnel import Person, PersonnelRole
        person = Person(
            id="ENG-001",
            name="John Smith",
            role=PersonnelRole.ENGINEER,
            department="Maintenance",
        )
        assert person.role == PersonnelRole.ENGINEER

    def test_knowledge_concentration(self):
        from app.domain.industrial.personnel import KnowledgeConcentration
        kc = KnowledgeConcentration(
            subject_id="P-101",
            subject_type="asset",
            total_experts=1,
            primary_expert_share=0.78,
            concentration_score=0.95,
            risk_level="CRITICAL",
        )
        assert kc.concentration_score == 0.95


# ---------------------------------------------------------------------------
# Test: Industrial Compliance Models
# ---------------------------------------------------------------------------

class TestComplianceModels:
    def test_compliance_gap(self):
        from app.domain.industrial.compliance import ComplianceGap, ComplianceStatus
        gap = ComplianceGap(
            id="GAP-001",
            requirement_id="REQ-001",
            asset_id="P-101",
            status=ComplianceStatus.OVERDUE,
            days_overdue=30,
            confidence=0.9,
        )
        assert gap.status == ComplianceStatus.OVERDUE
        assert gap.days_overdue == 30

    def test_compliance_status_distinction(self):
        """MISSING_EVIDENCE != NON_COMPLIANT — this is a core requirement."""
        from app.domain.industrial.compliance import ComplianceStatus
        assert ComplianceStatus.MISSING_EVIDENCE != ComplianceStatus.NON_COMPLIANT


# ---------------------------------------------------------------------------
# Test: Relationship & Node Type Enums
# ---------------------------------------------------------------------------

class TestRelationships:
    def test_industrial_relationships_defined(self):
        from app.domain.industrial.relationships import IndustrialRelationship
        assert IndustrialRelationship.CONTAINS.value == "CONTAINS"
        assert IndustrialRelationship.CAUSED_BY.value == "CAUSED_BY"
        assert IndustrialRelationship.EVIDENCE_FOR.value == "EVIDENCE_FOR"
        assert len(IndustrialRelationship) >= 30

    def test_industrial_node_types_defined(self):
        from app.domain.industrial.relationships import IndustrialNodeType
        assert IndustrialNodeType.ASSET.value == "asset"
        assert IndustrialNodeType.FAILURE_EVENT.value == "failure_event"
        assert len(IndustrialNodeType) >= 25

    def test_certainty_levels(self):
        from app.domain.industrial.relationships import CertaintyLevel
        assert CertaintyLevel.FACT.value == "FACT"
        assert CertaintyLevel.CAUSAL_HYPOTHESIS.value == "CAUSAL_HYPOTHESIS"


# ---------------------------------------------------------------------------
# Test: Extended Core Domain Enums (backward compatibility)
# ---------------------------------------------------------------------------

class TestDomainEnumExtensions:
    def test_entity_type_preserves_originals(self):
        """All original EntityType values must still exist."""
        from app.domain.entity_type import EntityType
        assert EntityType.DEVELOPER.value == "DEVELOPER"
        assert EntityType.MODULE.value == "MODULE"
        assert EntityType.FILE.value == "FILE"
        assert EntityType.REPOSITORY.value == "REPOSITORY"
        assert EntityType.PULL_REQUEST.value == "PULL_REQUEST"
        assert EntityType.ISSUE.value == "ISSUE"
        assert EntityType.RELEASE.value == "RELEASE"

    def test_entity_type_has_industrial(self):
        from app.domain.entity_type import EntityType
        assert EntityType.ASSET.value == "ASSET"
        assert EntityType.EQUIPMENT.value == "EQUIPMENT"
        assert EntityType.COMPONENT.value == "COMPONENT"
        assert EntityType.PERSON.value == "PERSON"
        assert EntityType.FAILURE_EVENT.value == "FAILURE_EVENT"

    def test_event_type_preserves_originals(self):
        from app.domain.event_type import EventType
        assert EventType.COMMIT.value == "COMMIT"
        assert EventType.PULL_REQUEST.value == "PULL_REQUEST"
        assert EventType.REVIEW.value == "REVIEW"

    def test_event_type_has_industrial(self):
        from app.domain.event_type import EventType
        assert EventType.MAINTENANCE_ACTION.value == "MAINTENANCE_ACTION"
        assert EventType.FAILURE_EVENT.value == "FAILURE_EVENT"
        assert EventType.INSPECTION.value == "INSPECTION"

    def test_predicate_type_preserves_originals(self):
        from app.domain.predicate_type import PredicateType
        assert PredicateType.MODIFIED.value == "MODIFIED"
        assert PredicateType.REVIEWED.value == "REVIEWED"
        assert PredicateType.TOUCHED.value == "TOUCHED"

    def test_predicate_type_has_industrial(self):
        from app.domain.predicate_type import PredicateType
        assert PredicateType.INSPECTED.value == "INSPECTED"
        assert PredicateType.MAINTAINED.value == "MAINTAINED"
        assert PredicateType.FAILED.value == "FAILED"


# ---------------------------------------------------------------------------
# Test: Industrial Ontology Schema
# ---------------------------------------------------------------------------

class TestIndustrialOntology:
    def test_schema_builds(self):
        from app.domain.industrial.ontology import INDUSTRIAL_SCHEMA
        assert INDUSTRIAL_SCHEMA.version == "industrial-v1"

    def test_schema_has_asset_node_type(self):
        from app.domain.industrial.ontology import INDUSTRIAL_SCHEMA
        assert "asset" in INDUSTRIAL_SCHEMA.node_types
        asset_def = INDUSTRIAL_SCHEMA.node_types["asset"]
        assert "equipment_tag" in asset_def.required_attributes

    def test_schema_has_relationships(self):
        from app.domain.industrial.ontology import INDUSTRIAL_SCHEMA
        assert "CONTAINS" in INDUSTRIAL_SCHEMA.edge_types
        assert "CAUSED_BY" in INDUSTRIAL_SCHEMA.edge_types
        assert "EVIDENCE_FOR" in INDUSTRIAL_SCHEMA.edge_types

    def test_schema_has_validation_rules(self):
        from app.domain.industrial.ontology import INDUSTRIAL_SCHEMA
        rule_ids = {r.id for r in INDUSTRIAL_SCHEMA.validation_rules}
        assert "orphan_asset" in rule_ids
        assert "unresolved_equipment_tag" in rule_ids


# ---------------------------------------------------------------------------
# Test: Industrial Graph Builder
# ---------------------------------------------------------------------------

class TestIndustrialGraphBuilder:
    def _make_builder(self):
        from app.knowledge.graph.builders.industrial_graph_builder import IndustrialGraphBuilder
        return IndustrialGraphBuilder()

    def test_add_asset_creates_node(self):
        from app.domain.industrial.asset import Asset
        builder = self._make_builder()
        asset = Asset(id="P-101", name="CW Pump", equipment_tag="P-101", asset_type="Pump")
        builder.add_asset(asset)
        graph = builder.build()
        assert builder.node_count == 1
        assert graph.nodes[0].id == "P-101"
        assert graph.nodes[0].type == "asset"

    def test_add_asset_with_system_creates_edge(self):
        from app.domain.industrial.asset import Asset, System
        builder = self._make_builder()
        builder.add_system(System(id="CWS-01", name="Cooling Water System"))
        builder.add_asset(Asset(id="P-101", name="CW Pump", equipment_tag="P-101", asset_type="Pump", system_id="CWS-01"))
        graph = builder.build()
        assert builder.node_count == 2
        assert builder.edge_count == 1
        assert graph.edges[0].relationship == "CONTAINS"

    def test_full_demo_graph(self):
        """Build the P-101 demo scenario graph."""
        from app.domain.industrial.asset import Asset, System, Component, Plant
        from app.domain.industrial.document import InspectionReport, MaintenanceWorkOrder
        from app.domain.industrial.failure import FailureEvent, FailureMode, FailureCause, FailureSeverity
        from app.domain.industrial.maintenance import Recommendation, RecommendationStatus, MaintenancePriority

        builder = self._make_builder()

        # Build hierarchy
        builder.add_plant(Plant(id="PLT-01", name="Main Plant"))
        builder.add_system(System(id="CWS-01", name="Cooling Water System", plant_id="PLT-01"))
        builder.add_asset(Asset(id="P-101", name="CW Pump", equipment_tag="P-101", asset_type="Centrifugal Pump", system_id="CWS-01"))
        builder.add_component(Component(id="B-101", name="Drive-End Bearing", component_type="Bearing", asset_id="P-101"))

        # Add inspection reports
        builder.add_inspection_report(InspectionReport(
            report_id="IR-104",
            document_id="DOC-003",
            asset_id="P-101",
            inspector="John Smith",
            findings=("High vibration on drive-end bearing",),
            recommendations=("Replace bearing within 30 days",),
            severity="HIGH",
        ))

        # Add failure
        builder.add_failure_mode(FailureMode(id="FM-001", name="Bearing Seizure", category="Mechanical"))
        builder.add_failure_cause(FailureCause(id="FC-001", name="Lubrication Degradation", category="Wear"))
        builder.add_failure_event(FailureEvent(
            id="F-17",
            asset_id="P-101",
            severity=FailureSeverity.MAJOR,
            failure_mode_id="FM-001",
            failure_cause_id="FC-001",
        ))

        # Add recommendation
        builder.add_recommendation(Recommendation(
            id="REC-001",
            asset_id="P-101",
            description="Replace drive-end bearing",
            priority=MaintenancePriority.URGENT,
            status=RecommendationStatus.DEFERRED,
        ))

        graph = builder.build()

        # Verify graph structure
        assert builder.node_count >= 8  # plant, system, asset, component, inspection, failure_mode, failure_cause, failure_event, recommendation, person
        assert builder.edge_count >= 6  # hierarchy + inspection + failure + recommendation edges

        # Verify node types
        node_types = {n.type for n in graph.nodes}
        assert "plant" in node_types
        assert "system" in node_types
        assert "asset" in node_types
        assert "component" in node_types
        assert "failure_event" in node_types
        assert "failure_mode" in node_types

        # Verify edges
        edge_types = {e.relationship for e in graph.edges}
        assert "CONTAINS" in edge_types
        assert "EXPERIENCED" in edge_types
        assert "FAILED_WITH" in edge_types
        assert "CAUSED_BY" in edge_types


# ---------------------------------------------------------------------------
# Test: Observation Domain Extensions
# ---------------------------------------------------------------------------

class TestObservationExtensions:
    def test_observation_type_has_industrial(self):
        from app.ingestion.observation.domain import ObservationType
        assert ObservationType.MAINTENANCE.value == "maintenance"
        assert ObservationType.FAILURE.value == "failure"
        assert ObservationType.INSPECTION_EVENT.value == "inspection_event"

    def test_observation_category_has_industrial(self):
        from app.ingestion.observation.domain import ObservationCategory
        assert ObservationCategory.MAINTENANCE.value == "maintenance"
        assert ObservationCategory.OPERATIONS.value == "operations"
        assert ObservationCategory.COMPLIANCE.value == "compliance"

    def test_maintenance_action_facts(self):
        from app.ingestion.observation.domain import MaintenanceActionFacts
        facts = MaintenanceActionFacts(
            work_order_id="WO-291",
            asset_id="P-101",
            equipment_tag="P-101",
            action_type="corrective",
            status="COMPLETED",
        )
        assert facts.work_order_id == "WO-291"

    def test_inspection_facts(self):
        from app.ingestion.observation.domain import InspectionFacts
        facts = InspectionFacts(
            inspection_id="IR-104",
            asset_id="P-101",
            findings=("High vibration",),
        )
        assert len(facts.findings) == 1

    def test_failure_event_facts(self):
        from app.ingestion.observation.domain import FailureEventFacts
        facts = FailureEventFacts(
            failure_id="F-17",
            asset_id="P-101",
            failure_mode="Bearing Seizure",
            downtime_hours=48.0,
        )
        assert facts.downtime_hours == 48.0

    def test_original_facts_preserved(self):
        """Original software CanonicalFacts must still work."""
        from app.ingestion.observation.domain import CommitFacts
        facts = CommitFacts(
            commit_id="abc123",
            message="Fix bug",
            author_name="dev",
            author_email="dev@example.com",
            authored_at=datetime.datetime(2024, 1, 1),
        )
        assert facts.commit_id == "abc123"
