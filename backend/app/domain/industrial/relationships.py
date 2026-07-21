"""Industrial relationship types.

Defines the canonical relationship types for the industrial
knowledge graph. These extend the existing graph schema
without modifying it.
"""
from __future__ import annotations

from enum import Enum


class IndustrialRelationship(str, Enum):
    """Relationship types for the industrial knowledge graph.

    These are used as `GraphEdge.relationship` values.
    They supplement the existing software-domain relationships.
    """

    # --- Structural ---
    CONTAINS = "CONTAINS"
    PART_OF = "PART_OF"
    LOCATED_IN = "LOCATED_IN"
    CONNECTED_TO = "CONNECTED_TO"
    DEPENDS_ON = "DEPENDS_ON"

    # --- Documentation ---
    DOCUMENTS = "DOCUMENTS"
    MENTIONS = "MENTIONS"
    APPLIES_TO = "APPLIES_TO"
    REFERENCES = "REFERENCES"

    # --- Personnel ---
    INSPECTED_BY = "INSPECTED_BY"
    MAINTAINED_BY = "MAINTAINED_BY"
    OPERATED_BY = "OPERATED_BY"
    HAS_EXPERT = "HAS_EXPERT"
    RESPONSIBLE_FOR = "RESPONSIBLE_FOR"
    AUTHORED_BY = "AUTHORED_BY"
    REPORTED_BY = "REPORTED_BY"

    # --- Lifecycle ---
    MANUFACTURED_BY = "MANUFACTURED_BY"
    COMMISSIONED = "COMMISSIONED"
    DECOMMISSIONED = "DECOMMISSIONED"

    # --- Failure / Causal ---
    EXPERIENCED = "EXPERIENCED"
    FAILED_WITH = "FAILED_WITH"
    CAUSED_BY = "CAUSED_BY"
    PRECEDED_BY = "PRECEDED_BY"
    FOLLOWED_BY = "FOLLOWED_BY"
    CONTRIBUTED_TO = "CONTRIBUTED_TO"

    # --- Maintenance ---
    RECOMMENDED_ACTION = "RECOMMENDED_ACTION"
    RESOLVED_BY = "RESOLVED_BY"
    DEFERRED = "DEFERRED"
    REPLACED = "REPLACED"
    REPAIRED = "REPAIRED"

    # --- Compliance ---
    REQUIRES = "REQUIRES"
    VIOLATES = "VIOLATES"
    SATISFIES = "SATISFIES"

    # --- Evidence ---
    EVIDENCE_FOR = "EVIDENCE_FOR"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"

    # --- Similarity ---
    SIMILAR_TO = "SIMILAR_TO"
    SAME_FAILURE_MODE = "SAME_FAILURE_MODE"
    SAME_SYSTEM = "SAME_SYSTEM"

    # --- Inspection ---
    INSPECTED = "INSPECTED"
    FOUND = "FOUND"
    MEASURED = "MEASURED"


class IndustrialNodeType(str, Enum):
    """Node types for the industrial knowledge graph.

    These supplement the existing software node types
    (developer, module, evidence, measurement, expertise, knowledge).
    """

    # --- Physical Assets ---
    PLANT = "plant"
    FACILITY = "facility"
    AREA = "area"
    SYSTEM = "system"
    SUBSYSTEM = "subsystem"
    ASSET = "asset"
    EQUIPMENT = "equipment"
    COMPONENT = "component"
    EQUIPMENT_TAG = "equipment_tag"

    # --- Personnel ---
    PERSON = "person"
    ENGINEER = "engineer"
    TECHNICIAN = "technician"
    OPERATOR = "operator"
    TEAM = "team"

    # --- Documents ---
    DOCUMENT = "document"
    INSPECTION_REPORT = "inspection_report"
    WORK_ORDER = "work_order"
    INCIDENT_REPORT = "incident_report"
    OEM_MANUAL = "oem_manual"
    PROCEDURE = "procedure"
    SOP = "sop"
    REGULATION = "regulation"

    # --- Operational ---
    FAILURE_EVENT = "failure_event"
    FAILURE_MODE = "failure_mode"
    FAILURE_CAUSE = "failure_cause"
    MAINTENANCE_ACTION = "maintenance_action"
    INSPECTION = "inspection"
    RECOMMENDATION = "recommendation"
    OPERATING_PARAMETER = "operating_parameter"

    # --- Intelligence ---
    RISK = "risk"
    EVIDENCE = "evidence"
    DECISION = "decision"
    INTERVENTION = "intervention"
    COMPLIANCE_GAP = "compliance_gap"
    FAILURE_PATTERN = "failure_pattern"

    # --- Manufacturer ---
    MANUFACTURER = "manufacturer"


class CertaintyLevel(str, Enum):
    """Certainty level for industrial intelligence outputs.

    Every important output must carry a certainty level
    so users understand the reliability of the information.
    """
    FACT = "FACT"                                # Directly observed or measured
    EXTRACTED_INFORMATION = "EXTRACTED_INFORMATION"  # Extracted from documents
    INFERENCE = "INFERENCE"                      # Derived from evidence
    PREDICTION = "PREDICTION"                    # Projected from trends
    CAUSAL_HYPOTHESIS = "CAUSAL_HYPOTHESIS"      # Causal explanation
    RECOMMENDATION = "RECOMMENDATION"            # Suggested action
    SIMULATION = "SIMULATION"                    # Counterfactual result
