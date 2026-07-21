"""Dictionary-based entity extractor.

Layer 2 extraction: matches known industrial terms against
pre-defined dictionaries. Lower confidence than regex (Layer 1)
but higher than LLM extraction (Layer 3).

Dictionaries:
- Equipment types (pump, valve, compressor, heat exchanger, etc.)
- Failure modes (bearing seizure, seal leak, corrosion, etc.)
- Component types (bearing, seal, impeller, shaft, etc.)
- Maintenance actions (replace, repair, inspect, lubricate, etc.)
- Inspection types (visual, vibration, ultrasonic, thermographic)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.extraction.entities.regex_extractor import ExtractedEntity


# ---------------------------------------------------------------------------
# Industrial Dictionaries
# ---------------------------------------------------------------------------

EQUIPMENT_TYPES: dict[str, list[str]] = {
    "centrifugal_pump": ["centrifugal pump", "centrifugal cooling pump", "centrifugal water pump"],
    "positive_displacement_pump": ["positive displacement pump", "reciprocating pump", "diaphragm pump"],
    "pump": ["pump", "booster pump", "feed pump", "sump pump"],
    "compressor": ["compressor", "gas compressor", "air compressor", "screw compressor"],
    "heat_exchanger": ["heat exchanger", "cooler", "condenser", "heater", "reboiler"],
    "valve": ["valve", "gate valve", "globe valve", "ball valve", "butterfly valve", "check valve", "relief valve", "control valve", "safety valve"],
    "vessel": ["vessel", "pressure vessel", "tank", "drum", "reactor", "column", "tower"],
    "motor": ["motor", "electric motor", "diesel engine"],
    "turbine": ["turbine", "steam turbine", "gas turbine"],
    "fan": ["fan", "blower", "exhaust fan"],
    "conveyor": ["conveyor", "belt conveyor", "screw conveyor"],
    "crane": ["crane", "hoist", "overhead crane"],
    "transformer": ["transformer", "power transformer"],
    "generator": ["generator", "diesel generator", "emergency generator"],
    "piping": ["piping", "pipeline", "pipe"],
    "instrument": ["instrument", "transmitter", "gauge", "analyzer", "sensor"],
}

FAILURE_MODES: dict[str, list[str]] = {
    "bearing_seizure": ["bearing seizure", "bearing seized", "bearing failure", "bearing seized up"],
    "bearing_degradation": ["bearing degradation", "bearing wear", "bearing deterioration"],
    "seal_leak": ["seal leak", "seal failure", "mechanical seal leak", "seal leaking"],
    "corrosion": ["corrosion", "corroded", "rusting", "rust", "pitting"],
    "erosion": ["erosion", "eroded", "impeller erosion", "cavitation erosion"],
    "fatigue": ["fatigue", "fatigue crack", "fatigue failure", "stress cracking"],
    "vibration": ["high vibration", "excessive vibration", "abnormal vibration", "vibration alarm"],
    "overheating": ["overheating", "overheated", "elevated temperature", "high temperature"],
    "misalignment": ["misalignment", "misaligned", "shaft misalignment"],
    "cavitation": ["cavitation", "cavitating"],
    "blockage": ["blockage", "blocked", "plugged", "clogged"],
    "electrical_fault": ["electrical fault", "electrical failure", "short circuit", "ground fault"],
    "instrument_failure": ["instrument failure", "transmitter failure", "sensor failure"],
    "lubrication_failure": ["lubrication failure", "lubrication degradation", "oil degradation", "lubrication issues"],
}

COMPONENT_TYPES: dict[str, list[str]] = {
    "bearing": ["bearing", "drive-end bearing", "non-drive-end bearing", "thrust bearing", "roller bearing", "ball bearing", "journal bearing"],
    "seal": ["seal", "mechanical seal", "o-ring", "gasket", "packing"],
    "impeller": ["impeller", "rotor", "runner"],
    "shaft": ["shaft", "drive shaft", "journal"],
    "coupling": ["coupling", "flexible coupling"],
    "gearbox": ["gearbox", "gear", "gearing"],
    "belt": ["belt", "drive belt", "v-belt"],
    "filter": ["filter", "oil filter", "air filter", "fuel filter"],
    "diaphragm": ["diaphragm"],
    "valve_internals": ["valve internals", "valve disc", "valve seat", "valve stem"],
    "electrical": ["winding", "stator", "rotor winding", "circuit breaker"],
}

MAINTENANCE_ACTIONS: dict[str, list[str]] = {
    "replace": ["replace", "replacement", "replaced"],
    "repair": ["repair", "repaired", "repaired"],
    "inspect": ["inspect", "inspected", "inspection"],
    "lubricate": ["lubricate", "lubricated", "lubrication", "greased", "oiled"],
    "overhaul": ["overhaul", "overhauled", "major overhaul"],
    "calibrate": ["calibrate", "calibrated", "calibration"],
    "clean": ["clean", "cleaned", "cleaning", "flushed"],
    "align": ["align", "aligned", "alignment", "realigned"],
    "tighten": ["tighten", "tightened", "torqued"],
    "balance": ["balance", "balanced", "balancing"],
    "test": ["test", "tested", "testing", "pressure test"],
    "monitor": ["monitor", "monitored", "monitoring"],
}

INSPECTION_TYPES: dict[str, list[str]] = {
    "visual": ["visual inspection", "visual"],
    "vibration": ["vibration analysis", "vibration monitoring", "vibration check", "vibration measurement"],
    "ultrasonic": ["ultrasonic inspection", "ultrasonic testing", "UT"],
    "thermographic": ["thermographic", "thermal imaging", "infrared inspection", "thermography"],
    "oil_analysis": ["oil analysis", "lubricant analysis", "oil sample"],
    "thickness": ["thickness measurement", "thickness testing", "wall thickness"],
    "radiographic": ["radiographic inspection", "radiography", "x-ray"],
    "magnetic_particle": ["magnetic particle inspection", "MPI", "magnetic particle testing"],
    "dye_penetrant": ["dye penetrant inspection", "DPI", "liquid penetrant"],
}


class DictionaryExtractor:
    """Dictionary-based entity extraction.

    Matches known industrial terms against pre-defined
    dictionaries. Uses case-insensitive word boundary matching.
    """

    def __init__(self) -> None:
        self._compiled_patterns: dict[str, dict[str, re.Pattern]] = {}
        self._compile_all()

    def _compile_all(self) -> None:
        """Pre-compile all dictionary patterns for performance."""
        dictionaries = {
            "equipment_type": EQUIPMENT_TYPES,
            "failure_mode": FAILURE_MODES,
            "component_type": COMPONENT_TYPES,
            "maintenance_action": MAINTENANCE_ACTIONS,
            "inspection_type": INSPECTION_TYPES,
        }

        for entity_type, dictionary in dictionaries.items():
            self._compiled_patterns[entity_type] = {}
            for canonical_name, synonyms in dictionary.items():
                # Sort by length descending to match longest first
                sorted_synonyms = sorted(synonyms, key=len, reverse=True)
                pattern_str = "|".join(
                    re.escape(s) for s in sorted_synonyms
                )
                self._compiled_patterns[entity_type][canonical_name] = re.compile(
                    rf'\b({pattern_str})\b',
                    re.IGNORECASE,
                )

    def extract(self, text: str) -> list[ExtractedEntity]:
        """Extract all dictionary-matched entities from text."""
        entities: list[ExtractedEntity] = []
        seen: set[tuple[str, int, int]] = set()  # dedup by (type, start, end)

        for entity_type, patterns in self._compiled_patterns.items():
            for canonical_name, pattern in patterns.items():
                for match in pattern.finditer(text):
                    key = (entity_type, match.start(), match.end())
                    if key in seen:
                        continue
                    seen.add(key)

                    entities.append(ExtractedEntity(
                        entity_type=entity_type,
                        value=canonical_name,
                        raw_text=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.80,
                        extraction_method="dictionary",
                        metadata={"matched_term": match.group(0).lower()},
                    ))

        return entities
