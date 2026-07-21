# Phase 17: The Great Purge (Semantic Bleed Extraction)

## Objective
A deep architectural review of the `app/measurement/` directory exposed three severe boundary violations that compromised the integrity of the Measurement Layer. A physics engine must calculate mathematical variants (Z-Scores) without retaining domain-specific cognitive intelligence. 

The anomalies discovered were:
1. **The Intelligence Leak (`intelligence/`):** Contained `semantic_graph.py`, modeling qualitative relationships like "DEPENDS_ON" and "CAUSES" between raw concepts.
2. **The Classifier Leak (`signal_intelligence/`):** Contained `signal_classifier.py`, actively tagging raw signals with qualitative labels (e.g., "high_risk", "security") using keyword heuristics and mock LLM integrations.
3. **The Adapter Leak (`subsystem/`):** Contained `boundary.py`, parsing Rust (`crates/`), Node (`packages/`), and GitHub monorepo architectures directly inside the core calculation tier.

The objective of Phase 17 was to ruthlessly execute "The Great Purge," surgically extracting these modules from the mathematical core and grafting them into their correct Domain-Driven Design (DDD) layers.

## Architectural Migrations

### 1. Adapter Leak Extraction
- **Action:** Extracted `app/measurement/subsystem/` -> `app/observation/ingestion/topology/`
- **Rationale:** Ecosystem-specific directory parsing (like `RustCratesProvider`) is exclusively an Observation/Adapter layer responsibility. The physics engine now expects a standardized metadata string, not raw file paths requiring Git parsing.

### 2. Intelligence Leak Extraction
- **Action:** Extracted `app/measurement/intelligence/` -> `app/evidence/semantic/knowledge/`
- **Rationale:** Constructing an in-memory Semantic Knowledge Graph with causal qualitative edges belongs to the Evidence Layer. The physics engine is completely decoupled from causal derivation.

### 3. Classifier Leak Extraction
- **Action:** Extracted `app/measurement/signal_intelligence/` -> `app/cognitive/classifiers/`
- **Rationale:** Identifying "CVEs", classifying LLM output, and generating ontological tags are purely Cognitive operations. The Measurement Layer now solely computes mathematical variance and passes the raw numbers upward for the Cognitive layer to interpret.

## Status: SEALED
The `app/measurement/` directory tree has been audited. The anomalous directories (`intelligence`, `signal_intelligence`, `subsystem`) have been physically deleted from the Measurement domain. A custom import script (`fix_imports.py`) was executed to rewrite the module paths across the entire `backend/` codebase to preserve downstream functionality while cementing the new boundaries.

The Measurement Layer is definitively, irreversibly, and cryptographically sealed. We proceed to the Evidence Layer.
