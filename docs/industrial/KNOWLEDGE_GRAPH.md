# Industrial Knowledge Graph

The Industrial Knowledge Graph (`app.knowledge.graph`) is the heart of PIA Industrial's deterministic intelligence.

## Graph Architecture

The current hackathon prototype implements the graph using `NetworkX` in memory. This allows for extremely rapid, localized pathfinding and topology queries without complex infrastructure.

## Graph Construction

As `Observation` events are processed by the ingestion pipeline, the `KnowledgeGraphBuilder` dynamically injects nodes and edges.

### Node Types
- `Asset`
- `Component`
- `Observation` (Inspections, Failures)
- `Engineer`
- `ComplianceRule`

### Edge Types
Edges contain metadata, including timestamps and confidence weights.
- `AFFECTS`: Links an anomaly to a component.
- `OBSERVES`: Links an observation report to an asset.
- `CAUSES`: A deterministically inferred edge linking a root cause to a failure event.

## Provenance

Every node derived from an unstructured document holds a reference back to its SQLite `ObservationStore` UUID. This allows any intelligence engine walking the graph to immediately pull the raw text (e.g., "Page 4 of Pump Manual") to justify its mathematical conclusion.

## Scalability Limitations

The `NetworkX` graph is currently re-hydrated on startup for the P-101 demo. A production deployment will require migration to a persistent, distributed graph database (e.g., Neo4j, Amazon Neptune, or Memgraph).
