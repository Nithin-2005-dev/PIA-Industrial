# M75 Hardcoding Audit

## Scope

Searched active backend/frontend Industrial paths for `P-101`, `P-102`, `P-103`, demo work-order IDs, demo inspection IDs, demo failure conclusions, compliance conclusions, and decision outputs.

## Release-Blocking Hardcoded Logic Removed

- `backend/app/api/routers/v1/industrial.py`: removed static asset lists, static P-101 Copilot answers, static graph/documents responses, static maintenance/failure/compliance/decision aggregation, and demo singleton dependency.
- `frontend/src/pages/*`: Industrial pages now call the shared API client with the selected `workspace.id` instead of unscoped demo endpoints.
- `frontend/src/api/useQueryAgent.ts`: Copilot now sends `workspace_id` explicitly.
- `frontend/src/features/graph/InteractiveGraph.tsx`: graph loading is scoped to the active workspace.

## Allowed Demo Fixture

- `data/demo/p101/`: retained as the P-101 synthetic demo dataset.
- `backend/app/industrial/workspace_runtime.py`: contains the `demo-p101` workspace label and loader path only. It loads P-101 through the same ingestion, extraction, graph, and query pipeline used by uploaded files.
- `frontend/src/store/workspaceStore.ts`: initializes the UI to `demo-p101` so the existing demo remains immediately available.

## Allowed Tests

- `backend/tests/unit/test_m58_industrial_domain.py` through `test_m72_api.py`: existing milestone fixtures continue to use P-101 examples.
- `backend/tests/integration/test_p101_real_document_pipeline.py`: retained as the canonical P-101 demo pipeline test.
- `backend/tests/unit/test_m75_industrial_platform.py`: adds unseen P-500 and HX-204 workspace isolation/persistence coverage.

## Allowed Documentation Examples

- `docs/industrial/*.md`: examples still mention P-101 as illustrative documentation, not active application logic.
- `backend/app/domain/industrial/asset.py`, `backend/app/copilot/router.py`, and extractor docstrings: examples only.

## Current Limitations

- Document deletion/reprocessing is not implemented in M75 because partial deletion propagation would risk stale graph evidence.
- Upload security is prototype-grade: extension validation, filename sanitization, size limit, isolated upload storage, and no execution of uploaded content.
- Graph persistence is JSON-backed and reconstructed into NetworkX-compatible runtime objects on restart.

