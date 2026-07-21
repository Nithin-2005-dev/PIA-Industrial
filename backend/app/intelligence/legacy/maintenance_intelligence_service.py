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
                
                # Deterministic confidence calculation:
                #   base:      min(occurrences / 5, 1.0) * 0.7   — more events = higher confidence, caps at 5
                #   diversity: min(unique_docs / 3, 1.0) * 0.2   — independent sources increase confidence
                #   temporal:  0.1 if events span > 1 day         — spread over time = not a single-event anomaly
                unique_docs = len(set(e.source_document_id for e in events if e.source_document_id))
                time_span_days = (events[-1].date - events[0].date).days if len(events) > 1 else 0
                
                base_confidence = min(len(events) / 5, 1.0) * 0.7
                diversity_bonus = min(unique_docs / 3, 1.0) * 0.2
                temporal_bonus = 0.1 if time_span_days > 1 else 0.0
                confidence = round(base_confidence + diversity_bonus + temporal_bonus, 2)
                
                pattern = FailurePattern(
                    pattern_id=str(uuid4()),
                    asset_id=asset_id,
                    failure_mode=mode,
                    frequency_days=avg_freq,
                    occurrences=len(events),
                    confidence=confidence,
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
                last_inspection = event
            elif event.event_type == ObservationType.WORK_ORDER.value:
                if "DEFERRED" in event.description:
                    deferred.append(
                        DeferredRecommendation(
                            finding_id=str(uuid4()),
                            asset_id=asset_id,
                            description=f"Deferred maintenance: {event.description}",
                            recommended_date=event.date,
                            days_overdue=0,
                            severity="MEDIUM",
                            confidence=0.8,
                            source_document_id=event.source_document_id,
                        )
                    )
                # Any work order clears the last inspection for the heuristic
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
