# Phase 28: Engineering PageRank Engine

## Objective
With the Evidence Layer fully stabilized and structurally isolated, the system required a mathematical engine capable of calculating the true structural power and authority of engineers within the organization. Standard metric aggregation fails at this task by prioritizing code volume over structural importance (The Endorsement Fallacy). 

This update documents the implementation of the `OrganizationalPageRankEngine`, utilizing a semantically-aware Markov Chain algorithm to calculate Eigenvector Centrality based on dependency gravity.

## The Flaw of Standard PageRank
Standard PageRank distributes gravity evenly across all outgoing edges. If a developer (Node A) commits a bug to a core router (Node B), standard PageRank would flow gravity *from the router back to the developer*, effectively rewarding the developer for causing a high-impact incident.

## Dynamic Topological Inversion
To resolve this, we introduced three strict semantic flow categories to control how gravity propagates through the graph:

### 1. Constructive/Ownership Flow (`AUTHORED`)
* **Direction:** Target (Code) -> Source (Human)
* **Mechanics:** When an engineer authors a module, the module gives its accumulated gravity back to the engineer. This ensures that engineers who build highly depended-upon infrastructure are algorithmically recognized as "Architects."

### 2. Dependency Flow (`DEPENDS_ON`, `CALLS`, `USES`)
* **Direction:** Source (Dependent) -> Target (Dependency)
* **Mechanics:** When a CSS file depends on a Core Router, the CSS file gives gravity to the Core Router. The Core Router absorbs the structural importance of the entire dependency tree.

### 3. Destructive Flow (`INTRODUCED_BUG_IN`, `CAUSED_INCIDENT`)
* **Direction:** Source (Human) -> Target (Code)
* **Mechanics:** This is the **Topological Inversion**. When an engineer breaks a system, gravity flows *away* from the engineer and *into* the system. This mathematically penalizes the liability of the engineer while correctly asserting the structural criticality of the broken system.

## Implementation Details

### The Mathematical Engine
* **File:** `app/evidence/ranking/ranking.py`
* **Components Added:**
  * `OrganizationalPageRankEngine`: Executes the core Power Iteration loop.
  * `DESTRUCTIVE_EDGES`: Pre-configured set of inverted relationships (`INTRODUCED_BUG_IN`, etc.).
  * `DEPENDENCY_EDGES`: Pre-configured set of forward-flowing relationships (`DEPENDS_ON`, etc.).
  * Applies a standard teleportation/damping factor (0.85) to prevent graph disconnection traps.

### The Ranking Service 
* **File:** `app/evidence/ranking/__init__.py`
* **Components Added:**
  * `RankingService`: Acts as the interface boundary.
  * Extracts the raw Graph Topology using the `IEvidenceGraphStore` interface.
  * Re-projects Measurement Layer Z-Scores as literal edge weights in the Markov transition matrix.
  * Persists the computed Eigenvector Centrality back to the Graph Database as the `structural_authority` property.

## Scientific Verification
* **Test Case:** `tests/test_engineering_pagerank.py`
* **Result:** The mathematical proof passed successfully. The test mathematically demonstrated that an Architect who authored a single, highly-depended Core Router receives vastly more structural gravity than a "Grinder" who authored 5 isolated, non-depended CSS files. Volume was entirely defeated by Gravity.
