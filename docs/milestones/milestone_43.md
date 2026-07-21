# Milestone 43: Runtime DI Migration

M43 moves the legacy intelligence bootstrap onto the platform runtime and dependency injection container.

## Delivered

- Added `IntelligencePlatformModule` for the existing intelligence service graph.
- Registered ownership, successor, coverage, concentration, risk, health, history, forecasting, transfer, readiness, and organization services through platform DI.
- Updated `IntelligenceContext` to build a `PlatformRuntime`, register default modules, register the intelligence module, and resolve services through the provider.
- Preserved the existing `IntelligenceContext` public attributes for current scripts and adapters.
- Fixed default `GraphService` DI by registering an empty `OrganizationalGraph`.
- Added `backend/scripts/test_runtime_di_migration.py`.

## Current Scope

This milestone migrates service construction to DI. It does not redesign the legacy services or replace the in-memory projection model.

## Known Limitations

- `IntelligenceContext` still owns runtime creation for compatibility.
- Organization services still depend on `IntelligenceContext` as a facade.
- Projection state is injected as an in-memory instance.
- Startup and shutdown hooks remain no-op for most legacy services.

## Verification

`python backend/scripts/test_runtime_di_migration.py`

