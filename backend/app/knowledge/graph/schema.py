from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Type

class ValidationSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

@dataclass(frozen=True)
class ValidationRule:
    id: str
    description: str
    severity: ValidationSeverity

@dataclass(frozen=True)
class EdgeTypeDefinition:
    relationship: str
    description: str
    allowed_sources: Set[str] = field(default_factory=set)
    allowed_targets: Set[str] = field(default_factory=set)

@dataclass(frozen=True)
class NodeTypeDefinition:
    type_name: str
    description: str
    required_attributes: Set[str] = field(default_factory=set)

class GraphSchema:
    """
    Defines the contract and rules for valid Knowledge Graphs.
    Separated from the GraphInstance to allow versioning and validation.
    """
    def __init__(self, version: str = "v1"):
        self.version = version
        self.node_types: Dict[str, NodeTypeDefinition] = {}
        self.edge_types: Dict[str, EdgeTypeDefinition] = {}
        self.validation_rules: List[ValidationRule] = []

    def register_node_type(self, node_type: NodeTypeDefinition):
        self.node_types[node_type.type_name] = node_type

    def register_edge_type(self, edge_type: EdgeTypeDefinition):
        self.edge_types[edge_type.relationship] = edge_type
        
    def add_validation_rule(self, rule: ValidationRule):
        self.validation_rules.append(rule)

# Default Schema Setup
DEFAULT_SCHEMA = GraphSchema(version="v1")

DEFAULT_SCHEMA.register_node_type(NodeTypeDefinition("developer", "A resolved developer identity"))
DEFAULT_SCHEMA.register_node_type(NodeTypeDefinition("module", "A code module or component"))
DEFAULT_SCHEMA.register_node_type(NodeTypeDefinition("evidence", "An evidence item"))
DEFAULT_SCHEMA.register_node_type(NodeTypeDefinition("measurement", "A measurement event"))
DEFAULT_SCHEMA.register_node_type(NodeTypeDefinition("expertise", "An expertise model"))
DEFAULT_SCHEMA.register_node_type(NodeTypeDefinition("knowledge", "A knowledge model"))

DEFAULT_SCHEMA.register_edge_type(EdgeTypeDefinition("OWNS", "Developer owns module", {"developer"}, {"module"}))
DEFAULT_SCHEMA.register_edge_type(EdgeTypeDefinition("CONTRIBUTED_TO", "Developer contributed to module", {"developer"}, {"module"}))
DEFAULT_SCHEMA.register_edge_type(EdgeTypeDefinition("DEPENDS_ON", "Module depends on module", {"module"}, {"module"}))
DEFAULT_SCHEMA.register_edge_type(EdgeTypeDefinition("SUPPORTS_EVIDENCE", "Measurement supports Evidence", {"measurement"}, {"evidence"}))
DEFAULT_SCHEMA.register_edge_type(EdgeTypeDefinition("SUPPORTS_EXPERTISE", "Evidence supports Expertise", {"evidence"}, {"expertise"}))
DEFAULT_SCHEMA.register_edge_type(EdgeTypeDefinition("SUPPORTS_KNOWLEDGE", "Expertise supports Knowledge", {"expertise"}, {"knowledge"}))

DEFAULT_SCHEMA.add_validation_rule(ValidationRule("missing_edges", "Graph contains 0 edges", ValidationSeverity.WARNING))
DEFAULT_SCHEMA.add_validation_rule(ValidationRule("duplicate_nodes", "Graph contains duplicate nodes", ValidationSeverity.ERROR))
DEFAULT_SCHEMA.add_validation_rule(ValidationRule("low_connectivity", "Graph is largely disconnected", ValidationSeverity.WARNING))
DEFAULT_SCHEMA.add_validation_rule(ValidationRule("orphan_ownership", "Ownership edge points to unresolved node", ValidationSeverity.ERROR))
