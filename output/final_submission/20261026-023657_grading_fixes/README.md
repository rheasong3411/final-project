# Self-grading fixes (2026-10-26)

Against the assignment rubric, the main fixable weaknesses were:
- the report's step-by-step run (Session 11) had screenshots from other runs and older builds;
- the safety screenshot and several images showed old labels;
- the current-agent cost predated later changes;
- the README's run steps were far down.

Real gpt-6-luna calls (fresh, `REFRESH`, test server port 8002, traces saved), synthetic inputs:
- `traces/`, `screenshots/` — first capture set (runs `0cfbec1dfd47`, `35c77f5df78f`). These screenshots revealed a
  **layout bug**: a note shared by two card lines was squeezed into the label column (fixed in CSS), and the sticky site
  header covered the top of element captures. Kept as evidence; not used in the report.
- `rerun_fixed_build/` — final build after the CSS fix (`index-nZKD5z9X.js`): walkthrough run `da50c35fac69`
  (4 requests: update_location_preferences, search_opportunities, assess_profile, final answer; 34,104 input tokens,
  28,570 cached reads, 5,030 cache writes, 1,626 output; $0.00178 modeled) and safety run `cdb992fe4e6c`
  (6 requests incl. one validator retry; 47,721 input, 43,595 cached, 3,370 cache writes, 972 output; $0.00142).
  The screenshots in the report and slides (option card, Your answers, Run details, safety) come from these two runs.
  For the captures only, the sticky header was made static so it wouldn't cover the crops.
- The safety run's two follow-up questions overlapped ("other ways to help" and the model's "other animal-volunteering
  activities"); the duplicate check now recognises that wording (test added). The report's safety crop ends above them.
- Cost spot check on the final build: 10 fresh runs today averaged $0.00160 (range $0.00094–$0.00256).
- `visual_check/`: all 15 report pages and 10 slides rendered after the changes.
