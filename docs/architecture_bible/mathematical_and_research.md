# Mathematical & Research Bible

This document translates the complex equations and research decisions that power the engine into plain English. 

## 1. Mathematical Bible (How We Calculate Things)
The system doesn't just guess; it uses math to prove its points. Here is a high-level explanation of the core calculations:

- **Confidence Scores**: When the AI answers a question, it calculates how sure it is. If it finds 5 pieces of solid evidence, the score goes closer to 100%. If the evidence contradicts itself, the score drops.
- **Expertise Weighting**: Not all actions are equal. Writing 1,000 lines of code gives you a high expertise score. Fixing a 1-line typo gives you a tiny score. The math equations ensure these are weighted fairly over time.
- **Degradation (Forgetting)**: Math is used to simulate human memory. If you wrote a piece of code 5 years ago and haven't touched it since, your expertise score slowly drops (decays) to reflect that you probably forgot how it works.
- **Bus Factor Equation**: We calculate risk by asking: "If Developer A leaves, what percentage of the codebase is left with zero experts?" The higher the percentage, the higher the "Bus Factor Risk Score."

## 2. Research Bible (Why We Built It This Way)
We make hundreds of design decisions. This section explains *why* we chose certain paths and rejected others.

- **Design Decisions**: Every time we choose a new database or a new AI model, we write down *why*. (e.g., "We chose a Graph Database because traditional databases are too slow for asking 'who knows who'.")
- **Rejected Approaches**: We also document the failures. (e.g., "We tried asking the AI to read 10,000 files at once, but its memory crashed, so we built the 'Planner' to read them one by one instead.")
- **Future Research Opportunities**: Ideas we want to explore later, like "Can we predict exactly which files will have bugs next month?"

## 3. Extension Bible (How to Add to the System)
The engine is built to grow. This is the instruction manual for future developers on how to add new features without breaking the core rules.

- **Adding Capabilities**: If someone wants to add a "Find Security Flaws" tool, they must follow strict rules: the tool must return evidence, and it must have a confidence score.
- **Adding Providers**: If a new, incredibly smart AI comes out tomorrow, this guide explains how to plug it into our Provider Manager seamlessly.
- **The Golden Rule (Invariants)**: The most important rule for extending the system is: **Never change the past.** Events are immutable. If an extension tries to delete historical data, the system will reject it.
