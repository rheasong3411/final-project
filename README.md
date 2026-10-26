# Animal Volunteer Finder — Greater New Haven

- **Repository:** https://github.com/rheasong3411/final-project
- **App link:** not hosted online. It runs locally from a fresh clone of this repository (steps under
  [Setup and run](#setup-and-run-local)); the `localhost` addresses below only work on your own computer.

A local web app that helps people find **animal-volunteering opportunities in Greater New Haven,
Connecticut**. People can browse and filter opportunities, compare requirements, and ask an AI
assistant which roles fit their age, interests, location, available hours and commitment length.

The key feature is the explanation. For each opportunity the assistant says **why it fits or does not
fit**, citing the organization's published rules. It flags information that is **missing or
conflicting**, and when someone can't meet a requirement it suggests **another way to help**.

## Quick start (about 1 minute of commands; Python 3.10+, no Node needed)

```bash
git clone https://github.com/rheasong3411/final-project.git
cd final-project
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Put PORTKEY_API_KEY=... in final-project/.env OR in the folder above it (../.env); see .env.example
uvicorn backend.api:app --port 8000                     # if 8000 is busy: --port 8001
```

Open http://localhost:8000. Browsing, details, Compare and "Check my fit" work without a key; Find my fit (the
AI assistant, gpt-6-luna via Portkey) needs the key. Details: [Setup and run](#setup-and-run-local).

> **What this app does not do:** it helps people prepare to apply. It does **not** approve volunteers,
> confirm openings or guarantee placement or shifts. Every rule comes from public web pages on the date
> shown in `data/sources.json`, and the organization has final say.

## Status

- **Stage 1: setup and data preparation** — done 2026-10-25.
- **Stage 1b: correction pass (schema v2)** — done 2026-10-25.
- **Stage 2: backend and real AI workflow** — done 2026-10-25. It includes a FastAPI backend,
  deterministic matching in plain Python, and one PydanticAI agent on **`gpt-6-luna` through Portkey**.
  It was tested offline (51 pytest tests after the Session 4 corrections) and with real model runs on synthetic inputs (see
  `output/agent_runs/`).

- **Stage 3: frontend** — done 2026-10-25. A React + TypeScript + Vite website in `frontend/` (Home,
  Explore, opportunity details, Compare, Find my fit, About) is connected to the backend. It was checked
  in a real browser (`scripts/ui_check.py`: 51 of 51 checks) and with real assistant turns sent from the
  website.

- **Session 10: location memory, optional ZIP distances, Find my fit display** — done 2026-10-25.
  Earlier messages collapse into "Previous conversation" (memory is kept). Where someone lives, how
  they travel and where they will volunteer are separate remembered fields. An explicit limit such as
  "I need to stay in New Haven" is enforced. With an optional ZIP code, roles that an official page places
  at a verified site show "Approx. X miles from your ZIP area" (a straight-line estimate). Explore's
  commitment filter is now "Any commitment / One-time / Ongoing / Flexible / varies". Evidence:
  `output/location_check/`, `output/screenshots/session10/`, `output/agent_runs/ui_location_s10__*`.

- **Session 11: structured replies, answers summary, distance binding, geo validation, application recheck**
  — done 2026-10-25. Each Find my fit option shows labelled fact lines rendered from the structured results
  ("Minimum age: 21+ | You: 23 | Meets requirement", with any "older form" note beside the rule). The written
  reply is a short opening, and there are at most 2 follow-up questions. "Your answers" is a compact
  summary with one "Confirm these details" action. Distances never appear in prose; each option's estimate
  comes from its own result. Branford's general application is now marked closed: its own form says it is
  disabled. Tails to Trails gained its form's requirements (age 25, own transportation, 4 hours a month).
  The report and slides were rebuilt. Evidence: `output/location_check/ui_session11_test_report.json`,
  `output/cost_eval/current_agent_session11.md`, `output/screenshots/session11/`.

- **Session 12: closed roles out of discovery, five location categories, "About" wording** — done 2026-10-25.
  Records whose applications are explicitly closed are left out of Home, Explore and the assistant's searches and
  alternatives by the backend (`include_closed` opts in; detail pages still work; the assistant explains a closed role
  when asked about it and never recommends one). Explore's application-status filter was removed (old URLs are
  cleaned). Status labels: "Accepting applications", "Ask about availability", "Applications closed". Every record
  has one location category: verified volunteering site, organization location only, published town only,
  home-based, or unknown. Labels: "About 6 miles to volunteering site", "Organization is about 9 miles away",
  "About X miles to [town] town center", "Less than 1 mile to volunteering site". Only verified sites are ranked by
  "Closest estimated volunteering site". Evidence: `output/location_check/ui_session12_test_report.json`,
  `output/screenshots/session12/`.

- **Session 15: sorting, Clear all filters, one shared filter, hard constraints** — done 2026-10-25. Explore sorts by
  "Default order", "Organization name A–Z" or "Closest estimated volunteering site" (only with a supported ZIP; the
  option explains its prerequisite). There's no time-based sort: only 9 of the 58 non-closed records publish minimum
  hours, in mixed units. "Clear all filters" also clears the browsing ZIP, which is now separate from Find my fit's
  answers. Explore and the assistant use the same filter (`Dataset.search`), so a town filter means the role's own
  published town on both pages, and "I can only do a one-time project" is a hard constraint: unknown commitments
  appear only under "Other activities to ask about". Evidence: `output/location_check/ui_session15_test_report.json`.

- **Session 16: simpler location display, one list sorted by distance** — done 2026-10-25. A distance goes to the
  verified volunteering site; if the activity site is unknown, to the organization's verified physical location (for
  an organization with several sites and none named for the role, the nearest one, by name); otherwise none. Mailing
  addresses and P.O. boxes are never used. Cards show one line: "North Haven · About 6 miles away",
  "Organization: New Haven · About 1 mile away" with the small note "Activity location may differ", or
  "Nearest organization site: CHS Wilton · About 27 miles away"; without a ZIP, the place only. Home-based activities
  say "Help from your home" (a sourced pickup site, or the organization for reference, appears underneath; a
  reference distance is never ranked and never "0 miles"). The separate "Other leads" section is gone: Explore and
  Find my fit show one list with one count, and "Distance: nearest first" sorts it by the unrounded distance, with
  records that have no distance last. Address, maps links, other sites and evidence stay in the details. Evidence:
  `output/location_check/ui_session16_test_report.json`, `output/screenshots/session16/`.

