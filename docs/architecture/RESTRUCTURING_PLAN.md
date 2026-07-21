# PIA Industrial Repository Restructuring Plan

## Phase 1: Core and Infrastructure
| Old Path | New Path | Reason |
|---|---|---|
| `app/adapters/` | `app/infrastructure/` | Database and external API adapters belong in infrastructure. |
| `app/ports/` | `app/infrastructure/ports/` | Interfaces matching the adapters. |
| `app/platform/` | `app/core/` | Sync engine, events, and projection registry belong in core platform code. |

## Phase 2: Ingestion & Extraction
| Old Path | New Path | Reason |
|---|---|---|
| `app/observation/` | `app/ingestion/` | Observation processing handles the raw parsing and ingestion of unstructured/structured data. |
| `app/extraction/` | `app/extraction/entities/` | Industrial entity extractors. |
| `app/extractor/` | `app/extraction/legacy/` | Legacy software engineering extractors (e.g. commit metrics). |

## Phase 3: Knowledge (Graph & Retrieval)
| Old Path | New Path | Reason |
|---|---|---|
| `app/graph/` | `app/knowledge/graph/` | Graph managers and builders. |
| `app/retrieval/` | `app/knowledge/retrieval/` | Evidence ranker, semantic search. |
| `app/evidence/` | `app/knowledge/evidence/` | Evidence generation logic. |

## Phase 4: Intelligence Services
| Old Path | New Path | Reason |
|---|---|---|
| `app/causal/` | `app/intelligence/causal/` | Industrial Causal RCA. |
| `app/temporal/` | `app/intelligence/temporal/` | Time-series and temporal models. |
| `app/forecasting/`, `app/forecast/` | `app/intelligence/forecasting/` | Failure forecasting and prediction. |
| `app/reasoning/` | `app/intelligence/reasoning/` | Reasoning engines. |
| `app/decision/` | `app/intelligence/decisions/` | Decision engines. |
| `app/risk/`, `app/knowledge_risk/` | `app/intelligence/risk/` | Risk calculation engines. |
| `app/expertise_mapping/`, `app/knowledge_transfer/` | `app/intelligence/expertise/` | Expertise tracking. |
| `app/simulation/`, `app/scenario/`, `app/intervention/` | `app/intelligence/counterfactual/` | Counterfactual simulations. |
| `app/health/` | `app/intelligence/assets/` | Asset health intelligence. |
| `app/measurement/` | `app/intelligence/measurement/` | Shared deterministic measurement processing. |
| `app/executive/`, `app/organization/`, `app/ownership/`, `app/successor/` | `app/intelligence/legacy/` | Legacy software organizational metrics. |

## Phase 5: Copilot
| Old Path | New Path | Reason |
|---|---|---|
| `app/copilot/` | `app/copilot/` | Copilot interfaces and routing. (Keep as-is). |

## Phase 6: Scripts & Data
| Old Path | New Path | Reason |
|---|---|---|
| `app/demo_seeder.py` | `scripts/demo/demo_seeder.py` | Demo seeding logic. |
| `tests/data/` | `data/demo/p101/` | P-101 demonstration documents. |

## Phase 7: Tests
| Old Path | New Path | Reason |
|---|---|---|
| `tests/validation/` | `tests/validation/` | System validation. |
| `tests/evaluation/` | `tests/evaluation/` | Benchmarks. |
| `tests/test_*.py` | `tests/unit/` | Unit and integration tests. |
