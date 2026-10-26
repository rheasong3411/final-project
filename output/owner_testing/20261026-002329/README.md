# Owner testing — first attempt (2026-10-26, superseded)

Kept as evidence; superseded by the later run folder (`../20261026-004520/`). ZIP 06510 is a synthetic test value. Synthetic messages; real gpt-6-luna calls via Portkey
(fresh, test server port 8002). This is owner testing, not a prospective-user test.

What this attempt found (console output: `first_attempt_console.txt`, traces in `traces/`):
- Withdrawn hours, hours period and months were cleared and stayed cleared; age, town, ZIP and interests kept.
- **App bug:** the 3-hour session limit was not recorded, because the model searched, found nothing and answered
  without calling `assess_profile`. Fixed by recording an explicit session limit from the newest message on the
  server ("3 hours total"), and by an instruction to record changed facts even when nothing matches.
- **App bug:** on a third turn the reply repeated the one-time gap sentence in a reworded form. Fixed: every variant
  is replaced by the exact sentence once.
- **Cosmetic:** the removal note listed two overlapping quotes and the label "Hours per"; fixed.
- **Test-script error:** a wrong key stopped the run during the age-15 case, so the safety, Compare and detail
  checks did not run here. The age-15 trace was saved.
