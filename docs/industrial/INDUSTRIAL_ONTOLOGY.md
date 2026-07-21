# Industrial Ontology

PIA Industrial normalizes fragmented industrial telemetry, work orders, and manuals into a strict typed ontology.

## Core Entities

1. **Asset** (`Asset`): A physical piece of equipment (e.g., Pump P-101, Compressor C-200).
2. **Component** (`Component`): A sub-part of an asset (e.g., Main Bearing, Shaft Seal).
3. **Observation** (`Observation`): An immutable fact recorded at a point in time. Types include:
   - `INSPECTION_EVENT`
   - `FAILURE`
   - `MAINTENANCE_ACTION`
   - `ANOMALY`
4. **Engineer** (`Engineer` / `Operator`): A human actor interacting with an asset.

## Entity Resolution

Raw text documents rarely use canonical asset names perfectly. The **Entity Resolver** (`app.extraction.entities.entity_resolver`) maps aliases back to the canonical ID.
- Example: "The main water pump" → `P-101`.
- Example: "P101" → `P-101`.

## Relationships

Entities are connected in the Knowledge Graph using directional edges:
- `Asset` **HAS_COMPONENT** `Component`
- `Observation` **OBSERVES** `Asset`
- `FailureMode` **AFFECTS** `Component`
- `Engineer` **PERFORMED** `MaintenanceAction`

## Compliance Relationships
- `Asset` **REQUIRES** `InspectionProtocol`
- `Observation` **SATISFIES** `InspectionProtocol`

This strict ontology allows the deterministic engines to confidently trace causation and evaluate compliance mathematically, rather than relying on LLM semantic grouping.
