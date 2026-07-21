# Milestone 41: Semantic Evidence Engine

M41 adds the first semantic evidence layer on top of M40 measurements. It does not modify measurement outputs; it interprets validated measurements into evidence objects using deterministic evidence definitions.

## Delivered

- Added `backend/app/evidence/semantic`.
- Added `SemanticEvidenceEngine` as a wrapper over the existing evidence synthesis and validation pipeline.
- Added M40-compatible semantic evidence definitions for code change volume, review activity, review latency, test execution, documentation update, and build execution signals.
- Registered `SemanticEvidenceEngine` in the Platform Runtime evidence module.
- Added `backend/scripts/test_semantic_evidence_engine.py`.

## Current Scope

M41 consumes `Measurement` objects and produces existing canonical `Evidence` objects in an `EvidencePackage`.

## Design Decisions

- Reuse the existing evidence domain, confidence model, validation pipeline, and package model.
- Keep measurements immutable and uninterpreted.
- Keep M41 deterministic and rule based.

## Verification

`python backend/scripts/test_semantic_evidence_engine.py`

## Known Limitations

- Evidence definitions are still narrow.
- No durable evidence store yet.
- Evidence does not yet drive a redesigned estimation layer.

