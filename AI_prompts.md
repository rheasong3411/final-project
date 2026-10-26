# AI prompts log — Animal Volunteer Finder (MGT409 Final Project)

This log records the prompts Rhea typed to her coding assistant (Claude Code) while building the
project, in her own words. Entries are added as the work happens and are not reconstructed afterward.
Short housekeeping replies are left out. Any secrets would be replaced with `[REDACTED]`.

Coding assistant: Claude Code. The app's runtime AI will be `gpt-6-luna` through Portkey; that is
separate from the coding assistant.

---

## Session 1 — 2026-10-25 — Project setup, rubric and sourced dataset

### Prompt (verbatim)

```text
ok, so we are starting my MGT409 final project. we are working inside my Final Project folder. the original assignment PDF is in Rubrics/. put the app and all its project files in animal-volunteer/ inside Final Project.

first confirm the exact paths. inspect existing files before changing anything and preserve existing work. do not initialize another Git repository inside an existing repository.

read the original assignment PDF in Rubrics/ before starting. use it as the authoritative reference. if you cannot read it, tell me before proceeding.

the project is an animal-volunteering website for Greater New Haven. people should be able to browse opportunities, filter them, compare requirements, and talk to an AI assistant about what fits their age, interests, location, available hours, and commitment length.

the important feature is that we explain why an opportunity fits or does not fit, flag missing or conflicting information, and suggest another way to help when someone cannot meet a requirement. we are helping people prepare to apply; we are not approving volunteers or guaranteeing openings.

for this first step, set up the project, document the rubric, and compile the sourced dataset. do not build the website or runtime agents yet.

1) set up the project

inside animal-volunteer/, create:

1) README.md — project purpose and instructions for inspecting and validating the data
2) AI_prompts.md — accurately record this prompt and later prompts as we work; do not invent conversation history
3) requirements.txt — packages needed for the data-preparation scripts
4) .gitignore — exclude real .env files, .venv, node_modules, credentials, and local personal data; allow .env.example
5) .env.example — PORTKEY_API_KEY with no real value
6) data/organizations.json
7) data/opportunities.json
8) data/sources.json
9) scripts/validate_data.py
10) output/data_audit.md
11) docs/project_requirements.md
12) docs/rubric_checklist.md

check whether Python, Node/npm, and Git are installed and report their versions. set up a Python virtual environment if needed and install only what is needed for this stage.

our later backend will use PydanticAI agents powered by gpt-6-luna through Portkey. Claude is the coding assistant; Luna will power the app’s runtime AI.

the backend must eventually load .env from the app’s repository root first, then one folder above it, without printing or committing secrets. we will verify the repository root when setting up Git so this works correctly for a fresh clone.

do not make model calls for this setup step. do not open or print existing API-key values.

2) record the original project requirements

read the assignment PDF and create docs/project_requirements.md as a faithful summary.

create docs/rubric_checklist.md with:

1) each requirement
2) its point value, where provided
3) the evidence needed
4) where we plan to satisfy it in the project
5) status: pending, implemented but unverified, or verified
6) evidence location when something is verified

include submission formats, report section order, page and slide limits, model restrictions, API-key handling, setup requirements, and the deadline.

use the original assignment as authoritative if it differs from this prompt. flag any conflict or ambiguity rather than silently choosing an interpretation.

make sure the checklist captures:

1) a useful, distinctive working AI-agent app using real tools and data
2) a GitHub repository with all necessary code, README, and .env.example
3) included data sufficient for graders to run the app; a small test dataset if the full dataset is large
4) local setup from a fresh clone within 10 minutes, or a working hosted app
5) support for .env in the repository root and its parent folder
6) gpt-6-luna only when using the course PORTKEY_API_KEY
7) a single report.html, 10–15 printed Letter-size pages, with embedded screenshots
8) report sections in this order: Title + links, Motivation, What is new here, The agents, Tokenomics, Safety, Impact, Limits + next steps
9) a single slides.html deck using reveal.js, maximum 10 slides, with embedded screenshots and diagram
10) real-run agent traces and screenshots
11) API-reported input, cached-input, and output usage
12) costs per run and per user per month, with projections for 100 and 10,000 users
13) evidence of cost-saving measures and their effect on performance
14) a demonstrated safety defense
15) evidence from a real prospective user trying the app
16) honest comparison with named existing products
17) an optional 2–3 minute demo video

knowing the full rubric does not mean building everything now. keep the checklist updated as we work and do not mark anything verified without evidence.

3) research the official sources

start with:

1) https://findafriendforlife.org/volunteer.html
2) https://theanimalhavenct.org/volunteer/
3) https://theanimalhavenct.org/volunteer-application/
4) https://branfordcompassionclub.org/how-to-help/volunteer/
5) https://branfordcompassionclub.org/contact-us/
6) https://www.branford-ct.gov/178/Volunteering
7) https://www.gnhcp.org/volunteer

for an optional wider Connecticut section, also inspect:

1) https://cattalesct.org/volunteer/
2) https://cthumane.org/volunteer/
3) https://www.pawsct.org/volunteer

prioritize Greater New Haven. clearly separate wider Connecticut organizations instead of presenting them as nearby.

follow relevant official links for requirements, locations, and applications. verify organization identity and location, since similarly named rescues exist in different states.

use publicly accessible information only. do not submit forms, create external accounts, contact organizations, or bypass blocked pages.

if you cannot access a source, record that limitation instead of filling gaps from memory. search results can help locate pages, but do not mark facts as verified without inspecting the supporting page.

earlier research found possible age-rule conflicts on Animal Haven’s pages, closed application categories on New Haven’s page, and a past orientation date on Branford’s page. recheck these rather than assuming they are still accurate.

4) compile the data

use consistent machine-readable field names and document their meanings in README.md. the three JSON files should each contain an array of records.

data/organizations.json

include one record per organization with:

1) organization_id
2) name
3) official_website
4) physical_address, when published
5) town, when known
6) geographic_scope: greater_new_haven or wider_connecticut
7) latitude
8) longitude
9) contact_page_url
10) source_ids

do not use a mailing address as a volunteering location. leave latitude and longitude null until verified; do not guess them.

for organizations with multiple sites, do not assign every role to headquarters. record the role’s actual location when published, or mark it unknown.

data/opportunities.json

include one record per distinct, explicitly described role or program with:

1) opportunity_id
2) organization_id
3) title
4) description — a short summary written in our own words
5) activity_tags
6) animal_tags, including not_applicable where appropriate
7) location_description
8) minimum_age
9) guardian_requirement
10) minimum_hours
11) hours_period: week or month, or null if unknown
12) minimum_commitment_months
13) published_schedule
14) training_requirements
15) fees, including amount, currency, and the conditions under which they apply
16) application_status
17) application_or_information_url
18) source_ids
19) field_evidence
20) unresolved_questions

choose and document consistent structures for guardian requirements, training requirements, fees, and field evidence.

use null for unknown values. an empty list should mean “none explicitly stated or applicable” only if that meaning is documented; do not let an empty list imply that no requirements exist.

never treat unknown as zero, unrestricted, or eligible.

for application_status, use:

1) explicitly_accepting_applications
2) explicitly_closed
3) needs_confirmation

a role description or application link alone does not prove a vacancy exists. even explicitly accepting applications does not guarantee placement or a specific shift.

in field_evidence, link every populated eligibility, schedule, commitment, training, fee, and status claim to its source_id and a concise supporting passage or faithful paraphrase.

preserve whether a rule applies to the entire organization or only one role. do not apply dog-walking requirements to administrative work unless the source supports that.

if sources disagree, preserve the conflicting claims in field_evidence and unresolved_questions. leave the disputed normalized value null rather than arbitrarily resolving it.

data/sources.json

include:

1) source_id
2) organization_id
3) url
4) page_title
5) accessed_at — actual timestamp with timezone
6) access_result
7) published_update_date, if stated
8) evidence_notes
9) conflicts_or_stale_information

the access timestamp means we inspected the page; it does not mean the organization confirmed the information that day.

use short evidence passages or concise paraphrases, not copies of entire websites.

do not invent exact shifts, openings, animal-handling permissions, transport accessibility, or remote work. administrative work is not automatically remote.

do not reuse shelter photos or logos without checking permission. we can use original visuals later.

create as many useful records as the evidence supports. do not pad the dataset to reach an arbitrary number or turn a donation request into a volunteer opening.

5) validate and audit the dataset

write scripts/validate_data.py using Python to check:

1) valid JSON and expected record structures
2) unique IDs
3) valid organization and source references
4) required fields and allowed status values
5) consistent field types
6) evidence references for factual constraints
7) nonnegative hours, fees, ages, and commitment lengths
8) valid coordinate ranges and source evidence for populated coordinates
9) both coordinates are present together or both are null
10) URLs have valid HTTP or HTTPS structure
11) no contradictory normalized values that ignore a recorded conflict

structural validation cannot establish factual accuracy. separately review the populated constraints against their cited sources and report which records and fields were checked.

run from animal-volunteer/:

python scripts/validate_data.py

fix structural errors. flag factual uncertainty for review rather than silently resolving it.

in output/data_audit.md, report:

1) actual organization and opportunity counts
2) counts by geographic scope and application status
3) coverage of each proposed filter
4) missing fields and inaccessible sources
5) contradictory rules
6) stale dates and application-status limitations
7) which records and constraints were checked against sources
8) which features this dataset supports
9) which features need more information
10) validation command and actual result
11) remaining decisions or questions for me

do not claim every record is complete, that all opportunities are currently open, or that source evidence guarantees eligibility.

6) keep the product scope grounded

our planned website will eventually include Home, Explore Opportunities, opportunity-detail, and About pages, with filters and a chatbot using the same data.

do not build these yet. use the data audit to assess whether we can support:

1) town/location filtering
2) animal and activity preferences
3) published age and guardian requirements
4) weekly or monthly hours
5) minimum commitment length
6) published schedule requirements
7) application status
8) evidence-backed explanations and application checklists

flag features we cannot support accurately. in particular, do not promise exact shifts, public-transit accessibility, live vacancies, or volunteer acceptance.

record that we need to compare existing services such as Idealist and Samaritan Scout before finalizing our novelty claim. AI volunteer search itself is not a new invention, so do not describe our project as the first or unique without evidence.

stop after this setup and data-preparation stage. show me:

1) the confirmed project and rubric paths
2) the folder structure
3) environment versions and setup results
4) the dataset counts
5) the validation result
6) a few representative records, including an uncertain or conflicting example if found
7) the unresolved issues we should review before building the app
```

### What happened

The assignment PDF was found at `Final Project/Rubrics.pdf`, not in a `Rubrics/` folder. Its text was
extracted and read in full, which showed the deadline is Mon Oct 26, 2026, 6:00 PM. The project folder,
docs, a 64-role sourced dataset from 34 inspected pages, a validator and a data audit were created. No
model calls were made, no Git repository was created, and no website or agents were built.

### Follow-up prompts

See Session 2. After reviewing the output, Rhea asked for a correction pass. The first dataset turned
some inferences and uncertain claims into values that a matcher could have used as hard eligibility
rules.

---

## Session 2 — 2026-10-25 — Data correction pass (before building the website)

**What was lacking in Session 1:**
- Guardian "not required" values were inferred from adult minimum ages.
- Claims from Animal Haven's possibly-legacy form looked like confirmed rules.
- Past orientation dates sat in the same field as recurring schedules.
- Checkbox-only interest areas and self-organized activities looked like shelter placements.
- CHS's one-time group project was recorded as a conflict with a six-month rule.

The follow-up below asked for those fixes, plus product-scope decisions.

### Prompt (verbatim)

```text
ok, i’ve reviewed the data-stage output. the dataset is a useful foundation, but before building the website, make the following corrections so the matching logic won’t turn uncertain information into hard eligibility decisions.

keep working inside animal-volunteer/. preserve the source evidence and existing IDs wherever possible. do not build the website or runtime agents yet.

1) correct guardian-rule handling

where guardian_requirement.required is false only because the minimum age is 18 or older, change guardian_requirement to null.

an adult minimum age does not prove the organization explicitly states that no guardian is required. preserve the minimum-age rule separately.

keep explicitly published guardian requirements, including program-specific exceptions. update the README, validator, evidence entries, and audit so they consistently distinguish unknown from explicitly not required.

2) distinguish published claims from rules that are safe to enforce

add a documented field-level applicability structure for normalized requirements, using statuses such as:

1) published_applicable
2) needs_confirmation
3) conflicting

link each assessment to the relevant source IDs and explain why uncertain claims need confirmation.

for Animal Haven, review the requirements taken only from the possibly-legacy on-site form, including the one-year commitment, dog-walking hours, and morning cleaning availability.

preserve the published claims and evidence, but mark uncertain current applicability. do not silently discard them or present them as confirmed current rules.

document the matching behavior we will implement later: an uncertain or conflicting requirement raises a confirmation question, rather than automatically accepting or rejecting someone. a clearly applicable published requirement can identify a mismatch, but the app still cannot guarantee eligibility or placement.

3) separate scheduling concepts

keep published volunteering hours separate from orientation dates and historical events.

add appropriately documented fields for:

1) recurring volunteering schedule
2) orientation information
3) dated events or historical notices

preserve the original wording and source. leave the year unknown when the source does not state it; do not turn an inferred year into a published fact.

past orientation dates must never appear as upcoming events or be used as recurring volunteer availability.

4) distinguish types of records

add a record_type field with documented values such as:

1) described_volunteer_role
2) interest_area_only
3) independent_support_activity

review all records and classify them based on their evidence.

Animal Haven’s checkbox-only interest areas should not look like established current placements. school supply drives, crafts, and advocacy activities can remain useful ways to help, but should not automatically appear as staffed shelter shifts.

do not delete useful records just to reduce the count. update the audit with counts by record type.

5) represent commitment types accurately

add commitment_type with values such as:

1) recurring
2) one_time
3) variable
4) unknown

recheck the CHS Newington group project against its official page. it explicitly describes a one-time 3–4 hour project.

treat a clearly stated role-specific exception as overriding a general recurring-program rule for that role. keep the supporting evidence and explain the scope. do not assign a six-month minimum to this one-time project.

review similar scope issues across the dataset. preserve ranges and units instead of reducing everything to a misleading single number.

6) update validation and evidence

update scripts/validate_data.py for the revised schema and run it.

check that uncertain rules cannot be represented as confirmed applicable constraints, that IDs and references remain valid, and that the new record and commitment types are documented.

the existing audit reports 297 verbatim quote matches and 21 validator self-tests. retain or reproduce the scripts and supporting evidence if available. if the original scratchpad evidence is unavailable, label those as previously reported results rather than independently reproducible checks.

do not fabricate test outputs or recreate source snapshots and label them as the original fetches.

7) settle the initial product scope

record these decisions:

1) keep Greater New Haven as the default view
2) retain wider Connecticut options in a clearly labeled separate scope
3) use town filtering initially; leave coordinates null and postpone distance and transit features
4) show source-check dates and uncertainty clearly
5) distinguish application status from requirement fit
6) label uncertain roles “confirm with organization,” not “open now”
7) keep application submission on the organization’s own website
8) do not select a visual theme yet unless i have explicitly chosen one
9) plan for animal-volunteer/ to be the repository root, subject to checking existing Git state
10) do not move or copy my real .env during this correction step; tell me the expected placement when we connect the backend

update README.md, output/data_audit.md, docs/rubric_checklist.md, and AI_prompts.md to reflect the actual changes.

stop after this correction pass. show the validation result, updated counts, a brief change summary, and before-and-after examples covering guardian uncertainty, a possibly-legacy requirement, a past orientation, and the CHS one-time project.
```

### What happened

The dataset was migrated to schema v2 with all 64 IDs preserved, and the CHS Newington page was
rechecked live (unchanged). The original page snapshots were still available, so the earlier quote
check was reproduced exactly (297 found and 44 derived on the pre-correction data). The original
snapshots were copied unchanged into a gitignored local folder. The quote check and the 21 self-tests
are now repo scripts, and the self-tests grew to 36 for the new rules. No website or agents were built,
no model calls were made, and the real `.env` was not touched.

### Follow-up prompts

None yet.

---

## Session 3 — 2026-10-25 — Backend and real AI workflow

### Prompt (verbatim)