**Prospective-user testing:** one informal test (2026-10-26), documented with the issues it raised, what our retest
reproduced and what was changed in `docs/user_test_findings.md`. It is not a broad usability study.

**Published:** https://github.com/rheasong3411/final-project (public). The app itself is not hosted online; it runs locally.
## Product scope decisions (recorded 2026-10-25)

1. **Greater New Haven is the default view.**
2. **Wider Connecticut options are kept**, but in a separate, clearly labeled scope that is never mixed
   into "nearby" results.
3. **Location is filtered by published town.** *(Updated in Session 10.)* Approximate straight-line
   distances are shown only when the person gives an optional ZIP code **and** an official page places
   the role at a site with a published street address (`data/volunteer_locations.json`). Everything
   else shows "Distance unavailable". Travel times, walkability and transit are still not offered.
   `organizations.json` coordinates stay `null`; site coordinates live in the separate locations file.
4. **Source-check dates and uncertainty are always visible**, for example "Checked 2026-10-25" and
   "Confirm with organization."
5. **Application status and requirement fit are shown separately.** A role can fit someone and still
   be closed, or be open and not fit.
6. **Uncertain roles are labeled "Confirm with organization," never "Open now."** Only
   `explicitly_accepting_applications` may say the organization is accepting applications, and even
   that comes with "placement not guaranteed."
7. **Applications are submitted on the organization's own website.** The app links out and never
   submits forms or collects applications.
8. **Visual theme (chosen by Rhea in Session 5):** warm cream `#FAF7F0`, forest green `#214D3C`, soft
   peach `#F3D2BD`, dark text `#24352D`, muted sage `#E4EBDF`, with Fraunces headings and Source Sans 3
   body text (both bundled). This explicitly overrides the workspace's earlier black-and-pink default.
9. **`animal-volunteer/` is planned as the Git repository root.** Checked 2026-10-25: there is no
   `.git` in `animal-volunteer/`, `Final Project/` or `MGT409 AI/`.
10. **The real `.env` has not been moved or copied.** See "Setup and run" below for the supported locations.

## Matching behavior (implemented in `backend/matching.py`)

The matcher works on `requirement_applicability`, not on raw values:

| Applicability of a requirement | What the app does |
|---|---|
| `published_applicable` | Compared with the person's answers. A clear miss is `not_met` ("doesn't match the published requirement"), with the source cited. The app never says "rejected" or "ineligible". |
| `needs_confirmation` | **Never accepts or rejects** on this rule. The result is always `needs_confirmation` (amber "Needs confirmation"), even when the person's answer matches every published version; that comparison is shown separately ("your answer matches the listed value", `listed_value_matched`). Green labels are reserved for applicable, supported rules (owner-testing fix, 2026-10-26). |
| `conflicting` | Same as `needs_confirmation`, and **both** statements are shown. One exception (2026-10-26): when **every** published minimum-age version is above the person's age (15 against Animal Haven's 18 and 21), the role is `not_met` and is not offered or suggested. The card says "Both published age requirements are above your age; confirm the current rule with the organization." It keeps the "Sources disagree" note and both quotes, and doesn't claim the conflict is resolved. Meeting some versions but not others (19) stays `needs_confirmation`, and a parent or guardian never overrides an age rule. |
| Not published | Shown as "not published (not the same as 'no minimum')". It is never treated as satisfied. For minors, an unpublished age or guardian rule raises a question. |

**More rules:**
- Overall: any definite failure of an applicable rule wins (`not_met`); otherwise any unresolved check gives
  "Possible fit — confirm requirements" (`needs_confirmation`); only when every checked rule is applicable and met
  is it "Meets the published requirements we checked". Application availability is always shown separately.
- Evidence shown for a result is the smallest useful set: exact repeats and excerpts contained in a longer passage
  from the same source are hidden (the sourced data is unchanged); distinct and conflicting passages stay, and the
  "Evidence (N)" count matches what is shown.
- A missing profile answer gives `needs_confirmation`, never a failure.
- One-time activities never get recurring hours or month minimums.
- Typical durations are not minimums.
- Free-text schedules are shown, not auto-judged.
- Orientation info and past notices are notes only.

**Hours conversion.** Hours are only converted between week and month when the periods differ, using
the documented method in `backend/matching.py`: a month has between 4 and 31/7 weeks, and only the
conclusions that hold for every month are drawn.

