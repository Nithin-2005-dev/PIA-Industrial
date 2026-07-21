from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Set

from app.knowledge.graph.organizational_graph import OrganizationalGraph
from app.knowledge.graph.schema import GraphSchema, DEFAULT_SCHEMA, ValidationSeverity
from app.knowledge.graph.graph_edge import GraphEdge

@dataclass
class GraphValidationIssue:
    rule_id: str
    message: str
    severity: ValidationSeverity

@dataclass
class GraphContractStatus:
    identity_resolution_rate: float
    relationship_coverage: float
    evidence_completeness: float
    schema_version: str
    is_valid: bool

@dataclass
class GraphBuildReport:
    nodes_created: int
    edges_created: int
    edges_rejected: int
    identity_resolution_rate: float
    evidence_coverage: float
    relationship_coverage: float
    missing_relationships: int
    validation_status: str
    warnings: List[str]

@dataclass
class GraphValidationReport:
    health_score: float
    warnings: List[GraphValidationIssue]
    errors: List[GraphValidationIssue]
    contract: GraphContractStatus
    suggested_fixes: List[str]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

class GraphQualityValidator:
    def __init__(self, schema: GraphSchema = DEFAULT_SCHEMA):
        self.schema = schema

    def validate(self, graph: OrganizationalGraph) -> GraphValidationReport:
        warnings = []
        errors = []
        suggested_fixes = []
        
        nodes_dict = {node.id: node for node in graph.nodes}
        
        if len(graph.edges) == 0:
            warnings.append(
                GraphValidationIssue("missing_edges", "Graph contains 0 edges", ValidationSeverity.WARNING)
            )
            suggested_fixes.append("Ensure EdgeFactory is extracting relationships correctly from evidence")
            
        # Check node uniqueness
        if len(nodes_dict) != len(graph.nodes):
            errors.append(
                GraphValidationIssue("duplicate_nodes", "Graph contains duplicate nodes", ValidationSeverity.ERROR)
            )
            
        # Check orphan edges
        for edge in graph.edges:
            if edge.source_id not in nodes_dict:
                errors.append(
                    GraphValidationIssue("orphan_edge", f"Source {edge.source_id} missing", ValidationSeverity.ERROR)
                )
            if edge.target_id not in nodes_dict:
                errors.append(
                    GraphValidationIssue("orphan_edge", f"Target {edge.target_id} missing", ValidationSeverity.ERROR)
                )

        # Graph Metrics
        identity_nodes = [n for n in graph.nodes if n.type == "developer"]
        resolved_identities = [n for n in identity_nodes if n.attributes and n.attributes.get("resolution_status") == "CANONICAL"]
        
        identity_resolution_rate = len(resolved_identities) / len(identity_nodes) if identity_nodes else 1.0
        
        health_score = 1.0
        if errors:
            health_score -= 0.5
        if warnings:
            health_score -= 0.1 * len(warnings)
            
        health_score = max(0.0, health_score)

        contract = GraphContractStatus(
            identity_resolution_rate=identity_resolution_rate,
            relationship_coverage=len(graph.edges) / len(graph.nodes) if graph.nodes else 0.0,
            evidence_completeness=1.0, # Placeholder
            schema_version=self.schema.version,
            is_valid=len(errors) == 0
        )
        
        return GraphValidationReport(
            health_score=health_score,
            warnings=warnings,
            errors=errors,
            contract=contract,
            suggested_fixes=suggested_fixes
        )
        
    def generate_build_report(self, graph: OrganizationalGraph, report: GraphValidationReport) -> GraphBuildReport:
        return GraphBuildReport(
            nodes_created=len(graph.nodes),
            edges_created=len(graph.edges),
            edges_rejected=0,
            identity_resolution_rate=report.contract.identity_resolution_rate,
            evidence_coverage=report.contract.evidence_completeness,
            relationship_coverage=report.contract.relationship_coverage,
            missing_relationships=0,
            validation_status="VALID" if report.is_valid else "INVALID",
            warnings=[w.message for w in report.warnings]
        )
