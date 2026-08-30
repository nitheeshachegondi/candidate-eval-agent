"""
LLM client wrapper.

Real mode: set GROQ_API_KEY (preferred, matches your usual stack) or
ANTHROPIC_API_KEY, then run with LLM_MODE=live.

Mock mode (default, LLM_MODE=mock): deterministic, rule-based stand-in
so the pipeline is runnable and testable with no API key and no cost.

IMPORTANT: mock-mode output is NOT evidence for your hackathon
submission. It exists only to prove the pipeline logic is wired
correctly end-to-end. Before you submit, run with LLM_MODE=live and
a real key, and use those numbers in your changelog / eval report.
"""

import os
import re
import json

try:
    from dotenv import load_dotenv
    load_dotenv()  # reads a .env file in the project root, if present
except ImportError:
    pass  # dotenv is optional — env vars can still be exported manually

MODE = os.environ.get("LLM_MODE", "mock")


def _call_live(system: str, user: str) -> str:
    provider = "groq" if os.environ.get("GROQ_API_KEY") else "anthropic"
    if provider == "groq":
        from groq import Groq
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        resp = client.chat.completions.create(
            model=os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0,
        )
        return resp.choices[0].message.content
    else:
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")


# ---- Mock heuristics (deterministic, no LLM) ----------------------------
# These intentionally model two DIFFERENT failure modes so the eval can
# show a real, explainable gap between baseline and agent:
#  - baseline mock: averages surface signals, no cross-source verification
#  - agent mock: runs an explicit contradiction check before deciding

_CONTRADICTION_MARKERS = [
    ("vague", "could not"), ("evasive",), ("vague",),
    ("could not explain",), ("could not self-correct",),
    ("contradicted",), ("doesn't match", "used flask"),
    ("named only", "the rest was attributed"),
]


def _score_surface(case: dict) -> float:
    """Rough 0-10 'looks good' score from assessment + CV polish only."""
    score = 5.0
    m = re.search(r"(\d+)/10", case["assessment_score"])
    if m:
        score = float(m.group(1))
    if any(w in case["cv_summary"].lower() for w in ["led", "owned", "expert", "improved"]):
        score += 1.0
    return min(score, 10.0)


def mock_baseline(case: dict) -> dict:
    score = _score_surface(case)
    decision = "advance" if score >= 6.5 else "reject"
    return {
        "decision": decision,
        "confidence": "high" if score >= 8 or score <= 3 else "medium",
        "reasoning": f"Surface score {score}/10 from CV polish + assessment; no cross-source check run.",
    }


def _has_contradiction(case: dict) -> bool:
    text = (case["interview_notes"] + " " + case["cv_summary"] + " " + case["assessment_score"]).lower()
    hits = 0
    for markers in _CONTRADICTION_MARKERS:
        if all(m in text for m in markers):
            hits += 1
    return hits > 0


def mock_agent(case: dict) -> dict:
    score = _score_surface(case)
    contradiction = _has_contradiction(case)
    if contradiction:
        decision = "reject_pending_verification"
        confidence = "medium"
        reasoning = "Cross-source check found a claim in the CV/assessment not substantiated in the interview."
    else:
        decision = "advance" if score >= 6.5 else "reject"
        confidence = "high"
        reasoning = f"No contradiction found across sources; surface score {score}/10 used directly."
    return {"decision": decision, "confidence": confidence, "reasoning": reasoning}


def get_decision(kind: str, case: dict, system: str = "", user: str = "") -> dict:
    if MODE == "live":
        raw = _call_live(system, user)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"decision": "parse_error", "confidence": "low", "reasoning": raw[:300]}
    return mock_baseline(case) if kind == "baseline" else mock_agent(case)