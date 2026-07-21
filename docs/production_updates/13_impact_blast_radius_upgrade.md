# Production Update: Architectural Blast Radius Upgrade (Impact Evaluator)

## Overview
We have replaced the naive file-counting algorithms in the `ChangeImpactEvaluator` with a mathematically rigorous **Architectural Entropy** and **Depth Weighting** model. The evaluator now calculates the true "Blast Radius" of a change by analyzing systemic coupling and foundational risk, rather than simply measuring text volume.

## 1. Trap 1: The "Deep Tree" Fallacy (Depth Weighting)
**The Trap:** Altering a root-level dependency (like `main.py` or a core logger) carries a vastly higher systemic risk than altering a leaf-node component (like a UI button). Naive evaluators weigh both files equally.
**The Fix:**
- The evaluator now inspects the file path depth using `_calculate_depth_penalty()`.
- **Foundational Multipliers:** Any file residing in a `/core/`, `/base/`, or `/shared/` directory is immediately flagged as a high-risk dependency and receives a `2.0x` blast multiplier.
- **Root Multipliers:** Files at the absolute root of the repository (depth 0) receive a `1.5x` multiplier, while files at depth 1 receive `1.2x`. Leaf nodes default to `1.0x`.

## 2. Trap 2: The "Wide Net" Fallacy (Operational Filtering)
**The Trap:** A developer modifying `.gitignore` or updating a massive `package-lock.json` touches the entire repository conceptually, but the change carries `0.0` operational runtime risk.
**The Fix:**
- The `_get_impact_weight()` filter was implemented specifically for blast radius.
- Documentation (`.md`, `.txt`), lockfiles (`.lock`, `lock.json`), binaries (`.svg`, `.png`), and configuration files (`.yaml`, `.gitignore`) are immediately stripped from the entropy calculation. 
- These files may break a build pipeline, but they cannot cause runtime memory leaks or logic crashes, so their operational impact score is forced to `0.0`.

## 3. Trap 3: The Coupling Distortion (Directory Entropy)
**The Trap:** A Pull Request modifying 5 files within a single domain (e.g., `/backend/auth`) is generally safe and highly cohesive. A Pull Request modifying 5 files across 5 different domains (e.g., `/auth`, `/db`, `/ui`, `/payment`, `/api`) indicates a massive, highly scattered architectural change with immense coupling risk.
**The Fix:**
- We implemented Shannon Entropy (`_calculate_directory_entropy`) across the root subsystem paths.
- The evaluator clusters the modified files by their top-level subsystem.
- A mathematically cohesive PR (all files in one subsystem) yields an entropy of `0.0`, adding no coupling penalty.
- A scattered PR mathematically increases the probability distribution, heavily scaling up the final impact multiplier: `total_blast_radius * (1.0 + entropy)`.

*(Note: Per architectural directives for active MVP development, the `logic_version` of the evaluator remains at `v1.0.0`).*
