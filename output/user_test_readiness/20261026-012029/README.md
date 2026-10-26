# Prospective-user test readiness check (2026-10-26)

**Not a user test.** This is a pre-session walkthrough by the project owner, with synthetic input, of the four
tasks in `docs/user_test_guide.md`. It ran on the server a participant would use (port 8001, no trace saving), as
a first-time visitor at 1440 × 900 and 390 × 844.

- **Walkthrough** (`readiness_report.json`): **28/28** checks.
  - **Pages and tasks:** Home; T1 Explore → detail page with the organization's links, a next step and Check my fit;
    T2 Compare with two roles; T3 Find my fit with the first example prompt (one real gpt-6-luna reply, cards, Your
    answers filled, Confirm these details); T4 the organization's page links on the cards.
  - **Session and errors:** Clear my session gives a fresh start. About works, and an unknown address shows a
    friendly page. No horizontal overflow, console errors or failed app requests.
  - **API-reported usage of the one real reply:** 4 requests; 31,801 input tokens
    (26,936 cached reads, 4,361 cache writes,
    504 uncached); 1,135 output tokens. Not traced; the server only
    logged a metrics line.
- **Fixed after the walkthrough:** "Your answers" showed hours as two rows ("Available hours 3", "Hours per week").
  They are now one row, "Hours you can give: 3 per week", edited in the form and removed together. Checked:
  `screenshots/your_answers_hours_row_desktop.png`. The earlier screenshots in this folder show the two-row version.
- **Known, left as is:** on a phone, after T2 the Compare selection bar can cover part of the Find my fit start
  screen until the person scrolls (`screenshots/find_my_fit_start_mobile.png`). The guide suggests a laptop.
- **After the fix:** earlier UI suite (`earlier_ui_check/`) 42/42; backend 231 tests. Build `index-_pNTeHKR.js`.
