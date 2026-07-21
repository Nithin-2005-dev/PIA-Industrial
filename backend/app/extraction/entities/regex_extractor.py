"""Regex-based entity extractor.

Deterministic extraction of structured entities from text using
regular expressions. This is Layer 1 — the highest-confidence
extraction method.

Extracts:
- Equipment tags (P-101, V-204, C-301, etc.)
- Dates and timestamps
- Numeric parameters with units (8.5 mm/s, 82°C, 150 bar)
- Work order IDs, report IDs
- Standard/regulation codes (API 510, OSHA 1910.119)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExtractedEntity:
    """An entity extracted from text with provenance."""
    entity_type: str                            # "equipment_tag", "date", "parameter", etc.
    value: str                                  # the extracted value
    raw_text: str                               # the original text span
    start_pos: int = 0                          # start position in source text
    end_pos: int = 0                            # end position in source text
    confidence: float = 1.0                     # extraction confidence
    extraction_method: str = "regex"            # how it was extracted
    metadata: dict[str, Any] = field(default_factory=dict)


class RegexExtractor:
    """Deterministic entity extraction using regular expressions.

    This is the highest-confidence extractor.
    Equipment tags, dates, and parameter readings are
    structurally defined and can be extracted with certainty.
    """

    # Equipment tag patterns (ISA format: letter(s) + dash + numbers)
    # Matches: P-101, V-204, C-301, HX-001, FV-102A, etc.
    EQUIPMENT_TAG_PATTERN = re.compile(
        r'\b([A-Z]{1,4}-\d{2,5}[A-Z]?)\b'
    )

    # Work order / report ID patterns
    WORK_ORDER_PATTERN = re.compile(
        r'\b(WO-\d{2,6})\b', re.IGNORECASE
    )
    INSPECTION_REPORT_PATTERN = re.compile(
        r'\b(IR-\d{2,6})\b', re.IGNORECASE
    )
    INCIDENT_REPORT_PATTERN = re.compile(
        r'\b(IN-\d{2,6})\b', re.IGNORECASE
    )

    # Date patterns
    DATE_PATTERN = re.compile(
        r'\b(\d{4}-\d{2}-\d{2})\b'             # ISO format: 2024-01-15
    )
    DATE_PATTERN_SLASH = re.compile(
        r'\b(\d{1,2}/\d{1,2}/\d{4})\b'         # US format: 1/15/2024
    )

    # Numeric parameter with unit
    # Matches: 8.5 mm/s, 82°C, 150 bar, 3.2 MPa
    PARAMETER_PATTERN = re.compile(
        r'\b(\d+\.?\d*)\s*(mm/s|m/s|°C|°F|bar|psi|MPa|kPa|rpm|Hz|kW|MW|hours?|hrs?|days?)\b',
        re.IGNORECASE,
    )

    # Standard/regulation codes
    STANDARD_PATTERN = re.compile(
        r'\b(API\s*\d{3,4}|ASME\s*[A-Z][\w.]+|OSHA\s*\d[\d.]+|ISO\s*\d{4,6}|NFPA\s*\d{2,4})\b',
        re.IGNORECASE,
    )

    # Severity keywords
    SEVERITY_PATTERN = re.compile(
        r'\b(CRITICAL|MAJOR|MODERATE|MINOR|NEGLIGIBLE|EMERGENCY|URGENT|ALARM|ELEVATED|NORMAL|SATISFACTORY|UNSATISFACTORY)\b',
        re.IGNORECASE,
    )

    def extract(self, text: str) -> list[ExtractedEntity]:
        """Extract all deterministic entities from text."""
        entities: list[ExtractedEntity] = []

        entities.extend(self._extract_equipment_tags(text))
        entities.extend(self._extract_work_orders(text))
        entities.extend(self._extract_report_ids(text))
        entities.extend(self._extract_dates(text))
        entities.extend(self._extract_parameters(text))
        entities.extend(self._extract_standards(text))
        entities.extend(self._extract_severities(text))

        return entities

    def _extract_equipment_tags(self, text: str) -> list[ExtractedEntity]:
        entities = []
        for match in self.EQUIPMENT_TAG_PATTERN.finditer(text):
            prefix = match.group(1).split("-", 1)[0].upper()
            if prefix in {"WO", "IR", "IN", "DOC"}:
                continue
            entities.append(ExtractedEntity(
                entity_type="equipment_tag",
                value=match.group(1),
                raw_text=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.95,
                extraction_method="regex",
                metadata={"pattern": "equipment_tag"},
            ))
        return entities

    def _extract_work_orders(self, text: str) -> list[ExtractedEntity]:
        entities = []
        for match in self.WORK_ORDER_PATTERN.finditer(text):
            entities.append(ExtractedEntity(
                entity_type="work_order_id",
                value=match.group(1).upper(),
                raw_text=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.98,
                extraction_method="regex",
            ))
        return entities

    def _extract_report_ids(self, text: str) -> list[ExtractedEntity]:
        entities = []
        for match in self.INSPECTION_REPORT_PATTERN.finditer(text):
            entities.append(ExtractedEntity(
                entity_type="inspection_report_id",
                value=match.group(1).upper(),
                raw_text=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.98,
                extraction_method="regex",
            ))
        for match in self.INCIDENT_REPORT_PATTERN.finditer(text):
            entities.append(ExtractedEntity(
                entity_type="incident_report_id",
                value=match.group(1).upper(),
                raw_text=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.98,
                extraction_method="regex",
            ))
        return entities

    def _extract_dates(self, text: str) -> list[ExtractedEntity]:
        entities = []
        for match in self.DATE_PATTERN.finditer(text):
            entities.append(ExtractedEntity(
                entity_type="date",
                value=match.group(1),
                raw_text=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.95,
                extraction_method="regex",
            ))
        for match in self.DATE_PATTERN_SLASH.finditer(text):
            entities.append(ExtractedEntity(
                entity_type="date",
                value=match.group(1),
                raw_text=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.90,
                extraction_method="regex",
            ))
        return entities

    def _extract_parameters(self, text: str) -> list[ExtractedEntity]:
        entities = []
        for match in self.PARAMETER_PATTERN.finditer(text):
            value = float(match.group(1))
            unit = match.group(2)
            entities.append(ExtractedEntity(
                entity_type="parameter_reading",
                value=f"{value} {unit}",
                raw_text=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.90,
                extraction_method="regex",
                metadata={"numeric_value": value, "unit": unit},
            ))
        return entities

    def _extract_standards(self, text: str) -> list[ExtractedEntity]:
        entities = []
        for match in self.STANDARD_PATTERN.finditer(text):
            entities.append(ExtractedEntity(
                entity_type="standard_code",
                value=match.group(1),
                raw_text=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.95,
                extraction_method="regex",
            ))
        return entities

    def _extract_severities(self, text: str) -> list[ExtractedEntity]:
        entities = []
        for match in self.SEVERITY_PATTERN.finditer(text):
            entities.append(ExtractedEntity(
                entity_type="severity",
                value=match.group(1).upper(),
                raw_text=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.85,
                extraction_method="regex",
            ))
        return entities
