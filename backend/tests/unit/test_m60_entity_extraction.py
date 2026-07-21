"""Tests for M60 — Entity Extraction Pipeline.

Validates:
1. Regex extraction (equipment tags, dates, parameters, IDs)
2. Dictionary extraction (equipment types, failure modes, components)
3. Entity resolution (normalization, dedup, confidence aggregation)
4. Full extraction pipeline (end-to-end)
5. Demo scenario extraction (P-101 story)
"""
from __future__ import annotations

import pytest


# Reuse the same demo texts from M59 tests
INSPECTION_TEXT = """
INSPECTION REPORT IR-104

Equipment: P-101 Centrifugal Cooling Water Pump
Location: Area A, Cooling Water System
Inspector: John Smith
Date: 2024-01-15

1. VIBRATION ANALYSIS
Drive-end bearing vibration reading: 8.5 mm/s (ALARM)
Non-drive-end bearing vibration reading: 3.2 mm/s (NORMAL)
Normal range: 0-7.0 mm/s per ISO 10816

2. TEMPERATURE READINGS
Drive-end bearing temperature: 82°C (ELEVATED)
Non-drive-end bearing temperature: 55°C (NORMAL)

3. FINDINGS
- High vibration on drive-end bearing exceeding alarm threshold
- Elevated temperature on drive-end bearing
- Pattern consistent with bearing degradation

4. RECOMMENDATIONS
- Replace drive-end bearing within 30 days
- Priority: URGENT
- Failure mode: Bearing degradation due to lubrication issues
""".strip()


INCIDENT_TEXT = """
INCIDENT REPORT IN-44

Equipment: P-101 Centrifugal Cooling Water Pump
Date: 2024-04-15
Severity: MAJOR

The drive-end bearing had seized completely, causing scoring
of the shaft journal. Work Order WO-291 for bearing replacement
was deferred. Inspection Report IR-104 identified high vibration.
Inspection Report IR-109 showed worsening trend.

Downtime: 48 hours
Repair cost: $4,500

Corrective: Emergency bearing replacement completed (WO-298).
""".strip()


MAINTENANCE_TEXT = """
work_order_id: WO-281, equipment_tag: P-101, title: Quarterly lubrication
work_order_id: WO-285, equipment_tag: P-101, title: Vibration check
work_order_id: WO-291, equipment_tag: P-101, title: Replace drive-end bearing, status: DEFERRED
work_order_id: WO-298, equipment_tag: P-101, title: Emergency bearing replacement
work_order_id: WO-295, equipment_tag: V-204, title: Valve inspection
""".strip()


# ---------------------------------------------------------------------------
# Tests: Regex Extractor
# ---------------------------------------------------------------------------

class TestRegexExtractor:
    def test_extract_equipment_tags(self):
        from app.extraction.entities.regex_extractor import RegexExtractor
        extractor = RegexExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        tags = [e for e in entities if e.entity_type == "equipment_tag"]
        tag_values = {e.value for e in tags}
        assert "P-101" in tag_values

    def test_extract_multiple_tags(self):
        from app.extraction.entities.regex_extractor import RegexExtractor
        extractor = RegexExtractor()
        entities = extractor.extract(MAINTENANCE_TEXT)
        tags = [e for e in entities if e.entity_type == "equipment_tag"]
        tag_values = {e.value for e in tags}
        assert "P-101" in tag_values
        assert "V-204" in tag_values

    def test_extract_dates(self):
        from app.extraction.entities.regex_extractor import RegexExtractor
        extractor = RegexExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        dates = [e for e in entities if e.entity_type == "date"]
        date_values = {e.value for e in dates}
        assert "2024-01-15" in date_values

    def test_extract_parameters(self):
        from app.extraction.entities.regex_extractor import RegexExtractor
        extractor = RegexExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        params = [e for e in entities if e.entity_type == "parameter_reading"]
        # Should find vibration readings and temperature readings
        assert len(params) >= 2
        param_values = {e.metadata.get("numeric_value") for e in params}
        assert 8.5 in param_values
        assert 3.2 in param_values

    def test_extract_work_orders(self):
        from app.extraction.entities.regex_extractor import RegexExtractor
        extractor = RegexExtractor()
        entities = extractor.extract(INCIDENT_TEXT)
        wos = [e for e in entities if e.entity_type == "work_order_id"]
        wo_values = {e.value for e in wos}
        assert "WO-291" in wo_values
        assert "WO-298" in wo_values

    def test_extract_report_ids(self):
        from app.extraction.entities.regex_extractor import RegexExtractor
        extractor = RegexExtractor()
        entities = extractor.extract(INCIDENT_TEXT)

        ir_ids = [e for e in entities if e.entity_type == "inspection_report_id"]
        assert len(ir_ids) >= 2
        ir_values = {e.value for e in ir_ids}
        assert "IR-104" in ir_values
        assert "IR-109" in ir_values

        in_ids = [e for e in entities if e.entity_type == "incident_report_id"]
        assert len(in_ids) >= 1
        in_values = {e.value for e in in_ids}
        assert "IN-44" in in_values

    def test_extract_severities(self):
        from app.extraction.entities.regex_extractor import RegexExtractor
        extractor = RegexExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        severities = [e for e in entities if e.entity_type == "severity"]
        sev_values = {e.value for e in severities}
        assert "ALARM" in sev_values
        assert "NORMAL" in sev_values
        assert "URGENT" in sev_values

    def test_extract_standards(self):
        from app.extraction.entities.regex_extractor import RegexExtractor
        extractor = RegexExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        standards = [e for e in entities if e.entity_type == "standard_code"]
        std_values = {e.value for e in standards}
        assert any("ISO" in v for v in std_values)

    def test_all_entities_have_positions(self):
        from app.extraction.entities.regex_extractor import RegexExtractor
        extractor = RegexExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        for entity in entities:
            assert entity.start_pos >= 0
            assert entity.end_pos > entity.start_pos
            assert entity.confidence > 0


