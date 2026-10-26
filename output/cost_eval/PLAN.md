# Cost-saving experiment: plan and quality checks (written before any comparison run)

Written: 2026-10-25T18:11:05-0400 (before running the comparison).

## Change being tested

- **baseline** (`AVF_TOOL_PROFILE=baseline`): tools and instructions exactly as in Sessions 3–5.
- **compact** (`AVF_TOOL_PROFILE=compact`):
  - `get_opportunity_details` no longer returns the fields `assess_profile` already returns
    (requirement applicability, unresolved questions, duplicated summary fields).
  - Evidence quotes are returned only when `include_evidence=true` is requested.
  - One instruction line tells the model that `assess_profile` already gives requirement wording,
    applicability, explanations and source IDs.
  - Offline, the details result is 50–68% smaller for the four records checked.
- **Held constant:** model `gpt-6-luna` via Portkey, deterministic matching, output validator, limits,
  and the dataset.

## Inputs (synthetic, identical for both configurations)

| Case | Message |
|---|---|
| C1 ordinary match | "I'm 26 and live in New Haven. I'd like to help with cats, about 3 hours a week, for at least 12 months, on weekday afternoons." |
| C2 conflicting requirements | "I'm 19 and I want to volunteer at The Animal Haven in North Haven, cleaning or socializing cats. I can commit about 6 months. Am I eligible?" |
| C3 minor / unsuitable | "I'm 15 and want to walk dogs at The Animal Haven. My dad can come with me on weekends. What can I do?" |

## Schedule

- **Runs:** 2 repetitions × 3 cases × 2 configurations = **12 runs**.
- **Order:** interleaved (for each repetition and case: baseline, then compact).
- **Every run is counted.** No run is repeated or dropped, including failures.
- **Gateway cache:** each request sends Portkey's documented `x-portkey-cache-force-refresh: true`, so
  identical inputs get a fresh model call (expected cache status `REFRESH`). Any run reporting
  `HIT` would be labelled a replay and excluded from token comparisons, with the exclusion reported.
- **Prompt caching is separate:** cached *input tokens* (`input_tokens_details.cached_tokens`) are the
  provider's prompt cache. They are part of fresh calls and are reported, never added on top of input
  tokens.

## Quality checks (pass/fail per run)

| ID | Check | Applies to |
|---|---|---|
| Q0 | Run succeeded (`ok`, no error) | all |
| Q1 | Profile agreement: every shown assessment's `profile_fingerprint` equals the final profile's, and `profile_used.age` equals the age in the message | all |
| Q2 | Requirement assessment correct: re-running the deterministic matcher on each shown record with `profile_used` gives identical overall and per-requirement statuses | all |
| Q3 | Application status correct: each shown record's status equals the dataset's; if a recommendation is explicitly closed, the answer says "closed" | all |
| Q4 | Sources: response sources include every source ID used by shown requirements, and there is at least one source | all |
| Q5 | Uncertainty: no requirement whose applicability is conflicting or needs confirmation is marked not_met | all |
| Q6 | C1: at least one recommendation that is not not_met and not explicitly closed | C1 |
| Q7 | C2: an Animal Haven record is shown, its minimum-age item is `conflicting` and not not_met, and the answer mentions the conflict or confirmation | C2 |
| Q8 | C3: Animal Haven dog walking is never presented as a fit (if shown, it is not_met and not in recommendations), and at least one other option or alternative is offered | C3 |
| Q9 | No approval, "eligible" or guaranteed-placement claims in the answer | all |
| Q10 | Returned model starts with `gpt-6-luna`; cache status is not `HIT` | all |

**Metrics per run (API-reported):** model requests, input tokens (including cached), cached input
tokens, uncached input = input − cached, output tokens (including reasoning), tool calls by name,
latency, cache status values and response IDs.

**Comparison:** per-configuration means and totals over all runs, the per-case difference, and quality
pass rates. With n = 6 runs per configuration, results are indicative, not statistically conclusive.
