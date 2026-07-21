import json
import dataclasses
from typing import Any
from app.kernel.models import DomainReport, TopContributorReport, OwnershipReport

class InformationalPresentationMapper:
    """
    Maps structured Domain Reports directly into Presentation Models for the Informational Pipeline.
    This prevents the LLM from having to extract facts from execution traces.
    """
    
    @staticmethod
    def map_report(report: DomainReport) -> dict:
        if isinstance(report, TopContributorReport):
            # Map TopContributorReport to the required presentation model
            contributors = report.contributors
            if contributors:
                top = contributors[0]
                return {
                    "title": "Top Contributor",
                    "contributor": top.get("name", "Unknown"),
                    "commits": top.get("commits", 0),
                    "confidence": getattr(report, "confidence", 1.0)
                }
            else:
                return {
                    "title": "Top Contributor",
                    "contributor": "None",
                    "commits": 0,
                    "confidence": 1.0
                }
        elif isinstance(report, OwnershipReport):
            profiles = getattr(report, "profiles", ())
            if profiles:
                top = profiles[0]
                return {
                    "title": "File Owner",
                    "owner": getattr(top, "developer", "Unknown"),
                    "ownership_score": getattr(top, "ownership_score", 0.0),
                    "confidence": getattr(report.quality, "confidence", 1.0) if getattr(report, "quality", None) else 1.0
                }
            return {"title": "File Owner", "owner": "None"}
            
        # Fallback to dictionary representation of the report
        if dataclasses.is_dataclass(report):
            return dataclasses.asdict(report)
        return {"data": str(report)}
