import json
from dataclasses import asdict, is_dataclass
from .models import ExecutionState, CapabilityResult, PreconditionFailure, Critique, VerificationStatus

class AnswerBuilder:
    """
    Deterministically converts Memory into a structured string report.
    This report is the fallback, and the foundation for LLM rewriting.
    """
    def build(self, state: ExecutionState) -> str:
        rm = state.repository_memory
        
        report = "### Repository Analysis\n\n"
        
        report += "#### Summary\n"
        report += "Deterministic analysis completed based on available evidence.\n\n"
        
        report += "#### Findings\n"
        if not rm.observations and not rm.facts:
            report += "- I do not have sufficient evidence.\n"
        else:
            for obs in rm.observations:
                if isinstance(obs.output, CapabilityResult):
                    # Use domain report if available, else fallback to normalized output safely
                    data_to_dump = asdict(obs.output.report) if getattr(obs.output, "report", None) and is_dataclass(obs.output.report) else obs.output.normalized_output
                    try:
                        dumped = json.dumps(data_to_dump, default=str)
                    except TypeError:
                        dumped = str(data_to_dump)
                    evidence = ", ".join(obs.output.evidence_ids) if obs.output.evidence_ids else "none"
                    provenance = obs.output.provenance.snapshot_id if obs.output.provenance else "unknown"
                    report += (
                        f"- **{obs.tool}** "
                        f"(confidence={obs.output.confidence:.2f}, evidence={evidence}, source={provenance}): "
                        f"{dumped}\n"
                    )
                elif isinstance(obs.output, PreconditionFailure):
                    report += f"- **{obs.tool}**: Failed due to missing preconditions.\n"
                else:
                    try:
                        dumped = json.dumps(obs.output, default=str)
                    except TypeError:
                        dumped = str(obs.output)
                    report += f"- **{obs.tool}**: {dumped}\n"
            for fact in rm.facts:
                report += f"- {fact}\n"
                
        report += "\n#### Recommendations\n"
        if not rm.observations and not rm.facts:
            report += "- Collect or execute an evidence-producing repository capability before making deterministic claims.\n"
        else:
            report += "- Review the evidence-backed findings to assess risk and ownership.\n"
        
        report += "\n#### Evidence\n"
        evidence_count = 0
        for obs in rm.observations:
            if isinstance(obs.output, CapabilityResult):
                evidence_count += len(obs.output.evidence_ids)
            else:
                evidence_count += len(obs.evidence_ids)
        report += f"Backed by {evidence_count} evidence artifacts.\n"
        
        if state.planner_confidence:
            report += f"\n#### Confidence\n"
            report += f"Topic Confidence: {state.planner_confidence.topic_confidence:.2f}\n"
            
        return report

    def extract_verified_claims(self, state: ExecutionState) -> list[Critique]:
        critiques = []
        rm = state.repository_memory
        for obs in rm.observations:
            if isinstance(obs.output, CapabilityResult) and obs.output.status == "SUCCESS":
                critiques.append(
                    Critique(
                        claim=obs.output.summary,
                        verification_status=VerificationStatus.VERIFIED,
                        confidence_score=obs.output.confidence,
                        reason="Backed by deterministic capability execution."
                    )
                )
        return critiques
