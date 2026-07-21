# Measurement Layer Architecture & Guidelines

The Measurement Layer is the statistical core of the multi-tenant platform. It is designed to act as a **Sterile Physics Engine**. It does not interpret semantic meaning, it does not hold domain logic, and it does not classify behaviors. It exists strictly to compute variance, fuse raw data securely, and cryptographically protect historical calculations.

If a calculation involves meaning (e.g., "Is this a security incident?"), it belongs in the Evidence or Cognitive layers. If a calculation involves physics (e.g., "What is the standard deviation of code volatility?"), it belongs here.

## 1. Core Architecture Map

The Measurement Layer is split into five un-bypassable structural pillars:

### 1. The Gateway & Fusion (The Resolvers)
* **Purpose:** Ingests raw data emitted by the Observation Layer and securely fuses it.
* **Mechanism:** Rather than naively averaging conflicting sensor data (e.g., GitHub showing 5 files changed, SonarQube showing 4), the `MultiSourceFusionEngine` applies **Bayesian Precision-Weighted Fusion**.
* **Guideline:** Do **not** apply temporal deduplication in this layer. The physics engine assumes the upstream Observation layer has already windowed the events (e.g., merging events occurring within a 60-second temporal buffer).

### 2. The Evaluator Sandbox (The Physics)
* **Purpose:** Computes the raw mathematical primitives (Complexity, Volume, Hotspots).
* **Mechanism:** Evaluators are completely stateless. They dynamically resolve environment specifics by polling the injected `MeasurementConfig`.
* **Guideline (The Hermetic Sandbox):** Custom DSL or PyTorch models must run exclusively within `plugins_runtime`. This runtime imposes strict limits: OS-level halting limits (2.0s), Python `__builtins__` stripping to prevent context escapes, and `weights_only=True` constraints on PyTorch models to defeat Pickle-based RCE payloads.

### 3. The Calibration Engine (The Truth)
* **Purpose:** Translates raw integer metrics into contextual, statistical reality.
* **Mechanism:** Implements **Windsorization** to isolate and squash extreme outliers (The Billionaire Fallacy). Applies dynamic time-series scaling, outputting standard deviations (Z-Scores) rather than raw counts.
* **Guideline:** A raw value is meaningless. The platform strictly operates on normalized variance. The engine guarantees that structural scoring scales equally regardless of whether a team commits 10 lines of code or 10,000.

### 4. The Enterprise Guards (Memory & Access)
* **Purpose:** Defends historical state from silent corruption and isolates multi-tenant data structures.
* **Mechanism:** 
  * **Recompute Quality Gates:** The `AppendOnlyRecomputeEngine` handles mathematical migrations safely. It yields cryptographic `supersedes_id` pointers, enforcing the rule that historical truth can never be destructively updated.
  * **Secure MQL Gateway:** The custom Measurement Query Language forcibly injects Tenant ID boundaries at the AST root. It guards against ReDoS with 2048-token length constraints and 1000ms timeouts. 
* **Guideline:** Any data requested from MQL must be delivered inside a cryptographic `LineagePayload`. Raw numbers cannot be returned without their accompanying provenance graph.

### 5. The Scientific Proving Grounds (The Laboratory)
* **Purpose:** Validates the underlying mathematical models mathematically against structural overfitting.
* **Mechanism:** 
  * **MCMC Simulator:** A Markov Chain Monte Carlo generator stresses evaluators by spawning thousands of alternate engineered realities based on probabilistic Transition Matrices.
  * **ECE Calibration:** Utilizes True Expected Calibration Error bucketing to actively penalize overconfident analytical adapters.
* **Guideline:** If a new mathematical evaluator is introduced, it must survive the MCMC Simulator prior to production availability.

---

## 2. Usage Guidelines (The Great Purge Rules)

To maintain absolute architectural purity in the Measurement Layer, the following principles are rigorously enforced:

* **No Domain Parsing:** The Measurement Layer will never parse directory structures (e.g., searching for `crates/` or `packages/`). Topology inference belongs entirely to the Observation Layer adapters.
* **No Semantic Graphs:** The Measurement engine computes covariance; it does not compute meaning. Semantic mappings (e.g., `DEPENDS_ON`, `CAUSES`) are exclusively owned by the Evidence Layer.
* **No Classifiers:** You cannot label a numeric output (e.g., `Z=+3.0`) as "High Risk" or "Critical" inside the Measurement Layer. Qualitative text categorization is strictly handled by the Cognitive Layer classifiers.
* **No LLMs:** Language Models have no place in a mathematical variance engine.

### Final Axiom
> **"The Measurement Layer is just atoms, velocity, and gravity. Evidence is where atoms bond to create chemistry."**
