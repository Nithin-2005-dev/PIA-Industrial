from typing import Dict, Any
from app.kernel.graph import GraphEngine, NodeType
from app.kernel.presentation.visualize import GraphVisualizer

class ExecutiveReportGenerator:
    """
    Compiles visuals, scored priorities, and phrased text into an executive report.
    """
    def __init__(self, graph: GraphEngine):
        self.graph = graph
        self.visualizer = GraphVisualizer(graph)
        
    def generate_markdown_report(self, phrased_impacts: Dict[str, str]) -> str:
        """
        Creates a stunning, executive-ready Markdown presentation.
        """
        lines = []
        lines.append("# Reasoning Operating System: Executive Intelligence Report")
        lines.append("> [!TIP]")
        lines.append("> This report was generated deterministically via pure graph topology. The LLM was used strictly for narrative styling.")
        lines.append("")
        
        # 1. Executive Summary
        lines.append("## Executive Summary")
        for impact_id, phrased_text in phrased_impacts.items():
            lines.append(phrased_text)
            lines.append("")
            
        # 2. Prioritized Risks
        lines.append("## Prioritized Risk Inferences")
        lines.append("| Priority | Insight | Score | Source |")
        lines.append("| :--- | :--- | :--- | :--- |")
        
        inferences = self.graph.get_all_nodes(NodeType.INFERENCE)
        # Sort by priority score descending
        inferences.sort(key=lambda x: x.properties.get("priority_score", 0), reverse=True)
        
        for inf in inferences:
            score = inf.properties.get("priority_score", 0.0)
            label = inf.properties.get("priority_label", "Unknown")
            insight = inf.properties.get("insight", "")
            lines.append(f"| **{label}** | {insight} | {score:.1f}/100 | Graph Topology |")
            
        lines.append("")
        
        # 3. Automated Mitigation Plans
        lines.append("## Automated Mitigation Plans")
        recommendations = self.graph.get_all_nodes(NodeType.RECOMMENDATION)
        for rec in recommendations:
            action = rec.properties.get("action", "")
            status = rec.properties.get("status", "")
            job = rec.properties.get("job_id", "Unscheduled")
            benefit = rec.properties.get("expected_benefit", 0)
            cost = rec.properties.get("implementation_cost", 0)
            reduction = rec.properties.get("risk_reduction", 0)
            lines.append(f"- **Action**: {action}")
            lines.append(f"  - **Status**: {status} (Job: `{job}`)")
            if benefit > 0:
                lines.append(f"  - **Pareto Metrics**: Expected Benefit: {benefit:.1f} | Cost: {cost:.1f} | Leverage: {reduction:.2f}x")
            
        lines.append("")
        
        # 4. Topological Lineage (Visual)
        lines.append("## Mathematical Proof of Reasoning (Topology)")
        lines.append("The exact evidence chain proving these conclusions:")
        lines.append("")
        
        # Optionally, embed a textual explain trace for the top inference
        if inferences:
            top_inf = inferences[0]
            lines.append(f"### Lineage Trace for Top Inference: {top_inf.properties.get('insight', 'Unknown')}")
            trace = self.graph.explain(top_inf.id)
            for step in trace:
                lines.append(f"- `{step['node_type']}`: {step['properties']}")
            lines.append("")

        lines.append(self.visualizer.generate_mermaid_diagram())
        lines.append("")
        
        return "\n".join(lines)
