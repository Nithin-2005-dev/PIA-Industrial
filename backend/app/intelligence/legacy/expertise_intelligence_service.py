"""Expertise Intelligence Service.

Infers asset expertise from maintenance and inspection history,
and calculates knowledge concentration risks (the industrial Bus Factor).
"""
from __future__ import annotations

import logging
from collections import defaultdict

from app.domain.industrial.expertise_intelligence import (
    AssetExpertise,
    CriticalKnowledgeConcentration,
)
from app.intelligence.legacy.asset_intelligence_service import AssetIntelligenceService
from app.ingestion.observation.domain import ObservationType

logger = logging.getLogger(__name__)


class ExpertiseIntelligenceService:
    """Service to evaluate knowledge distribution for industrial assets."""

    def __init__(self, asset_service: AssetIntelligenceService):
        self._asset_service = asset_service

    def evaluate_expertise(self, asset_id: str) -> CriticalKnowledgeConcentration:
        """Analyze the asset's timeline to determine who holds critical knowledge."""
        timeline = self._asset_service.get_asset_timeline(asset_id)
        
        # Track interactions per actor
        # actor_id -> count
        interactions: dict[str, int] = defaultdict(int)
        roles: dict[str, str] = {}
        
        for obs in timeline:
            if obs.event_type == ObservationType.INSPECTION_EVENT.value:
                actor = obs.metadata.get("inspector")
                if actor:
                    interactions[actor] += 1
                    roles[actor] = "INSPECTOR"
            elif obs.event_type == ObservationType.WORK_ORDER.value:
                actor = obs.metadata.get("technician")
                if actor:
                    interactions[actor] += 2  # Maintenance implies deeper expertise
                    roles[actor] = "MAINTENANCE"
                    
        total_interactions = sum(interactions.values())
        
        expertise_list: list[AssetExpertise] = []
        for actor, count in interactions.items():
            score = (count / total_interactions) if total_interactions > 0 else 0.0
            expertise_list.append(AssetExpertise(
                asset_id=asset_id,
                actor_id=actor,
                expertise_score=score,
                evidence_count=count,
                primary_role=roles.get(actor, "UNKNOWN"),
                evidence_summary=f"{count} documented interactions",
            ))
            
        expertise_list.sort(key=lambda x: x.expertise_score, reverse=True)
        
        expert_count = len(expertise_list)
        top_expert = expertise_list[0] if expertise_list else None
        
        # Calculate concentration (Gini-like or simple top-heavy check)
        if expert_count == 0:
            concentration = 1.0
            risk_level = "CRITICAL"
            rec = "No documented expertise. Immediate knowledge capture required."
        elif expert_count == 1:
            concentration = 1.0
            risk_level = "HIGH"
            rec = "Single point of failure for asset knowledge. Cross-train immediately."
        else:
            assert top_expert is not None
            concentration = top_expert.expertise_score
            if concentration > 0.8:
                risk_level = "HIGH"
                rec = "Highly concentrated knowledge. Rotate inspection duties."
            elif concentration > 0.5:
                risk_level = "MEDIUM"
                rec = "Moderate concentration. Ensure documentation is up to date."
            else:
                risk_level = "LOW"
                rec = "Knowledge is well distributed."
                
        return CriticalKnowledgeConcentration(
            asset_id=asset_id,
            expert_count=expert_count,
            top_expert_id=top_expert.actor_id if top_expert else None,
            concentration_score=concentration,
            risk_level=risk_level,
            recommendation=rec,
        )
