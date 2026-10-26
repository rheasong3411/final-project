# Tokenomics (computed tokenomics.py; rates in USD per 1M tokens)

Rates: input $0.1, cached $0.01, cache write $0.125, output $0.5. Source: Course Lecture 11 (Tokenomics) slides and vibe page, https://zlisto.github.io/mgt_409_fa26/lectures/slides/lec11-slides.html, which cite https://developers.openai.com/api/docs/pricing; both accessed 2026-10-25. gpt-6-luna, Standard tier, short context (<=272K): input $0.10, cached input $0.01, 30-minute cache write $0.125, output $0.50 per 1M tokens (USD). No date is printed on either page.

| Group | n | Mean requests | Mean input | Mean cached | Mean uncached | Mean output | Mean $/run |
|---|---|---|---|---|---|---|---|
| cost_eval:baseline | 6 | 4.7 | 30,484 | 22,993 | 588 | 1,490 | $0.00190 |
| cost_eval:compact | 6 | 4.3 | 23,552 | 19,014 | 546 | 1,068 | $0.00128 |
| earlier_real_runs_sessions3to6 | 16 | 4.4 | 26,989 | 19,267 | 559 | 1,496 | $0.00189 |

Typical run (compact): $0.00128. Per user per month at 4 runs: $0.0051. 100 users: $0.51/month. 10,000 users: $51.12/month (model cost only).
Optimization: $0.00190 -> $0.00128 per run (33% lower).
