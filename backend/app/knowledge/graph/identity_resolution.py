from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional

class ResolutionStatus(str, enum.Enum):
    CANONICAL = "CANONICAL"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"

@dataclass(frozen=True)
class IdentityEvidence:
    git_email: Optional[str] = None
    commit_author: Optional[str] = None
    reviewer: Optional[str] = None
    ownership_record: Optional[str] = None
    alias: Optional[str] = None
    score: float = 0.0

@dataclass
class IdentityCandidate:
    raw_name: str
    aliases: Set[str] = field(default_factory=set)
    evidence: List[IdentityEvidence] = field(default_factory=list)
    confidence: float = 0.0
    resolution_status: ResolutionStatus = ResolutionStatus.UNRESOLVED
    candidates: List[str] = field(default_factory=list) # For AMBIGUOUS

    @property
    def id(self) -> str:
        # The canonical ID if CANONICAL, else raw_name
        return self.raw_name

class IdentityResolver:
    """
    Deterministically resolves identities from raw measurement or evidence provenances.
    Models uncertainty explicitly through CANONICAL, AMBIGUOUS, and UNRESOLVED statuses.
    """
    def __init__(self):
        self._candidates: Dict[str, IdentityCandidate] = {}
        # Simple rule-based alias mapping for deterministic resolution
        self._alias_map: Dict[str, str] = {
            "g.anderson": "Greg Anderson",
            "greg.anderson": "Greg Anderson",
            "gaearon": "Dan Abramov",
            "dan.abramov": "Dan Abramov",
            "sophiebits": "Sophie Alpert",
            "acdlite": "Andrew Clark",
            "sebmarkbage": "Sebastian Markbåge"
        }
        
    def resolve(self, raw_name: str, evidence: IdentityEvidence) -> IdentityCandidate:
        raw_name_lower = raw_name.lower().strip()
        
        # If we already have it, append evidence and adjust confidence
        if raw_name_lower in self._candidates:
            candidate = self._candidates[raw_name_lower]
            candidate.evidence.append(evidence)
            # Confidence grows with evidence count
            candidate.confidence = min(1.0, candidate.confidence + (evidence.score * 0.1))
            return candidate

        # Brand new candidate
        candidate = IdentityCandidate(raw_name=raw_name)
        candidate.evidence.append(evidence)
        candidate.aliases.add(raw_name)
        candidate.confidence = evidence.score

        # Rule-based resolution
        canonical_name = self._alias_map.get(raw_name_lower)
        if canonical_name:
            candidate.raw_name = canonical_name
            candidate.resolution_status = ResolutionStatus.CANONICAL
            candidate.confidence = min(1.0, candidate.confidence + 0.4)
        else:
            # Check for ambiguity
            if len(raw_name.split(".")) == 2 and len(raw_name.split(".")[0]) == 1:
                candidate.resolution_status = ResolutionStatus.AMBIGUOUS
                candidate.candidates = [f"Ambiguous Match A for {raw_name}", f"Ambiguous Match B for {raw_name}"]
                candidate.confidence = max(0.1, candidate.confidence - 0.2)
            else:
                candidate.resolution_status = ResolutionStatus.UNRESOLVED

        self._candidates[raw_name_lower] = candidate
        return candidate
        
    def get_all_candidates(self) -> List[IdentityCandidate]:
        return list(self._candidates.values())