**Overall result:**
- `not_met` if at least one clearly applicable requirement is unmet.
- Otherwise `needs_confirmation` if anything is unresolved.
- Otherwise `meets_published_requirements_checked`, which means "meets the published requirements we
  checked, subject to the organization's confirmation".

**Shown separately from fit:** application status ("Accepting applications (placement not
guaranteed)", "Applications closed", "Confirm with organization") and placement or shift availability
(never published as bookable). An application link is never treated as an opening.

## Folder layout

```
animal-volunteer/                 ← planned Git repository root
├── README.md · AI_prompts.md · requirements.txt · .env.example · .gitignore
├── backend/                      Python API and agent
│   ├── config.py                 paths, model, Portkey settings, limits, .env loading
│   ├── schemas.py                Pydantic models: dataset mirror, profile, assessment, API I/O
│   ├── data.py                   loads data/ once; lookups, filter values, search, list/detail shapes
│   ├── matching.py               deterministic assessment, alternatives, application checklist
│   ├── tools.py                  the 6 agent tools + profile confirmation (update_profile)
│   ├── geo.py                    ZIP areas, verified sites, straight-line distances, maps links
│   ├── agent.py                  the single PydanticAI agent, output validation, run_assistant()
│   ├── run_log.py                API-reported usage, gateway-cache status, sanitizing, traces, metrics
│   └── api.py                    FastAPI routes + serves frontend/dist in production
├── frontend/                     React + TypeScript + Vite website
│   ├── index.html · vite.config.ts (dev proxy for /api) · tsconfig.json · package.json
│   ├── public/                   static files copied as-is (favicon)
│   ├── src/api/                  types.ts (mirrors the API) · client.ts (fetch wrapper)
│   ├── src/components/           shared UI: Layout, cards, status badges, forms, illustrations, icons
│   ├── src/pages/                Home, Explore, OpportunityDetail, Compare, FindMyFit, About
│   ├── src/lib/                  labels and requirement-row helpers
│   ├── src/state/                in-memory app state (profile, conversation, compare selection)
│   ├── src/styles/global.css     the design system (colours, type, spacing, components)
│   └── dist/                     production build (created by `npm run build`; served by FastAPI)
├── tests/                        pytest (backend)
├── data/                         the sourced dataset (the only data source)
│   ├── volunteer_locations.json  verified volunteering sites + where each record takes place (Session 10)
│   └── geo/                      Connecticut ZIP Code Tabulation Areas (Census 2026 Gazetteer) + metadata
├── scripts/                      data validator + self-tests, quote check, real agent cases, ui_check.py,
│                                 build_geo_data.py (ZIP areas, Census geocoding, location quote check)
├── output/
│   ├── data_audit.md
│   ├── agent_runs/               sanitized real-run traces, runs_index.jsonl, README with usage tables
│   ├── screenshots/              genuine screenshots of the running website (synthetic inputs)
│   ├── location_check/           Session 10 browser test report + independent distance check
│   └── ui_test_report.json       results of the last browser check run
├── docs/                         project_requirements · rubric_checklist · backend_design
└── local_data/                   (gitignored) page snapshots; API run metrics (no message text)
```

**Where new files go:**
- **Python API or agent logic:** `backend/`. Backend tests: `tests/`.
- **Website code:** `frontend/src/`. Pages in `pages/`, reusable pieces in `components/`, API shapes in
  `api/types.ts` (keep them in sync with `backend/schemas.py` and `backend/data.py`), styles in
  `styles/global.css`.
- **Data:** only `data/*.json`.
- **Evidence:** `output/`.
- **Planning and report material:** `docs/`.

The frontend talks to the backend only through `/api`. It never reads `data/*.json` directly and never
sees any credential.

## Profile answers: what is trusted (Find my fit)

| Where an answer comes from | Status | Used for requirement checks? |
|---|---|---|
| The person fills in the form, edits a field, or confirms | `confirmed` | Yes. This is the trusted path. Only a correction or withdrawal quoted from the person's **current** message changes it (see below). |
| The assistant read it from the person's message, **with a quote that appears verbatim in their messages** (and, for numbers, contains the number) | `from_message` | Yes, provisionally. "Your answers" marks it "from chat", with one **Confirm these details** action, Edit and Remove per field, and the quotes in an expandable section. |
| Anything else (no verifiable quote, or derived by the assistant) | `suggested` | **No** for age, guardian, hours, hours period, commitment months, session length, **town, ZIP code and a volunteering-area limit** (Session 10). Other fields (such as interests or days) only guide the search. |
| A chat value that differs from a confirmed answer | `conflicts_with_confirmed` | No. The confirmed answer is used. |

- **Across turns:** the browser sends confirmed answers as `profile`, and `from_message` facts with
  their supporting text as `message_facts`. The server re-verifies those quotes every turn.
- **Corrections and withdrawals (owner-testing fix, 2026-10-26):** the newest message wins. A replacement
  ("actually I'm 25") or a withdrawal ("I can't commit weekly or for 12 months") must be quoted from the current
  message; it applies even to confirmed answers (the response lists them in `confirmed_overrides`, and the page
  drops them). A withdrawn field becomes unknown, never a guessed replacement. The server detects plain
  withdrawals itself before any search or fit check, and the model can clear fields with `cleared_fields`.
  Withdrawn fields are returned as `withdrawn_fields` and sent back each turn, so older messages can never restore
  them; only a value stated in a later message can. "Your answers" lists them under "Removed at your request".
