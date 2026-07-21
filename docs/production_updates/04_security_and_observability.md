# Production Update: Security & Observability

## 1. The Problem: Implicit Trust & The "Black Box"
During our final audit of the Observation Layer, two major architectural gaps were identified:
1. **The "Secret" Vulnerability**: Adapters (e.g., GitHub, Jira) accepted raw credential tokens directly via configuration files or environment variables. This creates a massive security hole where plain-text keys are floating in memory or accidentally logged.
2. **The Observability Gap**: We had built a robust pipeline with dead letter queues and retry mechanisms, but we lacked real-time Telemetry. If the pipeline stalled, we were flying blind, unable to distinguish between a database lock, a network timeout, or an inefficient normalizer logic.

## 2. The Solution: Hardened Perimeters & Aspect-Oriented Telemetry

### A. The Secret Provider Interface (Security)
- **`secrets.py`**: We implemented the `ISecretProvider` protocol to serve as a hard wall between application logic and credential storage. 
- **Gateway Refactoring**: The `GitHubRestGateway` no longer accepts a raw token in its constructor. Instead, it accepts an `ISecretProvider` instance and a `secret_key`.
- **Just-In-Time Resolution**: The gateway dynamically calls `secret_provider.get_secret()` exactly when it needs to construct the HTTP Authorization header (`_get_headers`), ensuring the token is kept out of persistent application memory and configuration scopes.

### B. The Metrics Middleware (Observability)
- **Aspect-Oriented Design**: We explicitly avoided creating an "accumulator dataclass" that would clutter the business logic in `engine.py`. Instead, we introduced `MetricsMiddleware` in `metrics.py`.
- **Latency Tracking**: We utilize Python's `@wraps` decorator (`@middleware.track_latency`) to wrap the `normalizer.normalize()` method dynamically at runtime in the engine. This calculates the precise execution latency (in milliseconds) and maintains a rolling average without altering the `normalizer.py` codebase.
- **Explicit Counters**: The engine explicitly catches specific errors (`SchemaMismatchError`, `CircuitOpenException`) and increments dedicated counters (`schema_mismatches`, `circuit_opens`, `events_processed`, `failed_events`) in the middleware.
- **Out-of-Band Instrumentation**: The `StorageManager.rotate_logs()` method was also updated to accept the metrics instance, tracking `archival_events_count` to give us visibility into background database maintenance.

## 3. Conclusion
The Observation Layer is now fully mature and ready for production workloads.
- **Durable:** SQLite WAL guarantees no data loss.
- **Semantic:** Pydantic ensures only valid events enter the graph.
- **Concurrent:** Atomic claims and watchdogs prevent deadlocks/zombie states.
- **Resilient:** Circuit breakers and exponential backoff survive network chaos.
- **Secure:** Secret management protects credential perimeters.
- **Observable:** Middleware telemetry eliminates the "black box" operational risk.

We are officially ready to proceed to the Cognitive/Reasoning Brain.
