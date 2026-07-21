# Cognitive Engine (The AI Brain)

This document explains the inner workings of the "Cognitive Engine," which acts as the intelligent brain of the PIA project. When a manager asks a question like "Why is this project delayed?", this is the factory that figures out the answer.

## 1. Intent Routing (Understanding the Goal)
When you ask the system a question, it doesn't just blindly throw the text at an AI. The **Intent Router** acts as the front desk receptionist. It reads your question and decides: "Is this person asking about a developer's expertise, a code bug, or a schedule delay?" Once it figures out the core *intent* of your question, it routes you to the correct department.

## 2. Semantic Parsing (Translating English to Code)
Before the system can search its massive memory banks, it needs to translate your English question into strict, searchable rules. If you ask "Who fixed the login bug?", the Semantic Parser translates this into: 
- `Subject` = Person (Unknown)
- `Action` = FIXED
- `Object` = Issue (Title contains "login")

## 3. Planning & Goal Decomposition (Breaking the Problem Down)
A big question is usually made of smaller questions. If you ask "Is the team healthy?", the Planner breaks this massive goal into smaller chunks (Goal Decomposition):
- Sub-goal A: Check how many people are leaving the project.
- Sub-goal B: Check if there are massive bugs piling up.
- Sub-goal C: Check if only one person knows how the whole system works (Bus Factor).

## 4. Capability Retrieval (Picking the Right Tools)
The engine has a toolbox full of different "Capabilities" (like a calculator, a search engine, or a risk predictor). Once the Planner has its sub-goals, it looks at the toolbox and pulls out exactly the tools it needs to solve those specific problems. 

## 5. Execution & Reflection (Doing the Work and Double-Checking)
The system now uses the tools it selected to find the answers (Execution). However, the engine is self-aware. Once it finds an answer, it triggers a **Reflection** phase. The AI asks itself: "Did I actually answer the question that was asked? Does this answer make logical sense?" If it realizes it made a mistake, it goes back and tries again.

## 6. Verification (The Fact Checker)
Even after the AI reflects on its own work, we run a strict, non-AI rule checker (Verification). This step ensures the AI didn't hallucinate facts. If the AI says "Alice fixed the bug," the Verifier actually checks the database to make sure Alice's name is on the commit. 

## 7. Answer Generation & Confidence Computation (Giving the Final Report)
Once the facts are verified, the AI writes a clean, easy-to-read summary for you (Answer Generation). But crucially, it also gives you a **Confidence Score**. If the system only found partial evidence, it might say: "I believe the answer is X, but I am only 60% confident." It will never pretend to be 100% sure if it isn't.

## 8. Policy Engine (The Rulebook)
The AI isn't allowed to do whatever it wants. The Policy Engine is a strict set of company rules the AI must follow. For example, a policy might say: "Never reveal salaries to standard users," or "Always prioritize recent code over 5-year-old code." The AI must check this rulebook before making any decision.

## 9. Provider Management (Swapping AI Brains)
Sometimes the OpenAI brain is down, or we want to use a cheaper local AI brain for simple tasks. The Provider Manager handles this seamlessly. If one AI provider crashes, the manager instantly switches to a backup provider so the system never stops working.

## 10. Memory Updates & Event Emission (Learning for Next Time)
After the AI finishes answering a question, it doesn't just forget everything. It saves a summary of what it learned back into its Short-Term Memory. It also broadcasts an "Event" (like a loudspeaker announcement) to the rest of the system saying: "I just finished answering a question about the login bug." This allows other parts of the system to update their own records.
