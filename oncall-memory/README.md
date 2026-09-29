# On-Call Memory

An incident-response agent that remembers past incidents **and whether each fix worked or failed**, using [Hindsight](https://github.com/vectorize-io/hindsight) agent memory.

## How Hindsight is used
- `retain`: every resolved incident is stored with symptom, root cause, fix, and OUTCOME (`memory.py::retain_incident`). The UI also retains new outcomes live.
- `recall`: before answering any alert, the agent recalls relevant past incidents (`memory.py::recall`) and the recalled memories are shown in the "Memory used" panel.
- Behavior change: with memory OFF the agent gives generic advice ("restart the service"). With memory ON it says restart failed twice before (INC-101, INC-103) and recommends rollback/config revert.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # fill in your keys
python test_connection.py   # confirms Groq + Hindsight both work, BEFORE anything else
python seed.py               # loads 10 synthetic incidents
streamlit run app.py
```

If `test_connection.py` reports a failure, fix that first — it tells you exactly
which service (Groq or Hindsight) and why.

## Demo script
1. Toggle memory OFF, click "Payments pool exhaustion", Diagnose: generic answer.
2. Toggle memory ON, Diagnose again: cites INC-101..104, skips restart, recommends rollback.
3. Save a new outcome, re-run: the agent learns.
