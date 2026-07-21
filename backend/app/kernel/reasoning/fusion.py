from typing import Any, Dict, List
import dataclasses
import uuid

from app.kernel.models import CapabilityResult
from app.kernel.graph import GraphNode, NodeType

@dataclasses.dataclass(frozen=True)
class UnifiedEvidenceObject:
    id: str
    source_capabilities: List[str]
    properties: Dict[str, Any]
    confidence: float

class EvidenceFusion:
    """
    Fuses multiple CapabilityResults into unified evidence.
    """
    def __init__(self):
        self._unified_evidence: Dict[str, UnifiedEvidenceObject] = {}

    def fuse(self, results: List[CapabilityResult]) -> List[UnifiedEvidenceObject]:
        """
        Takes raw deterministic capability results and merges them.
        For Phase 2, we do a basic pass-through mapping each result to an Evidence node.
        """
        # Hierarchical Clustering
        # Level 1: Exact Entity
        entity_clusters = {}
        for result in results:
            entity = result.metadata.get("entity", "Repository")
            if entity not in entity_clusters:
                entity_clusters[entity] = []
            entity_clusters[entity].append(result)
            
        # Level 2 & 3: Semantic Entity & Ontology Relationship
        fused = []
        for entity, cluster in entity_clusters.items():
            # Group by ontology domain within the entity
            domain_clusters = {}
            for res in cluster:
                domain = res.metadata.get("domain", "Operational Risk")
                if domain not in domain_clusters:
                    domain_clusters[domain] = []
                domain_clusters[domain].append(res)
                
            for domain, group in domain_clusters.items():
                capabilities = [r.capability_id for r in group]
                avg_confidence = sum(r.confidence for r in group) / len(group) if group else 1.0
                
                # Merge raw outputs for unified observation
                merged_output = {}
                for r in group:
                    if hasattr(r.raw_output, "__dict__"):
                        merged_output.update(r.raw_output.__dict__)
                    elif isinstance(r.raw_output, dict):
                        merged_output.update(r.raw_output)
                
                # Generate Canonical ID
                ev_id = GraphNode.generate_id(NodeType.EVIDENCE, semantic_target=entity, cluster_id=domain)
                
                obj = UnifiedEvidenceObject(
                    id=ev_id,
                    source_capabilities=capabilities,
                    properties={
                        "summary": f"Fused evidence for {entity} concerning {domain}",
                        "domain": domain,
                        "entity": entity,
                        "raw_output": merged_output
                    },
                    confidence=avg_confidence
                )
                self._unified_evidence[obj.id] = obj
                fused.append(obj)
                
        return fused

    def to_graph_nodes(self) -> List[GraphNode]:
        nodes = []
        for ev in self._unified_evidence.values():
            nodes.append(GraphNode(
                id=ev.id,
                node_type=NodeType.EVIDENCE,
                properties=ev.properties,
                confidence=ev.confidence
            ))
        return nodes
