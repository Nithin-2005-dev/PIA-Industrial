from app.kernel.graph import GraphEngine

class GraphVisualizer:
    """
    Generates Mermaid.js diagrams directly from the deterministic Reasoning Graph.
    """
    def __init__(self, graph: GraphEngine):
        self.graph = graph
        
    def generate_mermaid_diagram(self) -> str:
        """
        Walks the graph and generates a beautifully styled Mermaid flowchart.
        """
        lines = ["```mermaid", "graph TD"]
        
        # Style definitions
        lines.append("    classDef impact fill:#ff4d4d,stroke:#fff,stroke-width:2px,color:#fff;")
        lines.append("    classDef rootCause fill:#ff9900,stroke:#fff,stroke-width:2px,color:#fff;")
        lines.append("    classDef inference fill:#3399ff,stroke:#fff,stroke-width:2px,color:#fff;")
        lines.append("    classDef observation fill:#99ccff,stroke:#fff,stroke-width:2px,color:#000;")
        lines.append("    classDef evidence fill:#e6e6e6,stroke:#999,stroke-width:1px,color:#000;")
        lines.append("    classDef recommendation fill:#00cc66,stroke:#fff,stroke-width:2px,color:#fff;")
        
        # Nodes
        for node in self.graph.get_all_nodes():
            label = ""
            node_type = node.node_type.value
            
            if node_type == "impact":
                label = f"{node.properties.get('business_domain', 'Impact')}\\n{node.properties.get('specific_risk', '')}"
                style = "impact"
            elif node_type == "root_cause":
                label = "Root Cause"
                style = "rootCause"
            elif node_type == "inference":
                label = node.properties.get("insight", "Inference")
                style = "inference"
            elif node_type == "observation":
                label = "Observation"
                style = "observation"
            elif node_type == "evidence":
                label = f"Evidence\\nConf: {node.confidence}"
                style = "evidence"
            elif node_type == "recommendation":
                label = f"Action: {node.properties.get('action', '')}"
                style = "recommendation"
            else:
                label = node_type
                style = "evidence"
                
            # Sanitize labels for Mermaid
            label = label.replace("\"", "'").replace("[", "(").replace("]", ")")
            lines.append(f'    {node.id}["{label}"]:::{style}')
            
        # Edges
        for edge in self.graph._edges:
            lines.append(f'    {edge.source_id} -- "{edge.edge_type.value}" --> {edge.target_id}')
            
        lines.append("```")
        return "\n".join(lines)
