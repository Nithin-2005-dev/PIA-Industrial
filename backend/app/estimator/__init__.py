"""
Estimator Layer

Responsibilities:
- Convert Evidence into Latent State Estimates.
- Contain domain algorithms.
- Remain independent of infrastructure.

Rules:
- Never access database directly.
- Never call GitHub API.
- Never mutate state.
- Always return new immutable estimates.
"""
from app.estimator.semantic_pipeline import ExpertiseProjectionResult
from app.estimator.semantic_pipeline import SemanticEvidenceExpertiseBridge
from app.estimator.semantic_pipeline import SemanticExpertiseProjectionPipeline

__all__ = [
    "ExpertiseProjectionResult",
    "SemanticEvidenceExpertiseBridge",
    "SemanticExpertiseProjectionPipeline",
]