```text
we are moving to the next stage of my MGT409 final project: build the backend and test the real AI workflow. do not build the frontend, report, or slides yet.

1) inspect the existing project first

confirm that we are working in:

`/Users/rhea/Desktop/MGT409 AI/Final Project/animal-volunteer/`

read the existing project instructions, README.md, docs/project_requirements.md, docs/rubric_checklist.md, output/data_audit.md, and the current data files before changing anything. preserve the sourced data and completed corrections.

use `/Users/rhea/Desktop/MGT409 AI/Final Project/Rubrics.pdf` as the authoritative assignment reference. if anything in our planning documents conflicts with it, flag the discrepancy and follow the original assignment.

rerun the existing data validator and its tests. run the evidence checker if its saved source snapshots are available. accurately distinguish passed, failed, and skipped checks. fix any problems that would affect the backend before proceeding.

record this prompt accurately in AI_prompts.md.

2) build a small, understandable backend

use Python, FastAPI, Pydantic, and PydanticAI. inspect the installed versions and current official documentation when needed rather than guessing API syntax.

organize the code into clear modules for data loading, schemas, matching rules, agent tools, agents, API routes, and run logging. choose a straightforward structure and explain it in the README.

load organizations.json, opportunities.json, and sources.json using paths relative to the project, not my computer’s absolute path.

the backend must work from the included dataset without needing the private source snapshots or scraping websites during each request.

provide API routes for:

1) health and configuration readiness, without exposing secrets
2) organizations and available filter values
3) filtered opportunities
4) an opportunity’s details, requirements, evidence, and source links
5) deterministic assessment of a volunteer profile against an opportunity
6) the AI assistant

use the existing dataset’s actual schema. do not create a second incompatible copy of the data.

3) implement matching rules in ordinary Python

create a typed volunteer profile that can represent age, guardian availability, town, geographic scope, interests, animal preferences, available hours and their period, commitment length, schedule availability, and relevant preferences.

collect only information needed for matching. do not request a full birth date, home address, medical history, or other unnecessary personal information.

Greater New Haven should be the default scope. include wider Connecticut only when requested.

keep these concepts separate:

1) whether the person meets a published requirement
2) whether information is missing or conflicting
3) whether the organization explicitly accepts applications
4) whether a specific placement or shift is available

never interpret an application link as proof of an opening.

assess each relevant requirement as met, not_met, or needs_confirmation. include the opportunity ID, requirement, profile information used, explanation, source IDs, and supporting evidence.

a missing profile answer must not become a failure. an unknown dataset value must not become unrestricted eligibility.

respect requirement_applicability. uncertain or conflicting requirements must not become definitive exclusions. preserve their evidence and explain what needs clarification.

respect commitment_type and the structured time information. do not apply recurring commitments to one-time activities. do not convert monthly hours into weekly hours without an explicit, documented method. orientation information and past notices must not become recurring volunteer schedules.

only mark an overall assessment not_met when at least one clearly applicable requirement is definitively unmet. otherwise return needs_confirmation when a relevant requirement remains unresolved. when all assessable requirements are met, describe the result as meeting the published requirements we checked, subject to organizational confirmation.

keep application status separate from this assessment.

default opportunity browsing should show described volunteer roles. label interest areas and independent support activities clearly and offer them as alternatives when relevant. do not present them as confirmed placements.

use town-based filtering for now. do not invent coordinates, mileage, travel times, transit access, remote availability, or exact shifts.

4) build the real AI workflow

use PydanticAI with `gpt-6-luna` through Portkey.

Claude is the coding assistant. Luna powers the app’s runtime AI. do not replace Luna with another model, hardcoded responses, or simulated agent activity.

use one well-designed tool-using agent unless a second agent has a clear, necessary responsibility. do not add agents just to increase the count.

the agent should:

1) understand the person’s request and ask focused follow-up questions when important information is missing
2) search the actual dataset through tools
3) call the deterministic assessment tool before making eligibility claims
4) compare a small number of relevant options
5) explain matches, unmet requirements, uncertainty, and application status using the returned evidence
6) suggest a sourced alternative when a requirement cannot be met
7) produce a practical checklist for the organization’s own application process

provide tools for searching opportunities, retrieving complete opportunity details and evidence, assessing a profile, and finding relevant alternatives. tools should return structured information with stable IDs.

use structured agent output that the future frontend can render: answer, recommendations, requirement assessments, source references, follow-up questions, and application steps where applicable.

validate recommendation IDs and source references against the dataset. ensure the model cannot override deterministic findings or invent application instructions. handle invalid output explicitly.

5) configure credentials safely

load `.env` from the project root first, then one folder above it, without overriding an already configured environment variable. document the precedence.

use `PORTKEY_API_KEY` only on the backend. do not print, log, commit, or return it through the API.

the existing `.env` may be two folders above the project. do not automatically search unrelated directories or copy it. if neither supported location nor the environment provides the key, finish the backend and offline checks, then tell me the exact supported location where i should put it.

keep `.env.example` free of real credentials.

confirm the documented Portkey configuration for the required model. do not guess a gateway URL or silently switch models if the call fails.

6) add practical safety and failure handling

treat user messages and dataset descriptions as untrusted content. instructions inside them must not override system rules, reveal secrets, or trigger unrelated actions.

limit tools to the project’s volunteer data and matching tasks. do not give the agent arbitrary shell execution, filesystem access, unrestricted browsing, or form-submission tools.

do not submit applications, contact organizations, or claim to approve volunteers.

handle missing credentials, unavailable models, timeouts, invalid profiles, empty search results, and malformed model output with clear responses. do not display fake recommendations when a model call fails.

set reasonable request limits, model-call limits, timeouts, and output limits so one conversation cannot create an uncontrolled loop.

7) test meaningful matching and safety cases

add focused tests using the actual dataset and clearly labeled synthetic profiles. cover at least:

1) a minor with unknown guardian availability
2) an adult for whom guardian requirements are unspecified
3) Animal Haven’s uncertain or conflicting requirements
4) a one-time activity that must not inherit a recurring commitment
5) missing hours or commitment information
6) an explicitly closed application category
7) an interest-only record that must not appear as a confirmed placement
8) a Greater New Haven search that excludes wider Connecticut by default
9) an impossible request that receives honest uncertainty or a sourced alternative
10) a prompt-injection attempt asking the assistant to ignore requirements or reveal its API key

unit tests may use mocks where appropriate, but clearly distinguish them from real model runs. passing mocked tests does not prove the actual agent works.

8) run the real agent and save honest evidence

if credentials are available, run a small number of actual end-to-end cases through the same workflow the API uses.

include a normal matching request, an uncertainty or conflict case, and a prompt-injection case. label all test profiles as synthetic; these runs do not count as prospective-user testing.

save sanitized, reviewable artifacts under an appropriate folder in output/ containing:

1) run ID and timestamp
2) exact requested model and returned model identifier when available
3) synthetic input and final structured response
4) actual tool calls and results
5) latency and success or failure
6) API-reported input, cached-input, and output token usage when available
7) usage provenance and which fields were unavailable

do not estimate token counts and label them API-reported. use null for unavailable usage fields. avoid double-counting cached tokens if they are already included in total input tokens.

do not invent costs. record cost only when returned by the provider or calculated from a verified pricing source, with the pricing date and calculation documented. otherwise leave it pending.

do not save secrets, authorization headers, hidden reasoning, or unnecessary personal information.

if a real run fails, preserve the sanitized error, explain the cause, and fix it where possible. do not mark the real workflow verified until an actual successful run occurred.

9) update documentation and stop at the checkpoint

update requirements.txt, README.md, .env.example, docs/project_requirements.md, and docs/rubric_checklist.md to reflect the actual implementation.

include exact commands for installation, starting the backend, running tests, and trying representative API requests. document the purpose of each main folder and which files the future frontend will use.

keep a concise record of the agent design, tools, matching logic, safety measures, and evidence locations for our later report. do not mark report, slides, cost optimization, fresh-clone setup, or prospective-user testing complete before they happen.

stop after the backend stage and show me:

1) the updated folder structure
2) what works and how to run it
3) test results, including skipped or failed checks
4) representative API and real-agent outputs
5) where the real traces and usage records are saved
6) unresolved issues and any action needed from me

do not build the frontend or choose its visual theme during this stage.
```

### What happened

**Data checks before building:** the validator found 0 errors (1 intentional warning), the 36 self-tests
passed, and the quote check ran because the local snapshots exist (376 found, 0 missing). The data files
were not changed.

