import asyncio
from typing import List, Dict, Any
from app.kernel.graph import GraphEngine, GraphNode, NodeType
from app.kernel.provider_manager import ProviderManager
from app.kernel.context import ExecutionContext

class InsightPhraser:
    """
    The ONLY component in the Reasoning OS that uses an LLM.
    Takes deterministic graph facts and styles them into beautiful, executive natural language.
    """
    def __init__(self, graph: GraphEngine, provider_manager: ProviderManager):
        self.graph = graph
        self.provider = provider_manager
        
    async def phrase_impacts(self) -> Dict[str, str]:
        """
        Takes raw IMPACT nodes and translates them into an executive summary paragraph.
        """
        impacts = self.graph.get_all_nodes(NodeType.IMPACT)
        if not impacts:
            return {}
            
        phrased_results = {}
        
        # Take Top K impacts to avoid context explosion
        # We can sort by confidence or leverage score if present
        impacts = sorted(impacts, key=lambda x: x.confidence, reverse=True)[:3]
        
        for impact in impacts:
            lineage = self.graph.explain(impact.id)
            trace_text = "\n".join([f"- {step['node_type']}: {step['properties']}" for step in lineage])
            
            prompt = f"""
You are an elite, executive-level technical writer for a Fortune 500 company.
Take the following raw deterministic intelligence data and rewrite it into a stunning, one-paragraph executive insight.
Focus on the business risk, the technical cause, and use professional, authoritative language. Do not invent facts, only style the provided data.

Data:
Domain: {impact.properties.get('business_domain')}
Specific Risk: {impact.properties.get('specific_risk')}
Description: {impact.properties.get('description')}
Confidence: {impact.confidence * 100}%

Reasoning Lineage (Mathematical Trace):
{trace_text}
"""
            # Use the LLM only for styling
            try:
                response = self.provider.generate(prompt)
                phrased_results[impact.id] = response.content.strip()
            except Exception as e:
                # Fallback to deterministic text if LLM is offline
                phrased_results[impact.id] = f"**{impact.properties.get('business_domain')}**: {impact.properties.get('description')}"
                
        return phrased_results
