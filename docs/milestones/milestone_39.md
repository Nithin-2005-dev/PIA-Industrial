# Milestone 39: Unified Observation & Ingestion Engine

M39 builds the front door of PIA: a provider-agnostic Observation and Ingestion Engine that converts external systems into canonical observations consumed by the platform runtime and downstream Measurement Engine.

## Delivered

- Extended the canonical observation domain with `COMMENT`, `MERGE`, `INCIDENT`, and `RELEASE` observation types and fact models.
- Extended the observation registry so standardized observations include commit, pull request, review, comment, issue, merge, deployment, incident, documentation, build, release, and test result.
- Added `backend/app/observation/ingestion` as the OIE package.
- Added common adapter contracts, adapter registry, static test adapter, and provider names for GitHub, GitLab, Bitbucket, Jira, Linear, Azure DevOps, Slack, Teams, Email, CI/CD, Kubernetes, Docker, and custom APIs.
- Added raw observation records and canonical normalization into existing `app.observation.domain.Observation`.
- Added incremental sync request/result models, cursor management, offset tracking, checkpoints, and replay query models.
- Added deduplication for raw provider records and normalized observation IDs.
- Added identity resolution from provider-specific users to unified developer IDs.
- Added separated ingestion storage for raw observations, normalized observations, and processed evidence references.
- Added replay by repository, organization, adapter, developer, and time range.
- Added rate limiting primitives for quota checks, retries, exponential backoff metadata, and circuit-breaker state.
- Added observation ingestion metrics for latency, throughput, failures, retries, duplicates, duplicate rate, and backlog.
- Integrated OIE into `PlatformRuntime` as `ObservationPlatformModule`; Measurement now depends on Observation in the default platform module graph.

## Impact

- Downstream systems can consume normalized observations without depending on provider-specific schemas.
- New external systems can be added by implementing the adapter contract and emitting raw records.
- The platform runtime now starts with Observation before Measurement, matching the canonical PIA flow.

## Verification

- Added `backend/scripts/test_observation_ingestion_engine.py`.
- The smoke test verifies provider registration, normalization, identity resolution, deduplication, checkpointing, replay, platform event emission, metrics, Measurement Engine compatibility, and platform module startup order.

## Follow-Up

- Add live adapters for GitLab, Bitbucket, Jira, Linear, Azure DevOps, Slack, Teams, Email, Kubernetes, Docker, and CI/CD providers.
- Add durable storage backends for raw and normalized observations.
- Add webhook signature validation per provider.
- Add distributed checkpoint and rate-limit stores.
- Connect OIE normalized events into the platform event bus used by other runtime modules.

