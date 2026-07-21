from typing import Dict, Any
from app.infrastructure.database.models import KnowledgeGraphProjectionRecord

class KnowledgeGraphDiff:
    def __init__(self, v1: KnowledgeGraphProjectionRecord, v2: KnowledgeGraphProjectionRecord):
        self.v1 = v1
        self.v2 = v2

    def compute(self) -> Dict[str, Any]:
        report = {
            "structural_changes": {},
            "semantic_changes": {},
            "statistical_changes": {},
            "validation_changes": {}
        }
        
        # Structural Changes (Nodes & Edges)
        v1_nodes = {n["id"]: n for n in self.v1.nodes}
        v2_nodes = {n["id"]: n for n in self.v2.nodes}
        
        nodes_added = set(v2_nodes.keys()) - set(v1_nodes.keys())
        nodes_removed = set(v1_nodes.keys()) - set(v2_nodes.keys())
        
        v1_edges = {f'{e["source"]}-{e["target"]}-{e["type"]}': e for e in self.v1.edges}
        v2_edges = {f'{e["source"]}-{e["target"]}-{e["type"]}': e for e in self.v2.edges}
        
        edges_added = set(v2_edges.keys()) - set(v1_edges.keys())
        edges_removed = set(v1_edges.keys()) - set(v2_edges.keys())
        
        report["structural_changes"] = {
            "nodes_added": list(nodes_added),
            "nodes_removed": list(nodes_removed),
            "edges_added": list(edges_added),
            "edges_removed": list(edges_removed),
        }
        
        # Semantic Changes
        semantic_changes = {
            "node_property_changes": [],
            "edge_confidence_changes": [],
        }
        
        common_nodes = set(v1_nodes.keys()).intersection(set(v2_nodes.keys()))
        for n_id in common_nodes:
            attrs1 = v1_nodes[n_id].get("attributes", {})
            attrs2 = v2_nodes[n_id].get("attributes", {})
            if attrs1 != attrs2:
                semantic_changes["node_property_changes"].append({
                    "id": n_id,
                    "from": attrs1,
                    "to": attrs2
                })
                
        common_edges = set(v1_edges.keys()).intersection(set(v2_edges.keys()))
        for e_id in common_edges:
            conf1 = v1_edges[e_id].get("confidence")
            conf2 = v2_edges[e_id].get("confidence")
            if conf1 != conf2:
                semantic_changes["edge_confidence_changes"].append({
                    "edge": e_id,
                    "from_confidence": conf1,
                    "to_confidence": conf2
                })
                
        report["semantic_changes"] = semantic_changes
        
        # Statistical & Validation Changes
        report["statistical_changes"] = {
            "v1_node_count": self.v1.node_count,
            "v2_node_count": self.v2.node_count,
            "v1_edge_count": self.v1.edge_count,
            "v2_edge_count": self.v2.edge_count
        }
        
        report["validation_changes"] = {
            "v1_validation": self.v1.validation_report.get("overall_score"),
            "v2_validation": self.v2.validation_report.get("overall_score")
        }
        
        return report
