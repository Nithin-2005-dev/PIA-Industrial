# The Encyclopedias (The System Catalogs)

This section serves as a directory of all the "lists" the system keeps track of. Instead of hard-coding everything, the engine uses these encyclopedias as living dictionaries.

## 1. Capability Encyclopedia (The Toolbox)
This is the list of every single tool the AI is allowed to use. 
- **Purpose**: To tell the AI what it can and cannot do.
- **Examples**: "Read a File", "Find Top Committer", "Simulate Developer Departure".
- **Execution Flow**: Each tool explains exactly what inputs it needs (e.g., a developer's name) and what outputs it returns (e.g., a list of files).

## 2. Model Encyclopedia (The Dictionary)
This defines the structure of every piece of data in the system.
- **Meaning**: Like a dictionary definition, it ensures that when the system talks about an "Event," everyone agrees on exactly what an Event looks like (e.g., it must have an ID, a Time, and an Actor).
- **Constraints**: It enforces rules, such as "A Confidence Score can never be higher than 100%."

## 3. Algorithm Encyclopedia (The Recipe Book)
This contains the step-by-step math equations the system uses to make predictions.
- **Problem**: How do we calculate if a file is dangerous to edit?
- **Trade-offs**: We might use a fast recipe that guesses, or a slow recipe that is 100% accurate. The encyclopedia documents *why* we chose the recipe we did.
- **Examples**: The "Bus Factor" algorithm calculates how many people need to quit before a project fails.

## 4. Prompt Encyclopedia (The AI Scripts)
We don't just say "Hey AI, do this." We give the AI highly specific instructions called "Prompts."
- **Purpose**: To guarantee the AI behaves predictably.
- **Construction**: Prompts are built like mad-libs. "Analyze the bug in [FILE_NAME] written by [DEVELOPER_NAME]."
- **Failure Cases**: The encyclopedia tracks what happens if the AI misunderstands the prompt, so engineers can fix it.

## 5. API Encyclopedia (The Front Door)
This documents how external users (like the web dashboard) talk to the engine.
- **Parameters**: What the user must provide (e.g., "Project ID").
- **Exceptions**: What errors the user gets if they do something wrong.
- **Compatibility**: Ensuring that old dashboards still work even when we upgrade the engine.

## 6. Event Encyclopedia (The History Book Categories)
Every time something happens in the real world, it is logged as an Event. This catalog lists the types of events.
- **Publisher**: Who created the event (e.g., GitHub).
- **Payload**: What information is inside it (e.g., a commit hash).
- **Timing**: How fast the system processes it.

## 7. Benchmark Encyclopedia (The Report Card)
We need to know if our AI is actually smart. This encyclopedia keeps track of all our tests.
- **Dataset**: The practice questions we give the AI.
- **Scoring**: How we grade the AI (e.g., did it find the right expert 9 out of 10 times?).
- **Acceptance Thresholds**: The minimum grade the AI must get before we let it talk to real users.
