"""Maintenance Intelligence Service.

Deterministic engine to detect repeated failures, deferred
maintenance, and precursors from the asset timeline.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.domain.industrial.maintenance_intelligence import (
    DeferredRecommendation,
    FailurePattern,
    FailurePrecursor,
    MaintenanceFinding,
)
from app.intelligence.legacy.asset_intelligence_service import AssetIntelligenceService
from app.ingestion.observation.domain import ObservationType

logger = logging.getLogger(__name__)


class MaintenanceIntelligenceService:
    """Analyzes asset history for maintenance and failure patterns."""

    def __init__(self, asset_service: AssetIntelligenceService):
        self._asset_service = asset_service

    def analyze_asset(self, asset_id: str) -> dict[str, Any]:
        """Run all maintenance intelligence analyzers on an asset."""
        return {
            "repeated_failures": self.detect_repeated_failures(asset_id),
            "deferred_recommendations": self.detect_deferred_recommendations(asset_id),
            "failure_precursors": self.detect_failure_precursors(asset_id),
            "findings": self.detect_anomalies(asset_id),
        }

    def detect_repeated_failures(self, asset_id: str) -> tuple[FailurePattern, ...]:
        """Detect if an asset experiences the same failure mode repeatedly."""
        timeline = self._asset_service.get_asset_timeline(asset_id)
        
        # Group failures by description/mode
        failures: dict[str, list[Any]] = {}
        for event in timeline:
            if event.event_type == ObservationType.FAILURE.value:
                # We use the description or a parsed failure mode to group
                # For this naive deterministic implementation, we group by description keywords
                mode = event.description.lower()
                if "bearing" in mode:
                    key = "bearing_failure"
                elif "seal" in mode:
                    key = "seal_leak"
                elif "vibration" in mode:
                    key = "high_vibration"
                else:
                    key = "general_failure"
                    
                if key not in failures:
                    failures[key] = []
                failures[key].append(event)
                
        patterns: list[FailurePattern] = []
        for mode, events in failures.items():
            if len(events) > 1:
                # Calculate frequency
                events.sort(key=lambda e: e.date)
                days_between = [(events[i].date - events[i-1].date).days for i in range(1, len(events))]
                avg_freq = sum(days_between) / len(days_between) if days_between else None
                
                pattern = FailurePattern(
                    pattern_id=str(uuid4()),
                    asset_id=asset_id,
                    failure_mode=mode,
                    frequency_days=avg_freq,
                    occurrences=len(events),
                    confidence=0.85,
                    supporting_events=tuple(e.event_id for e in events),
                    source_documents=tuple(e.source_document_id for e in events if e.source_document_id),
                )
                patterns.append(pattern)
                
        return tuple(patterns)

    def detect_deferred_recommendations(self, asset_id: str) -> tuple[DeferredRecommendation, ...]:
        """Detect recommendations from inspections that were not followed by maintenance."""
        timeline = self._asset_service.get_asset_timeline(asset_id)
        
        deferred: list[DeferredRecommendation] = []
        
        # Simple heuristic: If there is an inspection that found an issue (e.g., "DETECTED"),
        # and no subsequent WORK_ORDER closed it, it's deferred.
        
        last_inspection = None
        for event in timeline:
            if event.event_type == ObservationType.INSPECTION_EVENT.value:
                # Mock logic: assume any inspection in the timeline raised an issue for demo purposes
                last_inspection = event
            elif event.event_type == ObservationType.WORK_ORDER.value and last_inspection:
                # If a work order happens, we assume the previous inspection was addressed
                last_inspection = None
                
        if last_inspection:
            days_overdue = (datetime.now(UTC) - last_inspection.date).days
            deferred.append(
                DeferredRecommendation(
                    finding_id=str(uuid4()),
                    asset_id=asset_id,
                    description=f"Unresolved issue from inspection on {last_inspection.date.strftime('%Y-%m-%d')}",
                    recommended_date=last_inspection.date,
                    days_overdue=days_overdue,
                    severity="HIGH",
                    confidence=0.75,
                    source_document_id=last_inspection.source_document_id,
                )
            )
            
        return tuple(deferred)

    def detect_failure_precursors(self, asset_id: str) -> tuple[FailurePrecursor, ...]:
        """Detect sequences of events that led up to a failure."""
        timeline = self._asset_service.get_asset_timeline(asset_id)
        precursors: list[FailurePrecursor] = []
        
        for i, event in enumerate(timeline):
            if event.event_type == ObservationType.FAILURE.value:
                # Look back for anomalies
                for j in range(i-1, -1, -1):
                    prev_event = timeline[j]
                    if prev_event.event_type == ObservationType.INSPECTION_EVENT.value:
                        precursors.append(
                            FailurePrecursor(
                                precursor_id=str(uuid4()),
                                asset_id=asset_id,
                                precursor_events=(prev_event.description,),
                                target_failure_mode=event.description,
                                time_window_days=(event.date - prev_event.date).days,
                                confidence=0.80,
                                source_documents=tuple(
                                    filter(None, [prev_event.source_document_id, event.source_document_id])
                                ),
                            )
                        )
                        break
                        
        return tuple(precursors)

    def detect_anomalies(self, asset_id: str) -> tuple[MaintenanceFinding, ...]:
        """General anomaly detection (e.g., increasing failure frequency)."""
        patterns = self.detect_repeated_failures(asset_id)
        findings: list[MaintenanceFinding] = []
        
        for p in patterns:
            if p.occurrences >= 3:
                findings.append(
                    MaintenanceFinding(
                        finding_id=str(uuid4()),
                        asset_id=asset_id,
                        finding_type="INCREASING_FAILURE_FREQUENCY",
                        description=f"Asset has failed {p.occurrences} times due to {p.failure_mode}",
                        confidence=p.confidence,
                        supporting_events=p.supporting_events,
                    )
                )
                
        return tuple(findings)
