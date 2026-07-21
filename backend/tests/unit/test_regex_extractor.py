import pytest
from app.extraction.entities.regex_extractor import RegexExtractor

def test_regex_extractor_equipment_tags():
    extractor = RegexExtractor()
    
    # Valid tags
    text = "P-101 failed, check V-204 and HX-001."
    entities = extractor.extract(text)
    tags = [e.value for e in entities if e.entity_type == "equipment_tag"]
    assert "P-101" in tags
    assert "V-204" in tags
    assert "HX-001" in tags

def test_regex_extractor_excludes_non_assets():
    extractor = RegexExtractor()
    
    # Excluded tags
    text = "Incident IN-001 and IR-002 reported in EV-005 and LOG-040."
    entities = extractor.extract(text)
    tags = [e.value for e in entities if e.entity_type == "equipment_tag"]
    
    # None of these should be classified as equipment_tag
    assert "IN-001" not in tags
    assert "IR-002" not in tags
    assert "EV-005" not in tags
    assert "LOG-040" not in tags