- **Remove / Dismiss:** "Remove" (any answer) makes it unknown and adds it to the withdrawn fields. "Dismiss" (an
  unverified suggestion) sends it as `declined_fields`, so it is never applied from chat. Suggestions are never
  confirmed automatically.
- **Edit form:** "Add or edit your answers" shows the current answers (confirmed and "from chat"). Opening it
  confirms nothing; "Save my changes" confirms only the fields changed there, and clearing a filled field removes
  it. A new reply updates untouched fields without overwriting unsaved edits. The detail page's "Check my fit" form
  works the same way.
- **When preferences change**, the latest results are re-checked with the deterministic endpoint (no AI
  call). The page says the written reply was based on the earlier answers.
- **Memory across long conversations:** the model sees the last 10 turns, and older user messages are
  sent as `earlier_user_messages` only so remembered facts can still be re-verified. Collapsing
  earlier messages on screen never removes them from the session; "Clear my session" does.
- **Location facts:** a ZIP needs the five digits in the person's own words, so it can never be inferred
  from a landmark ("next to Yale SOM"). Changing the ZIP re-estimates distances; changing eligibility
  answers re-checks requirements.
- **Limits:** this reduces extraction errors but cannot remove them. A verbatim quote can still be
  misread, so the app asks the person to confirm.

## Setup and run (local)

Requires Python 3.10 or newer (tested on 3.14.7). Node.js 18 or newer (tested on 24.21.0) is needed
only to build or develop the website.

### Quick start for graders (no Node needed)

The built website (`frontend/dist/`) is included in the repository, so Python is enough.

```bash
git clone https://github.com/rheasong3411/final-project.git
cd final-project
python3 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Key: put PORTKEY_API_KEY=... in animal-volunteer/.env OR in the folder above it (../.env)
uvicorn backend.api:app --port 8000    # if port 8000 is busy, use another free port, e.g. --port 8001
```

Open **http://localhost:8000** (or the port you chose). Stop with Ctrl+C.

**Fresh clone from GitHub, tested 2026-10-26** (commit `c3f1e0a`, macOS 14.7, Python 3.14.7, pip cache off): the
commands above took about **23 s** from `git clone` to a running app (clone 5 s, venv 2 s, `pip install` 14 s,
server start 2 s), with `PORTKEY_API_KEY` read from `../.env`; a `.env` inside the repository folder also worked. Time to
read and type the steps is extra. See `output/final_submission/20261026-021552/README.md`. (Earlier clean-copy rehearsal:
`output/setup_rehearsal/clean_copy_rehearsal.md`.)

### Rebuilding the website (developers only)

```bash
cd frontend && npm ci && npm run build && cd ..   # rewrites frontend/dist/ from src/ (package-lock.json pins versions)
```

### Run the website (one terminal, production-style; after the quick start)

```bash
source .venv/bin/activate
uvicorn backend.api:app --port 8000    # no --reload, so there is only one server process
```

Open **http://localhost:8000**. FastAPI serves both the website (`frontend/dist/`) and the API (`/api/...`).
Direct links such as `/explore` or `/opportunities/<id>` work, and API docs are at `/docs`. Stop the
server with Ctrl+C (or `pkill -f "uvicorn backend.api:app"` if it runs in the background).

### Develop the website (two terminals)

```bash
# Terminal 1 — backend
source .venv/bin/activate && uvicorn backend.api:app --port 8000
# Terminal 2 — frontend with hot reload; /api is proxied to the backend
cd frontend && npm run dev
```

Open **http://localhost:5173**.

**If a port is busy** (on this machine another project already uses 8000, and sometimes 5173), pick
other ports:
- `uvicorn backend.api:app --port 8001`
- `AVF_API_PORT=8001 npm run dev -- --port 5174`, then open http://localhost:5174

Stop both terminals with Ctrl+C.

### Optional: save synthetic test traces from the website

Start the backend with `AVF_SAVE_TRACES=1 uvicorn backend.api:app --port 8000` **only** when sending
synthetic test messages. Each assistant run is then also saved to `output/agent_runs/ui_integrated__*.json`
(`AVF_TRACE_CASE=<label>` changes the prefix). ZIP codes are always redacted from saved traces.
It is off by default, so real visitors' conversations are never written to evidence files. Normal runs
only append a metrics line (no message text) to the gitignored `local_data/`.

**API keys.** `PORTKEY_API_KEY` is read only on the backend. The first value found wins, and nothing
is overridden:
1. a variable already set in the environment;
2. `animal-volunteer/.env` (the repository root);
3. `../.env` (the folder one level above the repository, where the course staff keep theirs).

No other folders are searched. The key is never printed, logged or returned. `GET /api/health` shows
only whether a key is present and which of those three sources it came from. Browsing, details,
assessment and alternatives all work **without** a key; only `/api/assistant` needs it.

## Try the API

