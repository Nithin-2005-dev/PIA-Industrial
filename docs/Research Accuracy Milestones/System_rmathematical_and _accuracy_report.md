# Mathematical and Architectural Audit Report

This report contains the mathematically and architecturally structured audit of the inspected intelligence layers. It has been modularized into distinct system boundaries—from raw event ingestion through the latent state engine up to the predictive and organizational tiers—providing a clear view of the exact data transformations, state accumulations, and heuristic thresholds currently implemented.

*Note: This reflects the exact, verified logic for the inspected layers; uninspected components (like parts of the Scenario Engine and Agent Layer) are excluded to maintain strict factual accuracy.*

---

## I. Event Ingestion & Normalization Layer

### 1. Event Collection & Normalization

**Purpose:** Fetch external repository activity (GitHub commits) and deterministically map them into normalized, internal `Event` objects.
**Files:** `app/adapters/github/adapter.py`, `app/ports/event_query.py`

* **Algorithm & Exact Mappings:**
* **Identifier:** Extracts `owner` and `repo` from `query.identifier`.
* **Type:** Always mapped to `COMMIT`.
* **Event ID:** Deterministic hashing based solely on the commit SHA:

$$id=\text{uuid5}(\text{NAMESPACE\_URL},\text{sha})$$


* **Actor Mapping:** Collapses missing authors into a single unknown entity.

$$actor\_ref=\begin{cases} (id=\text{"unknown"},type=\text{DEVELOPER}) & \text{if author is None} \\ (id=\text{author.login},type=\text{DEVELOPER}) & \text{otherwise} \end{cases}$$


* **Target References:** Extracts direct filenames.

$$target\_refs=\{(id=\text{file.filename},type=\text{FILE})\mid\text{file}\in\text{details.files}\}$$


* **Time & Payload:** ISO time conversion (Z $\to$ +00:00). Payload captures `sha`, `message`, and `stats` (additions/deletions/total).


* **Weaknesses:**
* Missing authors collapse into one developer entity.
* Targets are mapped as raw filenames, lacking module/path normalization.
* ID generation relies only on SHA, making repeated fetches of the same SHA yield identical events.


* **Complexity:** $\mathcal{O}\left(\sum_{i=1}^{N} (1 + |files_i|)\right)$ plus network I/O.

---

## II. The Latent State Engine (Evidence & Expertise)

### 2. Evidence Extraction & Strength Policy

**Purpose:** Convert normalized events into actionable `Evidence` records with quantified strength based on modification size.
**Files:** `app/extractor/expertise_extractor.py`, `app/extractor/policies/github_commit_strength_policy.py`

* **Mathematical Model (Strength Policy):**
Let $changes=\text{event.payload.total\_changes}$ (defaults to 0).

$$strength=\begin{cases} 0.1 & changes\le10 \\ 1.0 & 10<changes\le100 \\ 3.0 & 100<changes\le500 \\ 5.0 & 500<changes\le1000 \\ 10.0 & changes>1000 \end{cases}$$


* **Algorithm:**
* If `event.type` $\neq$ `COMMIT`, discard.
* For each target in `event.target_refs`, emit one `Evidence` object.
* **Fixed variables:** $predicate=\text{MODIFIED}$, $confidence=1.0$.
* **Evidence ID:** $e.id=\text{uuid5}(\text{NAMESPACE\_URL},\text{event.id}:\text{target.id})$.


* **Weaknesses:**
* Strength uses a coarse step function and ignores the ratio of additions to deletions.
* Predicate ignores semantic intent (always `MODIFIED`).
* Confidence is hardcoded to $1.0$.



### 3. Expertise Scoring & Time Decay

**Purpose:** Incrementally update the latent expertise state for a specific (developer, module) pair utilizing exponential time decay and evidence confidence.
**Files:** `app/estimator/expertise_estimator.py`, `app/estimator/policies/rule_expertise_scoring_policy.py`, `app/estimator/policies/exponential_decay_policy.py`

* **Mathematical Model:**
Given prior state ($S=\text{raw\_score}$, $C=\text{confidence}$, $t_{prev}=\text{updated\_at}$), and evidence ($c_e=\text{confidence}$, $\eta=\text{learning\_rate}$, $t=\text{current\_time}$):
* **Predicate Score:**

