# Simulation Package (The Time Machine)

This package contains the logic for **Simulation**. Once the system understands the past (Events) and the present (Knowledge Graph), the Simulation engine allows users to fast-forward into the future and see what happens if they change the rules. 

Unlike simple forecasting (which just draws a trend line), Simulation physically alters the Knowledge Graph in an isolated sandbox, allowing managers to test highly destructive decisions without actually harming the real project. Here is how it works step-by-step.

---

## 1. `engine.py` (The Simulator Core)
**Purpose**: The central brain that runs the time machine.
**Detailed Workflow**:
1. **Snapshot Isolation**: When a simulation starts, `engine.py` takes a complete snapshot of the massive Knowledge Graph. It places this snapshot into a secure, isolated sandbox. This ensures that any fake data created during the simulation does not permanently pollute the real company database.
2. **Applying Interventions**: It takes a hypothetical command (e.g., "Fire Alice") and forces that change onto the sandboxed graph. It removes all of Alice's connections to the code.
3. **Running the Clock**: It simulates the passage of time. It recalculates the "Bus Factor", productivity metrics, and expertise levels day by day, month by month in the sandbox.
4. **Generating the Delta**: Once the simulation ends (e.g., 6 months in the future), the engine compares the simulated reality against the current reality, and outputs exactly how much better (or worse) things got.

---

## 2. `interventions.py` (The "What If?" Scenarios)
**Purpose**: Defines the exact mathematical and structural changes for every hypothetical scenario you can run.
**Detailed Workflow**:
- **Developer Departure**: If the scenario is "Alice leaves," this script doesn't just delete her name. It mathematically forces a "Knowledge Decay" curve on every file she owned, showing exactly how fast the team will forget how her code works.
- **Team Expansion**: If the scenario is "Hire 3 Juniors," this script immediately applies a "Training Tax" to the Senior developers. It knows that adding Juniors will actually *slow down* the project for the first 3 months because the Seniors have to spend time reviewing their code.
- **Code Refactoring**: If the scenario is "Rewrite the Database Module," this script temporarily freezes new features in that module and simulates the massive bug spike that usually happens right after a rewrite.

---

## 3. `cost_model.py` (The Accountant)
**Purpose**: Every intervention has a hidden cost. This script forces the AI to calculate reality, rather than magical wishful thinking.
**Detailed Workflow**:
- **Productivity Loss Formula**: If you remove a senior developer, the team doesn't just lose their 40 hours a week. `cost_model.py` calculates the cascading delay: because the senior isn't there to review code, the juniors are blocked for an extra 2 days per ticket.
- **Onboarding Tax**: When simulating a new hire, the cost model enforces a rigid formula: Month 1 = 10% productivity, Month 2 = 30%, Month 3 = 60%. 
- **Why we need it**: It prevents managers from thinking that firing an expensive expert and replacing them with 3 cheap juniors will instantly solve a project's timeline problems.

---

## 4. `models.py` (The Time Machine Dictionary)
**Purpose**: Ensures all parts of the simulation engine speak the exact same language.
**Detailed Workflow**:
- It strictly defines what a `SimulationState` object looks like in memory. It guarantees that every simulation has a `Start Date`, an `End Date`, a list of `Applied Interventions`, and a rigid `Before/After` metrics comparison table.

---

## 5. `registry.py` (The Scenario Catalog)
**Purpose**: A central directory of all available simulations.
**Detailed Workflow**:
- If an engineer writes a new complex intervention script (e.g., "What if we switch from Python to Rust?"), they must register it here.
- The Cognitive Brain reads this registry to know exactly what scenarios it is allowed to offer the user when the user asks: "What are my options to speed this project up?"
