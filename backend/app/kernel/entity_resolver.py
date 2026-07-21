from typing import List
from .models import SemanticQuery, Entity, EntityType
from .repository_knowledge import RepositoryKnowledge
from .registry import CapabilityCard

class EntityResolver:
    def __init__(self):
        pass

    def resolve(self, query: SemanticQuery, repo_knowledge: RepositoryKnowledge, candidate_card: CapabilityCard = None) -> SemanticQuery:
        """
        Resolves entities based on the repository index.
        If a candidate capability is provided, resolution can be tailored to its specific domain 
        (e.g., Ownership expects modules, KnowledgeGraph expects symbol nodes).
        """
        resolved_entities = []
        
        for entity in query.entities:
            # Simple fuzzy/substring resolution
            results = repo_knowledge.search_entities(entity.value, entity.type.name)
            
            if len(results) == 1:
                # Perfect resolution
                resolved_entities.append(Entity(type=entity.type, value=results[0], confidence=1.0))
            elif len(results) > 1:
                # Ambiguity - keep the original value but mark confidence lower, let the capability handle it or ask user
                # For M57.15, we'll just take the top match but flag confidence.
                resolved_entities.append(Entity(type=entity.type, value=results[0], confidence=0.5))
            else:
                # No match found, leave as is
                resolved_entities.append(Entity(type=entity.type, value=entity.value, confidence=0.0))
                
        # Return a new SemanticQuery with resolved entities
        from dataclasses import replace
        return replace(query, resolved_entities=resolved_entities)

    def resolve_for_node(self, inputs: List[Entity], repo_knowledge: RepositoryKnowledge, candidate_card: CapabilityCard = None) -> List[Entity]:
        """Resolves a specific list of inputs for a node."""
        resolved = []
        for entity in inputs:
            results = repo_knowledge.search_entities(entity.value, entity.type.name)
            if results:
                resolved.append(Entity(type=entity.type, value=results[0], confidence=1.0 if len(results) == 1 else 0.5))
            else:
                resolved.append(entity)
        return resolved
