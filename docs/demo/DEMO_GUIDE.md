# Demo Guide: The P-101 Incident

This guide walks you through the canonical Hackathon demonstration for PIA Industrial.

## 1. Prerequisites

Ensure you have completed the [Getting Started](../GETTING_STARTED.md) guide and your `.env` is configured with `LLM_PROVIDER=mock` (or your preferred live provider).

## 2. Load the Demo Dataset

The demo utilizes synthetic shift logs and a dummy maintenance manual located in `data/demo/p101/`.

To load the data into the SQLite store and build the Knowledge Graph:
```bash
cd backend
python -m scripts.demo.demo_seeder
```

## 3. Start the Platform

**Terminal 1 (Backend):**
```bash
cd backend
uvicorn app.api.server:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

## 4. The Demo Flow

### Step A: The Copilot
In the Copilot chat window, ask:
> "What is the root cause of the P-101 vibration issue?"

**Expected Output:** The Copilot will deterministically query the `IndustrialCausalRCA` engine, identifying "Mechanical Wear" on the main bearing, citing the specific shift log from 09:30 on June 15th.

### Step B: Counterfactual Analysis
Ask the Copilot:
> "If we had replaced the bearing during the precursor event, would the failure have occurred?"

**Expected Output:** The system simulates the addition of a `MAINTENANCE_ACTION` edge in the graph, breaking the causal chain to the failure node, and confirms the failure was preventable.

### Step C: Compliance Risk
Ask the Copilot:
> "What is the compliance risk if we delay the V-204 inspection by another 30 days?"

**Expected Output:** The Compliance Engine calculates the temporal delta against the mandatory inspection protocol and returns an exact risk score.

## Fallback Demo Mode (Offline)
If you do not have internet access or an LLM API key during the hackathon, ensure `LLM_PROVIDER=mock`. The Copilot will use a pre-programmed semantic parser to route your exact questions directly to the deterministic engines and return structured JSON responses instead of natural language.