```bash
curl -s localhost:8000/api/health
curl -s localhost:8000/api/filters
curl -s "localhost:8000/api/opportunities"                                   # Greater New Haven, described roles
curl -s "localhost:8000/api/opportunities?town=Branford&animal=cats"
curl -s "localhost:8000/api/opportunities?scope=all&record_type=described_volunteer_role&record_type=independent_support_activity"
curl -s localhost:8000/api/opportunities/chs_newington_group_trails          # details, evidence, sources, location, checklist
curl -s -X POST localhost:8000/api/location/estimates -H 'content-type: application/json' \
     -d '{"zip_code":"06511","opportunity_ids":["ah_dog_walking","gnhcp_direct_care"]}'   # ZIP in the body, never the URL
curl -s -X POST localhost:8000/api/opportunities/branford_general_volunteer/assess \
     -H 'content-type: application/json' \
     -d '{"profile":{"age":14,"town":"New Haven","available_hours":2,"hours_period":"week"}}'
curl -s -X POST localhost:8000/api/alternatives -H 'content-type: application/json' \
     -d '{"profile":{"age":12,"interests":["dog_walking"]}}'
curl -s -X POST localhost:8000/api/assistant -H 'content-type: application/json' \
     -d '{"message":"I am 26 in New Haven, love cats, 3 hours a week for a year. Options?"}'
```

Interactive docs are at `http://localhost:8000/docs` while the server runs.

**Volunteer profile fields (all optional):**
- `age` (whole years), `guardian_available`, `town`, `include_wider_connecticut` (default `false`)
- `interests` (activity tags), `animal_preferences`, `prefers_no_animal_contact`
- `available_hours` + `hours_period` (`week`/`month`), `commitment_months`, `commitment_preference`
- `available_days`, `available_times`
- `max_session_hours`: the longest single continuous block the person can attend, used for one-time
  sessions. Weekly or monthly hours never answer this.
- Location, kept as separate facts (Session 10; none of them changes a requirement result except `town`,
  which residence-based rules such as non-resident fees use):
  - where they live: `town`, `zip_code` (exactly five digits, a string so leading zeros survive),
    `prefers_not_to_share_zip`;
  - how they travel: `has_car`, `wants_nearby`;
  - where they will volunteer: `volunteer_only_in` (an explicit limit to one town; replaces the earlier
    `restrict_to_town`) or `nearby_towns_ok`. On its own, `town` does not filter results.

Birth dates, addresses, contact details and medical history are **not** collected; unknown fields
are rejected with 422.

**Assistant request:** `{message (≤2000 chars), profile? (answers the person confirmed), message_facts? (facts from earlier messages, with the person's words), declined_fields?, history? (≤10 turns), earlier_user_messages? (older user messages, used only to re-verify remembered facts)}`.

**Assistant response:**
- `answer`, `recommendations` (suitable options, each with the deterministic `assessment`),
  `alternatives` (suitable, not closed), `explained_non_matches` (roles discussed because they don't
  fit or are closed; never shown as options)
- `requirement_assessments`, `follow_up_questions`, `sources` (every source the shown assessments and
  checklists use), `application_checklists`
- `profile_used`, `profile_provenance` (`app` / `user_stated` / `inferred` / `user_correction` per
  field), `profile_changes`
