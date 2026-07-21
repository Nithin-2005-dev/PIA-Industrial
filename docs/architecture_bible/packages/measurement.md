# Measurement Package (The Ruler & Data Organizer)

This package contains the logic for **Measurement**. It acts as the system's "Ruler." Before the AI Brain can make smart decisions, it needs hard, undeniable numbers. This package calculates exactly how many lines of code were changed, how fast bugs were fixed, and how much a developer actually knows.

Since this package is massive, it is organized into highly specialized sub-departments. Here is the exact breakdown of how data flows through them.

---

## 1. `core/` (The Engine Room)
**Purpose**: This is the heart of the measurement system. It orchestrates the reading of data, grading, and storing of results.
**Detailed Workflow**:
- `engine.py`: The boss of the measurement team. It is triggered by the system and given a target (e.g., "Measure the health of the entire project right now"). It then loads all the individual evaluators (graders) and runs them across the codebase.
- `calibration/models.py`: This acts as a tuner. If a developer writes 1,000 lines of code in one day, is that a "100/100" score, or is it normal for this project? This script ensures that scores are calibrated to the specific reality of the current project, ensuring a score of "High Risk" actually means high risk.

---

## 2. `evaluators/` (The Graders)
**Purpose**: These are specialized scripts that look at specific slices of the project and issue a grade.
**Detailed Workflow**:
- `file_activity.py`: Checks the "heat" of a file. It counts how many times a file is edited, by how many different people, and how often those edits result in bugs. If a file is edited 50 times a week by 10 different people, it flags it as a dangerous hotspot.
- `developer_activity.py`: Grades human behavior. It measures commit frequency, review speed, and size of code changes to detect if a developer is highly productive, stuck, or at risk of burning out.

---

## 3. `analytics/` & `benchmarks/` (The Report Cards)
**Purpose**: Takes the raw math from the evaluators and turns them into human-readable percentiles and charts.
**Detailed Workflow**:
- **Analytics**: Converts raw data into time-series trends. Instead of "Score: 4.5", it calculates "Score: 4.5 (Up 10% from last month)."
- **Benchmarks**: Compares the team against industry standards or historical averages. It calculates percentiles, answering questions like "Is a 2-day bug-fix turnaround time good or bad compared to the rest of the company?"

---

## 4. `scientific_engine/` & `scientific/` (The Research Labs)
**Purpose**: Contains heavy academic algorithms for deep statistical analysis. 
**Detailed Workflow**:
- It doesn't just do basic addition and subtraction. It calculates complex statistical deviations (e.g., Z-scores, P-values). 
- **Significance Testing**: If the bug rate drops by 2% this week, the scientific engine calculates whether that drop is a genuine improvement, or just random statistical noise. It prevents the AI from falsely celebrating random fluctuations.

---

## 5. `signal_intelligence/` (The Pattern Spotter)
**Purpose**: Looks at the combined grades across all evaluators and tries to spot hidden patterns ("Signals").
**Detailed Workflow**:
- **Cross-Referencing**: It takes a measurement from `developer_activity.py` (e.g., "Alice is working 80 hours a week") and crosses it with `file_activity.py` (e.g., "Alice is the only person editing the core database"). 
- **Signal Emission**: It combines those two facts to emit a high-level warning signal: "CRITICAL: Single-point of failure detected; key developer at high risk of burnout." 

---

## 6. `identity/` (The Detective Agency)
**Purpose**: Solves the problem of messy human usernames.
**Detailed Workflow**:
- In a large project, Alice might commit code using `alice@company.com` on her laptop, `alice.dev@gmail.com` on her home computer, and the GitHub username `AliceNinja`.
- This script uses heuristic matching (comparing names, emails, and timestamp patterns) to definitively merge all those different aliases into one single "Alice" profile. 
- **Why this matters**: Without this, the system would think 3 different people were working on the project, completely breaking all expertise calculations.

---

## 7. `domain/` & `query/` (The Dictionary & Search Engine)
**Purpose**: Structures the measurements and makes them searchable.
**Detailed Workflow**:
- `domain/`: Defines the rigid code structures for what a "Measurement" is. It ensures every measurement has a timestamp, a target, and a numerical value.
- `query/`: Handles the database logic. When the CEO's dashboard asks "Give me the health scores for the last 12 months," this script pulls millions of rows from the database in milliseconds and serves them up.

---

## 8. `plugins_runtime/` (The Expansion Slot)
**Purpose**: Allows external teams to write their own custom code without breaking the core engine.
**Detailed Workflow**:
- If a team wants to grade "Code Style Guidelines", they can write a custom Evaluator and drop it into this folder. The `engine.py` will automatically detect it and start running it during the next cycle without any core code needing to be modified.
