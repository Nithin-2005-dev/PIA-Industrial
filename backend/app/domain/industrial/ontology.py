"""Industrial Ontology Registry.

Centralizes the complete industrial ontology — entity types,
relationship types, validation rules, and the industrial
graph schema. This is the single source of truth for
what entities and relationships PIA Industrial understands.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.domain.industrial.relationships import (
    CertaintyLevel,
    IndustrialNodeType,
    IndustrialRelationship,
)
from app.knowledge.graph.schema import (
    EdgeTypeDefinition,
    GraphSchema,
    NodeTypeDefinition,
    ValidationRule,
    ValidationSeverity,
)


# ---------------------------------------------------------------------------
# Industrial Graph Schema
# ---------------------------------------------------------------------------


def build_industrial_schema() -> GraphSchema:
    """Build the complete industrial graph schema.

    This extends the default PIA schema with industrial
    node types, edge types, and validation rules.
    """
    schema = GraphSchema(version="industrial-v1")

    # --- Register Node Types ---

    # Physical hierarchy
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.PLANT.value, "A physical plant or site",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.FACILITY.value, "A facility within a plant",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.AREA.value, "A physical area within a facility",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.SYSTEM.value, "A functional system",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.SUBSYSTEM.value, "A subsystem within a system",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.ASSET.value, "A physical asset or equipment",
        required_attributes={"equipment_tag", "asset_type"},
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.COMPONENT.value, "A component within an asset",
    ))

    # Personnel
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.PERSON.value, "An industrial personnel",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.TEAM.value, "An operational or maintenance team",
    ))

    # Documents
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.DOCUMENT.value, "An industrial document",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.INSPECTION_REPORT.value, "An inspection report",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.WORK_ORDER.value, "A maintenance work order",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.INCIDENT_REPORT.value, "An incident report",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.OEM_MANUAL.value, "An OEM equipment manual",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.PROCEDURE.value, "An operating or maintenance procedure",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.REGULATION.value, "A regulation or standard",
    ))

    # Operational
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.FAILURE_EVENT.value, "A failure event",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.FAILURE_MODE.value, "A failure mode (how something fails)",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.FAILURE_CAUSE.value, "A failure cause (why something fails)",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.MAINTENANCE_ACTION.value, "A maintenance action performed",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.INSPECTION.value, "An inspection performed",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.RECOMMENDATION.value, "A maintenance recommendation",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.OPERATING_PARAMETER.value, "An operating parameter reading",
    ))

    # Intelligence
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.FAILURE_PATTERN.value, "A detected failure pattern",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.COMPLIANCE_GAP.value, "A compliance gap",
    ))
    schema.register_node_type(NodeTypeDefinition(
        IndustrialNodeType.MANUFACTURER.value, "An equipment manufacturer",
    ))

    # --- Register Edge Types ---

    # Structural
    _structural_sources = {
        IndustrialNodeType.PLANT.value,
        IndustrialNodeType.FACILITY.value,
        IndustrialNodeType.AREA.value,
        IndustrialNodeType.SYSTEM.value,
        IndustrialNodeType.SUBSYSTEM.value,
        IndustrialNodeType.ASSET.value,
    }
    _structural_targets = _structural_sources | {IndustrialNodeType.COMPONENT.value}

    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.CONTAINS.value,
        "Parent contains child in hierarchy",
        _structural_sources, _structural_targets,
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.PART_OF.value,
        "Child is part of parent in hierarchy",
        _structural_targets, _structural_sources,
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.LOCATED_IN.value,
        "Entity is located in a physical area",
    ))

    # Documentation
    _doc_types = {
        IndustrialNodeType.DOCUMENT.value,
        IndustrialNodeType.INSPECTION_REPORT.value,
        IndustrialNodeType.WORK_ORDER.value,
        IndustrialNodeType.INCIDENT_REPORT.value,
        IndustrialNodeType.OEM_MANUAL.value,
        IndustrialNodeType.PROCEDURE.value,
        IndustrialNodeType.REGULATION.value,
    }
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.DOCUMENTS.value,
        "Document documents an entity",
        _doc_types,
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.MENTIONS.value,
        "Document mentions an entity",
        _doc_types,
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.APPLIES_TO.value,
        "Regulation or procedure applies to an entity",
    ))

    # Personnel
    _person_types = {
        IndustrialNodeType.PERSON.value,
        IndustrialNodeType.TEAM.value,
    }
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.INSPECTED_BY.value,
        "Asset inspected by person",
        {IndustrialNodeType.ASSET.value}, _person_types,
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.MAINTAINED_BY.value,
        "Asset maintained by person",
        {IndustrialNodeType.ASSET.value}, _person_types,
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.HAS_EXPERT.value,
        "Asset has expert person",
        {IndustrialNodeType.ASSET.value, IndustrialNodeType.SYSTEM.value}, _person_types,
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.RESPONSIBLE_FOR.value,
        "Person is responsible for asset",
        _person_types, {IndustrialNodeType.ASSET.value, IndustrialNodeType.SYSTEM.value},
    ))

    # Failure / Causal
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.EXPERIENCED.value,
        "Asset experienced a failure event",
        {IndustrialNodeType.ASSET.value}, {IndustrialNodeType.FAILURE_EVENT.value},
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.FAILED_WITH.value,
        "Failure event involved a failure mode",
        {IndustrialNodeType.FAILURE_EVENT.value}, {IndustrialNodeType.FAILURE_MODE.value},
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.CAUSED_BY.value,
        "Failure mode or event caused by a failure cause",
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.PRECEDED_BY.value,
        "Event preceded by another event",
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.FOLLOWED_BY.value,
        "Event followed by another event",
    ))

    # Maintenance
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.RECOMMENDED_ACTION.value,
        "Recommendation for a maintenance action",
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.RESOLVED_BY.value,
        "Issue resolved by a maintenance action",
    ))

    # Compliance
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.REQUIRES.value,
        "Regulation requires an action",
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.SATISFIES.value,
        "Evidence satisfies a requirement",
    ))

    # Evidence
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.EVIDENCE_FOR.value,
        "Evidence supports a conclusion",
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.FOUND.value,
        "Inspection found a condition",
    ))

    # Similarity
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.SIMILAR_TO.value,
        "Entity is similar to another entity",
    ))
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.SAME_FAILURE_MODE.value,
        "Assets share the same failure mode",
    ))

    # Manufacturer
    schema.register_edge_type(EdgeTypeDefinition(
        IndustrialRelationship.MANUFACTURED_BY.value,
        "Asset manufactured by manufacturer",
        {IndustrialNodeType.ASSET.value}, {IndustrialNodeType.MANUFACTURER.value},
    ))

    # --- Validation Rules ---
    schema.add_validation_rule(ValidationRule(
        "orphan_asset", "Asset not connected to any system", ValidationSeverity.WARNING,
    ))
    schema.add_validation_rule(ValidationRule(
        "missing_document_link", "Document not linked to any asset", ValidationSeverity.WARNING,
    ))
    schema.add_validation_rule(ValidationRule(
        "unresolved_equipment_tag", "Equipment tag not resolved to asset", ValidationSeverity.ERROR,
    ))
    schema.add_validation_rule(ValidationRule(
        "failure_without_cause", "Failure event has no linked cause", ValidationSeverity.WARNING,
    ))
    schema.add_validation_rule(ValidationRule(
        "recommendation_without_asset", "Recommendation not linked to asset", ValidationSeverity.WARNING,
    ))

    return schema


# Singleton instance
INDUSTRIAL_SCHEMA = build_industrial_schema()
