# Evidence Platform Developer Guide

## Rule Of The Road

The production pipeline is:

```text
Observation -> Measurement -> Evidence -> Expertise -> Reasoning -> Decision
```

Do not add direct Measurement-to-Expertise dependencies. Evidence is the
contract boundary.

## Generating Evidence

```python
from app.evidence import EvidenceContext
from app.evidence import EvidenceSynthesisEngine

context = EvidenceContext(tenant_id="tenant-a")
package = EvidenceSynthesisEngine().synthesize(
    measurements,
    context,
)

expertise_input = package.for_expertise()
```

`measurements` must come from the Measurement Operating System after
normalization, validation, confidence estimation, uncertainty modeling, and
quality scoring.

## Adding An Evidence Definition

Add an `EvidenceDefinition` to an `EvidenceKnowledgeBase` or ship it through an
`EvidencePack`.

Definitions must include:

- semantic meaning
- triggering conditions
- required and optional measurements
- synthesis rules
- confidence strategy
- validation rules
- interpretation
- standards references
- business interpretation
- known limitations
- version history

## Adding Ontology Concepts

Use `EvidenceOntology.register_concept()` and
`EvidenceOntology.register_edge()` for plugin concepts and relationships.

Supported relationships include supports, contradicts, strengthens, weakens,
depends_on, derived_from, explains, caused_by, related_to, and impacts.

## Querying

```text
FIND Evidence
WHERE
confidence > 0.90
AND severity >= HIGH
ORDER BY priority DESC
```

Use `EqlParser` and `EqlEngine`, or `EvidenceApi.search()`.

## Testing

Run:

```text
python backend/scripts/test_evidence_platform.py
```

The test uses real MeasurementEngine output and verifies immutability,
validation, EQL, graph lineage, APIs, failed-measurement rejection, and
streaming replay.
