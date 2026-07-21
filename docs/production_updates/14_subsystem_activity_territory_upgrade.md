# Production Update: Subsystem Territory Activity Upgrade

## Overview
We have completely refactored the aggregation logic in the `SubsystemActivityEvaluator` to accurately map architectural boundaries and prevent statistical hallucinations in territory metrics. The evaluator now cleanly separates core domain logic from directory structures and mathematically mitigates both the Volume Multiplier bug and the Monolithic Blur.

## 1. Trap 1: The Monolithic Blur (Dynamic Domain Boundaries)
**The Trap:** In multi-tenant platforms, relying on a naive directory split (e.g., grouping `src/admin` and `src/client` into a single `src` bucket) blinds the engineering metrics. Leadership sees 100% of the effort going to `src/`, completely obscuring the resource split between the Admin Command Center and the Client Portal.
**The Fix:**
- The evaluator now implements a prioritized semantic router (`_resolve_subsystem`).
- **Strategic Mapping:** The router intercepts the path and scans for known strategic domains (e.g., `client_portal`, `admin_dashboard`, `vendor_dashboard`). If found, it routes the metrics directly to the business boundary, bypassing the directory tree.
- **Architectural Fallback:** If no strategic keyword is found, the router executes a standard depth-2 boundary split (e.g., `backend/auth`), ensuring granular architectural mapping without collapsing into monolithic root folders.

## 2. Trap 2: The Volume Multiplier (Event Duplication)
**The Trap:** If a developer touches 10 files in a single subsystem, naive evaluators emit a `+1` activity count for each file iteration in a loop. By the end of the month, the metrics database hallucinates a 10x engineering velocity for that specific subsystem, destroying resource allocation analytics.
**The Fix:**
- **Two-Pass Aggregation:** The main `evaluate` loop was fundamentally restructured into two distinct phases.
- **Pass 1 (Aggregation):** The engine first maps every file to its subsystem boundary, applies the operational `_get_file_weight()` filter (stripping out lockfiles and binaries), and sums the absolute raw churn into a deduplicated dictionary.
- **Pass 2 (Emission):** The engine parses the `Co-authored-by` metadata to extract pair programming collaborators. It then iterates over the deduplicated subsystem list, fractionally dividing the volume (`fractional_churn = churn / N`), and emitting **exactly one** `subsystem_contribution_count` per actor, per subsystem.

## Resulting Accuracy
The engine is now completely immune to volume magnification. A Pull Request touching 100 files in a single subsystem, authored by two developers via Pair Programming, now yields exactly two atomic activity points (one for each developer), while perfectly distributing the architectural coupling risk.

*(Note: Per architectural directives for active MVP development, the `logic_version` of the evaluator remains at `v1.0.0`).*
