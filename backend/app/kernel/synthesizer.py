from .models import ExecutiveResponse, CommunicationMode, AnswerConfidence
from .provider_manager import ProviderManager
from .prompts import PromptRegistry

class AdaptiveSynthesizer:
    """
    Takes a deterministic report and optionally uses an LLM to rewrite it for fluency.
    If the LLM fails, it falls back to the deterministic report gracefully.
    """
    def __init__(self, provider: ProviderManager):
        self.provider = provider

    def synthesize(
        self,
        deterministic_report: str,
        mode: CommunicationMode,
        confidence: AnswerConfidence
    ) -> ExecutiveResponse:
        
        # In a real system, we might decide to skip LLM rewrite for ENGINEER mode
        # and only use it for EXECUTIVE/TEACHER.
        # But we will try to rewrite it.
        
        prompt = PromptRegistry.get("rewriter", "v1").format(report=deterministic_report)
        response = self.provider.generate(prompt)
        
        if "[ALL_PROVIDERS_FAILED]" in response.content:
            # Fallback seamlessly to the deterministic report!
            final_text = deterministic_report
        else:
            final_text = response.content
            
        resp = ExecutiveResponse(
            executive_summary=final_text,
            technical_summary=final_text,
            actionable_recommendations=[],
            supporting_evidence=[],
            confidence=confidence.overall if confidence else 1.0,
            risks=[],
            alternative_strategies=[]
        )
        return resp
