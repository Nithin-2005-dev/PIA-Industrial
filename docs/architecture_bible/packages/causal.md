# Causal Engine Package (The "Why did this happen?" Detective)

This package contains the logic for **Causal Reasoning**. While the Knowledge Graph tells us *that* two things are connected (e.g., "Alice edited `auth.py`"), the Causal Engine figures out *why* they are connected, and more importantly, it identifies the root cause of complex events (e.g., "Why is the login module failing in production?").

The engine operates exactly like a team of detectives solving a mystery. Here is the step-by-step breakdown of every file in the package and exactly what it does during an investigation.

---

## 1. `engine.py` (The Chief Detective)
**Purpose**: This is the orchestrator of the entire causal subsystem. It is the only file that external systems talk to. 
**Detailed Workflow**:
1. **Receive the Case**: It receives an `Observation` (e.g., "The server crashed at 2 PM").
2. **Assign the Analysts**: It calls `hypothesis.py` and says: "Give me 5 theories as to why this crashed."
3. **Dispatch the Forensics Team**: It takes those 5 theories and passes them to `rules.py` and `graph.py` to check the facts against the database.
4. **Compile the Report**: Once the theories are proven or disproven, it passes the surviving theories to `explanation.py` to draft a final, human-readable report.
**Non-Technical Takeaway**: The engine itself doesn't do the heavy math; it acts as the project manager, making sure all the other scripts do their jobs in the correct order.

---

## 2. `hypothesis.py` (The Theory Generator)
**Purpose**: To generate educated guesses before the system starts searching through millions of records.
**Detailed Workflow**:
1. **Pattern Matching**: When given a problem (e.g., "Bug in `auth.py`"), this script looks at the `ontology.py` rulebook to see what usually causes bugs. 
2. **Theory Generation**: It generates specific, testable theories. 
   - *Theory A*: "A recent commit introduced a syntax error."
   - *Theory B*: "A core dependency was updated yesterday."
   - *Theory C*: "The developer who wrote this file recently left the company."
3. **Routing**: It attaches specific instructions to each theory detailing *how* to prove it. (e.g., "To prove Theory A, check the commit history of `auth.py` for the last 48 hours").
**Non-Technical Takeaway**: Without this file, the AI would blindly search the entire database. This file narrows the search down to the 3 or 4 most logical explanations.

---

## 3. `graph.py` (The Evidence Board)
**Purpose**: A highly specialized lens for viewing the Knowledge Graph, strictly designed to track cause-and-effect over time.
**Detailed Workflow**:
1. **Time-Aware Pathfinding**: Regular graphs just show connections. This script ensures that time flows correctly. It enforces the rule: "Cause must happen before Effect." If a bug was reported at 2:00 PM, it will completely ignore any code committed at 3:00 PM.
2. **Sub-graph Extraction**: It pulls only the relevant string of events out of the massive database and holds them in working memory.
**Non-Technical Takeaway**: It prevents the AI from getting confused by timelines, acting like a corkboard where every piece of evidence is strictly ordered by when it happened.

---

## 4. `rules.py` (The Logic Enforcer)
**Purpose**: Holds the mathematical rules used to officially "prove" or "disprove" a theory.
**Detailed Workflow**:
1. **Execution of Rules**: If `hypothesis.py` says "Check if a core dependency was updated," `rules.py` executes the actual math. 
2. **Confidence Scoring**: It doesn't just return "Yes" or "No". It returns a Confidence Score. If the dependency was updated 5 minutes before the crash, confidence is 99%. If it was updated 3 months ago, confidence is 5%.
**Non-Technical Takeaway**: This is the strict fact-checker. It relies purely on data and math, not AI guessing.

---

## 5. `explanation.py` (The Final Report Writer)
**Purpose**: Translates the raw math and data back into a human-readable argument.
**Detailed Workflow**:
1. **Structuring the Argument**: It forces the AI to output exactly three things:
   - **The Claim**: What happened? ("Bob's commit broke the server.")
   - **The Evidence**: How do we know? ("Bob edited the exact line of code that threw the error, and he did it 10 minutes before the crash.")
   - **The Confidence**: How sure are we? ("We are 95% confident.")
2. **Rejection**: If the AI tries to make a claim but cannot provide the hard evidence to back it up, this script rejects the report and throws an error.
**Non-Technical Takeaway**: This guarantees that the system never hallucinates. Every answer given to a user is backed by a structured, undeniable trail of evidence.

---

## 6. `ontology.py` (The Laws of Physics)
**Purpose**: Defines what is realistically possible in the software development universe.
**Detailed Workflow**:
1. **Defining Relationships**: It hardcodes rules like "A Pull Request contains Commits." It makes it impossible for the AI to think "A Commit contains Pull Requests."
2. **Preventing Paradoxes**: It ensures that an entity cannot cause itself to exist.
**Non-Technical Takeaway**: It gives the AI basic "common sense" so it doesn't waste time investigating impossible theories.

---

## 7. `models.py` (The Dictionary)
**Purpose**: Defines the rigid data templates used by all the other files.
**Detailed Workflow**:
1. **Type Safety**: It guarantees that an `Explanation` object will always have a `confidence` field that is a decimal number between 0.0 and 1.0. 
**Non-Technical Takeaway**: It ensures all the detectives on the team speak exactly the same language and use the same forms.