**What was built:**
- A FastAPI backend in `backend/`.
- Deterministic matching in plain Python.
- One PydanticAI agent with 5 dataset-only tools, running `gpt-6-luna` through Portkey (Responses API,
  base URL confirmed from Portkey's docs and a probe call).
- 37 pytest tests; the agent tests use a mocked model.

**Real runs (synthetic inputs):** 8 runs were saved to `output/agent_runs/`.
- The first prompt-injection run was blocked by the provider's content filter but was mislabeled as a
  generic HTTP error. Error mapping was fixed and the run repeated, and a subtler injection case was
  added. That case reached the model, which refused both the key and the approval claim.
- The first normal-match run recommended only roles whose applications are closed. The instructions
  were changed and the run repeated.

**Not touched or not done:** the real `.env` (the key came from the shell environment); the frontend,
report and slides. Cost is still pending.

### Follow-up prompts

None yet.

---

## Session 4 — 2026-10-25 — Backend corrections before the frontend

**What was lacking after Session 3:**
- Profile handling could mix results from different profiles within one run.
- One-time session lengths were never checked.
- Alternatives and cited sources were only loosely validated.
- The normal-match run searched too narrowly, so it recommended closed roles and a schedule mismatch.
- The chat summary misstated the deadline as "today".

### Prompt (verbatim)

```text
before we build the frontend, fix the following backend issues. preserve the existing implementation, data, and real-run evidence. do not rebuild the project or overwrite old traces.

1) make profile handling consistent throughout each run

inspect backend/tools.py and backend/agent.py.

currently each assessment call can replace deps.profile_used, while deps.assessed retains results produced from earlier profiles. assemble_response then recalculates every recommendation using the last profile.

use a consistent, validated profile for the final response. when new information changes that profile, invalidate or recompute affected assessments before validating final output.

do not silently invent profile facts. distinguish explicit user corrections from inferred information, and document how updated answers are handled.

add a regression test where two tool calls supply different profile fields. confirm that the final explanation, stated_fit, profile_used, and displayed assessments agree.

2) assess one-time session requirements

keep one-time activities exempt from recurring hours and minimum-month requirements.

however, inspect their structured time_commitment information. when a published session requires 3–4 hours, show that requirement and ask whether the person can attend the session.

weekly or monthly availability alone does not establish that someone can attend one continuous session. return needs_confirmation when session availability is unknown.

if needed, add an optional session-availability field to the profile. do not convert a maximum into a minimum or assume the person must attend the entire published range.

add meaningful tests for unknown session availability and clearly insufficient session availability, respecting requirement_applicability.

3) validate alternatives and evidence consistently

require alternatives presented as suitable options to have a current deterministic assessment under the same final profile as recommendations.

an ID merely appearing in a search or detail result is insufficient. preserve the ability to discuss an unsuitable role when explaining why it does not fit, but do not label it a suitable alternative.

validate cited sources against the records and claims actually used, rather than checking only whether a source ID exists somewhere in the dataset.

include all source references needed by alternative assessments and application checklists in the final response.

add regression tests for an unassessed alternative, an unrelated but valid source ID, and an assessment invalidated by a profile change.

4) improve search coverage before declaring no suitable options

the saved normal-match rerun recommends closed cat roles and a Saturday event that conflicts with weekday availability.

distinguish the person’s town of residence from an explicit request to volunteer only in that town.

when someone gives a home town without restricting volunteering to that town, search relevant roles across Greater New Haven. prioritize relevant options whose applications are not explicitly closed.

if a narrow search returns only closed roles or obvious mismatches, broaden within the authorized geographic scope before reporting that no suitable option was found.

do not expand to wider Connecticut unless requested. do not invent travel distances or claim that a nearby town is convenient for the user.

add a test covering residence town versus an explicit location restriction.

5) verify the fixes and preserve honest evidence

rerun the backend tests, data validator, and validator self-tests. clearly report passed, failed, and skipped checks.

run the normal matching case again through the actual Luna workflow. save a new trace with real tool activity and API-reported usage. preserve the previous runs for comparison.

verify that the final structured response and natural-language explanation agree. explicitly check closed application status, unresolved schedules, and profile consistency.

update README.md, docs/backend_design.md, docs/rubric_checklist.md, and AI_prompts.md with the actual changes and results.

correct the deadline wherever it is incorrectly described as October 25: the original rubric states Monday, October 26, 2026 at 6:00 p.m.

stop after these corrections. show the changed files, regression-test results, new real-run result, and any remaining limitations. do not build the frontend yet.
```

### What happened

**Fixes made:**
1. **One profile per run, with provenance.** Each field is tagged app, stated, inferred or correction.
   Inferred values only fill gaps, and only explicit corrections override earlier values. Every
   assessment is recomputed when the profile changes, and assessments are fingerprinted with the profile
   they used.
2. **One-time sessions.** A new `session_length` requirement uses the optional `max_session_hours`.
   Weekly or monthly hours never answer it.
3. **Alternatives and sources.** Alternatives and non-matches must have a current assessment.
   Unsuitable roles go in `non_matches`. Cited sources must belong to the records actually used, and the
   response includes every source the shown assessments and checklists need.
4. **Search coverage.** Residence town is kept separate from an explicit location restriction. Search
   lists non-closed roles first, offers `broader_options`, and the validator won't accept an answer with
   no suitable option unless the search was broadened.

**Checks:** pytest 51 passed (14 new regression tests), the data validator found 0 errors, the 36
validator self-tests passed, and the quote check found 376 of 376 quotes. Nothing failed or was skipped.

**New real Luna run:** `01_normal_match__9f57e5508031`. It searched all of Greater New Haven,
recommended two non-closed cat roles, made no schedule claims, and passed all 12 automated checks. All
earlier traces were kept. The chat summary's "deadline today" error was corrected; the project files
already said Mon Oct 26, 2026, 6:00 PM.

### Follow-up prompts

None yet.

---

## Session 5 — 2026-10-25 — Frontend (React + TypeScript + Vite) and integration

### Prompt (verbatim)

```text
we are ready to build the frontend for my MGT409 animal-volunteering project.

use a warm and polished visual direction: cream backgrounds, forest green, soft peach accents, thoughtful typography, and tasteful animal illustrations.

1) inspect and preserve the existing project

confirm we are working in:

`/Users/rhea/Desktop/MGT409 AI/Final Project/animal-volunteer/`

read the existing project instructions, README, backend schemas and routes, docs/backend_design.md, and docs/rubric_checklist.md before editing.

preserve the working backend, sourced dataset, tests, and real-run traces. make only the backend changes necessary for frontend integration and the profile-confirmation improvement below.

this prompt explicitly selects the visual theme and overrides any earlier default theme instructions.

record this prompt accurately in AI_prompts.md.

2) establish a cohesive visual design

use these starting colors, adjusting shades when necessary for accessible contrast:

1) warm cream: #FAF7F0
2) forest green: #214D3C
3) soft peach: #F3D2BD
4) dark text: #24352D
5) muted sage: #E4EBDF

pair an elegant serif heading font with a highly readable sans-serif body font. use locally available or bundled fonts with reliable fallbacks.

make the website feel like a thoughtfully designed local community service. use generous spacing, clear hierarchy, subtle borders, restrained shadows, and consistent rounded corners.

create a distinctive hero composition with original SVG animal illustrations and small botanical details. keep illustrations decorative and avoid copying shelter logos or photos.

use polished hover and focus states, subtle transitions, and reduced-motion support. avoid excessive animation, emoji as primary icons, and decorative elements that crowd the information.

use clear, natural website copy with normal capitalization. the lowercase style of this command is not an instruction to make all website text lowercase.

3) build the frontend using React, TypeScript, and Vite

place frontend files in a clearly named folder within the existing project.

use reusable components and a small shared design system. avoid unnecessary dependencies and do not add a database or authentication for this stage.

connect the website to the existing FastAPI backend. inspect the actual API contracts rather than inventing response fields.

configure a development proxy for `/api`. support a production build served through FastAPI if practical, with API routes kept intact and direct navigation to frontend routes working.

keep all credentials on the backend. do not put PORTKEY_API_KEY in frontend environment variables, browser storage, JavaScript bundles, or network responses.

4) build these pages and flows

the primary navigation should include Home, Explore, and About, plus a prominent “Find my fit” action.

Home:

1) create a clear hero explaining the value: find animal-volunteering opportunities and understand what you need before applying
2) include “Explore opportunities” and “Find my fit” actions that lead to working features
3) explain the three-step process: explore, check requirements, prepare to apply
4) show a few real opportunities from the API, selected transparently rather than described as objectively “best”
5) include a concise explanation of source checking and uncertain availability
6) use dataset-derived counts only when useful; never describe all records as open placements

Explore:

1) default to Greater New Haven and described volunteer roles
2) provide search and filters for location, activity, animal type, organization, commitment type, and application status where supported
3) keep wider Connecticut an explicit opt-in with a clear geographic label
4) distinguish a volunteering-location filter from the person’s town of residence
5) show active filters, result count, clear-all controls, and helpful empty states
6) label independent support activities and interest areas separately when included
7) show opportunity title, organization, town when published, activity tags, commitment information, and application-status label
8) use “Not published” or “Confirm with organization” for missing information rather than inventing values
9) allow comparison of up to three opportunities

Opportunity details:

1) show the description, organization, location information, and application status
2) present age, guardian, time, commitment, schedule, training, and fee information clearly
3) distinguish recurring schedules, orientation information, and historical notices
4) make conflicting or uncertain requirements visible beside the affected information
5) provide expandable evidence with source links and actual page-access dates
6) explain that a page-access date does not mean the organization confirmed the information that day
7) include a “Check my fit” action using the deterministic assessment endpoint
8) show application preparation steps from the backend
9) link to the organization’s official application or information page with an accurately labeled button; do not submit anything inside our app

Comparison:

1) compare up to three selected opportunities in an accessible layout
2) include age, guardian requirements, recurring or one-time hours, commitment length, schedule, fees, application status, and unresolved questions
3) show source evidence and uncertainty consistently
4) on mobile, use stacked cards or another readable layout rather than squeezing a wide table onto the screen

About:

1) explain the project’s purpose, geographic coverage, and how the data was compiled
2) explain how AI recommendations and deterministic requirement checks work in plain language
3) describe the limits: no guaranteed openings, approval, booking, live shifts, or verified travel times
4) explain the privacy approach and how to clear session information
5) avoid unsupported partnership claims, testimonials, impact statistics, or claims that AI volunteer search itself is new

5) integrate a useful AI assistant

build a dedicated “Find my fit” experience with a readable conversation area, optional profile form, recommendation cards, and requirement details.

connect it to the actual `/api/assistant` workflow powered by Luna. do not use canned answers or simulated tool activity.

include optional fields matching the backend’s supported profile: age, town of residence, guardian availability where relevant, interests, animal preferences, hours and period, commitment length, schedule preferences, and maximum session length.

allow “Not sure” or unanswered values. do not default unknown answers to zero, no guardian, unrestricted availability, or eligibility.

show an editable “Your preferences” summary. distinguish confirmed answers from suggestions inferred by AI.

fix the remaining profile issue: model-assigned provenance labels alone do not prove that someone stated a fact. inferred eligibility facts must remain unconfirmed and must not become definitive inputs for age, guardian, hours, commitment, or session-length decisions until confirmed by the user.

use explicit form confirmation as a trusted path for those values. when facts come from chat, preserve the supporting user text and ask for confirmation when uncertain. do not claim this eliminates all extraction errors.

when preferences change, refresh assessments so old results are not presented as current. preserve profile confirmation across conversation turns without silently promoting unconfirmed suggestions.

render requirement results with plain-language labels such as:

1) meets this published requirement
2) does not meet this published requirement
3) needs confirmation

use icons and text as well as color. keep application status separate from fit.

show alternatives and non-matches with their correct labels. surface relevant questions to ask the organization and the backend’s application checklist.

provide useful loading, timeout, rate-limit, missing-key, provider-filter, and invalid-output states. preserve the user’s draft if a request fails. do not generate fake recommendations as a fallback.

do not show invented progress messages such as “Checking shelter availability.” a neutral loading indicator is sufficient unless actual backend events support more specific updates.

6) protect privacy and keep the experience understandable

keep profile and conversation state in memory for this stage unless there is a documented reason to persist it. provide a clear reset action.

do not send chat messages to analytics or write ordinary users’ conversations into public evidence files.

render model output safely as text or sanitized Markdown. do not insert untrusted HTML.

use external links safely and make their destination clear.

keep developer details out of the main experience. an optional collapsed “Run details” section may show the actual run ID, returned model, and API-reported usage when available. do not invent costs.

7) test the actual website

run the existing backend tests and add focused tests for profile confirmation and any integration logic you change.

run the frontend production build and any relevant type checks.

use browser automation if available to test the actual running website. check:

1) navigation and direct page loads
2) filters, reset, and empty results
3) selecting, comparing, and removing opportunities
4) opportunity details and source links
5) deterministic fit checks with missing information
6) a real AI conversation and a follow-up preference change
7) confirmation of inferred profile facts
8) an unavailable-backend or AI-error state
9) keyboard navigation and visible focus
10) mobile and desktop layouts

inspect representative pages at approximately 390px and 1440px widths. fix clipped text, horizontal overflow, unreadable contrast, broken controls, and console errors.

if browser testing is unavailable, state exactly what was not checked. do not mark it verified.

save genuine screenshots of the running website under output/screenshots/ with descriptive filenames. use synthetic profiles and exclude secrets or personal information.

save a new sanitized real-agent trace for the integrated workflow, preserving earlier evidence. distinguish automated checks from manual visual inspection and real-user testing.

8) document and stop at the frontend checkpoint

update README.md with exact development and production commands, required terminal sessions, URLs, and where each major type of file belongs.

update docs/rubric_checklist.md with actual evidence locations. leave the report, slides, cost analysis, cost-saving comparison, prospective-user test, and timed fresh-clone verification pending until completed.

do not build the report or slides, deploy the app, or publish to GitHub during this stage.

when finished, show:

1) the updated folder structure
2) how i start and open the website
3) screenshots of the main pages on desktop and mobile
4) build and test results
5) the real AI workflow result and evidence locations
6) remaining limitations or decisions

complete the functioning frontend and its backend integration, then stop for review.
```

### What happened

**Built:** a React + TypeScript + Vite website in `frontend/`, using the theme Rhea chose (cream, forest
green and soft peach; Fraunces and Source Sans 3; original SVG animals). Pages: Home, Explore,
opportunity details, Compare, Find my fit and About. It connects to the existing backend through `/api`.
The Vite dev proxy works, and FastAPI serves the production build.

**Backend changes, limited to integration needs and the profile-confirmation fix:**
- Profile confirmation: a chat fact counts only with a supporting quote verified against the person's
  own text. Eligibility facts stay unused until confirmed. Form answers are the trusted path, with
  `message_facts` and `declined_fields` carried across turns.
- Summary fields `minimum_age_status` and `uncertain_requirements`.
- Serving of the built frontend.
- An off-by-default trace switch for synthetic UI tests.
- Recording of gateway-cache status.

**Checks:**
- pytest 59 passed (7 new profile-confirmation tests), the data validator found 0 errors, the 36
  validator self-tests passed, and the quote check found 376 of 376.
- `tsc` and `vite build` passed.
- Browser checks of the running site passed 51 of 51, including 2 real AI turns sent from the website.
  The backend-unavailable state was simulated.

**Findings:**
- Manual screenshot review found an oversized decorative sprig, a desktop menu toggle, an off-by-one
  date, a sticky composer overlapping replies, and noisy suggestion items. All were fixed.
- Portkey replayed cached responses for two repeated identical requests. Those traces are kept and
  labelled as replays, cache status is now recorded, and later runs used unique messages (cache MISS).
- Another project's server occupies port 8000 on this machine, so testing used port 8001.

**Not done (left pending):** the report, slides, cost analysis, cost-saving comparison, real-user
testing, the fresh-clone check, deployment and GitHub.

### Follow-up prompts

None yet.

---

## Session 6 — 2026-10-25 — Evidence for the report and slides (safety, cost, setup, user test)

### Prompt (verbatim)

```text
the frontend is approved for this stage. preserve the warm cream, forest green, and peach design.

we are now preparing the evidence required for the final report and slides. do not write the final report or slides yet.

1) inspect the rubric and remaining checklist

read Rubrics.pdf and docs/rubric_checklist.md again for this stage’s requirements.

preserve existing code, screenshots, and traces. accurately record this prompt in AI_prompts.md.

do not redesign the website or add unrelated features.

2) demonstrate the safety defense in the actual website

run a synthetic prompt-injection test through the frontend that asks the assistant to ignore a published requirement or falsely approve a volunteer.

verify that the app refuses the false claim or presents the correct requirement and uncertainty. distinguish an application-level defense from an upstream provider content filter.

capture a genuine screenshot showing the request and resulting defense. save the sanitized trace and actual usage.

also demonstrate one implemented spending or loop limit with a focused test. use a mocked model where appropriate to avoid unnecessary spending, and label that evidence accurately.

do not expose a real key or fabricate a successful defense.

3) measure one meaningful cost-saving change

first inspect the current tools and traces to identify unnecessary token use.

choose a small change such as reducing repeated tool-result fields or avoiding redundant detail calls. preserve the evidence and requirements needed for accurate answers.

keep a reproducible baseline and optimized configuration, with the same required Luna model and the same evaluation inputs.

use at least three representative synthetic cases, including an ordinary match, conflicting requirements, and a minor or unsuitable request.

define quality checks before comparing the results: correct requirement assessment, application status, sources, uncertainty, alternatives where relevant, and agreement with the final profile.

run the actual baseline and optimized workflows. record API-reported input, cached-input, and output tokens, request counts, latency, and quality results.

distinguish cached input tokens from a full gateway response replay. record cache status and response IDs when available. label replays separately; do not count them as fresh generation or as proof of the optimization.

use documented cache controls if supported. if requests must contain unique run identifiers to avoid replays, use the same method for both configurations and document the limitation.

report failures and quality regressions honestly. do not repeatedly rerun only failed optimized cases until the comparison looks favorable.

save the comparison, traces, configuration details, and calculation script in clearly named locations.

4) establish pricing and calculate tokenomics

look for the course’s published pricing guidance first, then authoritative provider documentation for the exact required model.

do not substitute another model’s prices or assume that the returned model suffix establishes its billing rate.

record the pricing source, access date, currency, units, and treatment of cached input and output tokens. distinguish provider cost from any course billing arrangement.

if the exact rates cannot be verified, finish the token measurements and create a calculation script that accepts the missing rates as inputs. mark dollar figures pending and tell me precisely which pricing information i need to obtain.

when rates are verified, calculate:

1) cost per measured run
2) average cost for a clearly defined typical workflow
3) cost per user per month using an explicit usage assumption
4) monthly model costs for 100 and 10,000 users
5) the measured effect of the optimization on cost and quality

do not double-count cached tokens. separate model costs from hosting costs and explain what the projections exclude.

5) verify the grader setup path

include frontend/dist/ in the submission repository so the grader can run the built website without Node. keep the frontend source and lockfile so it remains rebuildable.

verify that the included build matches the current source. document the rebuild command.

perform a timed setup in a clean temporary directory without relying on the existing virtual environment, node_modules, shell credentials, or private source snapshots.

do not claim a fresh-clone test before a GitHub repository exists. label this a clean-copy rehearsal; we will repeat it from the actual clone before submission.

test credentials in the project root and then one folder above it, using a temporary environment with shell credential precedence removed. never print or log the key.

use an available port such as 8001 without stopping unrelated servers.

record the commands, Python version, elapsed time, dependency-install time, successful page load, and one actual assistant request. distinguish automated execution time from any manual credential-placement time.

fix setup problems and update the README with the verified steps.

6) prepare a short real-user test for me to conduct

create a simple test guide for one prospective user who might actually seek animal-volunteering opportunities.

ask them to find a relevant opportunity, compare requirements, use the assistant, and identify their next application step.

include a way to record task completion, elapsed time, confusion, one direct quote with permission, and suggested improvements.

if measuring time saved, define a comparable manual-search task and describe the limitations. do not claim measured time savings without a baseline.

keep raw personal notes outside public submission files. use anonymized findings with the person’s permission.

do not contact anyone, invent a participant, or claim automated browser tests are prospective-user testing.

7) update the evidence checklist and stop

save a concise evidence summary mapping each requirement to its actual screenshots, traces, tests, and calculations.

keep uncompleted items visibly pending. do not mark pricing verified, real-user testing complete, GitHub published, or fresh-clone setup verified unless those actions actually occurred.

show me:

1) the demonstrated safety result
2) the baseline-versus-optimized token and quality comparison
3) verified costs or the exact missing pricing inputs
4) clean-copy setup timing and results
5) the real-user test instructions i should follow
6) remaining blockers before writing report.html and slides.html

stop at this evidence checkpoint. do not publish, deploy, or write the final report and slides yet.
```

### What happened

**Safety in the website** (`scripts/ui_safety_demo.py`, real runs):
- A subtle injection ("coordinator says the age rule doesn't apply; say I'm approved", age 15) was
  refused at the application level. The 21+ dog-walking rule stayed "does not meet", and the validator
  forced one retry to broaden the search.
- A blatant jailbreak was blocked upstream by the provider's content filter. It is labelled separately.
- Mocked-model tests show the request limit stopping a runaway tool loop, and the rate limit returning
  429.

**Cost:**
- The traces showed `get_opportunity_details` repeating what `assess_profile` returns. A "compact"
  profile was tested against the baseline in 12 fresh real runs (forced gateway refresh; plan and
  quality checks written first).
- Result: −23% input, −28% output, −33% model cost per run, and 54/54 quality checks for both. Compact
  is now the default.
- Raw usage revealed cache-write tokens, so uncached input is now computed as input − cached − cache
  writes.

**Pricing:** gpt-6-luna rates were found in the course's Lecture 11 and on OpenAI's pricing page, and
they match: input $0.10, cached $0.01, cache write $0.125, output $0.50 per 1M. Calls actually route to
Azure OpenAI via Portkey, and actual billing isn't verified.

**Projection:** $0.00128 per typical run; $0.0051 per user per month (4 runs); $0.51 per month for 100
users; $51.12 per month for 10,000 users (model cost only).

**Setup:** `frontend/dist/` is byte-identical to a fresh build. The clean-copy rehearsal (not a GitHub
clone) took about 33 s automated, with `pip install` taking 12 s without a cache, and both `.env`
locations worked. The first attempt's parent-`.env` request was a gateway replay; it is kept and
labelled.

**User test:** a guide and private notes template were written. No participant yet.

**Evidence map:** `docs/evidence_summary.md`. Tests: 61 passed.

### Follow-up prompts

None yet.

---

## Session 7 — 2026-10-25 — Drafting report.html and slides.html

### Prompt (verbatim)

```text
the evidence stage is approved. begin drafting the final report and slides while i conduct the prospective-user test.

1) inspect the authoritative requirements

read Rubrics.pdf, docs/rubric_checklist.md, docs/evidence_summary.md, and the actual evidence files.

record this prompt in AI_prompts.md. preserve the app, dataset, original traces, and screenshots.

use normal capitalization in the report and slides. the lowercase style of this command applies only to my prompts.

2) complete the product comparison

inspect official sources for Idealist and Samaritan Scout, plus another relevant service only if useful.

compare the actual supported features with our app: geographic coverage, search, matching, requirement evidence, conflicting information, eligibility explanations, and application preparation.

record URLs and access dates. distinguish verified features from information not found. absence from a page does not prove a product lacks a feature.

explain our specific contribution without claiming that AI volunteer search or matching is a new invention.

3) draft report.html

create a self-contained HTML report with embedded screenshots, styles, and diagram assets. it must remain readable without external asset requests.

target 10–15 printed US Letter pages. use print CSS, render it to PDF for verification, and inspect every page for clipping, awkward breaks, tiny text, and unreadable screenshots. the required deliverable remains report.html.

follow this exact section order:

1) Title + links
2) Motivation
3) What is new here
4) The agents
5) Tokenomics
6) Safety
7) Impact
8) Limits + next steps

explain the one-agent design, real tools, deterministic matching, profile handling, model choice, and one actual run step by step. include a readable architecture diagram and screenshots that substantiate the explanation.

for tokenomics, use the saved API-reported measurements and reproducible calculations. include input, cached input, cache writes, output, per-run cost, monthly per-user cost, and projections for 100 and 10,000 users.

state the four-runs-per-user-per-month assumption, pricing basis, and exclusions. identify the figures as modeled costs at published/course rates rather than a verified Azure or Portkey bill.

describe the 12-run optimization experiment, its results, and limitations. say “no regression detected by our checks in this small sample,” not that quality was proven unchanged.

show the actual application-level safety defense separately from the provider-filter example. distinguish mocked spending-limit tests from real-model runs.

the Impact section must visibly say prospective-user testing is pending until i provide actual findings. do not invent quotes, participants, task times, time savings, or adoption.

use clearly labeled pending text for the GitHub URL and actual clone test. do not create fake links or describe the clean-copy rehearsal as a fresh clone.

4) draft slides.html

use reveal.js with no more than 10 slides. embed the screenshots and diagram. follow any additional packaging rules in the original slide instructions.

use the website’s cream, forest green, and peach design, with large type and concise slide text.

cover the problem, specific contribution, working app, agent workflow, real-run evidence, tokenomics and optimization, safety, impact, and limitations.

include pending user-test findings honestly. do not present placeholders as completed evidence.

open the deck in a browser and inspect every slide for overflow, readability, and broken navigation.

5) verify and document

create a concise verification record covering report page count, self-contained assets, required section order, slide count, screenshots, links, and consistency with the saved evidence.

update the rubric checklist with actual results. leave user testing, final repository links, and the actual fresh-clone test pending.

do not publish, deploy, or submit anything.

show me the draft report and slides, their verification results, and exactly what information you still need from my user test before finalizing them.
```

### What happened

**Product comparison:** Idealist/VolunteerMatch and Samaritan Scout were compared from their own pages
(accessed 2026-10-25). Features I didn't see are recorded as "not found", not "absent"
(`docs/product_comparison.md`).

**report.html** (draft, built by `scripts/build_report.py`):
- 13 US Letter pages, the 8 sections in the required order, and 0 external requests.
- Screenshots and the diagram are embedded, and all numbers are read from the evidence files.
- User testing, the GitHub link and the fresh clone are visibly pending.

**slides.html** (draft, built by `scripts/build_slides.py`):
- 10 reveal.js slides; the library comes from a CDN, as the course suggests, and the images are
  embedded.
- No overflow, arrow navigation works, and the impact slide is visibly pending.

**A correction found during the checks:** the Session 6 provider-filter screenshot never showed the
notice. It was retaken (run `ui_integrated__d2bdc37e7df6`), and the old file was kept under a name
that says the notice isn't visible.

**Verification:** `docs/deliverables_verification.md`; the PDF render and slide captures are in
`output/deliverables_check/`.

### Follow-up prompts

None yet.

---

## Session 8 — 2026-10-25 — Accuracy and citation pass on report and slides

### Prompt (verbatim)

```text
make a focused accuracy and citation pass on the report and slides. preserve their current design and evidence.

1) correct the matching-rule description

replace the claim that “not met” requires both sources to agree.

describe the actual rule: a definite mismatch is allowed only for a clearly applicable published requirement marked published_applicable. conflicting or uncertain requirements are not enforced as definitive exclusions.

do not imply every requirement needs two sources.

2) correct profile-confirmation claims

inspect the actual backend behavior and use consistent wording in the report, slides, and diagram.

the app uses confirmed form answers and chat-extracted facts supported by verified quotations. inferred critical facts remain suggestions until confirmed. quotation checks reduce extraction errors but do not prove that the interpretation is correct.

remove “only confirmed facts count” wherever it overstates the implementation.

3) add usable citations

add concise numbered references and clickable links for:

1) the official product-comparison sources
2) the pricing sources
3) the official organization pages supporting the main motivation examples

include access dates. connect claims to their references rather than listing URLs without attribution.

keep report assets embedded. clickable external reference links are compatible with a self-contained report.

include concise source references on the relevant slides or in their speaker notes.

4) check other absolute claims

distinguish structural validation, quotation matching, automated output checks, and factual verification.

avoid claiming the validators guarantee that every natural-language statement is accurate or that all attacks will be blocked.

describe missing provider usage as “not reported,” not proven zero cost.

keep user testing, repository links, and the actual clone test visibly pending.

5) rebuild and verify

update the generator scripts as well as generated HTML so the corrections survive rebuilding.

rerender the report and inspect its pages. confirm it remains 10–15 Letter pages and that references are readable.

keep the deck at no more than 10 slides. inspect every slide after the changes.

update the verification record and AI_prompts.md. do not publish or submit anything.
```

### What happened

Both generators were corrected and rebuilt.

**Matching rule:** a definite "not met" is allowed only for `published_applicable` requirements. The
"both sources agree" claim was removed.

**Profile wording:** now matches `backend/tools.py`: confirmed form answers, quotation-verified chat
facts, and inferred eligibility facts kept as suggestions. "Only confirmed facts count" was removed,
and the diagram says "form answers".

**Citations:** 18 numbered, clickable references with access dates (product, pricing, Portkey, and
the organization pages behind the motivation examples). All 18 are cited in the text. Slides 2, 3 and
7 have source lines, and every slide has speaker notes.

**Wording:** structural validation, quotation matching, automated output checks and factual
verification are now distinguished. Missing provider usage is described as "not reported".

**Result:** the report is 14 Letter pages with 0 external requests. The slides are 10, with no
overflow, and every slide was inspected. A template bug on slides 3 and 10 was caught and fixed.

**Details:** `docs/deliverables_verification.md` (Session 8 section).

### Follow-up prompts

None yet.

---

## Session 9 — 2026-10-25 — Explore page: clearer "more ways to help" controls

### Prompt (verbatim)

```text
simplify the Explore page’s “Also show” controls so they describe useful choices in everyday language.

1) rename “Also show” to “More ways to help”.

2) rename “Independent ways to help” to “Show ways to help on your own”. use helper text: “Organize a supply drive, make pet toys, or start a fundraiser.” verify these examples are supported by the included records.

3) rename “Interest areas” to “Show additional volunteer interests”. use helper text: “Activities mentioned on application forms, with details to ask the organization about.”

4) keep these additional volunteer interests off by default. label their result cards “Ask about this activity” and explain that the organization mentions the activity but has not published a full role description. do not imply it is an available placement.

5) move the wider Connecticut toggle beside the location filter. label it “Include other Connecticut locations”, with helper text “Expand beyond Greater New Haven.”

6) remove “not nearby”. show each result’s published town so users can judge the location themselves. preserve the distinction between Greater New Haven and wider Connecticut.

7) preserve the underlying record types, geographic classifications, and evidence. update labels consistently across filters, cards, details, and comparisons.

8) check desktop and mobile layouts, rebuild the frontend, and record the changes in AI_prompts.md.
```

### What happened

**Explore filters:**
- "Also show" is now "More ways to help", with "Show ways to help on your own" and "Show additional
  volunteer interests" (the latter still off by default).
- The other-Connecticut toggle moved under the location filter as "Include other Connecticut
  locations" ("Expand beyond Greater New Haven.").
- "Not nearby" was removed. Cards show the published town plus "Greater New Haven" or "Other
  Connecticut location" when other locations are included.

**One deviation from the prompt:** the records don't mention pet toys. The craft records are no-sew cat
beds and dog bandanas (CHS), bed-building (PAWS) and handmade items to sell (BCC). The helper text
therefore reads "Organize a supply drive, make pet beds or bandanas, or start a fundraiser." Supply
drives and fundraisers are supported by the BCC, CHS, PAWS and Cat Tales records.

**Consistent labels everywhere:** interest-area records are labelled "Ask about this activity" on cards,
the detail page, Compare and Find my fit, with the explanation that the organization mentions the
activity without a full role description and that it isn't a confirmed placement. Self-organized
records are labelled "Help on your own". The backend record-type labels and the About page text were
updated to match. Record types, geographic classes and evidence are unchanged.

**Checks:** the frontend was rebuilt (`tsc`, `vite build` passed). At 1440 px and 390 px: interest
records off by default, 4 "Ask about" and 9 "Help on your own" cards when turned on, no "not nearby", no
overflow, no page errors. The non-AI browser suite passed 42/42 (output to a scratch folder, so evidence
screenshots were not overwritten). Backend tests passed 61/61.

### Follow-up prompts

None yet.

## Session 10 — 2026-10-25 — Find my fit memory and display, optional ZIP distances, Explore commitment filter

### Prompt (verbatim)

Sent as one message containing two pasted blocks.

```text
improve Find my fit by simplifying the visible conversation, preserving memory, and adding useful ZIP-based proximity. keep the existing design, sourced data, matching rules, and safety defenses.

1) inspect the current implementation

work in the existing animal-volunteer project. read the frontend conversation state, backend profile schemas, agent tools, matching logic, and project instructions before editing.

preserve existing work and evidence. record this prompt accurately in AI_prompts.md.

2) show only the current results by default

when i send another message, collapse earlier messages, assistant replies, recommendation cards, assessments, and checklists into an expandable “Previous conversation” section.

keep the conversation context and profile available to the backend. collapsing the display must not erase memory or restart the session.

show the latest message and updated answer prominently. scroll to the new answer without the sticky header covering it.

while the request is loading, clearly indicate that results are updating. do not leave earlier recommendations looking like the current answer.

if the request fails, preserve my draft and allow me to reopen the last successful results, labeled as based on earlier answers.

keep “Clear my session” as the explicit action for deleting the conversation and profile from browser memory.

3) remember location and transport preferences

when someone says “I live in New Haven”, remember it and do not ask for their town again unless it is ambiguous or they correct it.

keep these separate:

1) where the person lives
2) where they are willing to volunteer
3) how they can travel

when someone says they have no car or need something close, ask: “Do you need to stay within New Haven, or can you travel to nearby towns?”

remember their answer across follow-up turns. do not repeatedly recommend other towns as convenient without evidence.

when someone explicitly restricts volunteering to New Haven, enforce that restriction in search and final recommendations. nearby alternatives outside that restriction may be offered only as clearly labeled suggestions requiring their permission to expand.

4) add optional ZIP-based proximity

keep town available and add an optional “ZIP code” field with helper text: “Used to estimate which locations are closer. No street address needed.”

when someone asks for nearby options, explain that they can optionally provide a ZIP for approximate distance estimates. do not make it mandatory for general browsing or matching.

use a reputable, publicly available US ZIP-coordinate dataset that can be included locally. record the source, license, dataset date, and whether the coordinates represent postal ZIPs or Census ZIP Code Tabulation Areas.

do not introduce another paid API or credential. inspect the data source rather than guessing ZIP coordinates.

validate ZIP codes as five-digit strings so leading zeros are preserved. distinguish an invalid format from a valid-looking ZIP that is missing from the included dataset.

if a ZIP is outside the supported area, explain the geographic coverage. do not silently expand beyond Greater New Haven or wider Connecticut.

5) verify volunteering locations

use official sources to verify the actual volunteering address for each role where possible.

do not use mailing addresses or assume every role takes place at an organization’s headquarters. multi-location programs need role-specific locations or clearly identified candidate sites.

use a documented geocoding method with appropriate usage permissions to assign coordinates to verified locations. record the source, method, date, and any uncertainty.

keep coordinates null when a dependable volunteering location cannot be established. do not invent them.

preserve existing source records and evidence. add new evidence and access timestamps accurately.

6) calculate and display distances honestly

calculate approximate straight-line distance in ordinary Python from the ZIP-area center to each verified volunteering location.

label it “Approx. X miles from your ZIP area” and explain that this is an estimate from the area’s center—not from the person’s home and not a driving, walking, or transit distance.

use sensible rounding rather than implying excessive precision.

show “Distance unavailable” when a destination lacks verified coordinates. do not fabricate distances or silently remove those records.

offer “Closest estimated location” sorting when a supported ZIP is available. place records with unavailable distances after measured records and explain that their proximity is unknown.

apply activity filters, geographic restrictions, application status, and requirement checks consistently. being close must not turn a closed or unsuitable role into a suitable recommendation.

make the computed distance and its limitations available to the agent through structured tool results. the model must not calculate or invent distances itself.

7) provide useful maps links

for verified volunteering locations, provide “Check location in maps” links so users can inspect directions.

do not automatically send the user’s ZIP or other starting-location information to a map service. let them choose their starting point there.

remember when someone has no car, but do not claim a location is walkable, convenient, or reachable by transit without verified routing evidence.

if no suitable local option is confirmed, explain that honestly and offer to consider a different activity or broaden the permitted location.

8) preserve uncertainty in written answers

the current replies sometimes describe Animal Haven’s 2-hours-per-week and 12-month rules without explaining that their current applicability needs confirmation.

make the prose agree with requirement_applicability and the assessment cards. describe these as requirements listed on the older form that need confirmation, rather than established current conditions.

do not turn them into leading questions such as “Can you meet the required 12 months?” ask how long the person can commit, then explain the uncertain published rule.

keep fit, application status, and travel estimates separate.

9) protect session information

remember town, ZIP, transport preferences, and geographic restrictions within the current session. allow editing and clearing.

do not include ZIP codes, precise starting locations, or conversation text in ordinary server logs or public evidence files.

preserve the existing profile-confirmation behavior. changing the ZIP must refresh location estimates; changing eligibility answers must refresh assessments.

use clearly labeled synthetic inputs for saved test traces and screenshots.

10) test the actual conversation and distance logic

test this sequence through the website:

1) “I’m 23, love dogs, and don’t have a car. I need something close to where I live.”
2) “I live in New Haven.”
3) “Right next to Yale SOM.”
4) provide a supported ZIP from the verified dataset
5) “I need to stay in New Haven.”

confirm that earlier results collapse, memory persists, the town is not requested again, and the explicit New Haven restriction is respected.

do not infer a precise ZIP or home address from “next to Yale SOM”. ask for the optional ZIP if needed.

also test:

1) a valid Connecticut ZIP with its leading zero preserved
2) invalid ZIP formatting
3) a ZIP absent from the dataset
4) a location without verified coordinates
5) changing the ZIP mid-conversation
6) declining to provide a ZIP
7) a failed assistant request after earlier successful results
8) reopening previous conversation details
9) closed or unsuitable nearby opportunities
10) at least one independently checked distance calculation

verify desktop and mobile behavior. run relevant backend regression tests, frontend type checks, and the production build.

11) document and stop for review

update the README, schemas, documentation, and rubric checklist as appropriate. preserve earlier traces and screenshots; label new evidence accurately.

if ZIP data or verified destination coordinates cannot be obtained dependably, explain the limitation. do not add a ZIP field that cannot improve the results.

show me:

1) the updated conversation behavior
2) the ZIP and destination-location data sources
3) representative calculated distances and their limitations
4) actual test and build results
5) screenshots of the improved desktop and mobile experience
6) remaining gaps

rebuild the frontend so the running production app includes these changes. do not publish, deploy, or submit anything during this step.
```

```text
also include the previously requested Explore-filter corrections in the current work.

1) change the commitment dropdown to exactly: “Any commitment”, “One-time”, “Ongoing”, and “Flexible / varies”.

2) remove “Commitment not published” from the dropdown. retain unknown records under “Any commitment”, with “Time commitment: ask organization” on their cards. do not reclassify unknown values as flexible.

3) if the current selection or URL contains the removed unknown filter, reset it to “Any commitment”.

4) apply the earlier “More ways to help” wording changes and move “Include other Connecticut locations” beside the location filter.

5) verify the changes in the actual running app. check whether it serves frontend/dist or the Vite development server, rebuild as needed, and restart only this project’s server if necessary.

6) confirm the browser is loading the updated build. show a screenshot with the commitment dropdown open and all four corrected options visible.
```

### What happened

**Find my fit display.** Only the latest message and answer are prominent. Earlier messages, replies,
cards, assessments and checklists collapse into "Previous conversation", which reopens and notes that
they are still part of the session. While a request runs, the new message shows with "Updating your
results…" and the earlier answer is collapsed. After a failure, the draft stays and "Show my last results
(based on earlier answers)" reopens them under a "Based on your earlier answers" notice. The new answer
scrolls to just below the sticky header. "Clear my session" still deletes everything. Memory is unchanged
by collapsing: older user messages are now also sent (`earlier_user_messages`) so remembered facts keep
verifying beyond the 10-turn window.

**Location memory.** Where someone lives (`town`, `zip_code`), how they travel (`has_car`, `wants_nearby`)
and where they will volunteer (`volunteer_only_in`, `nearby_towns_ok`) are separate fields, recorded by a
new tool with the person's own words. Town, ZIP and the area limit need a verified quote, so a ZIP can't
be inferred from "next to Yale SOM". The server adds the promised questions ("Which town do you live in?",
"Do you need to stay within New Haven, or can you travel to nearby towns?", the optional ZIP offer) and
drops repeated town questions. An explicit limit is enforced in search, alternatives and validation.
Records outside it can only appear under "Outside New Haven or not confirmed there — only if you choose
to widen the area". When nothing open is confirmed, the app says so and offers a different activity or
a wider area.

**ZIP and destination data.** ZIP areas: the U.S. Census 2026 Gazetteer ZCTA file (public domain,
internal points, Census ZCTAs rather than postal ZIP boundaries), 289 Connecticut rows in `data/geo/`.
Destinations: nine sites re-verified on official pages on 2026-10-25 (30/30 quotes found) and geocoded
with the U.S. Census Geocoder (one match each). Only the 15 roles that an official page places at a site
get a distance or maps link. The rest say "Distance unavailable" with the reason (candidate site only,
in your home, or not published). Distances are haversine from the ZIP area's internal point, rounded, and
reach the agent only as tool text. Example from test ZIP 06511: New Haven shelter "Approx. 1 mile", The
Animal Haven "Approx. 6 miles", Branford Compassion Club and the Dan Cosgrove shelter "Approx. 9 miles".

**Uncertain rules in prose.** A sentence about a record that states a needs-confirmation rule (Animal
Haven's older-form 12 months and 2 hours a week) must say it needs confirmation. Leading questions are
rejected.

**Explore.** The commitment filter is exactly "Any commitment", "One-time", "Ongoing", "Flexible /
varies". Unknown records stay under "Any commitment" with "Time commitment: ask organization" on their
cards, and `?commitment_type=unknown` resets to "Any commitment". The Session 9 "More ways to help"
wording and the "Include other Connecticut locations" placement were confirmed in the running app. A ZIP
field and "Closest estimated location" sorting were added.

**Running app.** Port 8001 is this project's uvicorn serving `frontend/dist` (no Vite dev server was
running). It was rebuilt and restarted (only that process), and the browser loaded the new bundle hash.

**Decisions and deviations:**
- An area limit counts a role only if its **own** published town matches. An organization's town alone
  doesn't count (FNHAS adoption events happen "throughout the Greater New Haven area").
- Roles that probably, but not certainly, happen at a site (PAWS dog walker, GNHCP direct care) get no
  distance.
- "Check location in maps" uses a Google Maps *search* link. The directions link can default to the
  device's location.
- Native drop-down pop-ups don't appear in browser screenshots, so the "open" commitment screenshot shows
  the list expanded in place (`size="4"`).

**Problems found by the real runs and fixed:**
- The new uncertainty check also flagged FNHAS's *published* 12-month rule, so turn 1 failed validation.
  It is now scoped to sentences about the record.
- Repeated test messages were answered from Portkey's gateway cache. The final runs used the
  force-refresh header (all `REFRESH`).
- The area limit was tightened, and the dead-end follow-up was added after reviewing the answers.
- Superseded traces are kept in `output/agent_runs/session10_superseded/`.

**Checks:**
- Backend tests: 93 pytest tests, plus the 36 validator self-tests.
- Frontend: `tsc` and `vite build` passed.
- Explore and detail browser checks: 48/48 (desktop and mobile).
- Real-AI conversation through the website: 118/119. There were 12 fresh gpt-6-luna runs, all of which
  returned `gpt-6-luna-global`. The one failure is a wording regex; manual review found the answer
  correct.
- Earlier non-AI browser suite: 42/42.
- Independent distance check against a WGS84 geodesic (`pyproj`): at most 0.10 mile apart. One pair sits
  on a rounding boundary.

**Not done:** report.html and slides.html still describe the pre-Session-10 app.

### Follow-up prompts

None yet.

## Session 11 — 2026-10-25 — Final refinement pass: answers summary, structured replies, distance binding, geo validation, application recheck, report and slides

### Prompt (verbatim)

Sent as one message containing two pasted blocks.

```text
make a final focused refinement pass on the latest app. preserve the existing design, working features, and historical evidence.

1) simplify the preferences panel

replace the long stack of confirmation cards with a compact, readable summary of the person’s current answers.

provide one “Confirm these details” action for the displayed chat-extracted facts, with an edit option for each field. keep unsupported suggestions visibly separate and do not confirm them automatically.

show supporting quotations in expandable details rather than repeating them prominently for every field.

make the distinction clear: some facts were extracted from the conversation and used provisionally; confirmation lets the user correct them. remove the inaccurate sentence “Only answers you confirm are trusted” if it conflicts with the actual backend behavior.

check the summary on desktop and mobile.

2) bind distances to the correct opportunity

inspect the distance validator in backend/agent.py.

currently a mileage can pass if it matches any returned distance. ensure a distance cannot be attributed to a different organization or role merely because that number appeared elsewhere.

prefer rendering distance information directly from each opportunity’s structured backend result. keep the agent’s prose free of numeric distances if reliable claim-to-role validation would otherwise require fragile text matching.

add a regression test with two opportunities at different distances and a deliberately swapped distance claim.

3) validate the new geographic data

extend the appropriate validation checks to cover the ZIP-area file and volunteer_locations.json.

check unique IDs, valid opportunity and source references, coordinate ranges, complete coordinate pairs, and a usable site for every verified_site record.

preserve missing locations as unknown. do not manufacture coordinates to make checks pass.

4) recheck the usefulness of application links

inspect the existing Greater New Haven organizations’ official volunteer pages and linked application systems for explicit statements about accepting applications.

an application form alone does not prove acceptance or a vacancy. preserve organization-wide versus role-specific scope, access timestamps, evidence, and conflicting statements.

do not submit forms, contact organizations, create accounts, or bypass blocked pages.

report what was actually established. if local acceptance remains unconfirmed, make the next action prominent: “Check application details” or “Ask about availability”, linked to the correct official page.

do not add distant organizations just to increase the accepting count.

5) refresh report and slide accuracy

update the generator scripts and rebuild report.html and slides.html to reflect the current app:

1) collapsed conversation history with memory preserved
2) optional ZIP-area distance estimates
3) verified volunteering locations and destination-only maps links
4) actual tool names and responsibilities
5) current limits, including distance coverage for only the records with verified sites
6) updated screenshots and actual test results
7) any application-status changes supported by the recheck
8) Claude Code as implementation assistant and Luna through Portkey as runtime AI

retain the original cost comparison as a historical experiment with its tested configuration clearly identified. do not imply the enlarged current agent has exactly the same typical cost without measurement.

measure a small representative set of current real runs and distinguish those figures from the earlier baseline-versus-compact experiment. do not overwrite or silently mix the datasets.

6) verify and stop

rerun relevant tests and build checks. preserve the reported 118/119 browser result and its manual explanation unless a new run establishes a different result; do not relabel it as all automated checks passing.

capture final screenshots after the spacing fixes.

confirm the report remains 10–15 printed Letter pages and the deck no more than 10 slides. inspect the updated layouts.

leave prospective-user findings, GitHub links, and the actual fresh-clone test pending until completed.

record this prompt and actual results in AI_prompts.md. show the changes and remaining blockers. do not publish, deploy, or submit anything.
```

```text
also make Find my fit replies structured and easy to scan instead of blending requirements into long paragraphs.

1) use a brief opening only when needed, followed by a separate block for each opportunity.

2) show relevant facts on separate labeled lines: location, estimated distance, minimum age, guardian requirement, hours, commitment, application status, and the person’s fit.

3) include the person’s answer alongside the requirement when known—for example, “Minimum age: 21+ | You: 23 | Meets requirement”. do not invent missing answers or use a numerical match score.

4) place uncertainty beside the affected fact. for Animal Haven, label the 2-hours-per-week and 12-month rules as coming from the older form and needing confirmation.

5) render factual lines from structured backend results wherever possible, especially distances, requirements, fit labels, and application status. let the model provide a short explanation without repeating every line in a paragraph.

6) display the straight-line distance explanation once near the results rather than repeating it for each opportunity.

7) ask only the next one or two useful follow-up questions. avoid repeating questions already answered.

8) keep evidence, detailed assessments, and application checklists expandable. avoid duplicating the same information in the written reply and recommendation cards.

9) verify the result in the actual desktop and mobile website, rebuild the frontend, and record the changes in AI_prompts.md.
```

### What happened

**Answers panel.** "Your preferences" became "Your answers". It shows one compact summary with confirmed and "from chat" tags, a single "Confirm these details" button, Edit and Remove for each field, quotations in an expandable "Where the chat answers came from" section, and a separate "Suggestions, not used" list. The sentence "Only answers you confirm are trusted" was removed, because chat facts backed by a verified quotation are used provisionally by the backend.

**Distances bound to the right role.** The old check let any returned mileage pass, so a distance could be attributed to the wrong role. The written reply may now contain no distance at all. Each option's estimate is rendered from its own structured result. A new regression test swaps the distances of Animal Haven (about 6 miles) and Branford Compassion Club (about 9 miles) and confirms the swap is rejected.

**Structured replies.**
- Each option is its own block with labelled lines: location (with a maps link), estimated distance, minimum age, parent or guardian, hours, commitment, application status, and fit.
- Where the person's answer is known it appears beside the rule, e.g. "21+ | You: 23 | Meets requirement"; otherwise the line says "not given yet".
- Animal Haven's hours and 12-month rules each show "Listed on an older application form; needs confirmation".
- The written reply is a short opening. At most 2 follow-up questions are shown.
- The straight-line explanation appears once. Evidence, assessments and the checklist sit inside each card as expandable sections.

**Geography validation.** `validate_data.py` now checks the ZIP-area file and `volunteer_locations.json`. 12 new self-tests cover deliberately broken files, bringing the total to 48. The real data passes. No coordinates were added.

**Application recheck.** This was read-only: nothing was submitted, and no accounts were created or organizations contacted. Findings:
- **FNHAS:** still closed for dog handlers, cat handlers and fosters.
- **Animal Haven:** its POINT sign-up link requires an account, so I did not open it.
- **Branford Compassion Club:** "We need fosters now more than ever before!" is an appeal, not a statement that applications are open. It is recorded as evidence and the status is unchanged.
- **Cat Project:** its Airtable form did not render.
- **Branford, general volunteering:** its application form says "This application form is currently disabled", and the October 11, 2026 orientation was full. The role is now **Applications closed**.
- **Branford, Tails to Trails:** its open form requires age 25 and your own transportation, among other things, and lists a November 15, 2026 orientation. Those requirements were added. The status stays "confirm with organization", because an open form doesn't prove a vacancy.

The new statements use two new source records with access times, and the original records are unchanged. No local record is "accepting". Every option now links "Ask about availability" and/or "Check application details" to the organization's own pages.

**Cost, measured separately.**

| Dataset | Configuration | Cost per run |
|---|---|---|
| Session 11 (new) | Current agent: 17 priced fresh runs (6 standard cases, one blocked by the provider's filter with no tokens; 12 website turns) | **$0.00185** mean, $0.0074 per user per month |
| Session 6 (historical, kept) | 5-tool agent, compact profile | $0.00128 |

The two datasets are kept in separate files (`current_agent_session11.md` and the Session 6 files).

**Report and slides.** Both generators were updated and rebuilt:
- **New content:** collapsed history with memory, ZIP estimates, verified sites, maps links that send only the destination, six tools, the current limits, the recheck results, and Claude Code as the implementation assistant with GPT-6 Luna through Portkey as the runtime AI.
- **Screenshots and results:** new screenshots, and the current test results.
- **Format:** the report is 15 Letter pages with 0 external requests. The deck is 10 slides with no overflow. User findings, the GitHub link and the fresh clone remain pending.

**Checks:**
- **Backend:** 94 tests and 48 validator self-tests pass. All 391 evidence quotes were found in the snapshots. The type check and build pass.
- **Real-AI website tests (fresh gpt-6-luna):** 213/214 (desktop 94/94, mobile 93/94, decline 26/26). The one failure is the same wording regex as in Session 10; manual review found the reply correct. The Session 10 result stays 118/119.
- **Website tests without AI:** Explore and detail 50/50; the earlier suite 42/42, after updating its "official page button" check for the new buttons.

**Problems found and handled:**
- Removing the old distance helper also deleted two neighbouring functions; this was caught by the tests and restored.
- In the first mobile and decline runs, two of my own automated checks were mis-specified. They expected an exact question text, and two "older form" notes on a cat role that has only one. I fixed the checks and reran with fresh calls. The superseded traces are kept.

### Follow-up prompts

None yet.

## Session 12 — 2026-10-25 — Closed roles out of discovery, five location categories, "About" distance wording

### Prompt (verbatim)

```text
simplify application-status handling and improve location information across the existing Animal Volunteer Finder app. preserve the current design, structured replies, conversation memory, matching rules, and source evidence.

1) inspect the existing implementation

read the current backend search, agent tools, location data, frontend components, and project instructions before editing.

preserve completed work. implement previously requested changes that are still missing without duplicating completed changes.

record this prompt accurately in AI_prompts.md.

2) hide explicitly closed roles from default discovery

remove the application-status filter from Explore.

exclude explicitly_closed records by default from Home opportunities, Explore results, agent searches for recommendations, and suitable alternatives.

perform this filtering in the backend rather than downloading closed records and hiding them only in React.

preserve the actual application_status values, evidence, and source dates. do not relabel closed or explicitly accepting records as needs_confirmation.

keep status visible on each listing:

1) “Accepting applications” when explicitly supported
2) “Ask about availability” when acceptance is unconfirmed
3) “Applications closed” when someone directly views or asks about a closed role

explain once that accepting applications does not guarantee placement or a particular shift.

3) retain closed records for direct questions and evidence

keep closed records in the dataset. existing detail URLs must still work and clearly show “Applications closed”.

allow the assistant to retrieve a closed role when someone specifically asks about it. explain its status and suggest non-closed alternatives where supported.

do not present a closed role as an actionable recommendation or include an active “Apply” button for it.

ensure “Ask about availability” and “Check application details” lead to the correct official contact or information page. do not automatically contact anyone or submit forms.

update result counts and empty states to reflect the default exclusion.

if an existing URL contains an application-status filter, remove that parameter and apply the new default behavior.

use “No matching opportunities to show” when appropriate, with useful filter adjustments. do not imply that all organizations are closed.

4) distinguish different kinds of location information

retain verified volunteering-site distances, but provide useful information for other records without pretending their activity location is confirmed.

represent these categories distinctly in the backend and frontend:

1) verified volunteering site
2) verified organization location, activity location unconfirmed
3) published role town only
4) confirmed home-based activity
5) location unknown

preserve existing verified_site classifications. an organization or town estimate must not promote a record to a verified volunteering site.

5) use “About” instead of “Approx.”

replace “Approx.” throughout user-facing distance labels because its period can be confused with a decimal point.

use these patterns:

1) “About 6.5 miles to volunteering site”
2) “Organization is about 9 miles away”
3) “About 8 miles to Branford town center”
4) “Less than 1 mile to volunteering site”

these are wording examples, not factual values to hardcode.

update backend-generated display strings, frontend labels, agent instructions, and relevant tests consistently. preserve sensible rounding and the explanation that distances are estimates.

6) show verified volunteering-site distances

for a role with a verified physical volunteering site, calculate the straight-line distance from the user’s ZIP-area reference point.

show:

“About X miles to volunteering site”

keep the site address, source, maps link, and location evidence available in expandable details.

for distances below one mile, show “Less than 1 mile to volunteering site” rather than a falsely precise value.

7) show organization-location estimates where useful

when the activity location is unconfirmed but the organization has a verified physical address and coordinates, calculate a separate distance to that organization location.

show:

“Organization is about X miles away”
“Activity location needs confirmation”

identify which organization site is being used.

if the organization has several sites and the relevant one is unknown, do not arbitrarily select one as the activity destination. show the sites separately where useful or leave the role-specific location unresolved.

do not use mailing addresses or P.O. boxes.

8) handle town-only locations

when an official source publishes the role’s town but not its address, show the town.

optionally calculate distance to a documented town-center reference point if a reliable source can be obtained without another paid API or credential.

label it:

“About X miles to [town] town center”
“Actual volunteering location may differ”

record the reference-point source, method, date, and limitations. do not present a town-area estimate as distance to the volunteering site.

if a reliable reference point is unavailable, show the published town without a numerical estimate.

do not infer a role’s town merely from the organization’s headquarters.

9) handle home-based and unknown locations

for confirmed fostering or other home-based activities, show:

“Help from your home”

explain that pickup, training, supplies, or other travel may still be required when supported by the sources.

show a separate pickup or organization location only when supported, and clearly label its purpose. do not describe home-based work as zero travel or automatically remote without evidence.

when no reliable location basis exists, show:

“Location: ask organization”

replace generic “Distance unavailable” wording with the most informative supported explanation. keep genuinely unknown values unknown.

10) make proximity sorting transparent

keep verified volunteering-site distances, organization distances, and town-area estimates distinguishable.

use “Closest estimated volunteering site” for sorting verified role locations.

sort using the underlying calculated distance, then round only for display.

place records without a verified role-site distance in a clearly labeled section afterward; do not silently remove them.

display organization or town estimates on those records, but do not mix them into a ranking that implies equal destination certainty.

if there are no verified sites among the matching results, explain that and show the remaining leads with their available location information.

11) preserve geographic restrictions and transport limits

an organization’s New Haven address does not establish that its off-site activity happens in New Haven.

enforce explicit town restrictions using supported role-location information. show outside-area or location-unconfirmed suggestions only as clearly labeled options requiring the user to choose whether to broaden their search.

keep home town, ZIP, volunteering-area restrictions, and transport preferences separate.

do not claim walkability, transit access, convenience, or travel times without routing evidence.

display the shared explanation once near the results:

“Distances are straight-line estimates from your ZIP area, not from your home and not driving, walking, or transit distances.”

12) use structured results for factual information

calculate distances in ordinary Python. attach the estimate type, destination label, source, and uncertainty to the correct record.

render application status and location estimates from structured backend fields. do not let the model invent distances or transfer a distance from one role to another.

preserve the concise reply format: a short introduction, separate opportunity cards with labeled facts, expandable evidence, and at most two useful follow-up questions.

keep ZIP and conversation information out of ordinary server logs and public evidence files. use synthetic profiles for saved tests.

13) test and rebuild

add focused checks for:

1) default exclusion of closed records across Home, Explore, and agent recommendation searches
2) a direct question and detail-page visit for a closed role
3) explicitly accepting and unconfirmed application statuses
4) removal of an old application-status URL parameter
5) verified volunteering-site distance
6) organization-only distance with activity-location uncertainty
7) town-only location, including any supported town-area estimate
8) home-based work with possible travel requirements
9) a genuinely unknown location
10) sorting without mixing destination types
11) explicit town restrictions and multi-site organizations
12) changing or clearing the ZIP
13) “About” and “Less than 1 mile” labels, with no remaining “Approx.” in the current user interface
14) desktop and mobile layouts

run relevant backend tests, geographic validation, frontend type checks, and the production build.

verify the actual running app loads the updated build. restart only this project’s server if necessary.

14) update documentation and submission drafts

update the README, design notes, evidence summary, and rubric checklist to reflect the implemented behavior.

update the report and slide generator scripts, then rebuild report.html and slides.html. keep the report within 10–15 printed US Letter pages and the deck within 10 slides.

capture genuine final screenshots with synthetic inputs. preserve historical screenshots and traces unchanged, labeling older behavior accurately. do not rewrite historical evidence merely to replace “Approx.”

leave prospective-user testing, GitHub links, and the actual fresh-clone test pending until completed.

show me the implemented changes, representative results for each location category, actual test results, and remaining limitations. do not publish, deploy, or submit anything.
```

### What happened

**Closed roles.**
- **Where they're excluded:** the backend now leaves explicitly closed records (7 in total) out of the list route used by Home and Explore, the agent's search and `find_alternatives`. The route reports how many it left out, and Explore says so.
- **What still works:** the records and their statuses stay in the data. `include_closed=true` exists for direct questions, detail pages still show "Applications closed" (with only "Check application details"), and the validator rejects a closed role as a recommendation.
- **Explore:** the application-status filter is gone, and old `?application_status=` URLs are cleaned. The empty state reads "No matching opportunities to show".
- **Labels:** "Accepting applications", "Ask about availability" and "Applications closed", with one shared note that accepting applications doesn't guarantee a placement or shift.

**Location categories.** Every record now has one category, computed in `backend/geo.py`. Counts:

| Category | Records |
|---|---|
| Verified volunteering site | 15 |
| Organization location only, activity unconfirmed | 31 |
| Published role town only | 0 in the current data (tested with a synthetic variant) |
| Home-based | 6 |
| Unknown | 12 |

- **New data:** an `organization_locations` list (one verified site per organization; none for CHS's three sites or Cat Tales' P.O. box), and sourced travel notes for home-based roles (11 new quotes, 41/41 found).
- **Town reference points:** Census 2026 Gazetteer town internal points, 169 towns.
- **Labels:** for example "About 6 miles to volunteering site", "Less than 1 mile to volunteering site", "Organization is about 11 miles away · Activity location needs confirmation", "CHS Wilton is about 27 miles away · Help from your home…", and "Location: ask organization".
- **Sorting:** "Closest estimated volunteering site" ranks only verified sites, using the unrounded distance; other leads follow in a separate, unranked group.
- **Fixes:** the detail page and Compare no longer show the organization's town as the role's town.

**Checks:**
- **Backend:** 110 tests, including a new 16-test file for this prompt; 52 validator self-tests (organization locations, travel evidence and the town file are now validated).
- **Data:** 391 evidence quotes and 41 location quotes found.
- **Frontend:** the type check and production build pass.
- **Browser, no AI (desktop and mobile):** 56/56 status and location checks, and 42/42 for the earlier suite after updating its two expected strings.
- **Real AI (fresh gpt-6-luna calls):** 274/275 checks, covering a direct question about a closed role and the full location conversation. The one failure is the same wording regex on the "stay in New Haven" turn; manual review found the reply correct.
- **Old wording:** no "Approx" remains in the current interface, the report or the slides.

The report and slides were rebuilt: the report is 15 pages and the deck 10 slides. The cost figures are still the Session 11 measurement and are labelled as such.

**Correction (added in Session 13):** "7 in total" above is wrong. `data/opportunities.json` has **6** explicitly closed records: 4 in Greater New Haven (`fnhas_dog_handler`, `fnhas_cat_handler`, `fnhas_foster`, `branford_general_volunteer`) and 2 in wider Connecticut (`chs_foster_newington`, `chs_foster_waterford`). The report and slides already computed 6 from the data. The text above is left as written.

### Follow-up prompts

None yet.

## Session 13 — 2026-10-25 — Closed-count correction; availability text, official links and comparison controls

### Prompt (verbatim)

Sent as one message containing two pasted blocks.

```text
one count in your summary is incorrect: opportunities.json contains 6 explicitly_closed records, not 7—4 in Greater New Haven and 2 in wider Connecticut.

1) confirm the counts directly from the current dataset.
2) correct any current documentation or generated text that says 7. preserve historical logs, adding a correction rather than rewriting them.
3) derive displayed counts from the dataset instead of hardcoding them.
4) do not make further feature changes during this correction.
```

```text
clarify application availability and comparison controls on opportunity cards.

1) replace the status badge “Ask about availability” with “Availability not confirmed”. style it as informational text rather than an action button.

2) provide a keyboard-accessible explanation: “The source does not clearly state whether applications are being accepted. Check the organization’s volunteer page or contact them.”

3) add a separate, clearly clickable “Visit volunteer page ↗” link using the record’s official application_or_information_url. use “Contact organization ↗” for an official contact-page link when available.

4) label destinations accurately. use “Apply on organization’s website ↗” only when the destination is an actual application page and the listing is not explicitly closed. an application link does not establish an opening.

5) rename “+ Compare” to “Compare requirements”. after selection, show “Added to comparison” with an accessible way to remove it.

6) show a visible comparison bar when at least one opportunity is selected: “1 opportunity selected” or “2 opportunities selected”, with “View comparison”, “Clear”, and the existing maximum of three.

7) explain briefly: “Compare age, hours, commitment and fees side by side.” comparison is optional and must not block opening details or visiting the organization’s website.

8) preserve the actual backend application statuses and existing comparison behavior. update labels consistently across Explore, details, Find my fit, and Compare.

9) test the links, keyboard behavior, selection and removal, and mobile layout. rebuild the frontend and record the changes in AI_prompts.md.
```

### What happened

**Count correction (no feature changes).** The dataset was checked directly: there are 6 explicitly closed records, 4 in Greater New Haven and 2 in wider Connecticut. The only "7" was my Session 12 summary and its log entry. A correction note was added there, and the original text was left as written.

The report and slides already computed the closed count from the data ("6 in all", "Closed roles (6)"). Their other hand-typed counts (organizations, records, sources and verified sites in the diagram and text) are now derived from the data too. Both were rebuilt (15 pages, 10 slides) before any feature work.

**Availability and links.**
- **Status:** "Ask about availability" is now "Availability not confirmed", shown as plain informational text rather than a button-like badge. A small "?" button opens the requested explanation; it works by keyboard (Enter or Space) and has an accessible name.
- **Links:** "Visit volunteer page ↗" uses the record's `application_or_information_url`, and "Contact organization ↗" uses the recorded contact page when it is a different page. The accessible names say which site opens.
- **"Apply on organization's website ↗":** shown only when the destination is a recorded application page and the role isn't closed. No current destination is an application page, so it appears nowhere; a synthetic test covers the rule.
- **Unchanged:** the backend statuses, and the backend label for unconfirmed listings now reads "Availability not confirmed".

**Comparison.**
- **Button:** "Compare requirements" turns into "Added to comparison" with a Remove button.
- **Comparison bar:** shows "1 opportunity selected" or "N opportunities selected", "View comparison", "Clear", the limit of 3, and "Compare age, hours, commitment and fees side by side."
- **Never in the way:** space is reserved below the page so the bar never covers a link.
- **Everywhere:** Explore, the detail page, Find my fit and Compare all use the same labels.

**Checks:**
- **Backend:** 111 tests and 52 validator self-tests pass. The type check and build pass, and the running app serves the new build.
- **Browser, no AI (desktop and mobile):** 44/44. These cover the links matching their official destinations, keyboard explanation, add and remove, the 1/2/3-selected bar, the maximum of three, Clear, details still opening, a closed role with no Apply link, and no overflow.
- **Find my fit:** 10/10 with 2 fresh gpt-6-luna turns.
- **Earlier suite:** 42/42, after updating its compare and link labels.

**One problem found and fixed:** on mobile the comparison bar is taller than the space first reserved for it, so it could cover the last card's links. The reserved space now follows the bar's actual height.

**Not changed:** the report and slides still describe the Session 12 labels ("Ask about availability").

### Follow-up prompts

None yet.

## Session 14 — 2026-10-25 — Submission drafts updated to the current interface

### Prompt (verbatim)

```text
update the submission drafts to match the current interface.

1) update the report and slide generator scripts with the current availability explanation, official website links, and comparison controls.
2) replace outdated interface screenshots with the final Session 13 screenshots where relevant. preserve historical run screenshots when they substantiate a particular run, labeling them as historical.
3) rebuild report.html and slides.html. verify 10–15 printed Letter pages, no more than 10 slides, readable screenshots, and no overflow.
4) update the verification record and AI_prompts.md. keep user-test findings, GitHub links, and the actual fresh-clone test pending.
5) do not add features, publish, or submit anything.
```

### What happened

**Wording.** The report and slide generators now use the current interface wording:
- "Availability not confirmed", shown as information with a keyboard-accessible explanation;
- "Visit volunteer page ↗" and "Contact organization ↗";
- "Apply on organization's website ↗" only for a real application page that isn't closed. No current link is one, which the report says.

They also describe the optional comparison ("Compare requirements" → "Added to comparison", and the bar with the count, "View comparison" and "Clear"). "Ask about availability", "Check application details" and "Approx" no longer appear in either file.

**Screenshots.**
- **Interface screenshots replaced with final Session 13 captures:** the option card, Explore sorted by closest verified site, the comparison bar, the detail panel and Compare.
- **Two new captures:** Explore with a ZIP and the organization-only detail page were taken from the same unchanged build, because the Session 13 set had no such views.
- **Historical screenshots kept and labelled:** the Session 6 safety run and the Session 7 provider-filter retake. The slide-6 run is labelled as Session 11, with the card from another synthetic query.

**Checks.**
- The report prints at 15 Letter pages with 0 external requests, and the deck has 10 slides.
- The first rebuild overflowed slide 5 (754 px). Its images were made smaller and it now fits.
- The comparison-bar crop was widened so its text isn't cut off.

The verification record was updated. User-test findings, the GitHub link and the fresh-clone test remain pending. No features were added, and nothing was published.

### Follow-up prompts

None yet.

## Session 15 — 2026-10-25 — Sorting, Clear all filters, one shared filter, strict one-time requests

### Prompt (verbatim)

```text
fix sorting, Clear all filters, and consistency between Explore and Find my fit. inspect the actual implementation first and preserve the current design, evidence, and completed features.

1) make sorting usable and understandable

provide “Default order” and “Organization name A–Z” as available sorting options.

enable “Closest estimated volunteering site” only when a supported ZIP is supplied. disable that individual option with a clear explanation rather than disabling the entire dropdown.

keep the existing separation between verified volunteering-site distances and organization/town estimates. sort using unrounded distances.

inspect published time-commitment coverage before adding time-based sorting. add it only if enough comparable, clearly applicable values exist to make it useful.

do not mix hours per session, week, and month into one ranking. do not treat unknown hours as zero or one-time work as requiring zero commitment. if the information is too sparse or inconsistent, leave time-based sorting out and explain that in the implementation summary.

2) make Clear all filters actually clear the ZIP

the current clearAll function resets URL parameters and search text but leaves ZIP state untouched.

both Clear all filters buttons must reset the search, location filters, activities, animals, organization, commitment, optional record types, geographic expansion, sorting, and Explore ZIP.

clear both the typed ZIP draft and applied ZIP, including validation messages and derived distance results. reset sorting to Default order.

enable Clear all filters when ZIP or sorting is the only active setting.

if Explore currently shares ZIP state with Find my fit, separate the browsing state so clearing Explore does not silently erase confirmed chat answers or conversation history.

verify clearing works from normal results and the empty state, and that navigation does not restore the cleared ZIP unexpectedly.

3) use consistent eligibility and filter meanings across both pages

inspect Explore’s backend search and the agent tools. share the same deterministic filtering rules for geographic scope, role location, commitment, activity, animals, record type, and closed application status.

the same explicit filters must produce the same matching candidate set. the assistant may rank a subset and personalize assessments, but it must not silently broaden those filters.

distinguish a preference from a hard constraint. “I can only do a one-time project” is a hard constraint; an ongoing role or unknown commitment is not a confirmed match.

4) correct the one-time example

reproduce this message in Find my fit:

“I can only do a one-time project of a few hours with my coworkers.”

the current screenshot offers two event-related roles while acknowledging neither confirms a one-time group session.

if no published one-time opportunity matches the current scope, say:

“I couldn’t find a confirmed one-time opportunity matching your requirements.”

do not put unknown-commitment activities under “Options to consider” as though they meet the one-time constraint.

they may appear separately under “Other activities to ask about”, clearly stating “One-time participation and group availability need confirmation”. offer that expansion as optional.

do not infer one-time commitment from words such as event, fundraiser, or project.

do not convert “a few hours” into a specific numeric availability without confirmation.

if a suitable one-time opportunity exists only outside the selected geographic scope, explain that and offer to expand the area. do not expand automatically.

5) check similar inconsistencies

test equivalent Explore filters and assistant requests for:

1) one-time versus ongoing commitments
2) explicit town restrictions versus home town
3) Greater New Haven versus wider Connecticut
4) dogs, cats, and no-animal-contact requests
5) described volunteer roles versus independent activities or interest-only records
6) explicitly closed applications
7) unknown hours or commitment information

preserve “unknown” as unknown. do not change factual classifications just to produce more results.

where the assistant offers alternatives that relax a constraint, label the relaxed constraint explicitly and keep those alternatives separate from matching results.

6) verify the actual website

add focused regression tests for shared filtering, strict one-time requests, sorting, and clearing ZIP state.

test desktop and mobile, including:

1) no ZIP: alphabetical sorting works and distance sorting explains its prerequisite
2) supported ZIP: distance sorting works
3) ZIP alone: Clear all filters is enabled and clears it completely
4) empty results: Clear all filters restores default browsing
5) changing or clearing ZIP: no stale distances remain
6) identical explicit constraints: Explore and Find my fit agree on matching candidates
7) no confirmed one-time matches: the assistant explains the gap and separates uncertain alternatives

run relevant backend tests, frontend type checks, and the production build. confirm the running app serves the new build.

7) update documentation and stop

record this prompt and actual results in AI_prompts.md.

update affected report and slide wording through their generators, replacing screenshots only where needed. keep the report within 10–15 Letter pages and the deck within 10 slides.

preserve historical test evidence. show the actual fixes, test results, whether time-based sorting was supported, and remaining limitations.

do not add unrelated features, publish, deploy, or submit anything.
```

### What happened

**Sorting.**
- The options are "Default order", "Organization name A–Z" and "Closest estimated volunteering site". The distance option is disabled on its own until a supported ZIP is entered, with a hint explaining why.
- Distance sorting still ranks only verified volunteering sites, using unrounded distances.
- **No time-based sort.** Only 9 of the 58 non-closed records publish minimum hours, in mixed units (4/month and 8/month, 2–3/week, one only "needs confirmation"); 2 more give hours per session, and 46 have unknown commitment.

**Clear all filters.**
- The Explore ZIP used to be stored in Find my fit's confirmed answers. It is now a separate browsing ZIP, shared only with detail pages.
- Both Clear buttons now reset the search, every filter, the optional record types, wider Connecticut, sorting and that ZIP (typed draft, applied value, messages and distances). Find my fit answers and conversation are untouched.
- Clear is enabled when only the ZIP or sorting is set. Navigation doesn't restore a cleared ZIP.

**One shared filter.**
- Explore and the assistant's search both use `Dataset.search`. Explore's town filter now matches only a role's own published town, the same as the assistant, so New Haven and Branford are no longer offered: their only role-level records are closed.
- The assistant's search gained the commitment and organization filters.
- A hard limit (area, or `commitment_required`) is applied to every search and to alternatives. Matches outside the chosen area and commitment-unknown leads are reported separately, never mixed in.

**Strict one-time requests.**
- `commitment_required` is a new hard-constraint field, separate from the preference. The server detects an explicit "only … one-time" in the person's own words with a deliberately narrow pattern, so "only once a week" and "only volunteer in North Haven, weekly" don't trigger it.
- Matches must publish exactly that commitment. Unknown-commitment records may appear only under "Other activities to ask about", labelled "One-time participation and group availability need confirmation".
- With no match, the reply begins with the exact sentence, and the server offers, without doing it, to include other Connecticut locations, where the one-time CHS group project is.
- "A few hours" is never turned into a number.

**Problems found and fixed during the real tests:**
- The first desktop reply repeated the gap sentence, because the model's version added "in Greater New Haven".
- The mobile model didn't record the constraint.
- Then neither reply used the exact sentence. The server now records the constraint itself and replaces the model's variant with the exact sentence. Earlier attempts (6 traces) are kept in `session15_superseded/`.

**Checks:**
- **Backend:** 188 tests, including 77 new ones: shared-filter parity across 64 filter combinations plus town filters, one-time handling, quote checks and the detection rule. 52 validator self-tests; the type check and build pass, and the running app serves the new build.
- **Browser, no AI:** 46/46 on desktop and mobile, covering sorting, every clearing path, ZIP separation, the empty state and the town options. The earlier suite is 42/42 after its town check moved from Branford to North Haven; the Session 13 suite is 44/44.
- **Real AI:** 16/16 with fresh gpt-6-luna calls. The one-time request was tested on desktop and mobile, and a North Haven request was compared with Explore's North Haven candidates.
- **Historical:** the Session 12 script now fails its checks for the old "Ask about availability" label, as expected.

**Report and slides.** The wording was updated through the generators; no screenshots needed replacing. The report is 15 pages and the deck 10 slides. Slide 3 first overflowed by 5 px, so its sentence was shortened.

### Follow-up prompts

None yet.

## Session 16 — 2026-10-25 — Simpler location display, one list sorted by distance

### Prompt (verbatim)

```text
simplify location display and distance sorting across Animal Volunteer Finder. use the organization’s verified physical location when the actual volunteering site is unknown, and show one continuous results list.

1) inspect and preserve existing work

read the current location logic, search routes, frontend cards, sorting, and project instructions before editing.

preserve the sourced dataset, matching rules, application statuses, conversation memory, and historical evidence.

record this prompt accurately in AI_prompts.md.

2) choose the distance destination consistently

use this order:

1) the verified volunteering site, when available
2) the organization’s verified physical location, when the activity site is unknown
3) no distance when neither location is available

never use mailing addresses, P.O. boxes, or invented coordinates.

keep the destination type in the structured backend response so the frontend and agent know whether the distance refers to an activity site or the organization.

3) simplify the labels on each card

for a verified volunteering site, show:

“North Haven · About 6 miles away”

for an organization-address fallback, show:

“Organization: New Haven · About 2 miles away”

add a small note:

“Activity location may differ”

these are wording examples, not values to hardcode.

use “About” rather than “Approx.” throughout the current interface. for distances below one mile, use “Less than 1 mile away”.

avoid repeating the same town, distance, and uncertainty in several places on one card. keep the full address, maps link, and supporting evidence in the details.

when no supported ZIP is supplied, show the location without a numerical distance.

4) remove the separate “Other leads” section

remove:

“Other leads: no verified volunteering site (18)”

also remove its explanatory paragraph and the grouping that separates these records from the main results.

show one continuous results list with one total count after filters and default closed-role exclusions.

communicate the location distinction on each card rather than through separate sections. do not remove records merely because their volunteering site is unknown.

5) simplify distance sorting

rename the option to:

“Distance: nearest first”

sort the combined results by the unrounded distance to the destination selected in step 2. round only the displayed value.

keep the organization-fallback label visible so users understand what the estimate measures.

place records without a calculable distance last. use a stable secondary order for equal distances.

keep “Default order” and “Organization name A–Z” available. disable only the distance option until a supported ZIP is supplied, with a short explanation.

6) handle organizations with several sites

use the role’s associated site when supported by the data.

if the relevant site is unknown, use the nearest verified organization site and identify it explicitly:

“Nearest organization site: [site name] · About X miles away”
“Activity location may differ”

do not imply that this is the assigned volunteering location. preserve the other verified sites in the details.

7) handle home-based activities

keep “Help from your home” as the primary location description.

an organization distance may appear as secondary information, clearly labeled. do not imply that travel is required unless the sources establish pickup, training, or another travel requirement.

do not rank a home-based activity as zero miles away. when no travel destination is relevant, leave its sortable distance null and place it with the other records without a distance.

8) preserve location restrictions and accurate travel wording

using an organization address as a distance fallback must not establish that the activity happens in that town.

continue enforcing explicit volunteering-town restrictions using supported role-location information. do not silently broaden the permitted area.

keep home town, ZIP, volunteering-area restrictions, and transport preferences separate.

show one short shared explanation near the results:

“Distances are straight-line estimates from your ZIP area. For some activities, the distance is to the organization; the activity location may differ.”

do not claim walking times, driving times, transit access, or walkability.

9) apply the changes consistently

update Home cards, Explore, opportunity details, Compare, and Find my fit wherever location estimates appear.

calculate distances in ordinary Python and render them from structured backend fields. do not let the model invent distances or attach one record’s distance to another.

preserve the current structured reply format and concise follow-up questions.

keep all existing application-status behavior: closed roles excluded from default discovery, actual statuses preserved, and official volunteer/contact links available.

10) preserve ZIP reset behavior

Clear all filters in Explore must still clear its typed and applied ZIP, sorting, validation messages, and distance results.

clearing Explore must not erase Find my fit’s confirmed answers or conversation.

changing or clearing a ZIP must immediately refresh or remove displayed estimates without leaving stale distances.

11) test the changes

add focused tests for:

1) a verified volunteering site
2) an organization-address fallback
3) a multi-site organization with a supported role-site association
4) a multi-site organization without a confirmed role-site association
5) a home-based activity
6) no verified physical address
7) combined distance sorting and records without distances placed last
8) one results list and an accurate total count
9) explicit town restrictions remaining intact
10) changing and clearing the ZIP
11) alphabetical sorting without a ZIP
12) desktop and mobile layouts

verify the old “Other leads: no verified volunteering site” heading and paragraph are gone from the current interface.

run relevant backend tests, geographic validation, frontend type checks, and the production build. confirm the running app serves the updated build.

12) update documentation and submission drafts

update the README, design notes, and evidence summary with the simpler destination fallback and sorting behavior.

update the report and slide generator scripts, then rebuild their HTML files. keep the report within 10–15 printed US Letter pages and the deck within 10 slides.

replace affected current-interface screenshots while preserving historical evidence unchanged and labeled accurately.

record actual results in AI_prompts.md. show the updated desktop/mobile screenshots, representative location labels, test results, and remaining limitations.

do not add unrelated features, publish, deploy, or submit anything.
```

### What happened

**Destinations.**
- A distance now goes to the role's verified volunteering site. If the activity site is unknown, it goes to the organization's verified physical location. Otherwise there is no distance.
- For an organization with several verified sites and none tied to the role (Connecticut Humane Society), it goes to the nearest of them, named. A role's own site still wins (for example CHS Newington roles).
- Mailing addresses, P.O. boxes and invented coordinates are never used.
- Each estimate keeps its destination type in the backend response (`volunteering_site`, `organization_location`, `organization_nearest_site`, `related_site`, `organization_reference`), with unrounded `sort_miles` and a ready `label`.
- CHS records without a role site moved from "unknown" to the organization-location category. Counts are now: 15 verified sites, 33 organization locations, 6 home-based, 10 unknown.

**Labels (test ZIP 06511).**

| Case | Card text |
|---|---|
| Verified site | "North Haven · About 6 miles away" |
| Organization fallback | "Organization: New Haven · About 1 mile away", plus a small "Activity location may differ" |
| Several sites | "Nearest organization site: CHS Wilton · About 27 miles away", plus the same note |
| Home-based | "Help from your home", with "Supply pickup: CHS Wilton · About 27 miles away" underneath |
| Home-based, no travel stated | Organization distance marked "for reference; no travel is stated"; never ranked, never 0 miles |
| No physical address | "Location: ask organization", no distance |

- Under one mile the card says "Less than 1 mile away".
- Without a ZIP, cards show only the place, for example "Organization: New Haven".
- The street address, maps links, other sites and evidence stay in the details.
- One shared explanation is shown: "Distances are straight-line estimates from your ZIP area. For some activities, the distance is to the organization; the activity location may differ."
- The same structured text is used on Home, Explore, detail pages, Compare and Find my fit.

**One list.**
- The "Other leads: no verified volunteering site" section and its paragraph are gone, from Explore and from Find my fit's "Not ranked" group.
- Each page shows one list with one count.
- "Distance: nearest first" (renamed) sorts the combined list by the unrounded distance; records without a distance go last, in their previous order.
- "Default order" and "Organization name A–Z" are unchanged. Only the distance option is disabled without a supported ZIP, with the hint "Add a supported Connecticut ZIP code above to sort by distance."
- The assistant's search sorts the same way.
- Town limits still use the role's own published town, so an organization's location never puts a role in a town.
- ZIP handling is unchanged: Clear all still clears the typed and applied browsing ZIP, sorting, messages and distances, and leaves Find my fit's answers alone.

**Checks.**
- **Backend:** 190 tests pass, with 14 location tests new or rewritten for the new labels. They cover the verified site, organization fallback, multi-site with and without a role site, home-based, no address, combined sort, the "About" wording and the town variant.
- **Data:** validation 0 errors (the usual Branford all-ages warning); 41/41 location quotes found; the type check and build pass.
- **Running app:** the project server on port 8001 was restarted and serves the new build.
- **Browser, no AI (desktop and mobile):** 62/62. Every card matches the backend's label; one list and count (58 with all record types); combined order with no-distance records last; "Other leads" gone; ZIP change and clear; A–Z without a ZIP; Clear all; town filter; detail, Compare and Home; no overflow.
- **Real AI:** 14/14 on two fresh gpt-6-luna turns (returned `gpt-6-luna-global`). The Location rows match the backend labels, there is no mileage in the prose, and sorting by distance works. One earlier attempt stopped on a script error after four passing checks; its trace is kept and marked superseded in the test report. One more real turn was made for the report's option-card picture.
- **Earlier suites:** the earlier browser suite passes 42/42 and the Session 13 checks 44/44. The Session 15 checks first scored 38/46: the 8 failures were the intentionally changed checks (separate ranking heading, old element and hint text). After updating them, 46/46.
- **Results file:** `output/location_check/ui_session16_test_report.json`.

**A mistake.**
- While re-running the older check scripts I let them write their screenshots to their old locations. This overwrote 21 earlier screenshots (9 in the screenshots root, 8 in `session13/`, 4 in `session15/`) with captures of the Session 16 build.
- No backup copy existed, so the originals could not be restored. The files are listed and labelled in `output/screenshots/RECAPTURED_SESSION16.md` and noted in the session READMEs.
- That first run of the earlier suite also sent one untraced real assistant turn to the 8001 server before stopping on an outdated selector.
- Later re-runs wrote only to a scratch folder.

**Report and slides.** Rebuilt through the generators:
- The location table, sorting bullet, comparison-table rows and limits wording are updated, and a Session 16 test line is added.
- The current-interface pictures were replaced with Session 16 captures: Explore sorted by distance, the comparison bar, the organization-location detail panel, Compare with three items and an option card.
- The report is 15 Letter pages with no external requests; the deck is 10 slides with no overflow.

**Limits.** Organization distances may not be where the activity happens, so the distance order is approximate for those 33 records. Distances are straight lines from a ZIP area's center. User testing, the GitHub link and the fresh-clone test remain pending.

### Follow-up prompts

None yet.

## Session 16 follow-up — 2026-10-25 — Recovering the overwritten screenshots

### Prompts (verbatim)

```text
recover the historical screenshots accidentally overwritten during Session 16.

1) use Final_Project(20261026-024646).zip as the backup. it contains all 21 affected files listed in output/screenshots/RECAPTURED_SESSION16.md.

2) extract the backup into a temporary folder. do not replace current code, data, report, slides, or the current frontend build.

3) preserve the accidentally recaptured images in a clearly labeled Session 16 folder before restoring the 21 historical screenshots to their original paths.

4) verify the restored files are byte-identical to their counterparts in the backup ZIP.

5) update RECAPTURED_SESSION16.md with the recovery source and verification results. preserve the original mistake disclosure and append the recovery outcome.

6) confirm the report and slides still reference the intended current or historical screenshots. do not rebuild them unless their assets were affected.

7) make browser-test screenshot output use a new run-specific folder by default, so rerunning tests cannot overwrite historical evidence.

8) record the recovery in AI_prompts.md. do not make unrelated feature changes.
```

```text
i downloaded the earlier backup ZIP and renamed it “backup”.

1) check Downloads and /Users/rhea/Desktop/MGT409 AI/ for backup.zip. inspect its contents to confirm it contains the 21 historical screenshots listed in output/screenshots/RECAPTURED_SESSION16.md.

2) extract it into a temporary folder. preserve the recaptured Session 16 images separately, then restore only the 21 affected historical screenshots.

3) verify the restored files are byte-identical to the backup using SHA-256 hashes.

4) append the recovery outcome to RECAPTURED_SESSION16.md and record it in AI_prompts.md.

5) confirm the report and slides still reference the intended images.

do not replace current code, data, frontend builds, report, or slides. if the backup is not in either location, ask me for its path rather than searching my entire home folder.
```

### What happened

**First request.** `Final_Project(20261026-024646).zip` was not on this Mac. The only project ZIP was the one made
after the overwrite, and it already held the overwritten versions. Nothing was restored then. One part was done at
that point because it didn't need the backup: the browser-test scripts (`scripts/ui_check.py`,
`scripts/ui_safety_demo.py`) now write each run to a new `output/screenshots/runs/<script>_<date-time>/` folder by
default (the report file goes there too), so a rerun can't overwrite earlier evidence.

**Second request.**
- **Finding the backup.** `backup.zip` was not directly in Downloads or `MGT409 AI/`. It was one level down, at
  `MGT409 AI/Final Project/backup.zip` (saved 23:41, 502 entries). No wider search was made. It held all 21 files,
  with times from before the overwrite.
- **Restoring.**
  - The ZIP was extracted into a temporary folder outside the project.
  - The recaptured Session 16 images were copied first to `output/screenshots/session16/recaptured_overwrites/`
    (same relative paths, with a README).
  - Then only the 21 files were copied back. No code, data, build, report or slides were replaced.
  - A first attempt in zsh copied nothing, because the file list wasn't split into words. This was checked, and the
    restore was redone in Python.
- **Verification.**
  - SHA-256 of every restored file equals the hash of the same member read straight from `backup.zip` and of the
    extracted copy: **21/21 byte-identical**.
  - 19 of the recaptures differed from the originals; 2 happened to be identical.
  - Hashes: `session16/recaptured_overwrites/recovery_sha256.json`.
- **Records.** The recovery outcome was appended to `RECAPTURED_SESSION16.md`; the original disclosure is unchanged.
  The session READMEs, the evidence summary and the deliverables verification record were updated.
- **Report and slides.** They use none of the 21 files (only `session16/s16_*`, Session 11 and 12 captures,
  `mobile_home.png` and the two safety screenshots), so they were not rebuilt.

### Follow-up prompts

```text
exclude backup.zip and other backup archives from future project ZIPs and the Git repository. keep the backup file on my Mac; do not delete it.

package only the current project and required submission files, excluding virtual environments, node_modules, secrets, private notes, and backup archives. retain the built frontend and relevant evidence.

record that the screenshot recovery is complete. no further app changes are needed for this task.
```

- **The screenshot recovery is complete:** 21/21 historical screenshots are restored and SHA-256-verified. No further
  app changes were made.
- **Git:** `.gitignore` now excludes backup and packaged archives (`backup*.zip`, `*backup*.zip`, `Final_Project*.zip`,
  `*.zip`, `*.tar`, `*.tar.gz`, `*.tgz`, `*.7z`, `*.rar`). The project contains no such archives, so nothing current
  was hidden.
- **Backup:** `Final Project/backup.zip` stays on the Mac, outside the repository, and was not deleted.
- **Project ZIP:** rebuilt with only the project folder (`Final Project/animal-volunteer/`).
  - Excluded: `.venv`, `node_modules`, `.env` files (`.env.example` kept), `local_data/` (private notes, logs and
    backups), caches, `.DS_Store`, every archive (including `backup.zip`), and the course's `Rubrics.pdf`, which
    isn't a project file.
  - Kept: the built frontend (`frontend/dist`), `report.html`, `slides.html` and the evidence in `output/` and
    `docs/`.

## Session 17 — 2026-10-26 — Fixes from owner testing (profile corrections, uncertainty, form, Compare, evidence, age)

Owner testing: manual testing by the project owner. It does not replace the prospective-user test, which is still
pending.

### Prompt (verbatim)

```text
please fix the issues found during our manual app testing. inspect the current implementation first, preserve existing work, and keep the warm, polished design.
1. fix profile updates when the user changes their availability
we tested this sequence:
first message: “i'm 24 and live in New Haven, ZIP 06510. i'd like to walk dogs and can volunteer 2 hours per week for 12 months.”
second message: “actually, i can only do a one-time activity for 3 hours total. i can't commit weekly or for 12 months. keep my age, ZIP, and interest in helping dogs.”
the app added one-time only and a 3-hour session limit, but incorrectly retained 2 hours per week and a 12-month commitment. it then used that stale commitment to display a green match.
implement explicit replacement and clearing of withdrawn profile facts, including values previously confirmed through the form. distinguish unchanged fields from fields intentionally cleared. preserve age, town, ZIP, and interests unless changed. for this example, remove the recurring hours and period and the old 12-month value; retain one-time only and the 3-hour session limit. do not invent a replacement number of months.
update the profile before searching and checking fit. ensure old conversation history cannot restore withdrawn values. keep the latest exchange visible and older exchanges in collapsed history.
2. make uncertainty consistent throughout fit results
Animal Haven’s older hours and commitment requirements displayed warnings but also green “Meets requirement” labels and a green overall fit badge.
when a rule’s current applicability is uncertain, stale, or conflicting, use an amber label such as “Needs confirmation,” even when the user’s numbers match the published value. explain the numerical comparison separately if useful.
reserve green requirement labels for applicable, supported rules. an overall result with unresolved eligibility or commitment checks should say “Possible fit — confirm requirements.” a definite failure of an applicable rule must still take precedence. application availability must remain separate from personal fit.
apply the same interpretation across backend checks, assistant summaries, cards, details, and comparison views. keep unknown values unknown.
3. synchronize the edit form with the current profile
“Your answers” correctly displayed chat-derived details, but the expanded “Add or edit your answers” form remained blank.
populate the form with the current effective answers, preserving whether they came from chat or were confirmed. opening the form must not confirm anything automatically. saving one edited field must preserve unrelated answers; provide an intentional way to remove a value.
avoid overwriting unsaved edits when a response arrives. make confirmation, editing, removal, and session clearing behave consistently.
4. give comparison columns equal widths
the two selected opportunity columns had substantially different widths. use a narrower requirement-label column and equally sized opportunity columns for both two-role and three-role comparisons. long titles, links, and expanded evidence must wrap without changing those proportions. preserve readable mobile scrolling without page-wide overflow.
5. remove repetitive evidence from the display
expanded evidence repeated overlapping passages from the same source about the same hours and commitment requirements.
display the smallest useful set of passages supporting each claim. deduplicate exact repeats and redundant excerpts from the same source, while preserving distinct conditions, conflicting evidence, source links, and access dates. keep the original sourced data intact. evidence counts should match the displayed entries.
6. provide a more useful next step when someone cannot qualify
the age-15 dog-walking test correctly rejected roles requiring ages 21 and 25, even with a parent attending. preserve this behavior.
after explaining the restriction, offer to explore other ways to help, such as non-handling activities, using the dataset and existing tools. do not imply those activities accept minors without evidence. distinguish a supported option from an activity whose age eligibility needs confirmation. ask before broadening the user’s activity interests or geographic scope.
preserve the successful safety behavior: requests to ignore age rules, invent shelter approval, or confirm a shift must not change eligibility or fabricate a booking.
7. verify the changes
add focused regression tests for profile corrections and explicit clearing, including a correction to previously confirmed answers; preservation of unrelated facts; form synchronization and partial saves; uncertainty labels; and age restrictions.
run the existing relevant checks and rebuild the production frontend. test the exact two-message availability sequence through the real app using gpt-6-luna through Portkey. also repeat the age-15 parent-attendance test and the request to fabricate approval and a Saturday shift. inspect both the response and the resulting profile.
check comparison layouts with two and three roles and expanded evidence at desktop and mobile widths. verify Explore’s Clear all still removes the browsing ZIP and distance sorting without clearing the chat profile.
save new screenshots and traces in a new timestamped directory. never overwrite historical evidence or recovered screenshots. record actual API-reported usage for real model calls, and never print secrets.
8. document and stop for review
record this prompt accurately in AI_prompts.md and summarize the changes, checks actually run, results, and remaining limitations. label our testing as owner testing; it does not replace the prospective-user test.
update documentation where these fixes change described behavior. preserve historical evidence and distinguish it from new runs. if report.html or slides.html need changes, preserve their required formats and limits.
show me the changed files, test results, and representative screenshots. stop for review before publishing or rebuilding the submission ZIP. leave backup.zip untouched.
```

### What happened

**1. Profile corrections and explicit clearing.**
- **Cause:** the server re-applied earlier chat facts every turn, because their quotes were still in the history.
  Nothing could express "remove this value", so the withdrawn 2 h/week and 12 months came back.
- **Withdrawals and corrections:**
  - A withdrawal or correction must now be quoted from the newest message. It becomes unknown (never a guessed
    number) and applies even to form-confirmed answers; the page drops those (`confirmed_overrides`).
  - Withdrawn fields go back and forth as `withdrawn_fields`, so older messages can't restore them. Only a value in
    a later message can.
- **When the profile is updated:**
  - The server detects plain withdrawals ("can't commit weekly", "can't … for 12 months") after re-checking earlier
    facts and before any search or fit check. The model can also clear fields (`cleared_fields`).
  - A new verified value in the newest message replaces an earlier chat value.
- **Display:** "Your answers" lists cleared items under "Removed at your request", with the person's words. The
  latest exchange stays visible and earlier ones stay collapsed.

**2. Uncertainty.**
- `met` is now only possible for applicable published rules. A matching value on an older, uncertain or conflicting
  rule is amber "Needs confirmation", with "your answer matches the listed value" shown separately
  (`listed_value_matched`).
- The overall amber label is now "Possible fit — confirm requirements". A definite failure still takes precedence,
  and availability stays separate. This applies in the backend, the assistant's tool results, cards, detail pages
  and the fit check.

**3. Edit form.**
- "Add or edit your answers" shows the current answers, with "from chat" marks. Opening it confirms nothing.
- "Save my changes" confirms only the changed fields; clearing a field removes it.
- New replies update untouched fields without overwriting unsaved edits.
- Confirm, Edit, Remove and Clear my session all use one shared save path. "Check my fit" on detail pages works the
  same way.

**4. Compare.** A fixed table layout gives a narrow label column and equal opportunity columns for two or three
roles. Long text wraps, and mobile keeps the stacked cards.

**5. Evidence.** Exact repeats, and excerpts contained in a longer passage from the same source, are hidden (backend
and frontend). Distinct and conflicting passages, links and dates stay; counts match what is shown; the data is
unchanged.

**6. Age restrictions.** The model no longer switches activity or area on its own. After an age or guardian rule rules
out every option, the server offers other ways to help (such as no-handling activities) and says which publish an age
rule the person meets and which need confirmation. The age-15 rejections and the safety behaviour are unchanged.

**Problems found during the real runs and fixed:**
- **First attempt** (`output/owner_testing/20261026-002329/`, superseded and labelled):
  - The 3-hour session limit was lost, because the model searched, found nothing and never called `assess_profile`.
    The server now records an explicit session limit from the newest message, and the instructions say to record
    changed facts even when nothing matches.
  - A reworded one-time gap sentence was repeated.
  - The removal note was untidy.
  - A test-script error stopped that run early.
- **After the second run:** the age-15 reply had two near-identical "other ways to help" questions. The server's
  offer is now skipped when the model already asked; this is covered by a mocked test only.

**Checks actually run:**
- **Backend:** 210 tests, including 20 new regression tests in `tests/test_owner_testing_fixes.py`. One existing
  test was updated for the new uncertainty rule. Data validation: 0 errors and 1 warning.
- **Frontend:** the type check and production build pass. The project server on 8001 was restarted and serves
  `index-Cc7oOTzx.js`.
- **Real gpt-6-luna turns** (via Portkey, fresh calls; returned `gpt-6-luna-global`): 7 turns, all in
  `output/owner_testing/20261026-004520/` (82/82 checks).
  - The exact two-message sequence on desktop and mobile.
  - A third turn.
  - Age 15 with a parent.
  - The approval and Saturday-shift request.
- **Same run, no model calls:** form synchronisation and partial saves; Compare with 2 and 3 roles at 1440, 1024
  and 390 px with all evidence open; the detail fit check; Explore Clear all.
- **Earlier suites:** Session 13 44/44, Session 15 46/46, Session 16 62/62, earlier UI suite 42/42. The Session 15
  and 16 suites first stopped at the renamed "Save my changes" button.
- **API-reported usage (7 turns):** 23 requests; 168,678 input tokens (143,542 cached reads, 22,238 cache writes,
  2,898 uncached); 7,275 output tokens.
- **Superseded first attempt:** 4 turns; 12 requests; 84,837 input; 3,366 output.
- Screenshots and traces are only in the new timestamped folders; historical and recovered screenshots were not
  touched.

**Not changed, flagged for review:**
- Animal Haven's age sources conflict (18 vs 21), so they "never exclude", and a 15-year-old can still see those
  roles as "Possible fit — confirm requirements", with the age shown amber. Both versions exceed 15, so this may
  deserve a rule change.
- `report.html` and `slides.html` were not rebuilt. Their text isn't contradicted, but the report's option-card
  image shows the earlier overall badge text "Needs confirmation".
- The submission ZIP was not rebuilt; `backup.zip` was untouched.

### Follow-up prompts

None yet.

## Session 18 — 2026-10-26 — Conflicting minimum ages; correcting the earlier verification record

Owner testing (not the prospective-user test).

### Prompt (verbatim)

```text
please resolve the remaining conflicting-age issue and correct the verification documentation.
1. when all credible published minimum-age versions exceed the user’s age, keep the role out of recommended matches and suggested alternatives. explain: “both published age requirements are above your age; confirm the current rule with the organization.” preserve the conflicting values and evidence without claiming the conflict is resolved.
2. when the user meets some published versions but not others—for example, age 19 against conflicting minimums of 18 and 21—keep the result uncertain. do not mark it definitively eligible or ineligible.
3. apply this consistently across Find my fit, detail-page checks, and alternative suggestions. unknown age rules must remain unknown, and guardian attendance must not override an age rule without supporting evidence.
4. add focused regression tests for ages 15, 19, and 24 against conflicting minimums of 18 and 21. repeat the age-15 conversation and alternative-help follow-up through real gpt-6-luna calls via Portkey. verify the actual returned cards, not just the assistant’s summary.
5. correct the earlier verification README’s “no adult-only role offered” claim to describe what actually happened. preserve the original traces and screenshots, label the limitation, and save new evidence in a new timestamped folder.
6. run the relevant checks, rebuild the production frontend if needed, and record actual results and API-reported usage. keep backup.zip untouched. show the results before rebuilding the submission ZIP.
```

### What happened

**Rule change** (`backend/matching.py`):
- **Below every version:** for a conflicting minimum age whose every published version is above the person's age
  (read leniently, "over 18" = 18), the age line is now "not met" and the role is kept out of matches and suggested
  alternatives. The card says "Both published age requirements are above your age; confirm the current rule with the
  organization." The "Sources disagree" note and both quotes stay; the conflict is not called resolved.
- **Some versions met:** meeting some versions but not others (19 against 18 and 21) stays "Needs confirmation", and
  meeting both (24) stays amber too.
- **Unchanged:** unknown ages and unpublished rules stay unknown. The single uncertain CHS foster rule ("over 18, but
  children can assist their parents") is not an exclusion. A parent attending never overrides an age rule.
- **Where it applies:** the same assessment drives Find my fit, the detail-page check and alternative suggestions.
- **Other fix:** the server's "other ways to help" offer is now skipped only when the model already offered other kinds
  of help, not when it only offered a wider area.

**Correction of the earlier record:**
- `output/owner_testing/20261026-004520/README.md` had said "no adult-only role offered". That check only covered four
  dog-walking roles.
- In that run's safety request, two Animal Haven roles (both published ages above 15) were recommended to the
  15-year-old.
- The README now says so, in a labelled correction; its traces, screenshots and JSON are unchanged.
- The Session 17 entry above also described this case as an open question; it is resolved here.

**Checks actually run:**
- **Backend:** 231 tests. 21 are new: 20 collected from `tests/test_conflicting_age_exclusions.py` (11 functions, one
  run for each of the 10 Animal Haven roles), covering ages 15, 19 and 24 (plus 18, unknown age and unknown rules),
  the guardian rule, alternatives, the detail-page endpoint and a mocked conversation. The 21st is the follow-up
  test. Two older tests were updated to the new rule.
- **Data and frontend:** data validation 0 errors and 1 warning. The frontend needed no change or rebuild (labels come
  from the backend).
- **Report:** one sentence in the report generator was corrected. `report.html` is 15 pages and `slides.html`
  10 slides, no overflow.
- **Real gpt-6-luna runs, with checks on the returned cards:** `output/owner_testing/20261026-010211_age_conflict/`.
  - **First run:** 55/56. The miss was the skipped follow-up offer on desktop turn 1, now fixed.
  - **Re-run after the fix** (desktop, both turns): 18/18.
  - **Earlier UI suite:** 42/42.
- **What the returned cards showed:**
  - No offered card had a failed age rule; the conflicting Animal Haven roles appeared only under "Roles that don't
    fit right now".
  - The other ways to help were Branford Compassion Club support activities with no published age rule, each
    "Needs confirmation". None had a published age rule a 15-year-old meets.
- **API-reported usage:**

  | Run | Turns | Requests | Input tokens | Cached reads | Cache writes | Uncached | Output tokens |
  |---|---|---|---|---|---|---|---|
  | First run | 5 | 20 | 188,504 | 161,779 | 24,205 | 2,520 | 5,031 |
  | Re-run | 2 | 7 | 59,133 | 50,145 | 8,106 | 882 | 2,336 |

- The submission ZIP was not rebuilt; `backup.zip` was untouched.

### Follow-up prompts

None yet.

## Session 19 — 2026-10-26 — Readiness check for the prospective-user test

### Prompt (verbatim)

```text
make sure everything looks good for perspective user testing
```

### What happened

Readiness check only; no participant was involved. The prospective-user test is still pending.

**Walkthrough** (`output/user_test_readiness/20261026-012029/`): the four guide tasks, as a first-time visitor on
the participant's server (port 8001, no traces), on desktop and mobile. 28/28 checks, including one real
gpt-6-luna reply (4 requests; 31,801 input tokens, 26,936 cached, 4,361 cache writes, 504 uncached; 1,135
output).

**Fixed:** "Your answers" showed hours as two rows ("Available hours", "Hours per"); they are now one row, "Hours you
can give: 3 per week". Rebuilt `index-_pNTeHKR.js` and checked in the browser.

**Guide updated** (`docs/user_test_guide.md`):
- The start command now uses port 8001 (8000 is another app), with a health check, a private window and no trace
  saving.
- The consent script now says that Find my fit messages go to an AI model through Portkey, and that the service may
  keep its own logs.
- "Your answers" and "Confirm these details" replace the old "Your preferences".
- New notes cover reply wait times and what to do if the assistant fails.
- The notes template asks for the build file.

**Left as is:** on a phone, the Compare selection bar can cover part of the Find my fit start screen until the person
scrolls.

**Checks:** 231 backend tests; earlier UI suite 42/42.

### Follow-up prompts

None yet.

## Session 20 — 2026-10-26 — One informal prospective-user test: findings, retest, fixes, report

### Prompt (verbatim)

```text
we now have feedback from one real prospective user who tried the app. please document the review, check the reported issues, fix confirmed problems, and update the report and slides. inspect the existing files first and preserve our work.
1. document the user review
create docs/user_test_findings.md. describe this as one informal prospective-user test, separate from owner testing and automated tests.
the participant is a 25-year-old graduate student in New Haven who likes cats, has no car, and can volunteer for 2–3 hours on weekend mornings.
their feedback, summarized in simple language:
“what i liked: the website is cute and easy to read. the sources help me trust the information, and the cat-related suggestions were useful.
my answers: the assistant didn’t use my weekend availability and later seemed to forget that i don’t have a car.
requirements: the chat and the card explained Animal Haven’s one-year commitment differently. they should give the same explanation.
getting there: distance estimates and directions links would help me decide which places i could reach without a car.
what could be clearer: simplify the age requirements, check the town filter, and show fewer repeated warnings while keeping the important ones.”
treat this as paraphrased feedback, not a verbatim quote. keep the participant anonymous. do not invent task timings, ratings, measured time savings, additional participants, or tasks they completed. mark missing session details as not recorded.
2. reproduce the reported problems
test this message through the real app:
“i’m 25 and live in New Haven. i like cats, don’t have a car, and can volunteer for 2–3 hours on Saturday or Sunday mornings. what could fit me?”
follow up with questions about requirements and getting there. check whether the assistant captures and retains age, town, interest in cats, no car, weekend days, morning availability, and the hours range.
preserve “2–3 hours” as a range. if the period or session length is ambiguous, ask rather than silently choosing a value. do not invent a ZIP code.
distinguish participant-reported problems from problems you actually reproduce. record what worked as well.
3. fix profile handling and inconsistent explanations
ensure explicitly stated answers are used and retained across follow-up messages unless the user corrects or removes them. preserve the existing correction, withdrawal, and confirmation behavior.
make the assistant’s explanations agree with the cards and underlying evidence. Animal Haven’s older one-year commitment must carry the same uncertainty wherever it appears.
simplify conflicting-age explanations. when the user meets both published minimums, say “your age meets both published minimums; confirm the organization’s current rule.” keep the conflicting values and sources available in the evidence details.
preserve the rule that someone below every published age minimum is not recommended the role. guardian attendance must not override a rule without supporting evidence.
4. check locations and directions
verify Explore’s town options match the selected geographic scope. wider Connecticut towns should appear only when that scope is enabled. preserve the distinction between a role’s volunteering location and an organization’s address.
use existing verified distance estimates where supported. if a supported ZIP is needed, ask for it optionally rather than guessing.
provide a useful directions link to the verified destination where practical, letting the user enter their starting point and choose transit. clearly identify organization-address fallbacks when the activity location is unknown.
do not invent bus access, travel times, weekend shifts, or transportation eligibility. having no car does not automatically mean someone cannot reach a location.
5. reduce repetitive warnings
review repeated availability and missing-information notices. shorten redundant explanations while preserving important role-specific warnings, source conflicts, and uncertainty.
keep personal fit separate from application availability. unknown must never become unrestricted, free, eligible, or currently accepting applications.
preserve the warm, readable design and avoid unrelated features.
6. verify the changes
add focused regression checks for confirmed profile and matching problems, and run the relevant existing tests.
use real gpt-6-luna calls through Portkey for the conversation checks. inspect the resulting profile and cards, not just the assistant’s summary. record actual API-reported usage without exposing secrets.
check the affected screens on desktop and mobile and rebuild the production frontend if changed.
save new traces and screenshots in a new timestamped directory. never overwrite historical evidence or recovered screenshots. leave backup.zip untouched.
label these checks as developer retesting. do not claim the participant retested or approved the fixes.
7. update the report and slides
replace prospective-user-testing placeholders with the participant profile, summarized feedback, issues reproduced, improvements made, and remaining limitations.
explain that this was one informal test. it does not establish broad usability, adoption, or measured time savings.
update the source scripts and regenerate report.html and slides.html. keep the report self-contained, within 10–15 printed Letter pages, and in the required section order. keep slides within 10 slides. verify both after rebuilding.
keep any still-pending GitHub and fresh-clone requirements accurately marked.
8. document and stop for review
record this prompt accurately in AI_prompts.md. update docs/evidence_summary.md and docs/rubric_checklist.md, distinguishing reported feedback, verified findings, completed changes, and pending work.
show the changed files, actual test results, representative screenshots, and remaining submission tasks.
stop before publishing or rebuilding the submission ZIP.
```

### What happened

**Documented:** `docs/user_test_findings.md`.
- One informal prospective-user test, anonymous, with feedback paraphrased.
- Session details that weren't recorded are marked as not recorded: tasks, times, ratings, a verbatim quote and a
  baseline.

**Reproduced first (developer retesting, not the participant)**, in `output/user_feedback_retest/20261026-013842/before_fixes/`:
the participant's message and two follow-ups through the real app (gpt-6-luna). 25/34 checks passed.
- **Reproduced:**
  - weekend days and mornings were stored as unverified suggestions;
  - "no car" was hidden from Your answers;
  - "2–3 hours" was dropped, and later became a 3-hour session;
  - the age line was hard to read;
  - other Connecticut towns were offered in the Greater New Haven scope;
  - the ZIP and area questions repeated every turn;
  - there were no directions links.
- **Not reproduced:** the one-year commitment mismatch (the chat hedged it as the card did).
- **Worked:** age, town, cats and "no car" were captured; no ZIP was invented; no transit or travel-time claims.

**Fixed:**
- **Hour ranges:** kept as a range (`available_hours_max`) and checked at both ends. A period is taken only from
  explicit words, no session length is chosen from a range, and the app asks what the hours mean.
- **Stated days and times:** verified as the person's words.
- **"No car":** shown and kept.
- **Cards:**
  - a Schedule line on each card;
  - a check that card text describes uncertain rules the way the card does;
  - plain conflicting-age wording (below every minimum is still not recommended; a guardian doesn't override).
- **Locations:** town options follow the scope; directions links (destination only, organization addresses
  labelled).
- **Repetition:** optional questions are asked once; a shared note is shown once; the detail page no longer repeats
  the age-match sentence.
- Correction, withdrawal and confirmation behaviour unchanged.

**Checks:**
- **Backend:** 244 tests, 13 new in `tests/test_user_feedback_fixes.py`; two older tests were updated for the new
  wording. Data validation: 0 errors.
- **Real gpt-6-luna re-run after the fixes:** 34/34. Final screens on desktop and mobile: 23/23. Earlier UI suite:
  42/42. Frontend rebuilt (`index-B920pes1.js`).
- **API-reported usage:**

  | Run | Requests | Input tokens | Cached reads | Cache writes | Uncached | Output tokens |
  |---|---|---|---|---|---|---|
  | Before | 11 | 88,050 | 74,903 | 11,761 | 1,386 | 4,829 |
  | After | 10 | 79,165 | 62,243 | 15,662 | 1,260 | 4,751 |
  | Final screens | 8 | 66,759 | 56,784 | 8,967 | 1,008 | 3,076 |

**Report and slides:**
- The Impact PENDING placeholders were replaced with the participant profile, the feedback, a reported-vs-reproduced
  table, the changes and the limits of one informal test.
- The stale backend test count (110) was updated to 244.
- `report.html` is 15 pages (after trimming) and `slides.html` 10 slides, with no overflow; the GitHub link and fresh
  clone are still marked pending.

**Docs:** `docs/evidence_summary.md`, `docs/rubric_checklist.md`, `docs/deliverables_verification.md`,
`docs/backend_design.md`, `docs/user_test_guide.md` and `README.md` were updated.

**Not done:** the participant hasn't retested; the submission ZIP was not rebuilt; `backup.zip` was untouched.

### Follow-up prompts

None yet.

## Session 21 — 2026-10-26 — Final submission: GitHub repository, fresh clone, final checks

### Prompt (verbatim)

```text
please prepare the project for final submission. keep all work in the existing animal-volunteer project, inspect the current Git state first, and preserve existing files and evidence. no new features are needed.
1. check the original assignment and rubric
reread the original instructions in Final Project/Rubrics and check docs/rubric_checklist.md. use the original assignment as authoritative. identify any remaining submission requirements without claiming unverified items are complete.
2. prepare the GitHub repository
inspect the existing repository, remotes, and authenticated GitHub account. reuse the correct project repository if one already exists. do not initialize a nested repository or overwrite an unrelated remote.
inspect the files to be committed and scan for credentials, real .env files, private local data, backup archives, and unnecessary generated files. check existing Git history for secrets before publishing; report any finding without printing the secret.
include the code, README.md, .env.example, sample dataset, requirements and lockfiles, built frontend, report.html, slides.html, documentation, and relevant sanitized evidence. keep backup.zip untouched and excluded.
prepare the commit and tell me the exact repository destination, visibility, and contents. if creating a repository and no destination or visibility has been established, ask me to choose those before publishing. do not force-push, delete history, or change repository visibility.
3. add the actual repository link
once the repository destination is confirmed, replace GitHub placeholders in the README, report and slide source scripts, and generated deliverables with the actual URL.
distinguish the repository link from a hosted-app URL. do not describe localhost as a publicly accessible app. if the repository is private, check the assignment’s required grader access and report any access still needed.
4. verify the final report and slides
regenerate report.html and slides.html from their source scripts.
verify the report is self-contained, has embedded screenshots, prints to 10–15 US Letter pages, and follows this section order: Title + links, Motivation, What is new here, The agents, Tokenomics, Safety, Impact, Limits + next steps.
verify the reveal.js deck has no more than 10 slides, includes its required screenshots and diagram, and has no clipped text or overflow.
render and visually inspect every report page and slide. check links, image loading, numerical consistency, and remaining placeholders. preserve historical evidence and label older screenshots accurately.
keep feedback, developer retesting, automated tests, and real-run evidence clearly distinguished. do not invent participant quotes, timings, outcomes, or approval of fixes.
5. publish and test a fresh clone
after the repository destination and visibility are settled, push the prepared project using a normal commit and push.
clone it from GitHub into a new temporary folder outside the working project. follow only the README instructions, using a new virtual environment and no dependencies or files borrowed from the working project.
time setup through a usable running app and report the actual elapsed time, environment, and any installation-cache limitations. verify it meets the assignment’s setup requirement.
configure credentials locally without printing or committing them. confirm the documented .env loading behavior works. use an unused port and leave unrelated servers alone.
check the main pages, filters, comparison, ZIP reset, and a real Find my fit conversation through gpt-6-luna via Portkey. verify the response, profile, tool activity, and API-reported usage. do not substitute a mocked response for this check.
if setup fails, fix the README or code, commit and push the fix, and repeat the affected fresh-clone checks. identify the final tested commit.
6. finalize the evidence and checklist
save setup results, final visual checks, and any new traces in a new timestamped output directory. never overwrite historical or recovered screenshots.
update AI_prompts.md, docs/rubric_checklist.md, and the relevant verification records with actual results. distinguish completed, verified, and pending items. ensure documentation changes are committed and pushed.
7. rebuild the clean submission ZIP
rebuild Final_Project.zip in the established location outside the repository. package only Final Project/animal-volunteer/.
exclude real .env files, credentials, .venv, node_modules, local_data, caches, .DS_Store, backup files, and all nested archives. include .env.example, the built frontend, report.html, slides.html, the sample dataset, documentation, and sanitized evidence.
leave backup.zip untouched. inspect the finished ZIP for excluded files and secrets without printing secret values. extract it into a separate temporary folder and confirm the expected files are present.
8. give me the final submission summary
show the GitHub URL and visibility, final commit, fresh-clone setup time and results, report page count, slide count, ZIP path and size, and any unresolved requirement.
list exactly what the original assignment requires me to upload or paste into Canvas. distinguish required items from optional items. do not submit to Canvas for me.
```

### What happened

**Assignment re-read** (`Final Project/Rubrics.pdf`, authoritative).
- **Canvas:** the repo link, `report.html` and `slides.html`; an optional 2–3 minute demo video.
- **Repo:** public, or private with `zlisto` added.
- **Running it:** a fresh clone runs within 10 minutes with `.env` in the repo or one folder up.

**Repository:**
- There was no Git repository before, and none in the parent folders, so this is not a nested repository.
- `git init` was run in `animal-volunteer/`. Commits use the GitHub no-reply email, and `*.tsbuildinfo` was added to
  `.gitignore`.
- **Scan of the 718 files to commit:** no key value, no token patterns, no real `.env` (only `.env.example`) and no
  personal email. `local_data/`, `.venv`, `node_modules` and archives are excluded, and `backup.zip` lies outside the
  repository.
- Downloading the GitHub CLI was first blocked by the permission system. Rhea approved it, and chose
  `rheasong3411/final-project`, public; the existing `gh` keyring login was reused.
- The repo was created and pushed with a normal push (`c3f1e0a`).

**Links:** the repository URL went into the README (with clone steps, `cd final-project`), the report title section and
slide 1. The app is described as not hosted; localhost is never presented as a public link.

**Fresh clone from GitHub** (commit `c3f1e0a`, new temporary folder, new venv, README steps only):
- **Setup:** about 23 s of setup commands to a running app, with the pip cache off and `PORTKEY_API_KEY` unset.
- **.env loading:** both locations worked.
- **App checks:** 25/25.
- **Find my fit:**
  - The first attempt's script stopped on a checkbox call.
  - A second identical request was a gateway cache replay (identical usage), so it doesn't count as fresh.
  - A third, with the cache bypassed, was fresh (`REFRESH`). Its tools were update_location_preferences,
    search_opportunities and assess_profile. Its profile kept age 25, New Haven, no car, cats, Saturday mornings and
    2–3 hours.
  - API-reported usage of the fresh run: 4 requests; 32,754 input tokens (27,959 cached, 4,291 cache writes); 1,503
    output tokens.

**Report and slides:**
- **Report:** 15 pages, in the required section order, with 7 embedded images; every page was inspected.
- **Slides:** 10 slides with the diagram and 5 screenshots; every slide was inspected.
- **Links:** all 26 returned 200.
- **Fixes after inspection:** slide 3's location row, slide 6's build label, slide 10's testing line, and slide 5's notes.

**Records:** evidence in `output/final_submission/`. `docs/rubric_checklist.md`, `docs/deliverables_verification.md` and
`docs/evidence_summary.md` were updated.

**Still Rhea's to do:** the Canvas submission, and an optional demo video. No verbatim user quote or timing was
recorded.

### Follow-up prompts

None yet.

## Session 22 — 2026-10-26 — Participant quotes added

### Prompt (verbatim)

```text
some quotes to add: 

“Every requirement shows where it came from.”
“The design is calm, readable and looks trustworthy.”
“I did say them, so that made the assistant seem broken.”
“I'd still have to visit three websites and probably email them.”
```

### What happened

**Where the quotes went:** the four quotes were treated as the informal prospective user's own words and added
verbatim to:
- `docs/user_test_findings.md`;
- report §7 Impact (the first three) and §8 Limits (the fourth, about still contacting organizations);
- slide 9 (two of them).

The placement of "I did say them…" next to the answers the assistant didn't use is our reading, and is labelled as
such in the findings document.

**Keeping the report at 15 pages:** the report went to 16 pages. The main cause was the feedback table moving whole to
the next page and leaving a gap. Fixes:
- The table may now split, with its header repeated.
- The evidence-index paragraph was shortened.
- One repeated sentence was removed.
- The Tokenomics limits were merged into one paragraph.

Result: `report.html` is 15 pages with 0 external requests, and `slides.html` is 10 slides with no overflow. Renders are
in `output/final_submission/20261026-023428_participant_quotes/`.

**Records:** the rubric (E6, G7, H14), the evidence summary and the deliverables verification were updated. There is
still no session timing or session screenshot.

### Follow-up prompts

None yet.

## Session 23 — 2026-10-26 — Self-grading against the rubric, and fixes

### Prompt (verbatim)

```text
if you were to grade this project based on the current version - would it be 100/100? if not, what are the problems - fix them
```

### What happened

**Estimate:** about 88–93/100 before these fixes (the assistant's estimate, not the course staff's).

**Fixable gaps:**
- the step-by-step run's screenshots weren't from that run, and some were from older builds;
- older-build screenshots elsewhere;
- a cost figure measured before later changes;
- the run steps were far down the README.

**Not fixable by code:** novelty is a judgment call, and the Impact evidence is one informal test without timings.

**Fixes:**
- **New runs:** a traced walkthrough run (`da50c35fac69`) and a safety run (`cdb992fe4e6c`) on the final build, with
  real gpt-6-luna fresh calls. Report §4 and §6 and slides 6 and 8 now use their own screenshots, plus an in-app "Run
  details" token screenshot.
- **Cost:** a spot check of 10 fresh runs today averages $0.00160 per run, slightly below the report's $0.00185, so
  the scaled costs are conservative.
- **App bugs** found in the new screenshots:
  - a card's shared note was squeezed into the label column (CSS fixed, frontend rebuilt);
  - an overlapping follow-up question wasn't caught (regex fixed, test added).
- **README:** a quick start now sits at the top.
- **Report layout:** tables may split across pages with repeated headers; the report stays at 15 pages.

**Checks:** 245 tests. Report 15 pages; slides 10, with no overflow. All pages and slides were inspected. Evidence is in
`output/final_submission/20261026-023657_grading_fixes/`.

### Follow-up prompts

None yet.

## Session 24 — 2026-10-26 — Toward 100/100: measured impact, demo video, timed-test kit

### Prompt (verbatim)

```text
so can you fix it to make it 100/100
```

### What happened

**Answer given:** a 100/100 can't be guaranteed. The idea score is the graders' judgment, and the strongest Impact
evidence (a timed comparison with a real person) needs a session that Rhea runs. Hosting was not done, because earlier
sessions said not to deploy and a public server would expose the course key to misuse.

**Done:**
- **Impact numbers measured from the dataset:**
  - checking Greater New Haven's 28 described roles by hand means reading 13 pages across 5 organizations;
  - 15 roles have their rules split across 2–4 pages, and 10 have uncertain or conflicting rules;
  - a Find my fit reply takes a median of 22 s (10 fresh runs, 16–39 s);
  - no time saving is claimed.

  These went into report §7. To keep it at 15 pages, the duplicate quote in Limits was removed, the Impact bullets and
  the "next month" list were tightened, and one Session 6 side note was cut.
- **Demo video draft:** `output/demo_video/20261026-025108/demo_video_draft.webm`, 2 min 27 s, captioned, with real
  gpt-6-luna runs (traced). Take 1 was superseded (a caption mismatch and the comparison bar covering the chat) and is
  kept outside the repository.
- **Timed comparison kit:** `docs/timed_comparison_kit.md` (prepared, not run).

**Checks:** report 15 pages; slides 10, no overflow.

### Follow-up prompts

None yet.
