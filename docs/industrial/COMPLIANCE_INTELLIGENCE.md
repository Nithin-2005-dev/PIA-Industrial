# Compliance Intelligence

The `ComplianceIntelligenceService` ensures that regulatory checks and inspection mandates are evaluated mathematically against the factual record.

## Status Model

When an asset is evaluated against a compliance protocol (e.g., "Quarterly Seal Inspection"), the engine traverses the Knowledge Graph to find the most recent matching `Observation`.

It returns one of the following exact statuses:
- `COMPLIANT`: Evidence exists and is within the required temporal window.
- `PARTIALLY_COMPLIANT`: Evidence exists but lacks required metadata (e.g., signature missing).
- `MISSING_EVIDENCE`: No matching observation exists in the graph.
- `OVERDUE`: Evidence exists, but the temporal window has expired.
- `NON_COMPLIANT`: Explicit evidence of regulatory failure was recorded.
- `UNKNOWN`: The protocol itself is malformed or unmappable.

**Important Distinction:** `MISSING_EVIDENCE` != `NON_COMPLIANT`. The system strictly differentiates between "we do not have the document" and "the document proves we failed."

## Limitations

- The regulatory scope is limited to internal scheduling compliance as derived from ingested maintenance manuals. It does not actively cross-reference external governmental OSHA/EPA databases in this prototype.
