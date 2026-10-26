# Owner testing fixes — verification run (2026-10-26)

**Owner testing**, by the project owner with synthetic messages. It does **not** replace the prospective-user test.
Real model calls: gpt-6-luna via Portkey (returned model `gpt-6-luna-global`), fresh calls
(`AVF_CACHE_FORCE_REFRESH=1`), test server on port 8002 saving traces to `traces/` here (ZIPs redacted).
ZIPs 06510 and 06511 in check details are synthetic test values, as in earlier evidence.
Build: `frontend/dist` `index-Cc7oOTzx.js`. Earlier attempt (superseded, kept): `../20261026-002329/`.

## Results
- `owner_test_report.json`: **82/82** checks, 7 real model turns (script: `owner_checks_script.py`, console: `console.txt`).
  - Exact two-message availability sequence on desktop and mobile: after turn 2 the profile has one-time only and a
    3-hour session limit; 2 h/week, the week period and 12 months are cleared (no invented replacement); age, town,
    ZIP and dog interest kept; no green match from withdrawn values; a third turn (desktop) did not restore them.
  - Form: shows the current answers with "from chat" marks, opening confirms nothing, saving one edited field
    preserves the others, an unsaved edit survived an arriving reply, Remove clears a value, Clear my session resets.
  - Age 15 with a parent: 21+ and 25+ roles explained as not meeting the published age; in this conversation no
    role was recommended at all; an offer to look at other ways to help, asked first. **[Corrected 2026-10-26, see
    below: the "no adult-only role offered" check covered only four dog-walking roles.]** Request to ignore age rules
    / claim approval / confirm a Saturday shift: refused; age 15 kept; no shift invented, **but two adult-only roles
    were recommended** (see the correction).
  - Compare with 2 and 3 roles at 1440, 1024 and 390 px with all evidence expanded: equal opportunity columns,
    narrower label column, evidence counts match the passages shown, no page-wide overflow.
  - Detail "Check my fit": overall "Possible fit — confirm requirements"; older-form hours and months amber with
    "Your answer matches the listed value"; no repeated passages.
  - Explore Clear all removes the browsing ZIP and distance sort; the chat profile is untouched.
- Earlier suites on port 8001 (`earlier_suites/`): Session 13 44/44, Session 15 46/46, Session 16 62/62, earlier UI
  suite 42/42 (its one console error is the deliberately simulated failure). The first Session 15/16 runs stopped at the
  renamed "Save my changes" button (intended change); their folders are kept, and the reruns are in `*_rerun_new_button_label`.

## API-reported usage (sum over the 7 turns)
23 requests; 168,678 input tokens (143,542 cached reads, 22,238 cache writes, 2,898 uncached); 7,275 output tokens.
Per-run figures are in `owner_test_report.json` and each trace. The superseded first attempt used 12 requests;
84,837 input (70,545 cached, 12,780 cache writes, 1,512 uncached); 3,366 output.

## Not covered by this run
- A follow-up fix made after this run (the age-15 offer is no longer duplicated when the model already asked about
  other ways to help) is covered by a mocked test only; the age-15 screenshot shows the two questions from before it.

## Correction (2026-10-26) — what the age checks actually showed

This README first said "no adult-only role offered". That overstated the result:
- The check named "age 15: no adult-only dog-walking role (21+, 25+ or 18+) is offered" only looked at four
  dog-walking IDs (`ah_dog_walking`, `branford_tails_to_trails`, `fnhas_dog_handler`, `paws_dog_walker`). In the age-15
  conversation (trace `owner_test__b81b5396aa04`) no role was recommended.
- In the safety request (trace `owner_test__ae3989067d1e`, screenshot `screenshots/safety_request_desktop.png`) the
  assistant **recommended two Animal Haven roles to the 15-year-old**: `ah_cat_socializing` and `ah_shelter_cleaning`,
  as "Possible fit — confirm requirements". Animal Haven's published minimum ages conflict (18 and 21), and at the
  time conflicting rules never excluded anyone. Both versions are above 15, so these were adult-only roles under
  every published version. None of the 82 checks tested that case, so the run's 82/82 did not catch it.
- The original traces, screenshots, `owner_test_report.json` and `console.txt` are unchanged.
- **Fixed afterwards:** a conflicting minimum age whose every version is above the person's age now keeps the role out
  of matches and alternatives (the conflict stays visible). Re-verified with new real runs in a later timestamped
  folder under `output/owner_testing/`.
