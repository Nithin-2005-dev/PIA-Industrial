# Cognitive Package (The AI Brain)

This massive folder holds the 35 scripts that make up the system's "Brain." It handles everything from understanding what a user types to generating a final, verified answer. 

Because the AI must never hallucinate and must always follow strict corporate policies, it does not just "guess" answers. It routes the user's question through a highly structured 10-step assembly line. Here is exactly what happens when you type a question into the system.

---

## 1. `router.py` & `semantic_parser.py` (The Front Desk)
**Purpose**: To translate messy human English into strict computer logic.
**Detailed Workflow**:
- You ask: *"Why did the payment module crash yesterday?"*
- `router.py` acts as the receptionist. It looks at the sentence and decides which subsystem is best suited to answer it. (In this case, the Causal Engine).
- `semantic_parser.py` acts as the translator. It rips the English sentence apart and turns it into a strict query: 
  - `TARGET`: "Payment Module"
  - `EVENT`: "Crash"
  - `TIMEFRAME`: "Yesterday (Last 24 Hours)"
- **Why we need it**: AI models are unpredictable when dealing with free-form text. By forcing the text into a rigid box first, we guarantee the rest of the system knows exactly what it is looking for.

## 2. `planner.py` & `decomposer.py` (The Project Managers)
**Purpose**: To break a massive, impossible question into tiny, solvable steps.
**Detailed Workflow**:
- You ask: *"Is the team healthy?"* (A massive, ambiguous question).
- `decomposer.py` breaks this into 3 smaller goals:
  - 1. Check developer commit frequency over the last 30 days.
  - 2. Check the average time it takes to review a Pull Request.
  - 3. Check if the project has a dangerous "Bus Factor."
- `planner.py` then takes these 3 goals and creates a step-by-step checklist. It assigns a strict order to the tasks so the AI knows exactly what to do first, second, and third.

## 3. `tools.py` & `tool_search.py` (The Toolbox)
**Purpose**: To give the AI specific abilities, so it doesn't have to rely on its training data.
**Detailed Workflow**:
- The AI does *not* know your company's code. To answer questions, it must use tools. 
- `tools.py` defines these abilities, such as a tool called `find_top_committer(file_path)`. 
- `tool_search.py` helps the Planner figure out which tool to use. If the sub-goal is "Check the Bus Factor", it searches the toolbox and hands the `calculate_bus_factor()` tool to the Executor.

## 4. `retriever.py` & `repository_knowledge.py` (The Librarians)
**Purpose**: To fetch the actual data required by the tools.
**Detailed Workflow**:
- Once a tool is activated, it needs data. `retriever.py` dives into the massive Knowledge Graph and pulls out only the exact nodes and edges required for the task.
- `repository_knowledge.py` specifically fetches metadata about the codebase itself (like the folder structure, or the list of active branches).

## 5. `executor.py` & `orchestrator.py` (The Workers)
**Purpose**: The actual execution of the tasks.
**Detailed Workflow**:
- `orchestrator.py` is the assembly line boss. It reads the Planner's checklist and says "Okay, start Task 1."
- `executor.py` is the worker on the floor. It takes the tool, takes the data from the retriever, and runs the calculation. It then hands the result back to the Orchestrator, who crosses Task 1 off the list and moves to Task 2.

## 6. `reflection.py` & `critic.py` (The Self-Doubt Mechanism)
**Purpose**: To force the AI to double-check its own logic before proceeding.
**Detailed Workflow**:
- Once the Executor finishes a task, the AI doesn't just blindly accept it. 
- `reflection.py` asks: *"Did we actually answer the specific question that was asked? Did we miss anything?"*
- `critic.py` acts as an adversary. It actively tries to find flaws in the AI's logic. If it finds a gap (e.g., *"You said Alice is the expert, but she hasn't committed code in 2 years"*), it forces the Orchestrator to go back to the Planner and try again.

## 7. `verifier.py` & `validation.py` (The Fact Checkers)
**Purpose**: A non-AI safety net to prevent hallucinations.
**Detailed Workflow**:
- Even if the AI passes its own reflection, we don't trust it. 
- `verifier.py` takes the final claim and runs strict database queries to prove it. If the AI claims a file exists, the Verifier literally checks the hard drive to make sure the file exists. If it doesn't, the answer is rejected entirely.

## 8. `provider_manager.py` & `provider.py` (The AI Plugs)
**Purpose**: To manage the connection to the actual Large Language Models (LLMs).
**Detailed Workflow**:
- The system is completely agnostic to *which* AI is used. `provider.py` acts as a universal plug. You can plug in OpenAI's GPT-4, Google's Gemini, or a local open-source model.
- `provider_manager.py` handles fallbacks. If OpenAI crashes or rate-limits the system, the manager instantly and silently switches the connection to Gemini so the user never experiences an error.

## 9. `answer_builder.py` & `composer.py` (The Writers)
**Purpose**: To turn the raw data back into a beautiful, human-readable report.
**Detailed Workflow**:
- The Orchestrator hands the raw, verified facts (e.g., `[user_id: 123, confidence: 0.98, cause: bug_402]`) to the Composer.
- `composer.py` weaves these facts into a cohesive, polite, and perfectly formatted Markdown response for the user, ensuring that every claim is cited with a link back to the exact code commit that proves it.