$$\text{score}(e)=\begin{cases} 1.0 & \text{MODIFIED} \\ 2.0 & \text{REVIEWED} \\ 5.0 & \text{FIXED} \\ 3.0 & \text{CREATED} \\ 1.0 & \text{MERGED} \\ 0.2 & \text{COMMENTED} \\ 0.5 & \text{TOUCHED} \\ 0.0 & \text{otherwise} \end{cases}$$


* **Contribution:**

$$\text{contribution}=\text{score}(e)\cdot\text{strength}\cdot c_e\cdot\eta$$


* **Exponential Decay:**

$$\Delta=(t-t_{prev}).\text{days}$$


$$decay\_factor=\exp(-\lambda\Delta)$$



*(Default $\lambda = 0.001$)*
* **State Updates:**

$$S'=(S\cdot decay\_factor)+\text{contribution}$$


$$C'=\min(1.0,C+0.1\cdot c_e)$$


$$t'=t$$




* **Weaknesses:**
* $\Delta$ truncates to integer days, creating stepwise (non-continuous) decay.
* Confidence is hard-clamped at $1.0$ and utilizes a rigid linear gain ($0.1$).
* Raw score updates ignore the *current* confidence state ($C$), relying only on incoming evidence confidence ($c_e$).



### 4. Expertise Projection

**Purpose:** Aggregate and maintain the factorized expertise state across the system by applying the estimator sequentially.
**Files:** `app/estimator/expertise_projection.py`

* **Algorithm:**
* Define routing key: $key(e)=(e.\text{subject\_ref.id},e.\text{object\_ref.id})$.
* If key is absent, initialize with $S=0$, $C=0$, $t_{prev}=\text{current\_time}$.
* Apply the `ExpertiseEstimator` update sequence and store the new state.


* **Weaknesses:**
* Initialization using `current_time` can artificially minimize decay for the very first update depending on processing order.
* No cross-module coupling exists.



---

## III. Organizational Analytics & Risk Layer

### 5. Ownership & Successor Recommendation

**Purpose:** Convert continuous expertise states into discrete ownership proportions, levels, and rank potential successors.
**Files:** `app/ownership/ownership_service.py`, `app/successor/successor_service.py`, `app/query/expertise_query_service.py`

* **Mathematical Model (Ownership):**
For a given module $m$, compute the effective score for all experts $i$:

$$effective\_score_i=S_i\cdot C_i$$


$$T=\sum_i effective\_score_i$$


$$p_i=\frac{effective\_score_i}{T}$$


* **Levels:** `PRIMARY` ($p_i\ge0.60$), `SECONDARY` ($0.20\le p_i<0.60$), `CONTRIBUTOR` ($p_i<0.20$).


* **Algorithm (Successor):**
* Sort owners by $p_i$ descending.
* Drop the top owner (index 0).
* Rank remaining candidates $r \in \{1, 2, \dots\}$ using $score=effective\_score_i$.


* **Weaknesses:**
* Hard thresholding causes discontinuous level shifts.
* Successor ranking ignores magnitude gaps between candidates, relying purely on positional order.



### 6. Coverage & Concentration

**Purpose:** Measure the depth of expertise on a module and evaluate top-heavy key-person dependencies.
**Files:** `app/coverage/coverage_service.py`, `app/concentration/concentration_service.py`

* **Mathematical Model (Coverage):**
For module $m$ with expert raw scores $S_j$ and count $k$:

$$average=\frac{1}{k}\sum_{j=1}^k S_j$$


$$\phi(k)=\begin{cases} 0.50 & k=1 \\ 0.75 & k=2 \\ 0.90 & k=3 \\ 1.00 & k\ge4 \end{cases}$$


$$coverage\_score=average\cdot\phi(k)$$


* **Levels:** `STRONG` ($\ge70$), `MODERATE` ($40-69$), `WEAK` ($<40$).


* **Mathematical Model (Concentration):**

$$concentration\_score=\frac{\max_j S_j}{\sum_{j=1}^k S_j}$$


* **Levels:** `LOW` ($\le0.40$), `MODERATE` ($0.41-0.70$), `HIGH` ($>0.70$).


* **Weaknesses:**
* Concentration logic risks division-by-zero if all raw scores sum to 0.
* Both layers entirely discard the `confidence` variable.
* The multiplier $\phi(k)$ introduces arbitrary jumps.



### 7. Bus Factor & Organizational Health

