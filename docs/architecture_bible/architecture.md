# System Architecture (How it Works)

This document explains the physical layout and flow of the PIA project. Think of this as the blueprint for our "Intelligent Librarian."

## Overall Architecture
At a high level, the system acts like a massive funnel. At the top of the funnel, raw, messy data pours in from the outside world (like GitHub commits, Jira tickets, or Slack messages). As it travels down the funnel, it is cleaned, organized, and connected together until it forms a perfectly structured "Knowledge Graph." Finally, at the very bottom, an AI "Brain" (the Cognitive Engine) sits on top of this graph, ready to answer questions and make predictions.

## Subsystems
The engine is split into a few major factories:
1. **Adapters (The Ears and Eyes)**: These connect to external tools like GitHub. They listen for things happening and convert them into a standard format.
2. **The Measurement Engine (The Organizers)**: This takes the standard formats and figures out what they actually mean. Did Bob fix a bug, or did he create a new feature?
3. **The Knowledge Graph (The Memory)**: This is a massive web connecting every developer to every file they've ever touched.
4. **The Cognitive Engine (The Brain)**: The AI layer that actually reads the Knowledge Graph to answer user questions or make decisions.

## Execution Pipeline
When a new piece of information arrives, it goes down an assembly line:
1. **Ingest**: Grab the raw data.
2. **Parse**: Extract the "who, what, and when."
3. **Link**: Connect this new information to everything else we already know.
4. **Think**: Trigger the AI to review the new information and update its predictions (like "Does this team need more help?").

## Data Flow & Control Flow
Data flows strictly in one direction: from the outside world inward. The system never goes out and changes your code on GitHub. It is a read-only observer. The "Control Flow" (the boss deciding what happens next) is managed by an Orchestrator, which acts like a traffic cop directing data to the right factory.

## Capability Graph
A "Capability" is simply a tool the AI can use. For example, "Find Top Contributors" is a capability. The Capability Graph is a map that teaches the AI which tools it is allowed to use to answer a specific question. If you ask "Who is the best person to fix this bug?", the AI looks at the map and realizes it needs to use the "Find Top Contributors" tool and the "Analyze Bug History" tool.

## Memory Architecture
The system has two types of memory:
- **Repository Memory (Long-Term)**: This is the massive database storing years of project history. It never forgets.
- **Working Memory (Short-Term)**: When you ask the AI a question, it pulls only the most relevant pieces of information onto its "desk" (the Working Memory) so it doesn't get overwhelmed reading the entire history at once.

## Provider Architecture
The "Provider" is the actual AI model doing the reading and writing (like OpenAI's GPT-4, Google's Gemini, or a local open-source model). Our architecture allows us to unplug one AI and plug in a different one seamlessly, without breaking the rest of the system.

## Planning & Execution Architecture
When you ask the AI a complex question, it doesn't just guess. It creates a step-by-step **Plan** (Planning Architecture) and then follows it (Execution Architecture). It might say: "Step 1: Check who wrote the code. Step 2: Check if they are still at the company. Step 3: Recommend a backup reviewer."

## Validation Architecture
We don't trust the AI blindly. The Validation layer acts as an automated proofreader. If the AI hallucinates or gives an answer that breaks our rules, the Validator catches it and forces the AI to try again before showing the user the answer.

## Event & Telemetry Architecture
This is our internal security camera. It records exactly how long the AI took to think, which tools it used, and whether it succeeded. This helps the engineers make the system faster and smarter over time.

## Security Model & Scalability Strategy
- **Security**: The AI is kept in a restricted sandbox. It can read data, but it cannot execute arbitrary code on the user's computer or leak secrets.
- **Scalability**: The system is designed to handle thousands of events per second by queuing them up in an orderly line, rather than trying to process everything exactly at the same millisecond.

## Future Evolution
Eventually, this system will evolve from a passive observer (answering questions) into an active participant, capable of automatically assigning tasks, rebalancing team workloads, and warning managers weeks in advance if a project is going to miss its deadline.
