import uuid
from app.kernel.graph import GraphEngine, GraphNode, NodeType, GraphEdge, EdgeType
from app.kernel.intelligence.ontology import CoreOntology

class BusinessTranslator:
    """
    Translates Technical Inference nodes into Business IMPACT nodes using the Ontology.
    """
    def __init__(self, graph: GraphEngine, ontology: CoreOntology):
        self.graph = graph
        self.ontology = ontology
        
    def translate_inferences_to_impact(self):
        inferences = self.graph.get_all_nodes(NodeType.INFERENCE)
        
        for inf in inferences:
            # For Phase 3, we do a simplistic string match to ontology categories
            # "Single Point of Failure Detected" -> maps to "risk_knowledge_concentration"
            insight = inf.properties.get("insight", "")
            if "Single Point of Failure" in insight:
                # 1. Get Ontology Lineage
                lineage = self.ontology.get_lineage("risk_knowledge_concentration")
                if lineage:
                    top_level = lineage[-1] # e.g. Operational Risk
                    
                    # 2. Create IMPACT node
                    impact_id = f"imp_{uuid.uuid4().hex[:8]}"
                    impact = GraphNode(
                        id=impact_id,
                        node_type=NodeType.IMPACT,
                        properties={
                            "business_domain": top_level.name,
                            "specific_risk": lineage[0].name,
                            "description": f"Technical issue causes {top_level.name}"
                        },
                        confidence=inf.confidence
                    )
                    self.graph.add_node(impact)
                    
                    # 3. Create CAUSES edge (Inference -> Causes -> Impact)
                    edge = GraphEdge(
                        source_id=impact.id,
                        target_id=inf.id,
                        edge_type=EdgeType.CAUSES,
                        weight=1.0
                    )
                    self.graph.add_edge(edge)
