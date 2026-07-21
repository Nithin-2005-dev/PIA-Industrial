# Phase 15: The Secure MQL Engine

## Objective
The **Measurement Query Language (MQL)** subsystem (`app/measurement/query/`) serves as the gateway for downstream AI Agents and UI dashboards to fetch calculated Z-Scores and metrics. However, our forensic audit revealed severe vulnerabilities within the legacy parser:
1. **Multi-Tenant Bleed:** The parser trusted the query string for isolation boundaries, allowing Cross-Tenant Data Access via AST injection.
2. **ReDoS Vulnerability:** The parser lacked length and execution timeouts, creating a catastrophic Denial of Service vector.
3. **Lineage Severance:** The queries returned flat, naked values stripped of their cryptographic audit trail, undermining the entire purpose of the Measurement Layer.

The objective of Phase 15 was to seal these final three vulnerabilities before the Measurement Layer connects to the Cognitive AI Layer.

## Architectural Security Upgrades

### 1. The Cryptographic Wrapper (`lineage_query.py`)
Introduced the `LineagePayload` dataclass. The MQL engine will no longer return naked arrays of floats. Every single queried measurement is now inextricably bound to its `provenance_graph`. If an AI Agent receives a Z-Score of `3.1`, it concurrently receives the immutable map proving exactly which source observations generated the score, and which legacy computations were superseded.

### 2. Hard Tenant Boundaries (`mql.py`)
Developed the `SecureMqlEngine` to construct a physical, un-bypassable wall between tenants. The engine completely ignores any tenant parameters passed inside the `query_string`. Instead, it extracts the verified `tenant_id` from the secure `request_context` (JWT/Session) and forcefully injects an AST node (`AND measurement.tenant_id == verified_tenant`) at the very root of the query execution plan.

### 3. DoS Protection (ReDoS)
Hardened the Lexer and Evaluator by enforcing strict boundaries. The `SecureMqlEngine` now possesses a `MAX_QUERY_LENGTH = 2048` limit to prevent memory-exhausting AST compilation paths. It also establishes a `MAX_EXECUTION_TIME_MS = 1000` execution timeout loop to sever any maliciously crafted tokens attempting catastrophic backtracking. 

## Status: SEALED
The Measurement Layer is officially finalized. Every single evaluator is sterilized, historical computations are mathematically immutable, the Plugin ecosystem is hardware-isolated, scientific calibration calculates true ECE, and the query gateway strictly enforces multi-tenant boundaries and cryptographic lineage. 

The physics engine is complete. The system is ready to advance into Cognitive Modeling and Markov Chains.
