"""Industrial Knowledge Graph Manager.

Bridges the Entity Extraction Pipeline and the Graph Builder.
Takes ResolvedEntities and populates the Knowledge Graph.
Also provides graph queries for industrial intelligence
(e.g., asset neighborhood, failure timelines).
"""
from __future__ import annotations

import logging
from typing import Any

from app.domain.industrial.asset import Asset
from app.domain.industrial.document import (
    IncidentReport,
    InspectionReport,
    MaintenanceWorkOrder,
)
from app.domain.industrial.failure import FailureCause, FailureMode
from app.domain.industrial.relationships import IndustrialRelationship
from app.extraction.entities.entity_resolver import ResolvedEntity
from app.knowledge.graph.builders.industrial_graph_builder import IndustrialGraphBuilder
from app.knowledge.graph.organizational_graph import OrganizationalGraph

logger = logging.getLogger(__name__)


class IndustrialGraphManager:
    """Populates and queries the industrial knowledge graph."""

    def __init__(self, builder: IndustrialGraphBuilder | None = None) -> None:
        self._builder = builder or IndustrialGraphBuilder()

    @property
    def builder(self) -> IndustrialGraphBuilder:
        return self._builder

    def build_graph(self) -> OrganizationalGraph:
        """Return the constructed OrganizationalGraph."""
        return self._builder.build()

    # ------------------------------------------------------------------
    # Graph Population
    # ------------------------------------------------------------------

    def populate_from_entities(
        self,
        entities: tuple[ResolvedEntity, ...],
        document_id: str,
    ) -> None:
        """Populate the graph from extracted entities.

        Creates nodes and links them to the source document.
        """
        for entity in entities:
            if entity.entity_type == "equipment_tag":
                self._add_equipment_tag(entity, document_id)
            elif entity.entity_type == "work_order_id":
                self._add_work_order(entity, document_id)
            elif entity.entity_type == "inspection_report_id":
                self._add_inspection_report(entity, document_id)
            elif entity.entity_type == "incident_report_id":
                self._add_incident_report(entity, document_id)
            elif entity.entity_type == "failure_mode":
                self._add_failure_mode(entity, document_id)
            elif entity.entity_type == "failure_cause":
                self._add_failure_cause(entity, document_id)
            # Add other entity types as needed

    def _add_equipment_tag(self, entity: ResolvedEntity, document_id: str) -> None:
        asset_id = entity.canonical_value
        # Add basic asset node (will be enriched if structured data is available later)
        asset = Asset(
            id=asset_id,
            name=asset_id,
            equipment_tag=asset_id,
            asset_type="Unknown",  # To be filled by dict extraction later
        )
        self._builder.add_asset(asset)
        self._builder.link_document_to_asset(document_id, asset_id)

    def _add_work_order(self, entity: ResolvedEntity, document_id: str) -> None:
        wo_id = entity.canonical_value
        wo = MaintenanceWorkOrder(
            work_order_id=wo_id,
            title=f"Work Order {wo_id}",
        )
        self._builder.add_work_order(wo, document_id=document_id)

    def _add_inspection_report(self, entity: ResolvedEntity, document_id: str) -> None:
        ir_id = entity.canonical_value
        ir = InspectionReport(
            report_id=ir_id,
            document_id=ir_id,
        )
        self._builder.add_inspection_report(ir, document_id=document_id)

    def _add_incident_report(self, entity: ResolvedEntity, document_id: str) -> None:
        in_id = entity.canonical_value
        incident = IncidentReport(
            incident_id=in_id,
        )
        self._builder.add_incident_report(incident, document_id=document_id)

    def _add_failure_mode(self, entity: ResolvedEntity, document_id: str) -> None:
        fm_id = f"fm_{entity.canonical_value}"
        fm = FailureMode(
            id=fm_id,
            name=entity.canonical_value.replace("_", " ").title(),
        )
        self._builder.add_failure_mode(fm)
        # Link document to failure mode
        self._builder._add_edge(document_id, fm_id, IndustrialRelationship.MENTIONS.value)

    def _add_failure_cause(self, entity: ResolvedEntity, document_id: str) -> None:
        fc_id = f"fc_{entity.canonical_value}"
        fc = FailureCause(
            id=fc_id,
            name=entity.canonical_value.replace("_", " ").title(),
        )
        self._builder.add_failure_cause(fc)
        self._builder._add_edge(document_id, fc_id, IndustrialRelationship.MENTIONS.value)

    # ------------------------------------------------------------------
    # Graph Queries
    # ------------------------------------------------------------------

    def get_asset_neighborhood(self, asset_id: str) -> dict[str, Any]:
        """Get the neighborhood of an asset.

        Returns all documents, work orders, inspections, and failures
        linked to this asset.
        """
        graph = self.build_graph()
        neighborhood: dict[str, list[dict[str, Any]]] = {
            "documents": [],
            "inspections": [],
            "work_orders": [],
            "incidents": [],
            "failures": [],
            "components": [],
        }

        # Find edges connected to the asset
        for edge in graph.edges:
            target = None
            if edge.source_id == asset_id:
                target = edge.target_id
            elif edge.target_id == asset_id:
                target = edge.source_id

            if not target:
                continue

            # Find the target node
            node = next((n for n in graph.nodes if n.id == target), None)
            if not node:
                continue

            # Categorize by node type
            item = {"id": node.id, "type": node.type, "relationship": edge.relationship}
            
            if node.type == "document":
                neighborhood["documents"].append(item)
            elif node.type == "inspection_report":
                neighborhood["inspections"].append(item)
            elif node.type == "work_order":
                neighborhood["work_orders"].append(item)
            elif node.type == "incident_report":
                neighborhood["incidents"].append(item)
            elif node.type == "failure_event":
                neighborhood["failures"].append(item)
            elif node.type == "component":
                neighborhood["components"].append(item)

        return neighborhood

    def get_failure_chain(self, event_id: str) -> dict[str, Any]:
        """Get the causal chain for a failure event."""
        graph = self.build_graph()
        chain: dict[str, Any] = {
            "event_id": event_id,
            "failure_mode": None,
            "failure_cause": None,
            "asset_id": None,
            "resolutions": [],
        }

        for edge in graph.edges:
            if edge.source_id == event_id:
                if edge.relationship == IndustrialRelationship.FAILED_WITH.value:
                    chain["failure_mode"] = edge.target_id
                elif edge.relationship == IndustrialRelationship.CAUSED_BY.value:
                    chain["failure_cause"] = edge.target_id
            elif edge.target_id == event_id:
                if edge.relationship == IndustrialRelationship.EXPERIENCED.value:
                    chain["asset_id"] = edge.source_id
                elif edge.relationship == IndustrialRelationship.RESOLVED_BY.value:
                    chain["resolutions"].append(edge.source_id)

        return chain
