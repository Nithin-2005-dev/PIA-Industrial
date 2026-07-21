from typing import List
from .models import PromptArtifact, RetrievedEvidence
from .tools import ToolExecutionResult


class EvidenceRetriever:
    """
    Extracts structured PromptArtifacts from the raw ToolExecutionResults.
    Converts complex deterministic objects into LLM-safe summaries.
    """
    def retrieve(self, results: List[ToolExecutionResult]) -> RetrievedEvidence:
        artifacts = []
        
        for result in results:
            if result.data is None:
                continue
                
            if result.tool_name == "forecast":
                # Mock extraction from ForecastContext
                artifacts.append(
                    PromptArtifact(
                        id="forecast.org",
                        title="Organizational Forecast",
                        summary="Projected forecast from deterministic engine.",
                        evidence_ids=[],
                        confidence=0.90,
                    )
                )
            elif result.tool_name == "causal":
                # Extract from CausalContext
                primary_cause = getattr(result.data, "primary_cause", "Unknown")
                overall_conf = getattr(result.data, "overall_confidence", 0.0)
                root_causes = getattr(result.data, "root_causes", [])
                
                evidence_ids = []
                for rc in root_causes:
                    if hasattr(rc, "evidence_ids"):
                        evidence_ids.extend(rc.evidence_ids)
                
                artifacts.append(
                    PromptArtifact(
                        id="causal.root_cause",
                        title="Root Cause Analysis",
                        summary=f"Primary root cause identified as: {primary_cause}",
                        evidence_ids=evidence_ids,
                        confidence=overall_conf,
                    )
                )
            elif result.tool_name == "organization":
                artifacts.append(
                    PromptArtifact(
                        id="org.health",
                        title="Organization Health",
                        summary="Organizational intelligence metrics including bus factor.",
                        evidence_ids=["org-health-1"],
                        confidence=1.0,
                    )
                )
            else:
                # Generic fallback
                artifacts.append(
                    PromptArtifact(
                        id=f"{result.tool_name}.generic",
                        title=f"{result.tool_name.capitalize()} Data",
                        summary=f"Extracted {result.tool_name} data.",
                        evidence_ids=[],
                        confidence=1.0,
                    )
                )
                
        return RetrievedEvidence(artifacts=artifacts)