- `outside_area_suggestions` (only with `volunteer_only_in`: suitable records outside that town, or whose
  own location isn't published there, offered only if the person chooses to widen the area),
  `location_context` (where they live, ZIP status without the digits, travel, area limit), and a
  `location` on every recommendation (towns, verified site, maps link, distance, `in_chosen_area`)
- every recommendation also carries `next_actions` ("Ask about availability" → the organization's contact page,
  and/or "Check application details" → its volunteer or application page); each requirement result carries
  `uncertainty_note` (for example "Listed on an older application form; needs confirmation.")
- `requested_model`, `returned_models`, `usage` (API-reported), `error`, `disclaimer`

If the model fails, `ok` is `false` and `error` is one of `credentials_missing`,
`credentials_rejected`, `model_unavailable`, `rate_limited`, `timeout`, `content_filtered`,
`usage_limit_exceeded`, `invalid_model_output` or `internal_error`. No recommendations are shown.

## The agent (summary; details in `docs/backend_design.md`)

**One PydanticAI agent.** It runs `gpt-6-luna` through Portkey (`https://api.portkey.ai/v1`, OpenAI
Responses API) with no fallback model.

**Tools:**
- `search_opportunities` (Greater New Haven by default; other ways to help on request)
- `get_opportunity_details`
- `assess_profile` (deterministic)
- `find_alternatives`
- `get_application_checklist` (built from the dataset)
- `update_location_preferences` (Session 10: where they live, ZIP, car, closeness, area limit; returns the
  ZIP status)

**Division of labour:** the model picks records, extracts the facts the person stated, explains, and
asks follow-up questions. The code decides every requirement result, the application status, sources
and checklist steps.

**How updated answers are handled:** there is one profile per run. The rules are in "Profile answers:
what is trusted" above.
- Model-assigned labels are not trusted on their own; a chat fact needs a verifiable quote.
- A verified chat correction replaces an earlier chat value when the model marks it in
  `corrected_fields` or when the new quote comes from the current message.
- Confirmed answers win unless the person corrects or withdraws them in the current message.
- After an age rule rules out what the person asked for, the assistant explains it and asks before suggesting
  other kinds of activity or a wider area; it never implies an activity accepts minors without a published rule.
- Every profile change recomputes all stored assessments.

**Output validation:**
- Recommended, alternative and non-match IDs need a **current** assessment, computed under the final
  profile.
- `stated_fit` must equal that assessment's result.
- Recommendations can't be `not_met`. Alternatives can't be `not_met` or explicitly closed.
- Cited sources must belong to the records that are recommended, offered or discussed.
- If no suitable non-closed option is offered, a broad search or `find_alternatives` must have been run
  first.
- Answers can't contain the key, claim approval or guaranteed placement, say someone is "eligible", or
  assert that a schedule fits.
- Session 10: with `volunteer_only_in`, recommendations and alternatives must have their **own** published
  location in that town (an organization's town alone doesn't count); others may only be
  `outside_area_ids`. Travel times and "walkable", "convenient" or "by bus" claims are rejected unless
  clearly negated.
- Session 11: **no distance or mileage may appear in the written reply.** Matching a number to "some"
  returned distance could attribute one role's distance to another, so each option's estimate is rendered
  from its own structured result (regression test: two options with deliberately swapped distances).
  The reply is a brief opening (≤1,200 characters, about 70 words asked for); at most 2 follow-up questions
  are shown. The answer can't ask for a town
  already known. A requirement that only needs confirmation (for example Animal Haven's older-form
  12 months and 2 hours a week) can't be stated as a current rule or turned into a leading question.
- Server-added follow-ups (Session 10): "Which town do you live in?", "Do you need to stay within <town>,
  or can you travel to nearby towns?", the optional ZIP offer, and — when an area limit leaves nothing
  open — an offer to try a different activity or widen the area.
- Invalid output is retried up to 2 times, then discarded with `invalid_model_output`.

**Cost setting:** `AVF_TOOL_PROFILE=compact` is the default. The details tool doesn't repeat what the
requirement check returns, and evidence quotes come only on request. `AVF_TOOL_PROFILE=baseline`
restores the earlier behavior. Measured: −33% model cost per run with no quality loss in 12 real runs
(`output/cost_eval/comparison.md`).

**Search:**
- A home town does not filter the search, which covers all of Greater New Haven. An explicit
  `volunteer_only_in` limit is applied to every search and alternative list.
- With a supported ZIP, results carry a `distance` text; `sort_by_closest` orders by it (unknown last).
- Results list applications that aren't explicitly closed first.
- If every match is closed, `broader_options` are returned from the same scope.
- Wider Connecticut is only searched on request.
- One-time sessions are checked against `max_session_hours`.

**Limits per call:** ≤8 model requests, ≤14 tool calls, ≤120k tokens, ≤4,000 output tokens per
response, 60 s per request, 180 s per run. Per client: 6 calls a minute, 2 concurrent runs.

## Tests and checks

```bash
python -m pytest -q tests                  # 110 tests: matching, API/config, regressions, profile confirmation, geo/location; agent tests use a MOCKED model
python scripts/build_geo_data.py verify    # location quotes vs local page snapshots (30/30 on 2026-10-25)
cd frontend && npx tsc -b && npm run build && cd ..   # type check + production build
python scripts/ui_check.py http://127.0.0.1:8000      # browser checks of the RUNNING site (needs `pip install playwright` + Chrome; 2 real AI turns; add --no-ai to skip)
python scripts/ui_safety_demo.py http://127.0.0.1:8001 # safety demo through the website (real AI; start backend with AVF_SAVE_TRACES=1)
python scripts/cost_eval.py run                        # 12 REAL runs: baseline vs compact tool profile → output/cost_eval/
python scripts/tokenomics.py                           # costs from saved real usage (rates are inputs; see output/cost_eval/tokenomics.md)
python scripts/clean_copy_rehearsal.py --port 8001     # timed clean-copy setup rehearsal (temporary .env files, deleted afterwards)
python scripts/build_slides.py                         # rebuilds report.html and slides.html from the evidence (needs `pip install pillow`)
python scripts/validate_data.py            # dataset structure and consistency
python scripts/test_validate_data.py       # 52 validator self-tests (16 for the ZIP-area, town and location files)
python scripts/current_cost.py             # prices the Session 11 fresh runs → output/cost_eval/current_agent_session11.md
python scripts/check_evidence_quotes.py    # needs local snapshots; exit 2 = skipped (not available)
python scripts/run_agent_cases.py          # REAL model runs (uses the key and costs tokens) → output/agent_runs/
```

The agent tests in `tests/test_agent_mocked.py` use a scripted fake model. They check our validation
and error handling, **not** the real model's behavior. Real-model evidence is in `output/agent_runs/`.

**Data notes:** `validate_data.py` exits `0` on success (warnings may print). Since Session 11 it also checks
`data/geo/ct_zcta.csv` (5-digit IDs with leading zeros, unique, Connecticut coordinates, metadata row count)
and `data/volunteer_locations.json` (unique IDs, valid opportunity/source/organization references, complete
in-range coordinate pairs, a geocoded site for every `verified_site`, and no site for unknown locations). Passing validation means
the data is consistent, not that it is accurate. The quote check proves that quoted text appeared on
the pages as fetched on 2026-10-25. The snapshots stay local because they are full copies of
third-party pages.

## Data dictionary (schema v2)

All three files are JSON **arrays of records**. IDs are lowercase `snake_case` strings and stayed
the same through the correction pass.

### Conventions

| Value | Meaning |
|---|---|
| `null` | **Unknown or not published** in the sources we inspected. Never read it as zero, "no requirement", "not required", "unrestricted" or "eligible". |
| Empty list `[]` | Used only for bookkeeping lists (`unresolved_questions`, `conflicts_or_stale_information`, `reliability_flags`, `locations`, organization `field_evidence`), where it means "none recorded". **Requirement and schedule lists are never empty: `null` means not stated.** The validator enforces this. |
| `minimum_age: 0` | The source explicitly says **all ages** are welcome (one record: Branford general volunteer). Its published guardian rule still applies. |
| `scope` | `organization` (rule stated for the whole organization), `program` (a named program or group of roles) or `role` (this role only). Rules are only attached where the source applies them. A clearly stated role-specific rule overrides a general one for that role, with both statements kept in the evidence. |

### `data/sources.json`

| Field | Meaning |
|---|---|
| `source_id`, `organization_id` | ID; organization the page belongs to |
| `url`, `page_title` | Page inspected |
| `accessed_at` | ISO-8601 timestamp with timezone of **when we fetched the page**. It does **not** mean the organization confirmed the information then. A later recheck is a separate source record (e.g. `chs_newington_openings_recheck`). |
| `access_result` | `accessible`, `accessible_form_only`, `accessible_dynamic_content_not_rendered`, `not_found_404`, `not_accessible` |
| `published_update_date` | Update date if the page states one (none did; copyright years are not update dates) |
| `reliability_flags` | `possibly_superseded` (e.g. Animal Haven's on-site form, which the current page appears to have replaced with POINT), `undated` (PAWS flyer), `partially_outdated` (GNHCP volunteer page testimonials describe the old location) |
| `evidence_notes` | Short paraphrase of what the page supports |
| `conflicts_or_stale_information` | Conflicts, stale dates and limitations noticed |

### `data/organizations.json`

| Field | Meaning |
|---|---|
| `organization_id`, `name` | ID; official name |
| `official_website`, `contact_page_url` | URLs |
| `physical_address` | Published **physical** address. Never a P.O. box. `null` for multi-site organizations (CHS), so roles aren't assigned to headquarters. |
| `town` | Town of the physical address |
| `geographic_scope` | `greater_new_haven` or `wider_connecticut` |
| `latitude`, `longitude` | **Both `null` (decision 3).** If ever set, both must be set together with `coordinates` evidence. |
| `source_ids`, `field_evidence` | Sources; evidence (same structure as for opportunities) |
| `locations` | `{label, address, town, source_id}` for each published site |
| `notes` | Identity checks, mailing-vs-physical address and similar |

### `data/opportunities.json`

**Identity and type**

| Field | Meaning |
|---|---|
| `opportunity_id`, `organization_id` | ID; organization reference |
| `record_type` | `described_volunteer_role`: the organization describes the role or program itself. `interest_area_only`: named only as an application checkbox with no description; **not an established placement**. `independent_support_activity`: something a person or group does on their own or through a school (drives, crafts, bake sales, advocacy); a useful way to help, **never shown as a staffed shelter shift**. |
| `title`, `description` | Short title and summary in our own words |
| `activity_tags` | `dog_walking, animal_socialization, animal_care_cleaning, laundry, fostering, transport, events, fundraising, administrative, grant_writing, communications_marketing, maintenance_trades, gardening_grounds, education_outreach, supply_drives, crafts, adoption_support, tnr_feral_care, dog_training, youth_program, group_project` |
| `animal_tags` | `dogs, cats, small_animals`, `not_applicable` (no animal contact implied) or `unspecified` (may involve animals, but the source doesn't say which) |
| `location_description`, `location_town` | Where the role happens as published. Town only when the source places the role there. **Admin work is never assumed to be remote.** |

**Requirements (normalized for matching)**

| Field | Meaning |
|---|---|
| `minimum_age` | Integer or `null` (unknown or conflicting) |
| `guardian_requirement` | `null` unless the source **explicitly** states a guardian rule. Otherwise `{required, applies_under_age, details, scope}`. An adult minimum age is **not** treated as "no guardian required"; that would be an inference, not a published statement. |
| `commitment_type` | `recurring` (a per-week or per-month minimum is published), `one_time` (a single session or project), `variable` (the source says it varies or gives only a typical range) or `unknown` |
| `minimum_hours` + `hours_period` | Recurring minimum, `week` or `month`; both `null` otherwise |
| `minimum_commitment_months` | Published **minimum** length of service. Typical durations are never copied here. |
| `time_commitment` | `null` or a list of the published commitment statements, kept with their ranges and units: `{published_text, source_id, scope, hours_min, hours_max, hours_per (week \| month \| session), duration_months_min, duration_months_max, duration_is_typical_not_minimum, note}`. For example, "2-3 hours per week ... at least 6 months" keeps both the 2 and the 3. |
| `recurring_schedule` | `null` or `{original_text, summary, source_id, scope}` for **ongoing** volunteering hours, regular event days or listed open shifts. Never contains a specific calendar date. |
| `orientation_info` | `null` or the same structure, for how and when orientations happen in general (for example "monthly in spring and fall") |
| `dated_notices` | `null` or `{original_text, stated_date_text, stated_year, timing_assessment, assessed_on, note, source_id, scope}` for **specific dated announcements**. `stated_year` is `null` when the source prints no year; it is never inferred. `timing_assessment` is `appears_past_year_not_stated`, `past`, `upcoming` or `unknown`; `past` and `upcoming` require a printed year. Dated notices are **never** shown as upcoming events or used as availability. |
| `training_requirements` | `null` or `{type, description, scope, source_id}` with `type` from `orientation, training, mentorship, shadowing, video, interview, other` |
| `fees` | `null` or `{amount, currency, applies_when, payment_terms, covers, source_id}` |
| `other_requirements` | `null` or `{requirement, scope, source_id}` for actual requirements (insurance, residence area, group size, registration, and so on) |
| `notes_for_applicants` | `null` or `{note, type, scope, source_id}` for things that are **not requirements**: `advisory` (e.g. an allergy warning), `preferred_skill` ("computer and Excel skills" requested) or `process_note` (which form to use, whom to contact) |

**Requirement applicability**

`requirement_applicability` is an object keyed by requirement field: `minimum_age`,
`guardian_requirement`, `minimum_hours` (covers `hours_period`), `minimum_commitment_months`,
`commitment_type`, `time_commitment`, `recurring_schedule`, `training_requirements`, `fees` and
`other_requirements`. Each entry is `{status, source_ids, reason}`:

| `status` | Meaning |
|---|---|
| `published_applicable` | Stated on a current organization page at the recorded scope, so it is safe to compare against. It still doesn't guarantee eligibility. |
| `needs_confirmation` | Published somewhere, but its current applicability to this role is uncertain (a possibly-superseded source, ambiguous wording, or unclear scope). The claim and evidence are kept, and it raises a question instead of a decision. |
| `conflicting` | Sources disagree. The normalized value is `null`; both claims stay in `field_evidence` with `conflict: true`. |

The validator enforces these rules:
- Every populated requirement has an applicability entry.
- `published_applicable` can't rest only on `possibly_superseded` sources or on conflicting evidence.
- Every `needs_confirmation` or `conflicting` entry has a matching `unresolved_questions` item.

**Status and evidence**

| Field | Meaning |
|---|---|
| `application_status` | `explicitly_accepting_applications` (the page says it is accepting volunteers or lists the role as a current opening; placement is still not guaranteed), `explicitly_closed`, or `needs_confirmation` (everything else; a description or application link alone doesn't prove a vacancy). `interest_area_only` records can never be "accepting". |
| `application_or_information_url` | Where to read more or apply (on the organization's own site) |
| `source_ids` | Every source the record relies on |
| `field_evidence` | `{field, source_id, evidence, scope, conflict?, note?}`. `evidence` is a short quote (`...` marks omissions and `[...]` our notes) or a labelled non-quote. Guardian evidence must be a published statement. |
| `unresolved_questions` | `{field, question}`: what a volunteer should confirm with the organization |

### `data/volunteer_locations.json` and `data/geo/` (Session 10)

Kept separate from `opportunities.json`, so the original records and their evidence are unchanged.

| Part | Meaning |
|---|---|
| `sites[]` | `{site_id, organization_id, label, address, town, address_evidence[{source_id, url, quote, accessed_at}], geocoder_query, geocode, note}`. Nine physical sites, each re-checked on an official page on 2026-10-25. P.O. boxes and mailing addresses are never used. |
| `geocode` | `{latitude, longitude, matched_address, match_count, tiger_line_id, street_side, benchmark, geocoded_at}` from the U.S. Census Geocoder (`Public_AR_Current`). Coordinates are interpolated along street address ranges, so they are approximate. |
| `opportunity_locations[]` | One entry per record: `location_status` = `verified_site` (an official page places the role at the site; distance allowed), `candidate_site_unconfirmed` (a likely site only; no distance), `volunteer_home` (fostering; no distance) or `not_published`. Plus `site_id`, `candidate_site_id`, `related_site_id`, `evidence[]` and `note`. 15 verified, 6 candidate, 6 home-based, 37 not published. |
| `geo/ct_zcta.csv` | The 289 Connecticut ZIP Code Tabulation Areas from the Census 2026 Gazetteer: `zcta` (5-digit string), `intpt_lat`, `intpt_lon` (the Census "internal point"), `aland_sqmi`. ZCTAs approximate USPS ZIP areas; P.O. Box-only ZIPs such as 06501, and single-organization ZIPs such as 06520 (Yale), have none. |
| `geo/ct_towns.csv` | Session 12: the 169 Connecticut towns' Census internal points (2026 Gazetteer, county subdivisions), used only as "town center" reference points for roles that publish a town but no address. |
| `organization_locations[]` | Session 12: one verified physical site per organization (`site_id`), or none (CHS has several sites; Cat Tales only a P.O. box). Used for "Organization is about X miles away"; never counts as where a role happens. Home-based records may add `travel_note`, `travel_evidence`, `related_site_purpose`. |
| `geo/ct_zcta_metadata.json` | Source URL, file hash, dataset date, row counts, licence (U.S. Government work, public domain) and what the coordinates mean. |

Distances use the haversine formula (sphere of radius 3,958.8 miles) from the ZIP area's internal point
to the site. Under 1 mile is shown as "under 1 mile"; below 10 miles the value is rounded to the nearest
half mile, and from 10 miles to the nearest mile. Rebuild with `scripts/build_geo_data.py`.

## Sourcing rules followed

- Public pages only. No forms submitted, no accounts created, no organizations contacted, no blocked
  pages bypassed.
- Facts come only from pages we inspected. Search results and memory were not used as evidence.
- Short quotes or paraphrases only. Full page snapshots stay local.
- No shelter photos or logos are used. Visuals will be original.
- Nothing was invented: no exact shifts, live openings, animal-handling permissions, transit access or
  remote options.

## Organizations covered

**Greater New Haven (default view):** Friends of the New Haven Animal Shelter (New Haven), The Animal
Haven (North Haven), Branford Compassion Club (North Branford), Dan Cosgrove Animal Shelter (Town of
Branford), The Greater New Haven Cat Project (Northford).
**Wider Connecticut (separate scope):** Cat Tales (Middletown P.O. box; shelter address not
published), Connecticut Humane Society (Newington, Waterford and Wilton sites), PAWS (Norwalk).
