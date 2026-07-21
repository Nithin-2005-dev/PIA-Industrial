# Production Update: Network Resilience & Circuit Breakers

## 1. The Problem: The "Network Panic" Bug
Previously, the ingestion layer treated network interactions as guaranteed. A simple timeout, 502 Bad Gateway, or HTTP 429 Rate Limit from a provider like GitHub would propagate unhandled exceptions up the stack. This would instantly crash the `ObservationIngestionEngine`, halting *all* data processing across the entire platform due to a localized, transient network blip.

## 2. The Solution: Decoupled Resilience Boundary
We introduced a systems engineering approach to network I/O, shielding the ingestion engine behind a stateful resilience boundary.

### A. The Resilience Decorator (Thundering Herd Protection)
- **`resilience.py`**: We implemented the `@with_resilience` decorator to automatically retry transient errors (`ConnectionError`, `Timeout`, and HTTP 5xx responses).
- **Exponential Backoff with Jitter**: To prevent overwhelming a recovering API server (the "thundering herd" problem), retries use `delay = base * (2^retry)` with random jitter, spreading out the network load.

### B. The Circuit Breaker Pattern
- **`circuit_breaker.py`**: A state machine implementation (`CLOSED`, `OPEN`, `HALF_OPEN`) tracking consecutive failures.
- If 5 consecutive failures occur, the circuit trips to `OPEN`. This immediately fails-fast subsequent calls for 60 seconds (Recovery Timeout) rather than waiting for TCP timeouts, drastically saving CPU cycles and protecting the provider from abuse.

### C. Rate Limit Awareness
- **`rest_gateway.py`**: The GitHub API gateway now inspects `X-RateLimit-Remaining` headers on every response.
- **Precision Sleeping**: If the rate limit is exhausted (`Remaining == 0`), the gateway parses the `X-RateLimit-Reset` timestamp, calculates the exact seconds until reset, and blocks the worker explicitly (`time.sleep(sleep_time)`). This acts as a localized block without spamming the provider with 429 errors.

### D. The Engine-Level Graceful Skip
- **`engine.py`**: To solve the "Blocking Sleep" trap where one failing adapter blocks the entire engine's processing loop, `engine.py` was updated to inspect the adapter's state. 
- If `adapter.is_circuit_open()` returns True, the engine skips the adapter entirely (`logger.warning("Circuit OPEN. Skipping.")`) and returns an empty `SyncResult`. This ensures a localized Jira outage, for example, will never halt GitHub or Slack ingestion.

## 3. Conclusion
The ingestion engine is now completely decoupled from network volatility. It will automatically back off during instability, halt traffic entirely during severe outages (Circuit Breaker), respect rate limits perfectly, and ensure multi-adapter environments remain highly available even when individual providers fail.
