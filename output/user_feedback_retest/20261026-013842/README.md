# Developer retesting of the prospective user's feedback (2026-10-26)

**Developer retesting, not the participant.** A synthetic re-enactment of the participant's situation through the real
app (test server port 8002, fresh gpt-6-luna calls via Portkey, traces saved). The participant has not retested.
Findings and changes: `docs/user_test_findings.md`.

- `before_fixes/`: the build before the changes. **25/34** checks (failures = reproduced problems).
- `after_fixes/`: same conversation after the changes. **34/34**.
  - `after_fixes/final_screens/`: build `index-BxolrJIy.js`, desktop and mobile. The final build (`index-B920pes1.js`) differs
    only in removing the repeated age-match sentence on the detail page. **23/23**, one
    real message per viewport. A small follow-up check (no AI) confirmed the detail page no longer repeats the
    age-match sentence (`detail_age_simple_*.png`; its script counted the rule text too, so it printed FAIL while
    the page was correct).
  - `after_fixes/earlier_ui_check/`: earlier UI suite, 42/42.
- Usage (API-reported) is listed per run in each `report_*.json` / `screens_report.json`.
