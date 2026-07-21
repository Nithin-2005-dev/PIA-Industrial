"""Asset Intelligence Service.

Aggregates observations, measurements, and knowledge graph data
to build a deterministic 360-degree profile of an industrial asset.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.domain.industrial.asset import AssetCriticality, AssetStatus, RiskLevel
from app.domain.industrial.asset_intelligence import (
    AssetIntelligenceProfile,
    AssetTimelineEvent,
)
from app.knowledge.graph.industrial_graph_manager import IndustrialGraphManager
from app.ingestion.observation.domain import ObservationType
from app.ingestion.observation.storage import ObservationStore

logger = logging.getLogger(__name__)


class AssetIntelligenceService:
    """Service to generate deterministic asset intelligence profiles."""

    def __init__(
        self,
        graph_manager: IndustrialGraphManager,
        observation_store: ObservationStore,
    ):
        self._graph_manager = graph_manager
        self._obs_store = observation_store

    def get_asset_profile(self, asset_id: str) -> AssetIntelligenceProfile | None:
        """Build the complete 360 view of an asset."""
        # 1. Base Asset from Graph
        graph = self._graph_manager.build_graph()
        asset_node = next((n for n in graph.nodes if n.id == asset_id and n.type == "asset"), None)
        if not asset_node:
            return None

        # Determine core attributes (fallback to defaults if not heavily populated in mock graph)
        attrs = asset_node.attributes or {}
        equipment_tag = attrs.get("equipment_tag", asset_id)
        asset_type = attrs.get("asset_type", "Unknown")
        name = attrs.get("name", asset_id)

        # 2. Neighborhood from Graph
        neighborhood = self._graph_manager.get_asset_neighborhood(asset_id)
        documents = tuple(item["id"] for item in neighborhood.get("documents", []))
        failures = tuple(item["id"] for item in neighborhood.get("failures", []))
        work_orders = tuple(item["id"] for item in neighborhood.get("work_orders", []))
        inspections = tuple(item["id"] for item in neighborhood.get("inspections", []))

        # 3. Timeline from Canonical Observations
        timeline = self.get_asset_timeline(asset_id)

        # Build Profile
        profile = AssetIntelligenceProfile(
            asset_id=asset_id,
            equipment_tag=equipment_tag,
            name=name,
            asset_type=asset_type,
            documents=documents,
            failure_history=failures,
            maintenance_history=work_orders,
            inspection_history=inspections,
            timeline=timeline,
            graph_neighborhood=neighborhood,
            last_updated=datetime.now(UTC),
            operational_status=AssetStatus.UNKNOWN,  # To be computed by Measurement/Decision layer
            risk_level=RiskLevel.UNKNOWN,            # To be computed
        )
        return profile

    def get_asset_timeline(self, asset_id: str) -> tuple[AssetTimelineEvent, ...]:
        """Reconstruct chronological timeline from canonical observations."""
        # In a real database, we would query by target=asset_id.
        # For the hackathon, we filter the in-memory store replay.
        observations = self._obs_store.replay()
        
        events: list[AssetTimelineEvent] = []
        for obs in observations:
            # Check if this observation targets our asset directly (or implicitly via equipment_tag)
            # In our simplistic adapter, we linked some by entity ID (e.g., WO-999)
            # A full implementation would resolve WO-999 -> Asset in the graph
            # For demonstration, we just pull events that mention the asset_id or related documents.
            is_related = False
            
            # Direct target
            for t in obs.targets:
                if t.id == asset_id:
                    is_related = True
                    break
                    
            # Indirect via document
            if not is_related and obs.provenance.source_record_id:
                # Is this document in the asset's neighborhood?
                neighborhood = self._graph_manager.get_asset_neighborhood(asset_id)
                docs = {d["id"] for d in neighborhood.get("documents", [])}
                if obs.provenance.source_record_id in docs:
                    is_related = True

            if is_related:
                # Add to timeline
                desc = f"Observed {obs.observation_type.value}"
                if hasattr(obs.facts, "description") and getattr(obs.facts, "description"):
                    desc = getattr(obs.facts, "description")
                elif hasattr(obs.facts, "findings") and getattr(obs.facts, "findings"):
                    desc = " ".join(getattr(obs.facts, "findings"))
                metadata = {}
                if hasattr(obs.facts, "inspector") and obs.facts.inspector: # type: ignore
                    metadata["inspector"] = obs.facts.inspector # type: ignore
                if hasattr(obs.facts, "technician") and obs.facts.technician: # type: ignore
                    metadata["technician"] = obs.facts.technician # type: ignore
                    
                events.append(
                    AssetTimelineEvent(
                        event_id=obs.observation_id,
                        event_type=obs.observation_type.value,
                        date=obs.timestamp,
                        description=desc,
                        source_document_id=obs.provenance.source_record_id,
                        metadata=metadata,
                    )
                )

        # Sort chronological
        events.sort(key=lambda e: e.date)
        return tuple(events)

    def get_asset_failures(self, asset_id: str) -> tuple[str, ...]:
        profile = self.get_asset_profile(asset_id)
        return profile.failure_history if profile else ()

    def get_asset_maintenance_history(self, asset_id: str) -> tuple[str, ...]:
        profile = self.get_asset_profile(asset_id)
        return profile.maintenance_history if profile else ()

    def get_asset_inspections(self, asset_id: str) -> tuple[str, ...]:
        profile = self.get_asset_profile(asset_id)
        return profile.inspection_history if profile else ()

    def get_asset_documents(self, asset_id: str) -> tuple[str, ...]:
        profile = self.get_asset_profile(asset_id)
        return profile.documents if profile else ()
