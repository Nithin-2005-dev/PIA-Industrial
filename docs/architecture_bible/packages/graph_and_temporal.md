# Graph & Temporal Package (The Map and The Clock)

This section manages the physical storage of intelligence and the ability to time-travel through the project's history.

---

## 1. `graph/` (The Map Maker)
**Purpose**: The physical engine that builds and manages the Knowledge Graph.
**Detailed Workflow**:
- Traditional databases store data in rows and columns. This is terrible for asking questions like *"Who knows the person who wrote the file that broke the server?"*
- The `graph/` scripts manage a specialized database where data is stored as Nodes (Dots) and Edges (Lines connecting the dots). 
- It handles the math required to traverse millions of dots in a fraction of a second, ensuring the AI Brain never has to wait for data.

## 2. `temporal/` (The Clock)
**Purpose**: Manages time-travel, allowing the AI to ask questions about the past.
**Detailed Workflow**:
- If a manager asks: *"Who was our best developer 2 years ago?"*, the system cannot look at the graph today. It must rewind time.
- The `temporal/` engine achieves this because it never deletes anything. Every time a dot or line is changed in the graph, it receives a timestamp. 
- When the AI asks to travel back 2 years, this script simply filters out every single piece of data that has a timestamp newer than 2 years ago, instantly recreating the exact state of the project from the past.

## 3. `extractor/` & `estimator/` (The Miners)
**Purpose**: To pull missing data out of thin air.
**Detailed Workflow**:
- **Extractor**: Developers are lazy. They often write commit messages like *"Fixed stuff."* The `extractor/` script uses Natural Language Processing to scan the actual code changes to figure out what they really fixed, creating rich data out of poor human input.
- **Estimator**: Sometimes, the data is completely missing. If a developer joins the team and works entirely offline for a week, the system has a gap in its knowledge. The `estimator/` runs statistical math to fill in the blank, guessing what the developer probably did based on what files they eventually uploaded.