# ---------------------------------------------------------------------------
# Tests: Dictionary Extractor
# ---------------------------------------------------------------------------

class TestDictionaryExtractor:
    def test_extract_equipment_types(self):
        from app.extraction.entities.dictionary_extractor import DictionaryExtractor
        extractor = DictionaryExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        eq_types = [e for e in entities if e.entity_type == "equipment_type"]
        eq_values = {e.value for e in eq_types}
        # "Centrifugal Cooling Water Pump" should match pump types
        assert any("pump" in v for v in eq_values)

    def test_extract_failure_modes(self):
        from app.extraction.entities.dictionary_extractor import DictionaryExtractor
        extractor = DictionaryExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        fm = [e for e in entities if e.entity_type == "failure_mode"]
        fm_values = {e.value for e in fm}
        # "high vibration" and "bearing degradation"
        assert "vibration" in fm_values or "bearing_degradation" in fm_values

    def test_extract_components(self):
        from app.extraction.entities.dictionary_extractor import DictionaryExtractor
        extractor = DictionaryExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        components = [e for e in entities if e.entity_type == "component_type"]
        comp_values = {e.value for e in components}
        assert "bearing" in comp_values

    def test_extract_maintenance_actions(self):
        from app.extraction.entities.dictionary_extractor import DictionaryExtractor
        extractor = DictionaryExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        actions = [e for e in entities if e.entity_type == "maintenance_action"]
        action_values = {e.value for e in actions}
        assert "replace" in action_values

    def test_extract_inspection_types(self):
        from app.extraction.entities.dictionary_extractor import DictionaryExtractor
        extractor = DictionaryExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        insp = [e for e in entities if e.entity_type == "inspection_type"]
        insp_values = {e.value for e in insp}
        assert "vibration" in insp_values

    def test_all_entities_have_confidence(self):
        from app.extraction.entities.dictionary_extractor import DictionaryExtractor
        extractor = DictionaryExtractor()
        entities = extractor.extract(INSPECTION_TEXT)
        for entity in entities:
            assert entity.confidence > 0
            assert entity.extraction_method == "dictionary"


# ---------------------------------------------------------------------------
# Tests: Entity Resolver
# ---------------------------------------------------------------------------

class TestEntityResolver:
    def test_normalize_equipment_tag(self):
        from app.extraction.entities.regex_extractor import ExtractedEntity
        from app.extraction.entities.entity_resolver import EntityResolver

        resolver = EntityResolver()
        entities = [
            ExtractedEntity("equipment_tag", "P-101", "P-101", confidence=0.95),
            ExtractedEntity("equipment_tag", "P-101", "P-101", confidence=0.95),
            ExtractedEntity("equipment_tag", "P-101", "P-101", confidence=0.95),
        ]
        resolved = resolver.resolve(entities)
        assert len(resolved) == 1
        assert resolved[0].canonical_value == "P-101"
        assert resolved[0].occurrence_count == 3
        # Confidence should be boosted by multiple occurrences
        assert resolved[0].confidence > 0.95

    def test_deduplicate_entities(self):
        from app.extraction.entities.regex_extractor import ExtractedEntity
        from app.extraction.entities.entity_resolver import EntityResolver

        resolver = EntityResolver()
        entities = [
            ExtractedEntity("failure_mode", "bearing_degradation", "bearing degradation", confidence=0.80, extraction_method="dictionary"),
            ExtractedEntity("failure_mode", "bearing_degradation", "bearing wear", confidence=0.80, extraction_method="dictionary"),
        ]
        resolved = resolver.resolve(entities)
        assert len(resolved) == 1
        assert resolved[0].occurrence_count == 2

    def test_filter_low_confidence(self):
        from app.extraction.entities.regex_extractor import ExtractedEntity
        from app.extraction.entities.entity_resolver import EntityResolver

        resolver = EntityResolver(min_confidence=0.5)
        entities = [
            ExtractedEntity("equipment_tag", "P-101", "P-101", confidence=0.95),
            ExtractedEntity("severity", "MINOR", "minor", confidence=0.1),
        ]
        resolved = resolver.resolve(entities)
        # Only P-101 should pass (severity is below threshold)
        resolved_types = {e.entity_type for e in resolved}
        assert "equipment_tag" in resolved_types

    def test_merge_methods(self):
        from app.extraction.entities.regex_extractor import ExtractedEntity
        from app.extraction.entities.entity_resolver import EntityResolver

        resolver = EntityResolver()
        entities = [
            ExtractedEntity("component_type", "bearing", "bearing", confidence=0.90, extraction_method="regex"),
            ExtractedEntity("component_type", "bearing", "drive-end bearing", confidence=0.80, extraction_method="dictionary"),
        ]
        resolved = resolver.resolve(entities)
        assert len(resolved) == 1
        assert "regex" in resolved[0].extraction_methods
        assert "dictionary" in resolved[0].extraction_methods


