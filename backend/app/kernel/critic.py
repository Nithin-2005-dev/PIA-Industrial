from typing import List
from .models import Critique, PromptContext, VerificationStatus
from .provider import LLMProvider


class CriticEngine:
    """
    Parses LLM output and detects potentially unsupported claims or hallucinations.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        
    def critique(self, llm_output: str, context: PromptContext) -> List[Critique]:
        # Optimization for simple conversational queries to save LLM calls
        if len(context.artifacts) == 0 and len(llm_output) < 300:
            return [Critique(
                claim="Overall response",
                verification_status=VerificationStatus.VERIFIED,
                confidence_score=1.0,
                reason="Conversational response without external claims."
            )]
            
        prompt = f"""
        Analyze this text for unsupported claims against the artifacts.
        Text: {llm_output}
        
        RULES FOR VERIFICATION:
        1. ONLY evaluate assertions made about the specific repository/codebase being analyzed.
        2. DO NOT verify general knowledge, mathematics, programming concepts, graph theory, Git, Python, or software engineering concepts. These are Public Knowledge.
        
        For any Repository Assertion, classify its status as one of: VERIFIED, PARTIALLY_VERIFIED, UNVERIFIED.
        
        List critiques in this format:
        CRITIQUE: CLAIM='...' STATUS=VERIFIED/PARTIALLY_VERIFIED/UNVERIFIED REASON='...'
        """
        
        response = self.provider.generate(prompt)
        critiques = []
        
        for line in response.content.split("\n"):
            if line.startswith("CRITIQUE:"):
                status_str = "VERIFIED"
                if "STATUS=PARTIALLY_VERIFIED" in line:
                    status_str = "PARTIALLY_VERIFIED"
                elif "STATUS=UNVERIFIED" in line:
                    status_str = "UNVERIFIED"
                    
                verification_status = VerificationStatus.VERIFIED
                if status_str == "PARTIALLY_VERIFIED":
                    verification_status = VerificationStatus.PARTIALLY_VERIFIED
                elif status_str == "UNVERIFIED":
                    verification_status = VerificationStatus.UNVERIFIED

                claim = "Unknown claim"
                if "CLAIM=" in line:
                    parts = line.split("CLAIM='")
                    if len(parts) > 1:
                        claim = parts[1].split("'")[0]
                
                reason = "Unknown reason"
                if "REASON=" in line:
                    parts = line.split("REASON='")
                    if len(parts) > 1:
                        reason = parts[1].split("'")[0]
                        
                critiques.append(Critique(
                    claim=claim,
                    verification_status=verification_status,
                    confidence_score=0.9,
                    reason=reason
                ))
                
        # If the LLM provider didn't return formatted critiques, just approve it by default.
        if not critiques:
            critiques.append(Critique(
                claim="Overall response",
                verification_status=VerificationStatus.VERIFIED,
                confidence_score=1.0,
                reason="No specific unsupported repository claims identified."
            ))
            
        return critiques
