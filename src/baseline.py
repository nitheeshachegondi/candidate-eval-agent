"""
Baseline: one direct prompt, basic instructions, no tools, no
cross-source verification. This represents "how a recruiter using
plain ChatGPT/Claude with no extra engineering would do this today."
"""

from llm_client import get_decision

SYSTEM = (
    "You are helping a recruiter decide whether to advance a candidate. "
    "Read the job requirements and the candidate evidence, then respond "
    "ONLY with JSON: {\"decision\": \"advance|reject\", \"confidence\": "
    "\"high|medium|low\", \"reasoning\": \"...\"}"
)


def run_baseline(job: dict, case: dict) -> dict:
    user = (
        f"Job must-haves: {job['must_haves']}\n"
        f"Job red flags: {job['red_flags']}\n\n"
        f"CV: {case['cv_summary']}\n"
        f"Interview notes: {case['interview_notes']}\n"
        f"Assessment: {case['assessment_score']}\n\n"
        "Decide: advance or reject."
    )
    return get_decision("baseline", case, SYSTEM, user)
