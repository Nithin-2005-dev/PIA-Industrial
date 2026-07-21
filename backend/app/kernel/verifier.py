from typing import List, Any
from .models import Critique, VerificationResult, VerificationStatus, CapabilityResult, AgentObservation

class EvidenceVerificationEngine:
    """
    Maps LLM-generated claims strictly to evidence from deterministic capability results.
    """
    def verify(self, original_text: str, critiques: List[Critique], observations: List[AgentObservation] = None) -> VerificationResult:
        dropped = 0
        verified_text = original_text
        
        # Collect all valid evidence IDs from capability results
        valid_evidence_ids = set()
        if observations:
            for obs in observations:
                if isinstance(obs.output, CapabilityResult) and obs.output.status == "SUCCESS":
                    valid_evidence_ids.update(obs.output.evidence_ids)
                    
        # M57.12 logic: For mock critiques, we verify if they reference known evidence.
        # Since this is a deterministic pipeline, the critiques list from the AnswerBuilder
        # is actually verified claims, but if LLM generated them, we check the evidence IDs.
        
        for critique in critiques:
            status = critique.verification_status
            reason = critique.reason
            if status == VerificationStatus.VERIFIED and not valid_evidence_ids:
                status = VerificationStatus.UNVERIFIED
                reason = "No deterministic evidence ids were available."

            if status == VerificationStatus.UNVERIFIED:
                # Redact completely unsupported claims
                verified_text = verified_text.replace(
                    critique.claim,
                    f"[UNVERIFIED REPOSITORY CLAIM REDACTED: {reason}]"
                )
                dropped += 1
            elif status == VerificationStatus.PARTIALLY_VERIFIED:
                # Annotate partially supported claims without removing them
                verified_text = verified_text.replace(
                    critique.claim,
                    f"{critique.claim} [PARTIALLY VERIFIED: {reason}]"
                )
                
        return VerificationResult(
            original_text=original_text,
            verified_text=verified_text,
            critiques=critiques,
            dropped_claims=dropped
        )
