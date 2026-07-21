"""Compliance Intelligence Service.

Detects compliance gaps and compiles evidence packages based on
regulatory requirements and canonical inspection history.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.industrial.compliance_intelligence import (
    ComplianceEvidencePackage,
    ComplianceGap,
    InspectionRequirement,
    Regulation,
)
from app.intelligence.legacy.asset_intelligence_service import AssetIntelligenceService
from app.ingestion.observation.domain import ObservationType

logger = logging.getLogger(__name__)


# Mocked rules for the prototype
API_REGULATIONS = [
    Regulation(
        regulation_id="API-610",
        name="Centrifugal Pumps for Petroleum, Petrochemical and Natural Gas Industries",
        authority="API",
        description="Standard for centrifugal pumps.",
    )
]

INSPECTION_REQUIREMENTS = [
    InspectionRequirement(
        requirement_id="REQ-API610-1",
        asset_type="Pump",
        regulation_id="API-610",
        frequency_days=365,
        required_inspection_type="Vibration Analysis",
        description="Annual vibration and performance inspection.",
    )
]


class ComplianceIntelligenceService:
    """Service to evaluate compliance of industrial assets."""

    def __init__(self, asset_service: AssetIntelligenceService):
        self._asset_service = asset_service
        self._requirements = INSPECTION_REQUIREMENTS

    def evaluate_compliance(self, asset_id: str) -> ComplianceEvidencePackage:
        """Check asset history against requirements and return an evidence package."""
        profile = self._asset_service.get_asset_profile(asset_id)
        if not profile:
            raise ValueError(f"Asset {asset_id} not found.")

        timeline = self._asset_service.get_asset_timeline(asset_id)
        
        # Filter for inspections
        inspections = [e for e in timeline if e.event_type == ObservationType.INSPECTION_EVENT.value]
        inspections.sort(key=lambda x: x.date, reverse=True)
        
        gaps: list[ComplianceGap] = []
        docs: set[str] = set()

        for req in self._requirements:
            # Check applicability
            if req.asset_type.lower() not in profile.asset_type.lower():
                continue
                
            # Find the latest matching inspection
            # For this MVP, we assume any inspection satisfies the requirement if it exists
            # In a full version, we'd check req.required_inspection_type against the inspection's type
            latest_inspection = inspections[0] if inspections else None
            
            if not latest_inspection:
                gaps.append(ComplianceGap(
                    gap_id=str(uuid4()),
                    asset_id=asset_id,
                    requirement_id=req.requirement_id,
                    status="MISSING_EVIDENCE",
                    severity="HIGH",
                ))
            else:
                days_since = (datetime.now(UTC) - latest_inspection.date).days
                if latest_inspection.source_document_id:
                    docs.add(latest_inspection.source_document_id)
                    
                if days_since > req.frequency_days:
                    gaps.append(ComplianceGap(
                        gap_id=str(uuid4()),
                        asset_id=asset_id,
                        requirement_id=req.requirement_id,
                        status="OVERDUE",
                        days_overdue=days_since - req.frequency_days,
                        last_inspection_date=latest_inspection.date,
                        last_inspection_doc_id=latest_inspection.source_document_id,
                        severity="CRITICAL",
                    ))

        return ComplianceEvidencePackage(
            asset_id=asset_id,
            generated_at=datetime.now(UTC),
            compliant=len(gaps) == 0,
            gaps=tuple(gaps),
            supporting_documents=tuple(docs),
        )
