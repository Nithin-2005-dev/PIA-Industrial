# Milestone 46: Evidence-to-Expertise Estimation v2

M46 connects semantic evidence packages to the existing expertise projection model.

## Delivered

- Added `SemanticEvidenceExpertiseBridge`.
- Added `SemanticExpertiseProjectionPipeline`.
- Added deterministic conversion from validated semantic evidence to estimator-domain evidence.
- Added actor lineage from measurements into measurement metadata so semantic evidence can be attributed to developers.
- Registered the semantic expertise bridge and pipeline with the platform estimation module.
- Added `backend/scripts/test_semantic_expertise_estimation.py`.

## Current Scope

This milestone bridges M41 evidence to the existing rule-based expertise estimator. It does not replace the latent estimation algorithm.

## Known Limitations

- Developer attribution depends on observation actor IDs carried through measurement metadata.
- Semantic evidence without target entity or actor lineage is skipped.
- Weighting is deterministic and rule-based.
- No Bayesian, graph-aware, or team-level estimation yet.

## Verification

`python backend/scripts/test_semantic_expertise_estimation.py`

