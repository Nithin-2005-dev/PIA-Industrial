# Expertise & Transfer Package (The Teacher)

This section manages who knows what, and how to train people who don't know enough. When a senior developer leaves, this engine ensures their knowledge is safely transferred to the rest of the team.

---

## 1. `expertise_mapping/` (The Skill Radar)
**Purpose**: To build a continuous, live map of every developer's exact skill levels.
**Detailed Workflow**:
- This script does not just say "Alice is a Senior Developer." It builds a highly specific radar chart.
- It queries the graph and mathematically calculates her score on a 0-100 scale for every single file, folder, and language in the project. 
- Example Output: *"Alice knows the Database Module (99/100), the User Interface (20/100), and Python (95/100)."*
- **Fading Memory**: It also runs a forgetting curve. If Alice hasn't touched the User Interface in 2 years, her score slowly ticks down every month to reflect that the code has probably changed since she last saw it.

## 2. `knowledge_transfer/` (The Mentorship Planner)
**Purpose**: To automatically generate a curriculum when someone needs to learn a new part of the codebase.
**Detailed Workflow**:
- If Alice is leaving the company, the engine is given the command: *"Transfer Alice's knowledge to Bob."*
- The script looks at Alice's skill radar and Bob's skill radar. It subtracts Bob's knowledge from Alice's knowledge to find the exact "Gap."
- It then creates a step-by-step lesson plan: *"Bob must review these 15 specific Pull Requests that Alice wrote last year to understand the core database logic."*

## 3. `successor/` (The Backup Plan)
**Purpose**: To ensure every critical file has a designated backup owner.
**Detailed Workflow**:
- The system constantly runs a background check on the entire codebase. 
- For every file, it finds the true owner (e.g., Alice). Then it runs an algorithm to find the 2nd most knowledgeable person (e.g., Eve).
- It formally tags Eve as the "Successor" for that file. If Alice goes on vacation, the engine automatically knows to assign all of Alice's bugs directly to Eve.