# ---------------------------------------------------------------------------
# Tests: Full Extraction Pipeline
# ---------------------------------------------------------------------------

class TestExtractionPipeline:
    def test_extract_from_text(self):
        from app.extraction.entities.extraction_pipeline import ExtractionPipeline
        pipeline = ExtractionPipeline()
        resolved = pipeline.extract_from_text(INSPECTION_TEXT)

        # Should find key entities
        entity_types = {e.entity_type for e in resolved}
        assert "equipment_tag" in entity_types
        assert "component_type" in entity_types

        # P-101 should be found
        tags = [e for e in resolved if e.entity_type == "equipment_tag"]
        assert any(e.canonical_value == "P-101" for e in tags)

    def test_extract_from_chunks(self):
        from app.domain.industrial.document import DocumentChunk, DocumentProvenance
        from app.extraction.entities.extraction_pipeline import ExtractionPipeline

        chunks = [
            DocumentChunk(
                chunk_id="c1", document_id="DOC-001",
                content=INSPECTION_TEXT, page_number=1,
                provenance=DocumentProvenance(
                    document_id="DOC-001", document_name="IR-104.txt",
                    document_type="INSPECTION_REPORT",
                ),
            ),
            DocumentChunk(
                chunk_id="c2", document_id="DOC-001",
                content=INCIDENT_TEXT, page_number=2,
                provenance=DocumentProvenance(
                    document_id="DOC-001", document_name="IN-44.txt",
                    document_type="INCIDENT_REPORT",
                ),
            ),
        ]

        pipeline = ExtractionPipeline()
        result = pipeline.extract_from_chunks(chunks, "DOC-001")

        assert result.document_id == "DOC-001"
        assert len(result.chunk_results) == 2
        assert len(result.all_resolved_entities) > 0
        assert "equipment_tag" in result.entity_summary

    def test_demo_scenario_extraction(self):
        """Simulate the hackathon demo: extract from the P-101 documents."""
        from app.extraction.entities.extraction_pipeline import ExtractionPipeline

        pipeline = ExtractionPipeline()

        # Extract from all three document types
        inspection_entities = pipeline.extract_from_text(INSPECTION_TEXT)
        incident_entities = pipeline.extract_from_text(INCIDENT_TEXT)
        maintenance_entities = pipeline.extract_from_text(MAINTENANCE_TEXT)

        # P-101 found in all three
        for entities in [inspection_entities, incident_entities, maintenance_entities]:
            tags = [e for e in entities if e.entity_type == "equipment_tag"]
            assert any(e.canonical_value == "P-101" for e in tags)

        # Key entities from inspection
        insp_types = {e.entity_type for e in inspection_entities}
        assert "parameter_reading" in insp_types  # 8.5 mm/s, 82°C etc.
        assert "component_type" in insp_types      # bearing
        assert "date" in insp_types                # 2024-01-15

        # Key entities from incident
        incident_types = {e.entity_type for e in incident_entities}
        assert "work_order_id" in incident_types   # WO-291, WO-298
        assert "inspection_report_id" in incident_types  # IR-104, IR-109

        # Key entities from maintenance
        maint_types = {e.entity_type for e in maintenance_entities}
        assert "work_order_id" in maint_types      # WO-281, WO-285, etc.

        # Cross-document entity linking
        # WO-291 should appear in both incident and maintenance extractions
        incident_wos = {e.canonical_value for e in incident_entities if e.entity_type == "work_order_id"}
        maint_wos = {e.canonical_value for e in maintenance_entities if e.entity_type == "work_order_id"}
        assert "WO-291" in incident_wos
        assert "WO-291" in maint_wos
        # This is how the graph connects the incident to the deferred work order!

    def test_entity_summary(self):
        from app.domain.industrial.document import DocumentChunk, DocumentProvenance
        from app.extraction.entities.extraction_pipeline import ExtractionPipeline

        chunks = [
            DocumentChunk(
                chunk_id="c1", document_id="DOC-001",
                content=INSPECTION_TEXT, page_number=1,
                provenance=DocumentProvenance(
                    document_id="DOC-001", document_name="IR-104.txt",
                    document_type="INSPECTION_REPORT",
                ),
            ),
        ]

        pipeline = ExtractionPipeline()
        result = pipeline.extract_from_chunks(chunks, "DOC-001")

        # Summary should count entity types
        assert isinstance(result.entity_summary, dict)
        assert sum(result.entity_summary.values()) == len(result.all_resolved_entities)
