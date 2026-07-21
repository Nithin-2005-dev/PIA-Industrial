# Agent & Platform Package (The Orchestrators)

This section covers the scripts that boot up the engine and keep it running smoothly. It is the operating system that hosts the AI.

---

## 1. `agent/` (The Automated Worker)
**Purpose**: Defines how a fully autonomous AI agent operates in the background.
**Detailed Workflow**:
- The main Cognitive Engine answers direct questions from humans. But the `agent/` scripts define "Background Workers" that do not need human interaction.
- You can give an Agent a permanent goal: *"Every Friday at 5 PM, review all the code pushed this week and write a summary report."*
- The script handles waking the AI up, giving it memory of what it did last week, and letting it use tools completely autonomously.

## 2. `platform/` (The Operating System)
**Purpose**: The central nervous system of the entire project.
**Detailed Workflow**:
- Contains the `runtime.py` script, which is the massive heartbeat loop of the system. 
- It handles the exact order of operations: 
  1. Boot up the database.
  2. Start listening to GitHub.
  3. When an event arrives, pause the AI.
  4. Update the Knowledge Graph.
  5. Resume the AI.
- If this script crashes, the entire system halts.

## 3. `bootstrap/` (The Engine Starter)
**Purpose**: The script that runs when you first turn the system on.
**Detailed Workflow**:
- You cannot just turn on an AI and expect it to know your company.
- The `bootstrap/` scripts handle the heavy lifting of the first-time setup. It connects to the APIs, downloads the entire 10-year history of the company's code repository, and spends 3 hours aggressively crunching the numbers to build the initial Knowledge Graph. 
- Once it is done, it hands control over to the `platform/` runtime.

## 4. `ports/` (The Plugs)
**Purpose**: Defines strict interfaces (plugs) so the engine doesn't get permanently glued to specific external tools.
**Detailed Workflow**:
- The engine uses a database to store its graph. But what if the company wants to switch from Neo4j to a different graph database?
- The `ports/` folder uses "Dependency Inversion." It defines a generic plug called `DatabasePort`. 
- As long as the new database can fit the shape of the `DatabasePort`, it can be swapped in without modifying a single line of the core AI logic.
