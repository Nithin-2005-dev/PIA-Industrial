# Production Update: Two-Phase Cyclomatic Complexity Implementation

## Overview
We have upgraded the `ChangeComplexityEvaluator` from a naive "Lines of Code (LoC) volume metric" to an advanced, heuristically-weighted cyclomatic complexity engine. This update neutralizes the risk of statistical hallucination caused by auto-generated files (like lockfiles) and git aliasing (renamed files), ensuring the Measurement Layer strictly evaluates the true cognitive effort of a change.

## Phase 1: Observation Data Persistence Verification
Before altering the Measurement math, we conducted an audit of the Observation Layer boundary to ensure it fulfilled the architectural constraint of "no external network calls during measurement". 

- **Audit Results:** The `GitHubObservationTranslator` natively extracts the `patch` diff provided by the GitHub webhook payload and serializes it into the `FileChangeFacts` object.
- **Persistence Guarantee:** The `sqlite_store.py` ingestion layer persists the raw webhook JSON untouched. When the Measurement Layer runs (or replays), the `patch` string is perfectly preserved and fed directly into the evaluator, fully satisfying the local-data invariant.

## Phase 2: Cyclomatic Complexity Overhaul

The `app/measurement/evaluators/complexity.py` module was deeply refactored to implement file-by-file forensic analysis.

### 1. Global File Filtering & Weighting
To prevent the "Auto-Gen Explosion" and "Git Aliasing" illusions, all changes are now dynamically weighted:
- **0.0 Weight (Ignored):** Files marked with status `renamed` (prevents double-counting churn on `git mv`).
- **0.0 Weight (Ignored):** Auto-generated artifacts, binaries, and lockfiles (e.g., `.lock`, `lock.json`, `/build/`, `/dist/`, `.svg`, `.min.js`).
- **0.1 Weight (Heavily Discounted):** Documentation and configuration files (e.g., `.md`, `.json`, `.yaml`).
- **1.0 Weight (Full Value):** Core source code languages (e.g., `.py`, `.ts`, `.go`, `.rs`, `.java`, `.cpp`).

### 2. Sanitized McCabe Delta
The previous primitive string matcher has been upgraded to a robust Regex-based McCabe analyzer:
- **Sanitization:** String literals (e.g., `".*?"`) and single-line comments (`#...`, `//...`) are aggressively stripped from the patch diff prior to analysis. This prevents the evaluator from hallucinating complexity when a developer writes a comment containing words like "if" or "while".
- **Abstract Branch Counting:** The analyzer scores both additions (`+`) and deletions (`-`) by identifying branching keywords (`if`, `elif`, `for`, `while`, `case`, `catch`) and logical operators (`&&`, `||`, `?`). 
- **Destructive Effort:** Safely removing complex, nested code (deletions) correctly adds to the effort score, neutralizing the "Negative Engineering" penalty (the fallacy that deleting code is easier than writing it).

### 3. Effective Metrics Calculation
The final outputs of the evaluator are now heavily sanitized:
- `code_churn` = `effective_churn` (weighted by file type).
- `files_changed` = `effective_file_count` (weighted by file type).
- `patch_complexity_delta` = `effective_complexity_delta` (McCabe delta * file weight).

*(Note: Per architectural directives for active MVP development, the `logic_version` remains at `v1.0.0`).*

## Verification
A manual trace of the pipeline using a mock `Observation` proved the mathematics:
- A `package-lock.json` file with 1,500 lines of churn correctly resulted in `0.0` complexity and churn.
- A `renamed` file with 200 lines of churn correctly resulted in `0.0` complexity and churn.
- A `main.py` file with 15 lines of churn and one `if` statement correctly resulted in `15.0` churn and `1.0` complexity.
