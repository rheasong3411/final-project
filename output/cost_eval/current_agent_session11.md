# Current agent cost (Session 11, 2026-10-25) — measured separately from the Session 6 experiment

**What this is:** fresh real runs (Portkey force-refresh; gateway status `REFRESH`) of the agent as it is now:
6 tools (adds `update_location_preferences`), location memory, structured replies. Synthetic inputs.
**What it is not:** the Session 6 baseline-vs-compact experiment (`comparison.md`, `tokenomics.md`), which
measured the 5-tool agent of that time. Those figures are historical and are not mixed with these.

Rates (USD per 1M tokens): input $0.1, cached $0.01, cache write $0.125, output $0.5. Course Lecture 11 (Tokenomics) slides and vibe page, https://zlisto.github.io/mgt_409_fa26/lectures/slides/lec11-slides.html, which cite https://developers.openai.com/api/docs/pricing; both accessed 2026-10-25. gpt-6-luna, Standard tier, short context (<=272K): input $0.10, cached input $0.01, 30-minute cache write $0.125, output $0.50 per 1M tokens (USD). No date is printed on either page.

| Group | n | Mean requests | Mean input | Mean cached | Mean output | Mean $/run | Median $/run |
|---|---|---|---|---|---|---|---|
| standard_cases | 5 | 5.4 | 44,084 | 37,640 | 1,657 | $0.00199 | $0.00136 |
| website_location_conversation | 12 | 4.7 | 33,388 | 27,900 | 1,665 | $0.00178 | $0.00173 |

All 17 priced runs: mean $0.00185, median $0.00164 (range $0.00104–$0.00350) per run.
Same scaling assumption as Session 6 (4 runs per active user per month): $0.0074 per user per month; $0.74 for 100 users; $73.80 for 10,000 users (model cost only, modeled, not a bill).

Excluded (no tokens were generated): `03_prompt_injection__8d3d0cc4108b` (content_filtered)

Small sample: 18 runs (17 priced), chosen to cover the standard test cases and the location conversation; not a measurement of real users' traffic.
