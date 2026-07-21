import dataclasses
import re
from typing import Protocol, List
from .models import CapabilityCard, RequiredCapability

@dataclasses.dataclass(frozen=True)
class CapabilityCandidate:
    capability: CapabilityCard
    score: float
    confidence: float
    why_selected: str
    matched_terms: List[str]
    estimated_cost: float
    estimated_latency: float

class ToolSearchEngine(Protocol):
    def search(self, requirement: RequiredCapability, available_capabilities: List[CapabilityCard], top_k: int = 8) -> List[CapabilityCandidate]:
        ...

class KeywordSearchEngine(ToolSearchEngine):
    """
    M57 implementation of ToolSearchEngine using weighted keyword and alias matching.
    Designed to be cleanly swapped for an EmbeddingSearchEngine in M58.
    """
    def search(self, requirement: RequiredCapability, available_capabilities: List[CapabilityCard], top_k: int = 8) -> List[CapabilityCandidate]:
        candidates = []
        
        req_terms = set(re.findall(r'\w+', requirement.name.lower() + " " + requirement.reason.lower()))
        
        for cap in available_capabilities:
            score = 0.0
            matched_terms = []
            
            # Exact name match (Highest weight)
            if cap.name.lower() == requirement.name.lower():
                score += 10.0
                matched_terms.append(cap.name)
                
            # Alias match
            for alias in cap.aliases:
                if alias.lower() in requirement.name.lower() or alias.lower() in requirement.reason.lower():
                    score += 5.0
                    matched_terms.append(alias)
                    
            # Tag match
            for tag in cap.tags:
                if tag.lower() in req_terms:
                    score += 2.0
                    matched_terms.append(tag)
                    
            # Description text match
            desc_terms = set(re.findall(r'\w+', cap.description.lower()))
            overlap = req_terms.intersection(desc_terms)
            if overlap:
                score += len(overlap) * 0.5
                matched_terms.extend(list(overlap))
                
            if score > 0:
                confidence = min(score / 10.0, 1.0)
                candidates.append(
                    CapabilityCandidate(
                        capability=cap,
                        score=score,
                        confidence=confidence,
                        why_selected=f"Matched terms: {', '.join(set(matched_terms))}",
                        matched_terms=list(set(matched_terms)),
                        estimated_cost=cap.cost,
                        estimated_latency=cap.latency
                    )
                )
                
        # Sort descending by score
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:top_k]
