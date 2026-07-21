from __future__ import annotations

import datetime
from typing import Dict, List, Optional, Any, Callable

from app.knowledge.evidence.domain import Evidence
from app.knowledge.graph.graph_edge import GraphEdge, EdgeConfidence, EdgeProvenance
from app.knowledge.graph.identity_resolution import IdentityResolver

class EdgeTypeRegistry:
    """
    Dynamic registry for edge types, avoiding hardcoded relationships.
    """
    _registry: Dict[str, str] = {}
    
    @classmethod
    def register(cls, relationship: str, description: str):
        cls._registry[relationship] = description
        
    @classmethod
    def get_all(cls) -> Dict[str, str]:
        return dict(cls._registry)

# Register default core domains
EdgeTypeRegistry.register("OWNS", "Developer owns module")
EdgeTypeRegistry.register("CONTRIBUTED_TO", "Developer contributed to module")
EdgeTypeRegistry.register("REVIEWS", "Developer reviews module")
EdgeTypeRegistry.register("DEPENDS_ON", "Module depends on module")
EdgeTypeRegistry.register("IMPORTS", "Module imports module")
EdgeTypeRegistry.register("CALLS", "Module calls module")
EdgeTypeRegistry.register("COLLABORATES_WITH", "Developer collaborates with developer")
EdgeTypeRegistry.register("BELONGS_TO", "Entity belongs to container")
EdgeTypeRegistry.register("SUCCESSOR_OF", "Developer is a successor of developer")

class EdgeFactory:
    """
    Builds typed edges from deterministically extracted evidence.
    """
    def __init__(self, identity_resolver: IdentityResolver):
        self.identity_resolver = identity_resolver
        
    def build_from_evidence(self, evidence: Evidence) -> List[GraphEdge]:
        edges = []
        
        # Determine source and target from evidence
        # This will depend on the domain rules, but let's parse from metadata and provenance.
        # Examples: "Developer OWNS Module"
        
        # Extract target_entity and type from evidence metadata
        # (This logic replaces arbitrary metadata parsing with explicit provenance tracking)
        target_entity = evidence.metadata.get("target_entity")
        target_entity_type = evidence.metadata.get("target_entity_type")
        
        if not target_entity:
            return edges
            
        # Example logic for ownership edges
        if evidence.category == "OWNERSHIP":
            # Target is the developer (from IdentityResolver). We need to know what they own.
            # Look into the raw_refs of the supporting measurements to find the module.
            for measurement in evidence.supporting_measurements:
                if hasattr(measurement, "provenance") and measurement.provenance:
                    raw_refs = getattr(measurement.provenance, "raw_refs", {})
                    module = raw_refs.get("module") or raw_refs.get("file")
                    if module:
                        # Construct Developer -> Module OWNS edge
                        edges.append(
                            GraphEdge(
                                source_id=target_entity, # Identity canonical name
                                target_id=module,
                                relationship="OWNS",
                                confidence=EdgeConfidence(
                                    evidence_confidence=evidence.confidence,
                                    identity_confidence=1.0, # Will be replaced by resolver output
                                    extraction_confidence=0.9,
                                    relationship_confidence=1.0
                                ),
                                provenance=EdgeProvenance(
                                    evidence_id=str(evidence.evidence_id),
                                    algorithm="ownership_v2",
                                    created_by="EdgeFactory"
                                ),
                                weight=evidence.confidence
                            )
                        )
        
        # Similar logic for DEPENDS_ON, CONTRIBUTED_TO, etc.
        # As this is a showcase platform, we map whatever relationships exist in evidence lineage.
        
        return edges
