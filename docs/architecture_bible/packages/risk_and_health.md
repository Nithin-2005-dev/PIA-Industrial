# Risk & Health Package (The Doctor)

This section acts as the project's doctor. It doesn't just measure raw numbers; it runs complex diagnoses to warn managers before a project crashes. Here is exactly how the scripts in this package identify hidden illnesses in the project.

---

## 1. `health/` (The General Practitioner)
**Purpose**: To constantly monitor the overall vital signs of the project.
**Detailed Workflow**:
- The scripts here pull in the raw metrics from the Measurement Engine (like "Average Code Review Time = 4 days").
- They then apply health thresholds. If the standard policy says reviews should take 2 days, and they are taking 4 days, the health engine issues a diagnosis: *"Code Review Bottleneck Detected."*
- It aggregates hundreds of these micro-diagnoses into a single, understandable letter grade (e.g., "Project Health: B-").

## 2. `risk/` (The Emergency Room Triage)
**Purpose**: To flag imminent disasters that need immediate human intervention.
**Detailed Workflow**:
- While the `health` engine looks at long-term trends, the `risk` engine looks for acute emergencies.
- Example: If an intern suddenly deletes 50 files from the core authentication module, the Risk engine immediately flags this as a `Critical Severity Event` and alerts the orchestrator to pause deployments.

## 3. `concentration/` & `knowledge_risk/` (The Bus Factor Calculator)
**Purpose**: To detect if the project is secretly reliant on just one or two people.
**Detailed Workflow**:
- **The Bus Factor Math**: This engine asks a terrifying question: *"If a bus hit Developer A, what percentage of the codebase would be left with zero experts?"*
- It queries the Knowledge Graph for every file. If `database.py` is only connected to Developer A, that file is at 100% risk. 
- It then calculates this across the entire company. If it finds that 60% of the project relies solely on Developer A, it issues a severe `Knowledge Risk Alert`.

## 4. `ownership/` (The Landlord)
**Purpose**: To mathematically prove who actually "owns" a piece of code.
**Detailed Workflow**:
- In a large team, 10 people might edit a file to fix typos, but only 1 person built the complex logic. 
- This script calculates true ownership. It weighs line deletions vs. additions, structural changes vs. comment changes. 
- It might output: *"Bob is the owner of this file (85%), Alice is a contributor (10%), and Eve is a minor editor (5%)."*

## 5. `coverage/` (The Shield Inspector)
**Purpose**: To ensure the most dangerous code is protected by automated tests.
**Detailed Workflow**:
- If `auth.py` is flagged by the Risk engine as the most complex and critical file in the system, the `coverage/` engine checks to see if anyone has written automated tests to verify that it works.
- If it finds zero tests for a critical file, it mathematically drastically increases the risk score of the entire project, because a single typo could crash the company.
