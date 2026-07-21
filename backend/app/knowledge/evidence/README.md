# Evidence Intelligence Platform

`app.evidence` turns validated measurements into immutable, explainable
evidence for Expertise.

Use `EvidenceSynthesisEngine` or `EvidenceApi.generate()` with Measurement
Layer outputs. The package rejects failed or not-run measurements at intake and
only exposes validated evidence through `EvidencePackage.for_expertise()`.

```text
Measurement -> Evidence -> Expertise
```

Expertise must not directly consume measurements.

Main entry points:

- `EvidenceSynthesisEngine`
- `EvidenceApi`
- `EvidenceKnowledgeBase`
- `EvidenceOntology`
- `EqlParser` and `EqlEngine`
- `StreamingEvidenceEngine`

