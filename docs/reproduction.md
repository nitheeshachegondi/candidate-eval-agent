# Reproduction Guide

## Requirements
- Python 3.10+
- No external dependencies for mock mode.
- For live mode: `pip install -r requirements.txt` and one API key.

## Where to put your Groq credentials

1. Copy `.env.example` to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your real key:
   ```
   GROQ_API_KEY=gsk_your_real_key_here
   LLM_MODE=live
   ```
3. That's it — `.env` is already in `.gitignore`, so it never gets
   committed or included in your submission zip. `src/llm_client.py`
   loads it automatically via `python-dotenv`.

If you'd rather not use a `.env` file, exporting the same two
variables in your shell works identically:
```bash
export GROQ_API_KEY=gsk_your_real_key_here
export LLM_MODE=live
```

## Clean-environment steps

```bash
git clone <this-repo>
cd candidate-eval-agent
pip install -r requirements.txt

# 1. Mock run — validates the pipeline, no API key needed, ~1 second, $0
python3 src/eval_harness.py
cat docs/eval_report.md

# 2. Live run — submission-ready numbers (after setting up .env above)
python3 src/eval_harness.py
cat docs/eval_report.md
```

## What to expect
- Mock run: instant, deterministic, same output every time.
- Live run: ~12 cases × (1 baseline call + 1 agent call) = 24 API
  calls. At typical Groq Llama-3.3-70b pricing this is well under
  $0.10 and finishes in under a minute. Costs/timing will differ if
  you switch models — check current pricing for whichever model you use.

## Data
`data/candidates.json` — all 12 cases are synthetic, hand-authored
for this project. No real candidate data is used anywhere in this repo.

## Output locations
- `docs/eval_report.md` — comparison table (regenerated each run)
- `evidence/agent_trajectory_<case_id>.json` — one file per case
  showing the agent's extraction → verification → recommendation steps
