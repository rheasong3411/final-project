# Conflicting-age fix — verification (2026-10-26)

**Owner testing** with synthetic messages; it does not replace the prospective-user test. Real model calls:
gpt-6-luna via Portkey (returned `gpt-6-luna-global`), fresh calls, test server on port 8002; traces in `traces/`.
Checks inspect the **returned cards** (rendered DOM: section, Minimum age line, fit badge) and the structured response,
not only the reply text.

## Rule under test
Animal Haven's ten roles publish conflicting minimum ages (18 and 21). Age 15 is below both, so the role is not
offered and the card says "Both published age requirements are above your age; confirm the current rule with the
organization", with the conflict note and both quotes kept. Age 19 (between) and 24 (above both) stay "Needs
confirmation". A parent attending never overrides an age rule.

## Results
- **First run** (`age_conflict_report.json`, `console.txt`, `screenshots/`): **55/56**.
  - **Age-15 conversation, desktop and mobile:** turn 1 explained the 21+ and 25+ dog-walking roles as "doesn't fit"
    and offered no role. In turn 2 ("Yes, please show me other ways to help.") the returned cards were three Branford
    Compassion Club support activities under "Other ways to help", each with "No minimum age published | You: 15 |
    Needs confirmation" and "Possible fit — confirm requirements". No offered card had a failed age rule. No card had
    a published age rule that a 15-year-old meets (no green age), so nothing was presented as a supported option.
  - **The repeated approval/Saturday-shift request:** refused. `ah_cat_socializing` now appears only under "Roles that
    don't fit right now", with the conflicting ages and "Sources disagree".
  - **Detail page, ages 15, 19 and 24:** as expected, on desktop and mobile.
  - **The failure:** on desktop turn 1 the model offered only a wider area (Norwalk), and the server's "other ways to
    help" offer was wrongly skipped. Fixed: it is now skipped only when the model already offered other kinds of help.
- **Re-run after that fix** (`rerun_after_followup_fix/`, desktop, both turns): **18/18**. Turn 1 offered other ways to
  help; turn 2 returned three BCC support activities, all with unpublished age rules shown as needing confirmation.
- **Earlier UI suite** on port 8001 (`earlier_suites/ui_check/`): 42/42.

## API-reported usage
- First run (5 turns): 20 requests; 188,504 input tokens (161,779 cached reads, 24,205 cache writes, 2,520 uncached);
  5,031 output tokens.
- Re-run (2 turns): 7 requests; 59,133 input tokens (50,145 cached, 8,106 cache writes, 882 uncached); 2,336 output tokens.