**Purpose:** Quantify systemic risk via cumulative ownership thresholds and combine metrics into a unified module health score.
**Files:** `app/risk/bus_factor_service.py`, `app/health/health_service.py`

* **Mathematical Model (Bus Factor):**
Sort ownership percentages $p_i$ descending. Find the minimum $count$ such that:

$$\sum_{i=1}^{count} p_i\ge0.8$$


* **Risk Level:** `HIGH` ($count=1$), `MEDIUM` ($count=2$), `LOW` ($count\ge3$).


* **Mathematical Model (Health):**

$$concentration\_health=(1-concentration\_score)\cdot100$$


$$bus\_health=\begin{cases} 100 & b\ge4 \\ 75 & b=3 \\ 50 & b=2 \\ 25 & \text{otherwise} \end{cases}$$


$$health\_score=(0.4\cdot coverage\_score)+(0.4\cdot concentration\_health)+(0.2\cdot bus\_health)$$


* **Levels:** `HEALTHY` ($\ge75$), `WARNING` ($50-74$), `CRITICAL` ($<50$).



---

## IV. Predictive & Strategic Layer

### 8. Forecasting & Future Risk

**Purpose:** Analyze historical health snapshots to project future degradation and categorize severity.
**Files:** `app/history/trend_analyzer.py`, `app/forecasting/linear_forecast_policy.py`, `app/forecasting/forecast_severity_service.py`

* **Mathematical Model (Trend & Forecast):**
Given $n$ snapshots over time ($h_1$ to $h_T$):

$$slope=\frac{h_T-h_1}{n-1}$$


$$predicted\_health=\min(100,\max(0,current\_health+(slope\cdot horizon)))$$


* **Mathematical Model (Severity):**

$$risk\_score=current\_health-predicted\_health$$



If $current\_health>0$:

$$severity=\frac{current\_health-predicted\_health}{current\_health}$$


* **Levels:** `EXTREME` ($\ge0.75$), `HIGH` ($0.50-0.74$), `MODERATE` ($0.25-0.49$), `LOW` ($<0.25$).



### 9. Simulation Readiness & Transfer Priority

**Purpose:** Rank intervention scenarios and pair mentors with successors for knowledge transfer.
**Files:** `organization_readiness_service.py`, `knowledge_transfer/simple_priority_policy.py`

* **Mathematical Model (Simulation Readiness):**

$$normalized\_expertise=\min(raw\_score/100,1.0)$$


$$rank\_bonus=\begin{cases} 0.2 & successor.rank=1 \\ 0.1 & successor.rank=2 \\ 0.0 & \text{otherwise} \end{cases}$$


$$readiness=\min(1.0,(normalized\_expertise\cdot confidence)+rank\_bonus)$$


* **Mathematical Model (Transfer Priority):**
Filtered strictly for `HIGH` concentration modules.

$$priority\_score=(concentration\_score\cdot100)+\max(0,(3-bus\_factor)\cdot10)$$



*Mentors are assigned as the max-ownership owner, learners as the highest-ranked successor.*

---

## V. Pipeline Architecture & Information Flow

Based strictly on the inspected execution paths, data flows sequentially through the system as follows:

1. **Ingestion:** `GitHubRestGateway` $\to$ `GitHubAdapter.collect` $\to$ `Event`
2. **Extraction:** `Event` $\to$ `ExpertiseExtractor` $\to$ `Evidence` *(strength determined by payload size)*
3. **Estimation:** `Evidence` $\to$ `ExpertiseProjection` $\to$ `ExpertiseEstimator` *(applies time decay, calculates $S'$ and $C'$)*
4. **Query & Normalization:** `ExpertiseQueryService` calculates $effective\_score$ $\to$ `OwnershipService` normalizes into proportions.
5. **Analytics Fork:**
* $\to$ `SuccessorPolicy` (ranks remaining owners)
* $\to$ `CoveragePolicy` (aggregates raw scores)
* $\to$ `ConcentrationPolicy` (max/total ratio)
* $\to$ `BusFactorPolicy` (cumulative ownership accumulation)


6. **Synthesis:** All analytics $\to$ `OrganizationalHealthPolicy` (computes unified health score).
7. **Prediction:** Health snapshots $\to$ `TrendAnalyzer` $\to$ `LinearForecastPolicy` $\to$ `ForecastSeverityService`.
8. **Action:** Output metrics $\to$ `Organization` transfer, readiness, and strategic planning services.