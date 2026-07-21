# Decision Package (The Automated Manager)

This package contains the logic for **Decision Making**. While the Cognitive engine is great at answering questions, and the Simulation engine is great at predicting the future, the Decision engine is designed to actually suggest real-world actions for the team to take right now.

It acts as an automated, mathematically rigorous project manager that never sleeps. Here is a detailed breakdown of how it makes its decisions.

---

## 1. `optimization.py` (The Schedule Balancer)
**Purpose**: To ensure the team is working at peak efficiency without anyone burning out.
**Detailed Workflow**:
1. **Gather Workloads**: It constantly queries the Knowledge Graph to see exactly how many open tickets, bugs, and code reviews are currently assigned to every single developer on the team.
2. **Calculate Capacity**: It doesn't just count tickets; it calculates the *weight* of the tickets. It knows that 1 massive architectural ticket is heavier than 10 simple typo fixes.
3. **Run Optimization Algorithms**: If Bob is assigned 80% of the team's total ticket weight, and Alice is assigned 5%, the system runs a mathematical optimization routine. It looks at Alice's skill tree (via the Expertise engine) to see which of Bob's tickets she is actually qualified to take.
4. **Output Recommendations**: It generates a concrete recommendation for the human manager: *"Reassign Ticket #402 and Ticket #405 from Bob to Alice. This will reduce Bob's workload to a safe level while ensuring the tickets are still handled by a qualified developer."*

---

## 2. `reviewer_recommendation.py` & `reviewer_recommendation_service.py` (The Matchmakers)
**Purpose**: To completely automate the process of finding the perfect person to review a complex code change.
**Detailed Workflow**:
1. **Analyze the Change**: When a developer submits a massive Pull Request containing 50 changed files, the script intercepts it. It breaks the Pull Request down and figures out exactly which parts of the system are being modified (e.g., "The Database" and "The User Interface").
2. **Query the Graph**: The service queries the Knowledge Graph: *"Find me the top 5 developers who have the highest expertise scores in these specific 50 files."*
3. **Apply Filters**: It then runs those 5 names through a series of strict filters. 
   - Is Developer A on vacation? (Drop them).
   - Is Developer B already swamped with 10 other reviews? (Drop them).
   - Did Developer C actually write this exact code originally? (Move them to the top of the list).
4. **Make the Match**: It outputs the absolute best 2 candidates to review the code, ensuring high code quality without overloading the same senior developers every time.

---

## 3. `policies/` (The Rule Enforcers)
**Purpose**: Holds the rigid, company-specific laws that the Automated Manager must obey before it makes any decision.
**Detailed Workflow**:
- An AI should never blindly optimize without boundaries. The `policies/` folder contains hard-coded scripts that act as boundary lines.
- **Example Policy 1 (Conflict of Interest)**: "A developer is never mathematically allowed to be recommended as a reviewer for their own code."
- **Example Policy 2 (Security)**: "If a file is tagged as `CRITICAL_SECURITY`, only developers with an expertise score of 90+ can be assigned to review it. Junior developers must be filtered out."
- **Execution**: Before `optimization.py` or `reviewer_recommendation.py` outputs their final answer, the result is run through every single script in the `policies/` folder. If a policy fails, the decision is thrown out and recalculated.
