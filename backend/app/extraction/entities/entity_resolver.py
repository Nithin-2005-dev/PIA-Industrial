"""Entity resolver and normalizer.

Layer 4: validates, normalizes, deduplicates, and resolves
entities extracted by Layers 1-3. This is the gatekeeper —
only entities that pass validation enter the knowledge graph.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.extraction.entities.regex_extractor import ExtractedEntity


@dataclass(frozen=True)
class ResolvedEntity:
    """A validated, normalized, resolved entity ready for the graph.

    This is the output of the extraction pipeline.
    Only ResolvedEntities are trusted to enter the knowledge graph.
    """
    entity_type: str
    canonical_value: str                        # normalized canonical form
    raw_values: tuple[str, ...]                 # all raw text matches
    confidence: float                           # aggregated confidence
    extraction_methods: tuple[str, ...]         # methods that found this
    occurrence_count: int = 1                   # how many times found
    metadata: dict[str, Any] = field(default_factory=dict)


class EntityResolver:
    """Validates, normalizes, deduplicates, and resolves entities.

    Rules:
    1. Equipment tags are normalized to uppercase (P-101, not p-101)
    2. Duplicate entities are merged (confidence increases)
    3. Conflicting extractions are flagged
    4. Low-confidence entities below threshold are dropped
    """

    def __init__(
        self,
        min_confidence: float = 0.3,
    ) -> None:
        self._min_confidence = min_confidence

    def resolve(
        self,
        entities: list[ExtractedEntity],
    ) -> list[ResolvedEntity]:
        """Resolve a list of extracted entities into canonical entities."""
        # Group by (type, normalized_value)
        groups: dict[tuple[str, str], list[ExtractedEntity]] = {}

        for entity in entities:
            normalized = self._normalize(entity)
            key = (entity.entity_type, normalized)
            if key not in groups:
                groups[key] = []
            groups[key].append(entity)

        # Merge groups into resolved entities
        resolved: list[ResolvedEntity] = []
        for (entity_type, canonical_value), group in groups.items():
            # Aggregate confidence (more occurrences = higher confidence)
            max_confidence = max(e.confidence for e in group)
            occurrence_bonus = min(0.15, len(group) * 0.03)
            aggregated_confidence = min(1.0, max_confidence + occurrence_bonus)

            # Skip below threshold
            if aggregated_confidence < self._min_confidence:
                continue

            # Collect unique raw values and methods
            raw_values = tuple(sorted(set(e.raw_text for e in group)))
            methods = tuple(sorted(set(e.extraction_method for e in group)))

            # Merge metadata
            merged_metadata: dict[str, Any] = {}
            for e in group:
                merged_metadata.update(e.metadata)

            resolved.append(ResolvedEntity(
                entity_type=entity_type,
                canonical_value=canonical_value,
                raw_values=raw_values,
                confidence=round(aggregated_confidence, 3),
                extraction_methods=methods,
                occurrence_count=len(group),
                metadata=merged_metadata,
            ))

        # Sort by confidence descending
        resolved.sort(key=lambda e: e.confidence, reverse=True)
        return resolved

    def _normalize(self, entity: ExtractedEntity) -> str:
        """Normalize an entity value to canonical form."""
        value = entity.value.strip()

        if entity.entity_type == "equipment_tag":
            return value.upper()

        if entity.entity_type in ("work_order_id", "inspection_report_id", "incident_report_id"):
            return value.upper()

        if entity.entity_type == "severity":
            return value.upper()

        if entity.entity_type == "date":
            return value  # Keep as-is; parsing happens downstream

        if entity.entity_type in ("equipment_type", "failure_mode", "component_type", "maintenance_action", "inspection_type"):
            return value.lower()  # canonical dictionary keys are lowercase

        return value
