"""
Runs baseline and agent on the same cases, scores both against the
human-reviewer ground truth, and writes:
  - docs/eval_report.md   (the comparison table for the submission)
  - evidence/agent_trajectory_<id>.json  (per-case agent trajectory)
  - memos/memo_<id>.md    (recruiter-facing memo per case, agent only)
"""

import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(__file__))
from baseline import run_baseline
from agent import run_agent
from memo import build_memo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_cases():
    with open(os.path.join(ROOT, "data", "candidates.json"), encoding="utf-8") as f:
        return json.load(f)


def normalize(decision: str) -> str:
    # Treat reject_pending_verification as "not a clean advance" for the
    # coarse accuracy metric, but track it separately for the more
    # important contradiction-catch metric below.
    return decision


def score(cases, job, runner, kind):
    rows = []
    correct = 0
    hard_cases = [c for c in cases if "conflicting_signals" in c["label"]]
    hard_caught = 0

    for case in cases:
        if kind == "agent":
            out = runner(job, case)
            decision = out["result"]
            traj = out["trajectory"]
            with open(os.path.join(ROOT, "evidence", f"agent_trajectory_{case['id']}.json"), "w", encoding="utf-8") as f:
                json.dump(traj, f, indent=2)
            os.makedirs(os.path.join(ROOT, "memos"), exist_ok=True)
            with open(os.path.join(ROOT, "memos", f"memo_{case['id']}.md"), "w", encoding="utf-8") as f:
                f.write(build_memo(job, case, decision))
        else:
            decision = runner(job, case)

        gt = case["ground_truth"]["decision"]
        match = normalize(decision["decision"]) == normalize(gt)
        correct += int(match)

        if case in hard_cases and decision["decision"] == "reject_pending_verification":
            hard_caught += 1

        rows.append({
            "id": case["id"], "label": case["label"],
            "ground_truth": gt, "predicted": decision["decision"],
            "match": match, "reasoning": decision.get("reasoning", ""),
        })

    accuracy = correct / len(cases)
    contradiction_recall = hard_caught / len(hard_cases) if hard_cases else 0.0
    return {"accuracy": accuracy, "contradiction_recall": contradiction_recall, "rows": rows}


def main():
    data = load_cases()
    job, cases = data["job"], data["cases"]

    baseline_result = score(cases, job, run_baseline, "baseline")
    agent_result = score(cases, job, run_agent, "agent")

    report_lines = [
        "# Evaluation Report",
        "",
        f"Mode: `{os.environ.get('LLM_MODE', 'mock')}` "
        f"({'REAL model output — submission-ready' if os.environ.get('LLM_MODE') == 'live' else 'MOCK heuristic — pipeline validation only, re-run with LLM_MODE=live before submitting'})",
        "",
        "## Primary metric: agreement with human-reviewer ground truth",
        "",
        "| System | Accuracy (12 cases) | Contradiction catch rate (4 hard cases) |",
        "|---|---|---|",
        f"| Baseline (single prompt) | {baseline_result['accuracy']:.0%} | {baseline_result['contradiction_recall']:.0%} |",
        f"| Agent (extract → verify → recommend) | {agent_result['accuracy']:.0%} | {agent_result['contradiction_recall']:.0%} |",
        "",
        "## Case-by-case detail",
        "",
        "| Case | Label | Ground truth | Baseline | Agent |",
        "|---|---|---|---|---|",
    ]
    b_by_id = {r["id"]: r for r in baseline_result["rows"]}
    a_by_id = {r["id"]: r for r in agent_result["rows"]}
    for cid in b_by_id:
        b, a = b_by_id[cid], a_by_id[cid]
        report_lines.append(
            f"| {cid} | {b['label']} | {b['ground_truth']} | "
            f"{'✅' if b['match'] else '❌'} {b['predicted']} | "
            f"{'✅' if a['match'] else '❌'} {a['predicted']} |"
        )

    report_lines += [
        "",
        "## The hard case (C03)",
        "",
        "CV and take-home both look excellent in isolation. Interview cannot "
        "substantiate the CV's ownership claims, and the take-home coding "
        "style doesn't match the candidate's live-coding behavior. A system "
        "that scores sources independently and averages them will advance "
        "this candidate. A system that cross-checks sources against each "
        "other should flag it for human review instead.",
    ]

    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    with open(os.path.join(ROOT, "docs", "eval_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("\n".join(report_lines))


if __name__ == "__main__":
    main()