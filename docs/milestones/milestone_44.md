# Milestone 44: Real Adapter Pack 1

M44 adds the first provider-specific adapter pack for the Observation & Ingestion Engine.

## Delivered

- Added a shared `ProviderPayloadAdapter` batching base.
- Added `GitHubRestObservationAdapter` for commits, pull requests, reviews, comments, merges, releases, and documentation events.
- Added `JiraObservationAdapter` for issues, incidents, and comments.
- Added `SlackObservationAdapter` for comments and incident-style messages.
- Added `GitHubActionsObservationAdapter` for builds, tests, and deployments.
- Registered the adapter pack with the default platform observation module.
- Added `backend/scripts/test_adapter_pack_1.py`.

## Current Scope

The adapters consume already-fetched API or webhook payload dictionaries. They do not perform authenticated network calls yet.

## Known Limitations

- No provider API clients or OAuth/token handling.
- Payload coverage is intentionally narrow and focused on common fields.
- Pagination is offset based over local payload batches.
- Provider-specific error handling is not yet implemented.

## Verification

`python backend/scripts/test_adapter_pack_1.py`

