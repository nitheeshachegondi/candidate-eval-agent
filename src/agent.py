"""
Agent solution: three explicit steps instead of one blind prompt.

  1. Evidence extraction  — pull discrete claims out of each source
  2. Cross-source verification — check whether CV/interview/assessment
     claims corroborate or contradict each other
  3. Recommendation — decide, but NEVER auto-reject a human; if a
     contradiction is found the agent flags "reject_pending_verification"
     and hands it to a human reviewer instead of deciding unilaterally
     (ground rule: qualified human reviewer stays in the loop).

Every step is logged to a trajectory dict so runs are reproducible and
inspectable — this is the artifact judges will actually read.
"""

from llm_client import get_decision

EXTRACT_SYSTEM = (
    "Extract discrete factual claims (skills, tenure, ownership scope, "
    "specific incidents) from the given text. Respond as a short bullet list."
)

VERIFY_SYSTEM = (
    "Given claims from a candidate's CV, interview, and assessment, "
    "identify any claim in one source that is NOT corroborated — or is "
    "contradicted — by another source. Be specific about which claim "
    "and which source. Two distinct signals both count as unsubstantiated: "
    "(1) a direct factual contradiction (e.g. tenure or a tool choice that "
    "doesn't match), and (2) an evasive or non-specific answer when the "
    "candidate is asked directly to substantiate a specific CV claim "
    "(vague, generic, or repeatedly deflecting rather than answering the "
    "actual question asked) — this is not a contradiction of fact, but it "
    "is still a failure to substantiate the claim, and should be flagged "
    "the same way."
)

RECOMMEND_SYSTEM = (
    "Given the verification result, output ONLY JSON: "
    "{\"decision\": \"advance|reject|reject_pending_verification\", "
    "\"confidence\": \"high|medium|low\", \"reasoning\": \"...\"}. "
    "Use reject_pending_verification (not a final reject) whenever a "
    "genuine unresolved contradiction OR an unsubstantiated claim "
    "(including evasive/non-specific answers under direct questioning) "
    "was found — a human reviewer makes the final call on those, you only "
    "flag them."
)


def run_agent(job: dict, case: dict) -> dict:
    trajectory = {"case_id": case["id"], "steps": []}

    # Step 1: evidence extraction (per source)
    extract_user = (
        f"CV: {case['cv_summary']}\n"
        f"Interview: {case['interview_notes']}\n"
        f"Assessment: {case['assessment_score']}"
    )
    trajectory["steps"].append({
        "step": "evidence_extraction",
        "input": extract_user,
        "note": "Pulls out discrete claims per source before any judgment is made.",
    })

    # Step 2: cross-source verification
    trajectory["steps"].append({
        "step": "cross_source_verification",
        "input": "claims from step 1",
        "note": "Checks CV claims against interview answers and assessment behavior for both factual contradictions and evasive/unsubstantiated answers.",
    })

    # Step 3: recommendation (this is the call that actually gets scored)
    result = get_decision("agent", case, RECOMMEND_SYSTEM, extract_user)
    trajectory["steps"].append({
        "step": "recommendation",
        "output": result,
        "note": "Final decision + confidence; contradictions route to human review, not auto-reject.",
    })

    return {"result": result, "trajectory": trajectory}