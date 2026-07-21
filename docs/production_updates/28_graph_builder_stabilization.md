# Phase 30 & 31: Graph Stabilization

## Objective
The Evidence Graph must be the leanest, most mathematically precise expression of organizational topology. Prior to these phases, the Graph was vulnerable to two catastrophic failures when receiving data from the Measurement Layer:

1. **The "God Node" Fallacy (Landmine 4):** Indiscriminate creation of structural edges toward config/lock files (`yarn.lock`, `README.md`) artificially concentrated structural gravity in non-architectural components.
2. **Graph Corruption via Supersession (Landmine 5):** The append-only nature of the Measurement Layer resulted in geometric edge duplication upon re-computation, as older structural edges were never removed.

## Phase 30: Ontological Stop-Word Filter
To address the "God Node" fallacy, we implemented the `OntologicalStopWordFilter`.
* **File:** `app/evidence/graph/filters.py`
* **Mechanics:** It intercepts all structural targets against a strict list of regex patterns (e.g., `^package\.json$`, `^.*\.lock$`).
* **Effect:** Stops the creation of `AUTHORED` or `DEPENDS_ON` edges for low-value structural files, keeping the PageRank transition matrix pure and anchored strictly to application logic.

## Phase 31: Supersession Graph Handler
To address Graph Corruption, we established the `EvidenceGraphBuilder` as an Anti-Corruption Layer between raw Evidence and the physical `IEvidenceGraphStore`.
* **File:** `app/evidence/graph/builder.py`
* **Mechanics:** 
  * Prior to inserting new edges, the Builder examines the incoming `supersedes_id` metadata.
  * If a supersession is detected, it executes a physical `DELETE` operation (`remove_evidence`) against the graph store for the old evidence node and all connected structural edges (tracked via `origin_id`).
* **Architectural Decision (Delete vs Tombstone):** We explicitly chose physical deletion to avoid the massive traversal penalty (`WHERE edge.is_active = true`) during PageRank computation. The Graph is a *materialized read-view* of current reality; the Measurement Layer remains the append-only source of truth.

## Scientific Verification
* **Stop-Word Tests:** `tests/test_ontological_stop_words.py` confirmed that God Nodes like `yarn.lock` are completely excluded from the graph.
* **Supersession Tests:** `tests/test_supersession_graph_handler.py` confirmed that incoming supersession payloads successfully locate and physically delete older iterations of their structural edges, maintaining graph integrity.

With the graph stabilization complete, the data pipeline from Ingestion -> Measurement -> Evidence -> Risk Analysis is fully sealed.
