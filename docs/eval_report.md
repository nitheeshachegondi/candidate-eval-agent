# Evaluation Report

Mode: `live` (REAL model output — submission-ready)

## Primary metric: agreement with human-reviewer ground truth

| System | Accuracy (12 cases) | Contradiction catch rate (4 hard cases) |
|---|---|---|
| Baseline (single prompt) | 67% | 0% |
| Agent (extract → verify → recommend) | 92% | 100% |

## Case-by-case detail

| Case | Label | Ground truth | Baseline | Agent |
|---|---|---|---|---|
| C01 | clean_strong | advance | ✅ advance | ✅ advance |
| C02 | clean_weak | reject | ✅ reject | ✅ reject |
| C03 | conflicting_signals_HARD | reject_pending_verification | ❌ reject | ✅ reject_pending_verification |
| C04 | clean_strong | advance | ✅ advance | ✅ advance |
| C05 | gap_explained | advance | ✅ advance | ✅ advance |
| C06 | gap_unexplained | reject_pending_verification | ❌ reject | ✅ reject_pending_verification |
| C07 | clean_weak | reject | ✅ reject | ✅ reject |
| C08 | nice_to_have_boost | advance | ✅ advance | ✅ advance |
| C09 | conflicting_signals_moderate | reject_pending_verification | ❌ reject | ✅ reject_pending_verification |
| C10 | clean_strong | advance | ✅ advance | ✅ advance |
| C11 | clean_weak_confident | reject | ✅ reject | ❌ reject_pending_verification |
| C12 | conflicting_signals_moderate | reject_pending_verification | ❌ reject | ✅ reject_pending_verification |

## The hard case (C03)

CV and take-home both look excellent in isolation. Interview cannot substantiate the CV's ownership claims, and the take-home coding style doesn't match the candidate's live-coding behavior. A system that scores sources independently and averages them will advance this candidate. A system that cross-checks sources against each other should flag it for human review instead.