# Domain & History Package (The Dictionary and The Archive)

This section covers how the system defines fundamental truths and remembers the past. 

---

## 1. `domain/` (The Universal Dictionary)
**Purpose**: Holds the absolute definitions of reality. Every other factory in the engine must use these exact definitions to communicate.
**Detailed Workflow**:
- If the Measurement Engine calculates a score, and the Cognitive Engine wants to read it, they must speak the same language. 
- The `domain/` folder contains strict Python "Data Classes" that define exactly what an `Event`, an `Entity`, or a `Measurement` is. 
- Example: It hardcodes the rule that an `ExpertiseScore` must be a float between 0.0 and 100.0. If the Cognitive Engine tries to pass a score of "High", the system will throw an error and crash. This strictness is what makes the engine so reliable.

## 2. `history/` (The Archive)
**Purpose**: Stores the chronological ledger of everything that has ever happened in the project.
**Detailed Workflow**:
- The Knowledge Graph can be queried and analyzed, but the `history/` archive is the raw backup of the universe. 
- **Immutable Law**: History is immutable. Once a developer commits code, the raw JSON of that event is stored here forever. It can never be edited or deleted. If a mistake was made, a *new* event must be added to correct it. 

## 3. `observation/` (The Watchtower)
**Purpose**: Tracks real-time occurrences in the project before they are officially logged.
**Detailed Workflow**:
- If a CI/CD build fails, it is an "Observation." The system sees it happen.
- This script catches the observation and immediately passes it to the Causal Engine to investigate. Once the investigation is complete, the observation is permanently etched into the `history/` archive as an official Event.

## 4. `query/` (The Librarian's Desk)
**Purpose**: Provides standard, hyper-fast ways to ask the system simple questions without spinning up the massive AI brain.
**Detailed Workflow**:
- Running the full AI Cognitive Brain is expensive. If a user just clicks a button on the dashboard that says "Show all developers", we shouldn't ask the AI to calculate the answer.
- The `query/` scripts contain hard-coded, perfectly optimized database searches. They bypass the AI entirely and just fetch the data instantly.
