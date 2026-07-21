# Milestone 47: Knowledge Graph v1

M47 adds the first usable knowledge graph builder and query algorithms.

## Delivered

- Added `KnowledgeGraphBuilder`.
- Builds developer, module/file, evidence, and measurement nodes from expertise estimates and evidence packages.
- Adds `HAS_EXPERTISE_IN`, `SUPPORTS`, and `SYNTHESIZES_TO` relationships.
- Expanded `GraphService` with node type queries, degree centrality, shortest path, and subgraph extraction.
- Registered `KnowledgeGraphBuilder` with the platform graph module.
- Added `backend/scripts/test_knowledge_graph_v1.py`.

## Current Scope

The graph is in-memory and deterministic. It is suitable for runtime queries and smoke-test scale graph construction.

## Known Limitations

- No durable graph database.
- No incremental graph updates.
- No graph schema migration or indexing.
- Algorithms are simple in-memory implementations.

## Verification

`python backend/scripts/test_knowledge_graph_v1.py`

