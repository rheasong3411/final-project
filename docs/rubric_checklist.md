# Rubric checklist — MGT409 Final Project

Source of truth: `Final Project/Rubrics.pdf` (summarized in [project_requirements.md](project_requirements.md)).
Keep this file current as work proceeds. **Do not mark a row `verified` without an evidence location.**

Status values: `pending` · `implemented but unverified` · `verified`

Last updated: 2026-10-26 (final submission prep: public repo https://github.com/rheasong3411/final-project; fresh clone verified; report 15 pages, slides 10; only the Canvas upload itself remains, plus optional items. Four verbatim participant quotes added later the same day; no session timing recorded.) Previous: 2026-10-26 (one informal prospective-user test documented; reported issues reproduced and fixed by developer retesting; report.html and slides.html REBUILT. Still pending: GitHub link and timed fresh clone; a verbatim quote/timing was not recorded.) Previous: 2026-10-25 (Session 16: distances to the verified site, else the organization's verified location; one results list sorted by "Distance: nearest first"; report.html and slides.html REBUILT. User test, GitHub link and fresh clone still pending.) Previous: 2026-10-25, ~21:41 EDT (Session 12: closed roles left out of discovery, five location categories, "About" distance wording; report.html and slides.html REBUILT. User test, GitHub link and fresh clone still pending). Verification: `docs/deliverables_verification.md`.

> ⚠️ **Deadline: Monday, October 26, 2026, 6:00 PM (Canvas)**, per the original rubric. This update was made on Sunday, October 25, 2026, the day before the deadline.

## A. Submission and format

| # | Requirement (from PDF) | Pts | Evidence needed | Where we plan to satisfy it | Status | Evidence location |
|---|---|---|---|---|---|---|
| A1 | Submit on Canvas: repo link, `report.html`, `slides.html` (video optional) | — | Canvas submission | Canvas | **pending (Rhea submits)**: files ready; nothing submitted by the assistant | Repo link https://github.com/rheasong3411/final-project; `report.html`, `slides.html` at the repo root |
| A2 | Due **Mon Oct 26, 2026, 6:00 PM** | — | Submitted on time | Canvas | pending (Rhea submits) | |
| A3 | Solo project | — | — | — | verified (one author; built with Claude Code as stated in the report) | |
| A4 | Both HTML files self-contained: open by double-click on any computer, all screenshots embedded | — | Open each file from another folder with no network images missing | `report.html`, `slides.html` | implemented but unverified (drafts) | report: 0 external requests, 8 embedded images; slides: 5 embedded images plus diagram, reveal.js from CDN (course instruction) so the library needs internet; `docs/deliverables_verification.md` |
| A5 | Repo is public, **or** private with `zlisto` added as collaborator | — | GitHub settings screenshot or public URL | GitHub repo (account `rheasong3411`) | **verified: public** (2026-10-26) | https://github.com/rheasong3411/final-project; no collaborator needed |
| A6 | Optional 2–3 min demo video of a real example, start to finish, narrated | (backup for "It works" and "Look + feel"; not for "staff can run it") | Video file | Canvas upload | **draft ready** (2:27, captioned, silent; real gpt-6-luna runs); narration and upload are Rhea's choice | `output/demo_video/20261026-025108/demo_video_draft.webm` |

## B. The idea (21 pts)

| # | Requirement | Pts | Evidence needed | Where | Status | Evidence location |
|---|---|---|---|---|---|---|
| B1 | Useful, distinctive working AI-agent app for real people, using real tools and real data | 21 | Working app, plus a report case for novelty and value | App and report §2–3 | pending | Dataset groundwork: `data/*.json`, `output/data_audit.md` |
| B2 | Avoid the overdone-idea cap (risk: "chat with a pile of documents") with a real twist | (caps the tier) | Report shows what the agents do beyond retrieval: eligibility reasoning against cited rules, conflict/missing-info flags, alternative ways to help | Agents and report §3 | pending | |

## C. The app (30 pts)

| # | Requirement | Pts | Evidence needed | Where | Status | Evidence location |
|---|---|---|---|---|---|---|
| C1 | It works end to end: agents use real tools and real data and give useful results without crashing | 15 | Real runs, screenshots, traces | Website + backend + agent | verified (locally, synthetic inputs) | Browser checks 51/51 with 2 real AI turns sent from the website (`output/ui_test_report.json`, `output/screenshots/`); integrated traces `output/agent_runs/ui_integrated__af1ced1eab65.json`, `ui_integrated__5795fd1e411f.json`; `pytest` 59 passed. **Session 10:** 93 backend tests; 12 fresh real gpt-6-luna runs sent from the website (`output/agent_runs/ui_location_s10__*`, all `REFRESH`); conversation checks 118/119 (1 wording-regex miss, manually reviewed as correct), Explore/detail checks 48/48, earlier non-AI checks 42/42 (`output/location_check/ui_location_test_report.json`) |
| C2 | Clean repo, **no secrets committed** | (in C1) | `git ls-files` contains no `.env`; secret scan | `.gitignore`, repo | **verified** (2026-10-26): new repo, single history; scan of all 718 committed files found no key value, no token patterns and no real `.env` (only `.env.example`); `local_data/`, `.venv`, `node_modules` and archives excluded | |
| C3 | GitHub repo with all necessary code | (in C1/C4) | Fresh-clone dry run | Repo | verified (fresh clone of commit c3f1e0a ran) | `output/final_submission/20261026-021552/` |
| C4 | Staff can run it: online, or a fresh clone runs via the README within **10 minutes** (otherwise 0) | 5 | Timed fresh-clone dry run with `.env` one folder up | README "Quick start for graders" | **verified** on one Mac: about 23 s of setup commands from `git clone` to a running app (pip cache off), key from `../.env`; also from `./.env` | `output/final_submission/20261026-021552/fresh_clone_setup.json` |
| C5 | App loads `.env` from the **repo root first, then the parent folder** | (in C4) | Test: move `.env` up one folder and the app still runs | `backend/config.py` `load_credentials` | **verified** in the fresh clone: `../.env` (credential source "parent-folder .env") and `./.env` ("project .env") | `output/final_submission/20261026-021552/fresh_clone_setup.json` |
| C6 | `README.md` explains what the app is and how to run it step by step | (in C4) | README | `README.md` | verified (followed from a fresh GitHub clone, 2026-10-26) | `output/final_submission/20261026-021552/` |
| C7 | `.env.example` lists every needed key with no real values | (in C4) | File contents | `.env.example` | verified | `.env.example` contains only `PORTKEY_API_KEY=` (empty), checked 2026-10-25 |
| C8 | Key names exactly `PORTKEY_API_KEY` or `OPENAI_API_KEY` | (in C4) | Code and `.env.example` | Config | verified | `backend/config.py` `KEY_NAME = "PORTKEY_API_KEY"` (only key read); `.env.example` |
| C9 | Data needed to run is included; a small test dataset if the full one is large | (in C4) | Data in repo | `data/` (about 64 roles, small, so no separate test set should be needed) | implemented but unverified | `data/organizations.json`, `data/opportunities.json`, `data/sources.json` |
| C10 | Look + feel: clean layout, clear buttons and screens, first-time-user friendly | 10 | Screenshots, user test | Website in `frontend/` (cream / forest green / peach theme chosen by Rhea) | implemented but unverified (no real user has tried it) | Screenshots at 1440 px and 390 px in `output/screenshots/`; no horizontal overflow on checked pages; keyboard focus visible (`desktop_keyboard_focus_visible.png`); manual visual inspection by the coding assistant only. Session 10 screenshots (desktop 1440 px and mobile 390 px, synthetic inputs): `output/screenshots/session10/` |

## D. Model, keys and budget

| # | Requirement | Pts | Evidence needed | Where | Status | Evidence location |
|---|---|---|---|---|---|---|
| D1 | Course `PORTKEY_API_KEY` → **`gpt-6-luna` only**, no other models | (affects C1) | Config uses only `gpt-6-luna`; Portkey responses show the returned `model` field | `backend/config.py` `MODEL_NAME`; run logs | verified | Every successful real run returned `gpt-6-luna-global` (`output/agent_runs/runs_index.jsonl`); probe call 2026-10-25 same; no fallback model in code |
| D2 | Never commit or expose the real key (repo, docs, screenshots, ZIPs) | (in C1) | Secret scan before submit | `.gitignore`, scrubbing in `backend/run_log.py`, output validator | implemented but unverified | Scan 2026-10-25: 0 of 129 project files contain the key value. Must be repeated before commit and for screenshots/ZIPs. |
| D3 | Overspending guard (budget cap, rate or turn limits) | (in Safety) | Test or screenshot | `backend/config.py` limits; `UsageLimits`; rate limiter in `backend/api.py` | verified (mocked tests) | `tests/test_limits.py`: a runaway tool-calling model (MOCKED) is stopped at the request limit with `usage_limit_exceeded` and no recommendations; the 7th call in a minute gets HTTP 429 (mocked run) |

## E. Report — `report.html` (41 pts)

Format: a single HTML file, **10–15 printed Letter pages** (regular font, screenshots included), embedded screenshots, no filler. Sections **in this order**:

| # | Section / requirement | Pts | Evidence needed (otherwise at most half) | Where | Status | Evidence location |
|---|---|---|---|---|---|---|
| E0 | 10–15 printed Letter pages; single self-contained HTML | — | Print preview page count | `report.html` | **verified**: 15 Letter pages, 7 embedded images, 0 external requests, sections in the required order (2026-10-26) | `output/final_submission/20261026-021552/visual_check/` |
| E1 | **1. Title + links:** project name, name, repo link (same as Canvas), app link if online, one-sentence summary | (in sections) | — | `report.html` | verified (repo link; app stated as not hosted, runs locally) | |
| E2 | **2. Motivation** (who has the problem, today's workaround and its cost, why care) and **3. What is new here** | 8 | **Named existing products compared** | `report.html` §2–3 | implemented but unverified (draft) | Idealist/VolunteerMatch and Samaritan Scout compared from their own pages (accessed 2026-10-25): `docs/product_comparison.md`; report §3 table |
| E3 | **4. The agents:** each agent, its tools, organization and diagram, model choice and why, one real run step by step | 10 | **One real run traced with screenshots of what each agent did** | `report.html` §4 | implemented but unverified (draft) | Diagram, tool table, matching rules, profile rules, run `ui_integrated__af1ced1eab65` step by step with screenshot |
| E4 | **5. Tokenomics:** input, cached-input and output tokens per typical run; cost per run, per user per month, at 100 and 10,000 users; cost cuts and whether they hurt performance | 8 | **Real API-reported token counts**; evidence on whether cuts hurt quality | `report.html` §5 | implemented but unverified (draft) | Modeled at course/OpenAI published rates (actual Azure/course billing not verified); 12-run experiment with limitations |
| E5 | **6. Safety:** relevant risks and built defenses | 8 | **Screenshot or test of a defense actually stopping an attack or malfunction** | `report.html` §6 | implemented but unverified (draft) | Real website run (application level), provider-filter case shown separately, mocked limit tests labelled |
| E6 | **7. Impact:** numbers (hours, reach, quality) with sources | 5 | **A real prospective user tried it** (quote, screenshot, or before/after time). Guesses alone get half. | `report.html` §7 | **done with quotes** (one informal prospective-user test: four verbatim quotes provided by Rhea, paraphrased feedback, issues reproduced and fixed); no screenshot of the session or timing recorded | `docs/user_test_findings.md`, `output/user_feedback_retest/` |
| E7 | **8. Limits + next steps** | (in E6) | Honest list | `report.html` §8 | implemented but unverified (draft) | |
| E8 | Report design: clean, readable, sharp, well-placed visuals | 2 | — | `report.html` | implemented but unverified (draft) | All pages visually inspected; fixes listed in `docs/deliverables_verification.md` |

## F. Slides — `slides.html` (8 pts)

| # | Requirement | Pts | Evidence needed | Where | Status | Evidence location |
|---|---|---|---|---|---|---|
| F1 | Single HTML file using **reveal.js**, **max 10 slides**, arrow keys and F for full screen | — | Open and step through | `slides.html` | implemented but unverified (draft) | 10 slides; arrow navigation tested; reveal.js 5.1.0 from CDN |
| F2 | Content: whole story, with **diagram, screenshots and key numbers** embedded | 6 | — | `slides.html` | verified (10 slides, diagram and 5 embedded screenshots, no overflow; visually inspected 2026-10-26) | `output/final_submission/20261026-021552/visual_check/` |
| F3 | Design: big readable text, consistent style (same colors as app) | 2 | — | `slides.html` | implemented but unverified (draft) | Cream / forest / peach; body 24–32 px; no overflow |

## G. Evidence we must collect while building

| # | Item | Status | Evidence location |
|---|---|---|---|
| G1 | Real-run agent traces | verified | `output/agent_runs/*.json` (synthetic inputs, 2026-10-25) |
| G2 | Screenshots of good runs, bad runs and safety catches | verified | `output/screenshots/` (real replies, follow-up, confirmation, error state, safety: `safety_app_level_defense_injection.png`, `safety_provider_filter_blatant_injection.png`) |
| G3 | API-reported input / cached-input / output usage per run | verified | `usage_api_reported` in each trace; table in `output/agent_runs/README.md` |
| G4 | Cost per run and per user per month; projections at 100 and 10,000 users | implemented (calculated at course-published rates); **actual billing not verified** | `output/cost_eval/tokenomics.md`: $0.00128 per typical run; $0.0051 per user per month (4 runs); $0.51 per month for 100 users; $51.12 per month for 10,000 users (model cost only) |
| G5 | Cost-saving measures plus before/after quality evidence | verified (n = 6 per configuration; indicative) | `output/cost_eval/comparison.md`: compact tool profile −33% model cost per run, quality 54/54 vs 54/54, all 12 runs fresh (REFRESH), none rerun |
| G6 | Demonstrated safety defense (test or screenshot) | verified | Website screenshot `output/screenshots/safety_app_level_defense_injection.png` (real run `ui_integrated__6adf5a88c619`); mocked tests in `tests/test_agent_mocked.py`, `tests/test_limits.py` |
| G7 | Real prospective user tries the app (quote, screenshot, timing) | done: one informal test (2026-10-26) with four verbatim quotes; no session screenshot or timing recorded | `docs/user_test_findings.md` |
| G8 | Honest comparison with named existing products (Idealist, Samaritan Scout, others) | verified (official pages, accessed 2026-10-25; "not found" ≠ absent) | `docs/product_comparison.md` |
| G9 | Fresh-clone dry run with `.env` one folder up, timed under 10 minutes | **verified** (2026-10-26): about 23 s of setup commands; app checks 25/25; a real gpt-6-luna Find my fit run (fresh, REFRESH) | `output/final_submission/20261026-021552/README.md` |

## H. Data-stage items (this step)

| # | Item | Status | Evidence location |
|---|---|---|---|
| H1 | Sourced dataset compiled (organizations, opportunities, sources) | implemented but unverified (structurally valid; quotes checked against the 2026-10-25 snapshots; **not confirmed by organizations**) | `data/`, `output/data_audit.md` |
| H2 | Structural validation passes (schema v2) | verified | `python scripts/validate_data.py` → 0 errors, 1 intentional warning (2026-10-25 16:23 EDT); `output/data_audit.md` §10 |
| H3 | Evidence passages found in source snapshots | verified (quote presence only, not current accuracy). Reproducible only where the local snapshots exist. | `python scripts/check_evidence_quotes.py` → 376 found / 13 labels / 0 not found; the earlier 297/44 result was reproduced on the pre-correction data; `output/data_audit.md` §7 |
| H4 | Validator self-tests | verified | `python scripts/test_validate_data.py` → 36 tests OK (2026-10-25 16:23 EDT); `output/data_audit.md` §10 |
| H5 | Correction pass: guardian inferences removed; requirement applicability, schedule separation, record and commitment types added | verified (structurally, by validator and tests) | `output/data_audit.md` §0, §2, §5 |
| H6 | Uncertain or conflicting requirements raise questions instead of decisions | implemented but unverified (rule documented and enforced in the data; matching code not built) | README "Planned matching behavior"; validator rules |
| H7 | Product scope decisions recorded (GNH default, separate wider-CT scope, town filter only, visible check dates, status separate from fit, "Confirm with organization", apply on org sites, no theme yet, repo root, `.env` untouched) | verified (documented) | README "Product scope decisions"; `output/data_audit.md` §11 |
| H8 | Backend tests | verified | `python -m pytest -q tests` → 61 passed (2026-10-25, Session 6). Agent and limit tests use a **mocked** model. |
| H9 | Real AI workflow (gpt-6-luna via Portkey) end to end | verified (synthetic inputs only; not user testing) | `output/agent_runs/` and one real `POST /api/assistant` call (run `8c18f82ac5aa`, metrics in local_data) |
| H10 | Session 4 corrections: one consistent profile per run, one-time session check, alternatives and sources validated against the records used, residence town vs. location restriction | verified (tests and one real run) | `tests/test_regressions.py` (14 tests); real run `output/agent_runs/01_normal_match__9f57e5508031.json` (12 automated checks pass) |
| H11 | Frontend type check and production build | verified | `npx tsc -b` exit 0; `npm run build` exit 0 (2026-10-25); bundle scanned: no key value, no "portkey" string |
| H12 | Browser checks of the running website (navigation and direct loads, filters, reset, empty state, compare and remove, details and source links, fit check with missing info, real AI conversation plus preference change, fact confirmation, error state, keyboard focus, 390/1440 layouts) | verified (automated; the backend-unavailable error was **simulated** by aborting the request) | `scripts/ui_check.py` → `output/ui_test_report.json` (51/51); only console error = the deliberately aborted request |
| H13 | Profile confirmation: unconfirmed chat facts never drive eligibility checks | verified (tests and real runs) | `tests/test_profile_confirmation.py` (7 tests); integrated traces show "for at least a year" kept as an unused suggestion |
| H14 | Real-user / prospective-user testing | done (one informal test) | Four verbatim quotes and paraphrased feedback in `docs/user_test_findings.md`; reproduced issues verified and fixed by developer retesting (`output/user_feedback_retest/`), not by the participant. |
| H15 | Pricing source for gpt-6-luna | course-published and OpenAI rates verified (2026-10-25); **actual billing (Azure via Portkey, course arrangement) not verified** | Lecture 11 slides and vibe page; https://developers.openai.com/api/docs/pricing; `output/cost_eval/tokenomics.md` |
| H16 | `frontend/dist/` included and matching source | verified | Byte-identical to a fresh `vite build` (14 files, SHA-256); not gitignored; `package-lock.json` kept |

## Conflicts and ambiguities to resolve (do not silently choose)

1. **Rubric path:** the prompt said `Rubrics/`, but the actual file is `Final Project/Rubrics.pdf`.
2. **Repo root vs. `.env` location (Q2):** if the Git repo root is `animal-volunteer/`, the parent is
   `Final Project/`, but the existing workspace `.env` is two levels up (`MGT409 AI/.env`). The app
   will not find it unless it is copied to `Final Project/` or `animal-volunteer/` (gitignored).
   *Update 2026-10-25:* the repo root is planned as `animal-volunteer/`. Per Rhea's instruction the
   real `.env` was **not** moved or copied; placement will be decided when the backend is connected.
3. **Hosted vs. local:** the PDF allows either. Local must run within 10 minutes from a fresh clone.
   Not decided yet.
4. **"API-reported input, cached-input, and output usage":** the PDF asks for real token counts
   (input, cached input, output) "shown in your logs or in screenshots." It does not literally say
   "API-reported"; using the Portkey/OpenAI response `usage` fields satisfies both readings.
5. **Overdone-idea risk:** a chatbot over a document set is on the overdone list. Our twist must be
   demonstrable (rule-by-rule fit explanations, conflict and missing-info flags, alternatives), not
   just claimed.
6. **Page count:** "10–15 pages when printed" on Letter paper. Check with print preview, not by
   estimating.
7. **Slide outline:** the PDF suggests 9 slides; the maximum is 10.
8. **Theme (resolved in Session 5):** Rhea explicitly chose cream / forest green / soft peach, which
   overrides the workspace's black-and-pink default for this project.
9. **Shipping the built website:** `frontend/dist/` is not gitignored. If it is committed, graders can run
   the website with Python only (no Node). Otherwise they need `npm install && npm run build` (adds setup
   time against the 10-minute rule). Decide before publishing.
10. **Port 8000 is busy on this machine** (another project's server). The documented default stays 8000;
   check that the grader's dry run isn't affected.

## Self-assessment against the rubric (2026-10-26, after the final fixes)

Estimated by the coding assistant, not by the course staff. Fixed today: a traced step-by-step run with screenshots from
the same run (Agent design), current-build safety screenshot, in-app token usage screenshot and a current-build cost spot
check (Tokenomics), a card layout bug, repeated follow-up wording, README quick start at the top. Remaining limits that
cannot be fixed by code: novelty is a judgment call (Idea, 21); Impact rests on one informal user test with quotes but
no task timing or before/after measurement (5); the app is local, not hosted.
- 2026-10-26 (later): added a measured "reading effort" comparison to Impact (13 pages across 5 organizations; 15 of 28 roles
  split across 2–4 pages; median 22 s per Find my fit reply over 10 fresh runs) and a captioned demo-video draft. A timed
  manual-vs-app comparison is prepared (`docs/timed_comparison_kit.md`) but not run.

