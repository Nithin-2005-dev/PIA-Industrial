# Production Update: Structural & Causal Risks

## 1. The Problems: Logical Vulnerabilities at Scale
After hardening the storage and network perimeters of the Observation Layer, an audit revealed three hidden logical vulnerabilities that would corrupt causal graphs and cripple multi-tenant scaling:

1. **The "Infinite Mirror" (Replay Feedback Loop)**: The engine's replay mechanism fetched historical observations without metadata, meaning downstream cognitive engines couldn't distinguish a replayed event from a live one, triggering repeated side-effects.
2. **The "Temporal Drift" (Timezone Ambiguity)**: The data normalizer parsed ISO8601 strings but didn't enforce UTC on naive timestamps. This caused timezone split-brain issues across different adapters (e.g. GitHub vs. local Git).
3. **Registry Staticity (The "Scale" Constraint)**: `AdapterRegistry` relied on instantiated objects, meaning spinning up a new adapter (e.g. for a new Jira tenant) required a code change rather than dynamic configuration.

## 2. The Solutions

### A. Replay Metadata (Tracing Headers)
- **`domain.py` & `Observation`**: Introduced `ProcessingMode(str, Enum)` containing `LIVE` and `REPLAY`. Attached `processing_mode` to `Observation` as a default `ProcessingMode.LIVE`.
- **`normalizer.py` & `replay.py`**: The normalizer stamps all incoming raw events as `LIVE`. The `ObservationReplayEngine` now explicitly overrides this using `dataclasses.replace(processing_mode=ProcessingMode.REPLAY)`, implementing a tracing header pattern that downstream engines must filter on to prevent the "Infinite Mirror".

### B. Fail-Fast Temporal Normalization
- **`normalizer.py`**: Updated the `_time` parsing function to check `tzinfo`. If a timestamp is naive, it explicitly logs a warning (providing an audit trail for misbehaving adapters) and forces it to `timezone.utc`. This guarantees SQLite `created_at` ordering remains globally consistent and causality graphs are pristine.

### C. Dynamic Client Onboarding (Factory Pattern)
- **`adapters.py`**: Refactored `AdapterRegistry` from a rigid instance-based dictionary to a robust Factory Pattern.
- **Dynamic Instantiation**: The registry now implements `register_factory` and `instantiate(name, config)`. 
- **Type Validation**: The `instantiate` method includes an implicit interface check to ensure the generated class provides `.fetch()`, `.name`, and `.provider`. This prevents broken configurations from crashing the hot-path ingestion loop.

## 3. Observation Layer Status
The entire `app/observation` package has been fortified against storage, network, and logical vulnerabilities. It is now officially marked as **[STABLE]**.
