"""Entity Extraction Pipeline for PIA Industrial.

This package extracts industrial entities from document chunks
using a 4-layer architecture:
1. Regex extraction (equipment tags, dates, parameters)
2. Dictionary matching (failure modes, components, actions)
3. LLM-assisted extraction (complex entities, relationships)
4. Validation & resolution (schema check, normalization, dedup)

Rule: LLM-extracted entities are NEVER trusted facts.
They must pass through validation before entering the graph.
"""
