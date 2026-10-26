# Cost-saving change: baseline vs compact tool profile (real gpt-6-luna runs, 2026-10-25)

The plan and quality checks were written before the runs (`PLAN.md`, 18:11 EDT). The runs were made
with `python scripts/cost_eval.py run` (18:12–18:15 EDT), and the summary with
`python scripts/cost_eval.py summarize`. Costs come from `python scripts/tokenomics.py`.

## What changed

The traces showed `get_opportunity_details` was the largest tool result (about 5,900 characters per
call, about 1.6 calls per run). Most of it repeated what `assess_profile` returns anyway: requirement
applicability, explanations, source IDs and questions.

**Compact** (now the default; `AVF_TOOL_PROFILE=baseline` restores the old behavior):
- Drops the duplicated fields from the details result.
- Returns evidence quotes only when the model asks (`include_evidence=true`).
- Adds one line to the instructions saying so.

**Held constant:** the model (`gpt-6-luna`), matching rules, validator, limits, data and the 3 synthetic
inputs.

## Fresh-generation control

- Every request sent Portkey's documented `x-portkey-cache-force-refresh: true`.
- All 12 runs reported gateway cache status `REFRESH` (fresh calls). Replays (HIT): 0, so nothing was
  excluded.
- "Cached reads" below are the provider's **prompt cache**, which is part of fresh calls. That is
  different from a gateway replay.

## Results (all 12 runs counted; none rerun)

| Mean per run (n = 6 each) | Baseline | Compact | Change |
|---|---|---|---|
| Model requests | 4.7 | 4.3 | −9% |
| Input tokens (all) | 30,484 | 23,552 | −23% |
| of which cached reads | 22,993 | 19,014 | −17% |
| of which cache writes | 6,903 | 3,993 | −42% |
| of which uncached | 588 | 546 | −7% |
| Output tokens (incl. reasoning) | 1,490 | 1,069 | −28% |
| Latency | 16.5 s | 13.0 s | −21% |
| **Model cost per run** (course rates; see `tokenomics.md`) | **$0.00190** | **$0.00128** | **−33%** |
| `get_opportunity_details` calls (total) | 14 | 5 | |
| Quality checks passed (Q0–Q10, as applicable) | 54/54 | 54/54 | no regression |

**By case** (mean input tokens, baseline → compact):

| Case | Mean input tokens | Quality (runs passing all checks) |
|---|---|---|
| C1 ordinary match | 28,745 → 29,646 (**no saving**) | 2/2 → 2/2 |
| C2 conflicting requirements | 24,538 → 13,437 | 2/2 → 2/2 |
| C3 minor / unsuitable | 38,169 → 27,575 | 2/2 → 2/2 |

## Things not covered by the pre-written checks (reported for completeness)

- **Application checklists in responses:** 11 vs 11 in total. Runs with at least one checklist: 5/6
  baseline, 6/6 compact.
- **Recommendation counts:** the same, except one compact C1 run showed 2 recommendations instead of 3.
  One baseline C3 run had an extra alternative.
- **Answers** were about 6% shorter with compact (mean 992 → 933 characters).
- **No validator retries** in any of the 12 runs.

## Limits of this evidence

- **Small sample:** n = 6 per configuration, with run-to-run variation (baseline C1 ranged from 20,288
  to 37,202 input tokens). The direction is consistent for C2 and C3 but not for C1, so the averages are
  indicative, not statistically conclusive.
- **Narrow quality checks:** the checks test the structure and correctness of the deterministic output,
  status, sources, uncertainty and profile agreement. They do not grade the prose.
- **Token accounting history:** traces saved before Session 6 reported "uncached" as input − cached
  reads, which included cache writes. This comparison and `tokenomics.py` use input − cached − cache
  writes (course Lecture 11 rule). The backend now reports cache writes separately.

**Files:**
- `PLAN.md` (plan)
- `runs/` (12 sanitized traces, each with `quality_checks` and `metrics`)
- `results.json` (summary)
- `tokenomics.json` and `tokenomics.md` (costs)
- `scripts/cost_eval.py` and `scripts/tokenomics.py` (scripts)
