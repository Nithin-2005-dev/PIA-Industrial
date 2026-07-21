from abc import ABC, abstractmethod

from app.domain.evidence import Evidence


class EvidenceScoringPolicy(ABC):
    """
    Strategy interface for scoring Evidence.

    Different implementations may use:
    - Rule-based systems
    - Machine Learning
    - Bayesian inference
    - Graph Neural Networks
    - LLM reasoning
    """

    @abstractmethod
    def score(self, evidence: Evidence) -> float:
        """
        Returns the contribution score of the given evidence.
        """
        pass