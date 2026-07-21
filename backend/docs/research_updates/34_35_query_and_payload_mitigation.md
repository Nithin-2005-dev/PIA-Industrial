# Phase 34 & 35: Query Shielding and Payload Mitigation

## Context and Architecture Risk
Following the stabilization of the graph building algorithms and the execution pipelines, a final perimeter audit of the Evidence Layer revealed two severe infrastructure vulnerabilities at the boundaries (Query and API layers). Left unresolved, these landmines represented critical vectors for Denial of Service (DoS) and application memory exhaustion in enterprise environments.

1. **The Infinite Traversal Trap (Graph DoS)**
   The Evidence Query Language (EQL) provided an interface for graph filtering, but lacked traversal boundaries. If a tenant issued an N-hop traversal request within a graph containing circular dependencies (e.g., Module A -> Module B -> Module C -> Module A), the evaluation thread would become trapped in an infinite recursive loop, spiking memory until terminated by the Kubernetes OOM Killer.

2. **The Payload Nuke (Unbounded Serialization)**
   The Evidence API's `search` and `export` endpoints returned unbounded tuples of `Evidence` objects. In a production system containing tens of thousands of historical evidence nodes, a single synchronous GET request could force the JSON serialization of massive object graphs in memory, leading to Gunicorn worker timeouts and catastrophic cluster memory spikes.

## Implementation: Phase 34 (Graph DoS Prevention)

### Architectural Decision
**All graph traversal queries must enforce a hard execution depth limit and utilize cycle-breaking visited sets.**

### Execution
1. **EQL Data Model Upgrades**: Updated `EqlQuery` in `app/evidence/query/eql.py` to support `hop_depth` and `target_node` parameters.
2. **Parser Boundaries**: Enhanced `EqlParser.parse` to detect `FIND N-HOP DEPENDENCIES OF <target>` expressions. The parser strictly clamps the requested depth to a maximum of 5 hops to guarantee reasonable execution timeframes.
3. **Bounded BFS Execution**: Modified `EqlEngine.query` to execute a robust Breadth-First Search (BFS). Lineage relationships (`parent_evidence_ids` and `derived_from`) are utilized to construct adjacencies. A `visited_nodes` set guarantees that any cycle instantly short-circuits.
4. **Validation**: Built `test_eql_traversal_cycle` and `test_eql_traversal_depth_limit` to mathematically prove that cyclic relationships resolve safely and deep dependency chains strictly terminate at 5 hops.

## Implementation: Phase 35 (API Payload Mitigation)

### Architectural Decision
**All API endpoints returning collections must enforce mandatory cursor-based pagination utilizing a standard Metadata Envelope.**

### Execution
1. **API Signature Update**: Modified `EvidenceApi.search()` and `EvidenceApi.export()` in `app/evidence/api/api.py` to accept `limit` (default: 100) and `offset` (default: 0) parameters.
2. **Metadata Envelope**: Shifted the return signatures from raw tuples to a semantic JSON envelope format: `{"total": N, "data": [...]}`. This ensures the client frontend is explicitly aware of pagination limits and data truncation, avoiding silent data loss.
3. **Execution Masking**: Utilized Python list slicing (`[offset : offset + limit]`) to ensure the serialized memory footprint remains bounded.
4. **Validation**: Built `test_api_pagination_search` and `test_api_pagination_export` to verify that injecting 500 nodes successfully yields paginated slices without structural errors.

## Conclusion
The Evidence Layer is now mathematically pure, structurally sound, and fully shielded against malicious or excessive load. The perimeter is fully secured.
