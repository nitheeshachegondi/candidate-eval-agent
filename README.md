# Candidate Evaluation Agent — micro1 Agentic Workflows Hackathon

## Who has this problem
Recruiters and hiring managers deciding whether to advance a candidate.
The evidence they need lives in three places that are rarely read
together with equal rigor: the CV, the interview notes, and any
take-home / assessment result.

## What bottleneck makes it worth solving
Reviewed in isolation, each source can look fine on its own while
contradicting the others. A polished CV plus a strong take-home score
often gets a candidate advanced even when the interview couldn't
substantiate the CV's claims — because nobody explicitly checked the
three sources against each other. That's a real hiring-quality problem,
not a hypothetical one: a false "advance" costs an interview loop and
possibly a bad hire; a false "reject" costs a good candidate.

## Does the agent solve it well
The agent runs three explicit steps — evidence extraction,
cross-source verification, and recommendation — instead of one blind
prompt. When it finds a genuine contradiction (a claim in one source
not substantiated by another), it does **not** auto-reject. It flags
`reject_pending_verification` and hands the case to a human reviewer,
per the hackathon's ground rule that a qualified human stays in the
loop for consequential decisions.

## Can another person reproduce the result
Yes — see [docs/reproduction.md](docs/reproduction.md). One command
reruns baseline, agent, and the comparison report from a clean clone.

---

## ⚠️ Important caveat before you read the numbers

This repo ships in **mock mode** by default (`LLM_MODE=mock`) — a
deterministic, rule-based stand-in for the LLM calls, so the pipeline
is fully runnable and inspectable with zero API cost and no key. The
67% vs 92% numbers in `docs/eval_report.md` right now are **pipeline
validation only** — they prove the extract → verify → recommend
architecture is wired correctly, not that a real model behaves this
way.

**Before submitting, set `LLM_MODE=live` and a real `GROQ_API_KEY`
(or `ANTHROPIC_API_KEY`) and rerun `src/eval_harness.py`.** Use those
real numbers in your changelog and video — not the mock ones. Say so
explicitly in your submission; judges connect claims to evidence, and
claiming mock output as real model behavior would misrepresent your
result.

## Repo layout
```
data/candidates.json     12 synthetic candidate cases (1 hard, 3 moderate conflicting-signal cases)
src/llm_client.py        real API call (Groq/Anthropic) + mock fallback, clearly labeled
src/baseline.py          single direct-prompt approach (no verification)
src/agent.py             3-step agent: extract → verify → recommend
src/eval_harness.py      runs both, scores against ground truth, writes docs/eval_report.md
evidence/                per-case agent trajectories (extraction → verification → recommendation)
docs/eval_report.md      generated comparison table
docs/changelog.md        improvement changelog (baseline → final)
docs/reproduction.md     exact commands for a clean-environment run
```

## Ground rules followed
- No real candidate data — all 12 cases in `data/candidates.json` are synthetic.
- Human reviewer stays in the loop: the agent never issues a final
  `reject` on a contradiction, only `reject_pending_verification`.
- No credentials in the repo; API keys are read from environment variables only.
