"""Industrial Knowledge Graph Builder.

Constructs the industrial knowledge graph from industrial
domain models. Creates nodes and edges with full provenance,
building a connected graph of assets, documents, people,
failures, maintenance, and their relationships.
"""
from __future__ import annotations

import datetime
from typing import Any

from app.domain.industrial.asset import Asset, Component, System, Plant
from app.domain.industrial.document import (
    Document,
    InspectionReport,
    MaintenanceWorkOrder,
    IncidentReport,
)
from app.domain.industrial.failure import FailureEvent, FailureMode, FailureCause
from app.domain.industrial.maintenance import (
    MaintenanceAction,
    Inspection,
    Recommendation,
)
from app.domain.industrial.personnel import Person, AssetExpertise
from app.domain.industrial.compliance import Regulation, RegulatoryRequirement, ComplianceGap
from app.domain.industrial.relationships import (
    IndustrialNodeType,
    IndustrialRelationship,
)
from app.knowledge.graph.graph_edge import GraphEdge, EdgeProvenance, EdgeConfidence
from app.knowledge.graph.graph_node import GraphNode
from app.knowledge.graph.organizational_graph import OrganizationalGraph
from app.knowledge.graph.builders.graph_builder import GraphBuilder


class IndustrialGraphBuilder(GraphBuilder):
    """Builds an industrial knowledge graph from domain models.

    Incrementally adds nodes and edges as documents are processed.
    All edges carry provenance linking back to source documents.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []

    def build(self, **kwargs: Any) -> OrganizationalGraph:
        """Return the current graph as an OrganizationalGraph."""
        return OrganizationalGraph(
            nodes=list(self._nodes.values()),
            edges=list(self._edges),
        )

    # ------------------------------------------------------------------
    # Node creation
    # ------------------------------------------------------------------

    def _ensure_node(
        self,
        node_id: str,
        node_type: str,
        attributes: dict[str, Any] | None = None,
    ) -> GraphNode:
        """Add a node if it doesn't exist; return it."""
        if node_id not in self._nodes:
            self._nodes[node_id] = GraphNode(
                id=node_id,
                type=node_type,
                attributes=attributes or {},
            )
        elif attributes:
            existing = dict(self._nodes[node_id].attributes)
            for key, value in attributes.items():
                if value not in (None, "", "Unknown"):
                    existing[key] = value
                elif key not in existing:
                    existing[key] = value
            self._nodes[node_id] = GraphNode(
                id=node_id,
                type=node_type,
                attributes=existing,
            )
        return self._nodes[node_id]

    def _add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship: str,
        evidence_id: str | None = None,
        confidence: float = 1.0,
        algorithm: str = "industrial_graph_builder",
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Add a directed edge with provenance."""
        self._edges.append(GraphEdge(
            source_id=source_id,
            target_id=target_id,
            relationship=relationship,
            confidence=EdgeConfidence(
                evidence_confidence=confidence,
                identity_confidence=1.0,
                extraction_confidence=confidence,
                relationship_confidence=1.0,
            ),
            provenance=EdgeProvenance(
                evidence_id=evidence_id,
                algorithm=algorithm,
                created_by="industrial_graph_builder",
            ),
            properties=properties or {},
        ))

    # ------------------------------------------------------------------
    # Asset hierarchy
    # ------------------------------------------------------------------

    def add_plant(self, plant: Plant) -> None:
        self._ensure_node(
            plant.id, IndustrialNodeType.PLANT.value,
            {"name": plant.name, "location": plant.location},
        )

    def add_system(self, system: System) -> None:
        self._ensure_node(
            system.id, IndustrialNodeType.SYSTEM.value,
            {"name": system.name, "system_type": system.system_type},
        )
        if system.plant_id:
            self._add_edge(
                system.plant_id, system.id,
                IndustrialRelationship.CONTAINS.value,
            )

    def add_asset(self, asset: Asset) -> None:
        self._ensure_node(
            asset.id, IndustrialNodeType.ASSET.value,
            {
                "name": asset.name,
                "equipment_tag": asset.equipment_tag,
                "asset_type": asset.asset_type,
                "manufacturer": asset.manufacturer,
                "model": asset.model,
                "status": asset.status.value if hasattr(asset.status, 'value') else str(asset.status),
                "criticality": asset.criticality.value if hasattr(asset.criticality, 'value') else str(asset.criticality),
                "risk_level": asset.risk_level.value if hasattr(asset.risk_level, 'value') else str(asset.risk_level),
            },
        )
        if asset.system_id:
            self._add_edge(
                asset.system_id, asset.id,
                IndustrialRelationship.CONTAINS.value,
            )

    def add_component(self, component: Component) -> None:
        self._ensure_node(
            component.id, IndustrialNodeType.COMPONENT.value,
            {"name": component.name, "component_type": component.component_type},
        )
        self._add_edge(
            component.asset_id, component.id,
            IndustrialRelationship.CONTAINS.value,
        )

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    def add_document(self, document: Document) -> None:
        node_type = IndustrialNodeType.DOCUMENT.value
        self._ensure_node(
            document.document_id, node_type,
            {
                "name": document.name,
                "document_type": document.document_type.value if hasattr(document.document_type, 'value') else str(document.document_type),
                "format": document.document_format.value if hasattr(document.document_format, 'value') else str(document.document_format),
            },
        )

    def add_inspection_report(
        self,
        report: InspectionReport,
        document_id: str | None = None,
    ) -> None:
        self._ensure_node(
            report.report_id, IndustrialNodeType.INSPECTION_REPORT.value,
            {
                "inspection_type": report.inspection_type,
                "inspection_date": str(report.inspection_date) if report.inspection_date else None,
                "severity": report.severity,
                "findings": list(report.findings),
                "recommendations": list(report.recommendations),
            },
        )
        if report.asset_id:
            self._add_edge(
                report.report_id, report.asset_id,
                IndustrialRelationship.INSPECTED.value,
                evidence_id=report.report_id,
            )
        if report.inspector:
            person_id = f"person:{report.inspector}"
            self._ensure_node(person_id, IndustrialNodeType.PERSON.value, {"name": report.inspector})
            self._add_edge(
                report.report_id, person_id,
                IndustrialRelationship.INSPECTED_BY.value,
            )
        doc_id = document_id or report.document_id
        if doc_id:
            self._add_edge(
                doc_id, report.report_id,
                IndustrialRelationship.DOCUMENTS.value,
            )

    def add_work_order(
        self,
        wo: MaintenanceWorkOrder,
        document_id: str | None = None,
    ) -> None:
        self._ensure_node(
            wo.work_order_id, IndustrialNodeType.WORK_ORDER.value,
            {
                "title": wo.title,
                "work_type": wo.work_type,
                "priority": wo.priority,
                "status": wo.status,
            },
        )
        if wo.asset_id:
            self._add_edge(
                wo.work_order_id, wo.asset_id,
                IndustrialRelationship.APPLIES_TO.value,
                evidence_id=wo.work_order_id,
            )
        doc_id = document_id or wo.document_id
        if doc_id:
            self._add_edge(
                doc_id, wo.work_order_id,
                IndustrialRelationship.DOCUMENTS.value,
            )

    def add_incident_report(
        self,
        incident: IncidentReport,
        document_id: str | None = None,
    ) -> None:
        self._ensure_node(
            incident.incident_id, IndustrialNodeType.INCIDENT_REPORT.value,
            {
                "title": incident.title,
                "severity": incident.severity,
                "incident_date": str(incident.incident_date) if incident.incident_date else None,
                "downtime_hours": incident.downtime_hours,
                "safety_impact": incident.safety_impact,
            },
        )
        if incident.asset_id:
            self._add_edge(
                incident.incident_id, incident.asset_id,
                IndustrialRelationship.APPLIES_TO.value,
                evidence_id=incident.incident_id,
            )

    # ------------------------------------------------------------------
    # Failures
    # ------------------------------------------------------------------

    def add_failure_event(self, failure: FailureEvent) -> None:
        self._ensure_node(
            failure.id, IndustrialNodeType.FAILURE_EVENT.value,
            {
                "description": failure.description,
                "severity": failure.severity.value if hasattr(failure.severity, 'value') else str(failure.severity),
                "failure_date": str(failure.failure_date) if failure.failure_date else None,
                "downtime_hours": failure.downtime_hours,
            },
        )
        self._add_edge(
            failure.asset_id, failure.id,
            IndustrialRelationship.EXPERIENCED.value,
            evidence_id=failure.source_document_id,
        )
        if failure.failure_mode_id:
            self._add_edge(
                failure.id, failure.failure_mode_id,
                IndustrialRelationship.FAILED_WITH.value,
            )
        if failure.failure_cause_id:
            self._add_edge(
                failure.id, failure.failure_cause_id,
                IndustrialRelationship.CAUSED_BY.value,
            )

    def add_failure_mode(self, mode: FailureMode) -> None:
        self._ensure_node(
            mode.id, IndustrialNodeType.FAILURE_MODE.value,
            {"name": mode.name, "category": mode.category},
        )

    def add_failure_cause(self, cause: FailureCause) -> None:
        self._ensure_node(
            cause.id, IndustrialNodeType.FAILURE_CAUSE.value,
            {"name": cause.name, "category": cause.category},
        )
        if cause.parent_cause_id:
            self._add_edge(
                cause.id, cause.parent_cause_id,
                IndustrialRelationship.CAUSED_BY.value,
            )

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def add_recommendation(self, rec: Recommendation) -> None:
        self._ensure_node(
            rec.id, IndustrialNodeType.RECOMMENDATION.value,
            {
                "description": rec.description,
                "action_required": rec.action_required,
                "status": rec.status.value if hasattr(rec.status, 'value') else str(rec.status),
                "priority": rec.priority.value if hasattr(rec.priority, 'value') else str(rec.priority),
            },
        )
        if rec.asset_id:
            self._add_edge(
                rec.id, rec.asset_id,
                IndustrialRelationship.RECOMMENDED_ACTION.value,
                evidence_id=rec.source_document_id,
            )

    # ------------------------------------------------------------------
    # Personnel
    # ------------------------------------------------------------------

    def add_person(self, person: Person) -> None:
        self._ensure_node(
            person.id, IndustrialNodeType.PERSON.value,
            {
                "name": person.name,
                "role": person.role.value if hasattr(person.role, 'value') else str(person.role),
                "department": person.department,
            },
        )

    def add_asset_expertise(self, expertise: AssetExpertise) -> None:
        self._add_edge(
            expertise.asset_id, expertise.person_id,
            IndustrialRelationship.HAS_EXPERT.value,
            confidence=expertise.confidence,
            properties={"expertise_score": expertise.expertise_score},
        )

    # ------------------------------------------------------------------
    # Compliance
    # ------------------------------------------------------------------

    def add_regulation(self, regulation: Regulation) -> None:
        self._ensure_node(
            regulation.id, IndustrialNodeType.REGULATION.value,
            {"name": regulation.name, "issuing_body": regulation.issuing_body},
        )

    def add_compliance_gap(self, gap: ComplianceGap) -> None:
        self._ensure_node(
            gap.id, IndustrialNodeType.COMPLIANCE_GAP.value,
            {
                "status": gap.status.value if hasattr(gap.status, 'value') else str(gap.status),
                "description": gap.description,
                "days_overdue": gap.days_overdue,
            },
        )
        if gap.asset_id:
            self._add_edge(
                gap.id, gap.asset_id,
                IndustrialRelationship.APPLIES_TO.value,
            )

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def link_document_to_asset(
        self,
        document_id: str,
        asset_id: str,
        relationship: str = IndustrialRelationship.DOCUMENTS.value,
    ) -> None:
        """Explicitly link a document to an asset."""
        self._add_edge(document_id, asset_id, relationship)

    def link_temporal_sequence(
        self,
        earlier_id: str,
        later_id: str,
    ) -> None:
        """Link two events in temporal sequence."""
        self._add_edge(
            earlier_id, later_id,
            IndustrialRelationship.PRECEDED_BY.value,
        )
        self._add_edge(
            later_id, earlier_id,
            IndustrialRelationship.FOLLOWED_BY.value,
        )

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._edges)
