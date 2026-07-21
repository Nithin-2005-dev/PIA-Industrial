from typing import Tuple
from .models import SemanticQuery, CapabilityCandidate, CapabilityCard, CapabilityStatus
from .registry import CapabilityRegistry
from .repository_knowledge import RepositoryKnowledge

class CapabilityRetriever:
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def retrieve(self, semantic_query: SemanticQuery, repo_knowledge: RepositoryKnowledge) -> Tuple[CapabilityCandidate, ...]:
        """
        Scores and retrieves the Top K capability candidates based on semantic overlap
        between the query's topics/keywords and the capability's metadata.
        """
        candidates = []
        
        query_terms = set([t.lower() for t in semantic_query.topics] + [k.lower() for k in semantic_query.keywords])
        if not query_terms and not semantic_query.goals:
            return ()
            
        for card in self.registry.get_all():
            score, diagnostics = self._score_capability(card, semantic_query, query_terms)
            
            if score > 0.0:
                available, reason = self._check_preconditions(card, repo_knowledge)
                if card.contract.implemented != CapabilityStatus.IMPLEMENTED:
                    available = False
                    reason = f"Capability status is {card.contract.implemented.name}"
                    score *= 0.05
                if not available:
                    score *= 0.25
                
                candidates.append(CapabilityCandidate(
                    card=card,
                    why_selected=diagnostics.get("Match Reason", "Semantic match"),
                    score=score,
                    confidence=card.confidence,
                    estimated_latency=card.latency,
                    estimated_cost=card.cost,
                    satisfied_goals=[g for g in semantic_query.goals if g in card.contract.supported_goals],
                    available=available,
                    missing_prerequisites=[reason] if not available else [],
                    diagnostics=diagnostics
                ))
                
        # Sort by score descending and take Top K
        candidates.sort(key=lambda c: c.score, reverse=True)
        return tuple(candidates[:10])

    def _score_capability(self, card: CapabilityCard, semantic_query: SemanticQuery, query_terms: set[str]) -> Tuple[float, dict]:
        # Build document from capability metadata
        card_terms = set([card.name.lower()] + [t.lower() for t in card.tags] + [a.lower() for a in card.aliases])
        # Add words from description
        desc_words = [w.lower() for w in card.description.split() if len(w) > 3]
        card_terms.update(desc_words)
        
        # Calculate overlap (simple Jaccard-like or token intersection)
        overlap = query_terms.intersection(card_terms)
        
        # To avoid zero score for valid tags, give partial score
        keyword_match = len(overlap) / max(len(query_terms), 1.0)
        goal_hits = [g for g in semantic_query.goals if g in card.contract.supported_goals]
        entity_hits = [e.type for e in semantic_query.entities if e.type in card.contract.supported_entities]
        scope_hit = semantic_query.scope in card.contract.supported_scopes
        
        # We can also add substring matches for stronger retrieval
        for term in query_terms:
            for ct in card_terms:
                if term in ct or ct in term:
                    keyword_match += 0.2
        
        keyword_match = min(keyword_match, 1.0)
        goal_match = len(goal_hits) / max(len(semantic_query.goals), 1.0)
        entity_match = len(entity_hits) / max(len(semantic_query.entities), 1.0) if semantic_query.entities else 0.0
        scope_match = 0.15 if scope_hit else 0.0
        semantic_score = min((goal_match * 0.45) + (keyword_match * 0.35) + (entity_match * 0.05) + scope_match, 1.0)
        
        diagnostics = {
            "Capability": card.name,
            "Semantic Match Score": semantic_score,
            "Goal Match Score": goal_match,
            "Keyword Match Score": keyword_match,
            "Entity Match Score": entity_match,
            "Scope Matched": scope_hit,
            "Matched Terms": list(overlap),
            "Matched Goals": [g.name for g in goal_hits],
            "Latency Score": min(card.latency / 1000.0, 0.2),
            "Threshold": 0.1
        }
        
        if semantic_score == 0.0:
            diagnostics["Final Score"] = 0.0
            diagnostics["Rejected"] = True
            return 0.0, diagnostics
            
        diagnostics["Match Reason"] = f"Matched goals {[g.name for g in goal_hits]} and terms {list(overlap)}"
        
        base_score = semantic_score * card.confidence
        # Apply penalties (normalized roughly)
        latency_penalty = diagnostics["Latency Score"]
        cost_penalty = min(card.cost / 1.0, 0.2)
        
        final_score = max(base_score - latency_penalty - cost_penalty, 0.1)
        diagnostics["Final Score"] = final_score
        diagnostics["Rejected"] = False
        
        return final_score, diagnostics

    def _check_preconditions(self, card: CapabilityCard, repo_knowledge: RepositoryKnowledge) -> Tuple[bool, str]:
        """Checks if the capability's required layers are present in the repository knowledge."""
        for req in card.contract.required_measurements:
            pass
            
        for post in card.contract.postconditions:
            if post == "forecast_available":
                try:
                    repo_knowledge.adapter.forecast()
                except Exception as e:
                    return False, f"Missing prerequisite layer: {str(e)}"
                    
        return True, ""
