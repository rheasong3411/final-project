# Backend design record (for the report)

Status as of 2026-10-25 (Session 5): backend and frontend built and integrated; tested offline, in a real
browser, and with real `gpt-6-luna` runs on synthetic inputs. **Not done yet:** report, slides, cost
analysis, cost-saving comparison, fresh-clone dry run, and prospective-user testing.

## Architecture

```
FastAPI (backend/api.py)
 ├─ GET  /api/health, /api/organizations, /api/filters, /api/opportunities, /api/opportunities/{id}
 ├─ POST /api/opportunities/{id}/assess  ─┐
 ├─ POST /api/alternatives               ─┤→ matching.py (plain Python, deterministic)
 └─ POST /api/assistant → agent.run_assistant
        └─ ONE PydanticAI agent (gpt-6-luna via Portkey, OpenAI Responses API)
             tools (tools.py): search_opportunities · get_opportunity_details · assess_profile
                               · find_alternatives · get_application_checklist
             all tools read only data.py (in-memory JSON) and matching.py
        → output validator → server assembles the final response from deterministic data
```

**Why one agent.** The task is a single loop: understand the request, search, assess, explain. All
eligibility logic is ordinary Python, so a second "judge" agent would add tokens without adding a
distinct responsibility.

**Division of labour.**
- **The model decides:** which records to look at, which profile facts the person stated, and how to
  explain the results in plain language. It also writes the follow-up questions.
- **The code decides:** every met / not_met / needs_confirmation result, application status, costs,
  sources and application checklists.

## Model and gateway

- **Model:** `gpt-6-luna` only, defined once in `backend/config.py` as `MODEL_NAME`. Every real response
  identified itself as `gpt-6-luna-global`.
- **Gateway:** Portkey at `https://api.portkey.ai/v1`. The base URL comes from the Portkey docs and was
  confirmed with a probe call (status `completed`).
- **API:** the OpenAI Responses API, via PydanticAI `OpenAIResponsesModel` and the OpenAI SDK. In HW5,
  chat completions rejected tools plus reasoning for this model.
- **No fallback:** if a call fails, the error is returned. The app never switches to another model.

## Matching rules (backend/matching.py)

- **Per-requirement results:** `met`, `not_met` or `needs_confirmation`. Each result records the
  requirement, the profile fields used, an explanation, source IDs and evidence quotes.
- **When `not_met` is allowed:** only for `published_applicable` requirements, plus one exception added
  2026-10-26: a `conflicting` minimum age where every published version (read leniently, "over 18" = 18) is above
  the person's age. A test checks this across every opportunity and 80 synthetic profiles.
- **Conflicting or uncertain rules:** never exclude anyone, except for that age case. There the role is kept out
  of recommendations and alternatives, the conflict and both quotes stay, and the person is told to confirm the
  current rule. A single uncertain version (CHS fosters: "over 18 but children can assist their parents") and
  unpublished rules stay `needs_confirmation`, and a guardian never overrides an age rule.
  - The result is always `needs_confirmation`. If the person meets every published version (for example, age
    30 vs. "18" and "21"), `listed_value_matched` is true and a note says so; until 2026-10-26 this case was
    `met` (changed after owner testing, so green labels mean an applicable, supported rule).
  - A question for the organization is raised.
- **Missing answers and unpublished rules:**
  - A missing profile answer gives `needs_confirmation`.
  - An unpublished rule is listed as "not published (not the same as 'no minimum')" and is never treated
    as satisfied.
- **Guardians:** a guardian rule is only applied where the source states one. For minors where no rule is
  published, the result is `needs_confirmation` with "does not mean a guardian is not required".
- **Commitment types:**
  - `one_time` never gets recurring hours or month minimums.
  - `variable` shows the published wording.
  - Typical durations are never treated as minimums.
- **Hours conversion** (only when the periods differ), using 4 to 31/7 weeks per month:
  - Weekly availability vs. a monthly minimum: `met` if 4 × weekly ≥ minimum; `not_met` if
    (31/7) × weekly < minimum; otherwise `needs_confirmation`.
  - Monthly availability vs. a weekly minimum: `not_met` if monthly < 4 × weekly minimum; otherwise
    `needs_confirmation`.
- **Schedules:** published schedules are free text, so they are always `needs_confirmation` and shown
  next to the person's availability. Orientation info and dated notices are notes only, never
  availability.
- **Overall result:**
  - `not_met` if any applicable requirement is clearly unmet.
  - Otherwise `needs_confirmation` if anything is unresolved.
  - Otherwise `meets_published_requirements_checked` ("…subject to the organization's confirmation").
- **Kept separate from fit:** application status (three labels; "Confirm with organization" ≠ open) and
  placement or shift availability (always "not published", except listed CHS open shifts, which are
  marked as not a booking).
- **Browsing and record types:** default browsing shows `described_volunteer_role` only. Interest areas
  and independent activities appear as labelled alternatives.

## Session 4 corrections (2026-10-25)

**One consistent profile per run** (`backend/tools.py`, `update_profile`):
- The run has a single `deps.profile`. Each field records where it came from: `app`, `user_stated`,
  `inferred` or `user_correction`.
- Inferred values only fill gaps.
- A stated value that conflicts with an existing value is **not** applied unless the model marks the
  field in `corrected_fields`. The conflict is logged in `profile_changes`.
- Explicit corrections override earlier values, including app-supplied ones.
- Any change recomputes **all** stored assessments. Each assessment carries the `profile_fingerprint` it
  was computed with.
- The output validator only accepts current assessments, and the response reuses those exact objects,
  never recomputing them with another profile.
- `profile_used`, `profile_provenance` and `profile_changes` are returned.

**One-time sessions** (`matching._sessions`):
- Session lengths published per session (for example "3-4 hours, one time") become a `session_length`
  requirement, checked against the new optional `max_session_hours`. Weekly or monthly availability
  never answers this.
- Unknown → `needs_confirmation`. At or above the top of the range → `met`. Below the bottom → `not_met`
  (only when `published_applicable`). Inside the range → `needs_confirmation`.
- Recurring hours and month minimums still never apply to one-time activities.

**Alternatives and evidence:**
- `recommendations` and `alternative_ids` must have a current assessment. Recommendations can't be
  `not_met`. Alternatives can't be `not_met` or explicitly closed.
- Unsuitable roles can still be discussed, through `non_matches` (returned as `explained_non_matches`).
- Cited sources must belong to a record that is recommended, offered or discussed.
- The response includes every source ID used by the assessments, application status and checklists of
  all shown records.

**Search coverage:**
- `town` is residence. A town filter (`only_in_town`) is used only for an explicit restriction
  (`restrict_to_town`).
- Search lists applications that aren't explicitly closed first.
- If every match is closed or nothing matches, the search returns `broader_options` in the same scope.
- The validator rejects a final answer with no suitable non-closed option unless a broad search or
  `find_alternatives` was done.
- It never widens to wider Connecticut on its own.

**Claim checks added:**
- Asserting that a schedule fits is rejected; hedged or negated wording is allowed.
- "You are eligible" and "you qualify" are rejected.

## Session 5: profile confirmation and frontend integration (2026-10-25)

**Problem fixed:** model-assigned provenance labels alone did not prove that the person stated a fact.

**New rule** (`backend/tools.py`, `update_profile`):
- **`confirmed`:** answers from the form or a **Confirm** click arrive in the request's `profile`. This
  is the trusted path, and chat never overrides it.
- **`from_message`:** a chat fact is used only with a supporting quote that appears verbatim in the
  person's own messages. For numbers, the quote must contain the number; for hours period or guardian, a
  matching keyword. The UI shows these with the person's words and a Confirm / Not right choice.
- **`suggested`:** anything else. For the eligibility fields (age, guardian, hours, hours period,
  commitment months, session length), suggestions are **never used** in requirement checks until
  confirmed.
- **Across turns:** facts are carried in `message_facts` and re-verified by the server each turn.
- **"Not right":** marked fields go in `declined_fields` and are never re-applied from chat.

**Real evidence:** in the integrated runs, "for at least a year" (no number) stayed a suggestion and was
not used, and Luna asked the person to confirm it each time. 7 new pytest tests cover this
(`tests/test_profile_confirmation.py`). This reduces extraction errors but cannot eliminate them.

**Frontend integration:**
- `GET /api/opportunities` summaries now include `minimum_age_status` and `uncertain_requirements`, so
  cards can say "Not published" versus "Confirm with organization".
- FastAPI serves `frontend/dist`, with direct loads of client routes falling back to `index.html`.
  `/api/*` routes are unchanged, unknown API paths stay JSON 404s, and a path-traversal attempt returned
  404.
- `AVF_SAVE_TRACES=1` (off by default) saves traces of **synthetic** UI tests only.

**Gateway-cache finding (relevant to tokenomics):**
- Portkey replayed stored responses for two **identical** repeated requests: the same provider response
  IDs, at 1.5–2.6 s instead of 18–25 s.
- Every model call now records the `x-portkey-cache-status` header (`gateway_cache_status`, and
  `gateway_cache_hits` in the usage summary).
- Replays repeat the original `usage` numbers and must not be counted as new tokens. Whether a cached
  replay is billed has not been verified.
- Exact-match caching could be a cost lever for repeated questions, but it has not been measured yet.

## Session 6: evidence (2026-10-25)

- **Cost optimization, adopted as the default (`AVF_TOOL_PROFILE=compact`):**
  - The details tool no longer repeats what `assess_profile` returns, and evidence quotes come only on
    request.
  - Measured on 12 fresh real runs (forced-refresh header, all `REFRESH`): −33% model cost per run at
    course rates, quality 54/54 vs 54/54.
  - See `output/cost_eval/comparison.md`.
- **Token accounting fix:** raw usage reports **cache writes** separately. Uncached input is now input −
  cached reads − cache writes (course Lecture 11 rule), and `usage` includes
  `cache_write_input_tokens`.
- **Pricing:** gpt-6-luna course-published and OpenAI Standard short-context rates, verified
  2026-10-25. Actual billing (Azure via Portkey, course arrangement) is not verified. See
  `output/cost_eval/tokenomics.md`.
- **Safety in the website:** the application-level defense and the upstream filter are shown
  separately (`output/agent_runs/README.md`). Limits are tested with mocked models
  (`tests/test_limits.py`).
- **Setup:** a clean-copy rehearsal took about 33 s automated, and both `.env` locations worked. This
  was not yet a GitHub clone.

## Session 10: location memory, optional ZIP distances, Find my fit display (2026-10-25)

**Three separate location facts** (`VolunteerProfile`): where the person lives (`town`, `zip_code`,
`prefers_not_to_share_zip`), how they travel (`has_car`, `wants_nearby`) and where they will volunteer
(`volunteer_only_in`, `nearby_towns_ok`). `restrict_to_town` was replaced by `volunteer_only_in`.
- A new tool, `update_location_preferences`, records them with the person's own words. Town, ZIP and the
  area limit now need a verified quote (like the eligibility fields): a suggested value is shown but
  never used. A ZIP quote must contain the five digits, so "next to Yale SOM" can't become a ZIP.
- Location fields are excluded from the assessment fingerprint (they never change fit); `town` stays
  in it because residence rules (non-resident fees, foster town lists) use it.
- Memory across long conversations: older user messages travel as `earlier_user_messages`, used only to
  re-verify remembered facts; the model still sees 10 turns.
- Server-added follow-ups (`agent.follow_ups`): the town question, "Do you need to stay within <town>,
  or can you travel to nearby towns?", the optional ZIP offer, and a different-activity-or-widen offer
  when an area limit leaves nothing open. A repeated question about a known town is dropped.

**Area limit enforced, not suggested.** `Dataset.confirmed_in_town` requires the role's **own**
published location (`location_town`). An organization's town alone doesn't count: FNHAS adoption events
happen "throughout the Greater New Haven area". Search, `find_alternatives`, the validator and
`in_chosen_area` all use this rule. Suitable records outside the limit can only appear as
`outside_area_ids`, which the page labels "only if you choose to widen the area".

**ZIP areas and destinations** (`backend/geo.py`, `data/geo/`, `data/volunteer_locations.json`):
- ZIP areas: 289 Connecticut ZCTAs from the U.S. Census 2026 Gazetteer (internal points; public domain).
  Status is `invalid_format`, `outside_coverage` (not 06xxx), `not_in_dataset` (e.g. 06520, 06501) or
  `supported`. A ZIP never widens the search.
- Destinations: nine sites re-verified on official pages on 2026-10-25 (30/30 quotes found in page
  snapshots) and geocoded with the U.S. Census Geocoder (exactly one match each). 15 roles are
  `verified_site`; 6 are only candidates, 6 happen at home and 37 have no published location. Only
  verified roles get a distance or a maps link.
- Distance: haversine from the ZIP area's internal point, rounded (under 1 mile / nearest 0.5 below
  10 / nearest 1). Independent check against a WGS84 geodesic (`pyproj` 3.8.0): at most 0.10 mile
  apart over 18 pairs; one pair on a rounding boundary rounds differently (06513 to the FNHAS shelter:
  3.747 vs 3.756 miles, shown as "3.5" vs "4" miles). See `output/location_check/`.
- The agent sees distances only as tool text (`travel.distance`). The validator rejects any other mile
  figure, travel times, and "walkable", "convenient" or "by bus" claims unless negated.

**Uncertain rules in prose.** For requirements whose applicability is `needs_confirmation` or
`conflicting` (for example Animal Haven's older-form 12 months and 2 hours a week), a sentence that
names the record and states the number must say it needs confirmation. A leading question ("Can you
meet the required 12 months?") is rejected; open questions are used instead. The check is scoped to
sentences about that record, so FNHAS's published 12-month rule is unaffected (a bug found in the first
real run and fixed).

**Privacy.** ZIPs are sent only in POST bodies (`/api/location/estimates`), never in URLs or access logs.
The model prompt shows a form-confirmed ZIP as "provided; status: supported", not the digits.
`location_context` never contains the digits. Every saved trace runs through
`run_log.redact_locations`, which replaces `zip_code` values and standalone 5-digit numbers.

**Frontend.** Only the latest exchange is prominent; earlier turns, cards and checklists collapse into
"Previous conversation". While a request runs, the new message shows with "Updating your results…" and
the earlier answer is collapsed. After a failure, the draft stays, and "Show my last results (based on
earlier answers)" reopens the last results under a "Based on your earlier answers" notice. Explore and
the detail page gain an optional ZIP field, "Closest estimated location" sorting (unknown last, with a
note), distance lines and "Check location in maps" (Google Maps search URL with the destination only).
Explore's commitment filter is exactly "Any commitment", "One-time", "Ongoing", "Flexible / varies";
unknown records stay under "Any commitment" and their cards say "Time commitment: ask organization".

**Tested** (all inputs synthetic): 93 backend tests; type check and production build; 48/48 Explore and
detail browser checks (desktop and mobile); 118/119 real-AI conversation checks through the website
(12 fresh gpt-6-luna runs, all `REFRESH`; the one failed check is a wording regex, and manual review
found the answer correct); 42/42 earlier non-AI browser checks.

## Session 11: structured replies, distance binding, geo validation, application recheck (2026-10-25)

- **Distance binding.** The Session 10 validator let a mileage pass if it matched *any* returned distance, so
  one role's figure could be attributed to another. Reliable claim-to-role matching would need fragile text
  parsing, so the written reply may now contain **no** distance or mileage (digits or words). Each option's
  estimate is rendered from its own `Recommendation.location.distance`. Regression test:
  `test_swapped_distance_claim_is_rejected_and_cards_keep_their_own_distance` (Animal Haven about 6 miles vs Branford
  Compassion Club about 9 miles, deliberately swapped).
- **Structured replies.** `AgentOutput.answer` is a brief opening (instructions ask for under about 70 words;
  hard cap 1,200 characters), `why_relevant` is one sentence, and at most 2 follow-ups are shown (server ones
  first). The page renders each option's facts as labelled lines from the structured results: location,
  estimated distance, minimum age, guardian, hours, commitment, application status and fit, with the
  person's own answer ("You: 23") and each requirement's new `uncertainty_note` beside it. Evidence, detailed
  assessments and the checklist are inside the option card, expandable.
- **Next actions** (`Dataset.next_actions`): "Ask about availability" (contact page) plus "Check application
  details" unless a page explicitly says it is accepting (then only details); closed roles get "Check
  application details".
- **"Your answers" panel.** A compact summary: confirmed and "from chat" answers, one "Confirm these details"
  action for the chat facts, Edit and Remove per field, quotations in an expandable section, and unverified
  suggestions listed separately and never confirmed automatically. The old "Only answers you confirm are
  trusted" sentence was removed: chat facts with a verified quote *are* used provisionally.
- **Geo validation** in `scripts/validate_data.py` (+12 self-tests): ZIP-area file and `volunteer_locations.json`.
- **Application recheck:** see `output/data_audit.md` (Session 11 section). Branford's general role is now
  `explicitly_closed`; Tails to Trails gained its form's requirements (age 25 and more).
- **Measured cost of the current agent:** `output/cost_eval/current_agent_session11.md`: mean $0.00185 per run over
  17 fresh runs, kept separate from the Session 6 experiment ($0.00128 for the 5-tool compact profile then).
- **Tested:** 94 backend tests; 48 validator self-tests; type check and build; 213/214 real-AI website checks
  (one wording-regex miss, reviewed manually), 50/50 Explore/detail and 42/42 earlier browser checks.

## Session 12: closed roles out of discovery, location categories, "About" wording (2026-10-25)

- **Closed roles:** `Dataset.search(include_closed=False)` by default, so `/api/opportunities` (Home, Explore), the
  agent's `search_opportunities` and `find_alternatives` never list `explicitly_closed` records. The list route reports
  `closed_hidden`. `include_closed=true` exists for the API and for the agent when a person names a specific role;
  the validator rejects a closed role as a recommendation (only `non_matches`). Statuses themselves are unchanged.
  The `application_status` list parameter and Explore filter were removed; old URLs are cleaned.
- **Labels:** "Accepting applications" / "Ask about availability" / "Applications closed"; one shared note that
  accepting applications doesn't guarantee a placement or shift.
- **Location categories** (`geo.location_of().kind`): verified_site (15), organization_location (31), town_only (0 in
  the current data; tested with a synthetic variant), home_based (6), unknown (12). Organization locations come from
  the new `organization_locations` list (one verified site per organization, none for CHS's three sites or Cat Tales'
  P.O. box). Home-based records carry sourced travel notes (CHS supply pickup and meet-and-greets, FNHAS orientation,
  BCC vet-hospital proximity; PAWS: none published). Town references: Census 2026 town internal points.
- **Estimates** carry `type`, `display`, `secondary`, `destination_label` and unrounded `sort_miles`. Sorting ranks only
  `volunteering_site` estimates; other leads are a separate, unranked group in Explore and Find my fit.
- **Tested:** 110 backend tests, 52 validator self-tests, 41/41 location quotes; browser: 56/56 status and location
  checks without AI, 42/42 earlier suite, 274/275 real-AI checks (the same wording-regex miss, reviewed manually).

## Session 16: destination fallback and one combined distance sort (2026-10-25)

- **Destination order** (`Geo.distance`): (1) the role's verified volunteering site (`type="volunteering_site"`);
  (2) when the activity site is unknown, the organization's verified physical location (`organization_location`), or,
  for an organization with several verified sites and none tied to the role (CHS), the nearest of them, named
  (`organization_nearest_site`); (3) nothing. P.O. boxes and mailing addresses are never destinations. A role's own
  site still wins for multi-site organizations (for example CHS Newington roles).
- **Home-based** records keep "Help from your home" as the primary text. A sourced travel site (supply pickup,
  orientation) is `related_site` and sortable; otherwise the organization's location is `organization_reference` with
  `sort_miles = null` (shown as reference only, sorted with the no-distance records, never 0 miles).
- **Fields:** each estimate carries `type`, rounded `miles`, unrounded `sort_miles`, `place_label`, `display`,
  `label` (`place_label · display`), `secondary` and the shared explanation ("Distances are straight-line estimates
  from your ZIP area. For some activities, the distance is to the organization; the activity location may differ.").
  `location_of()` adds `place_label` / `place_note` for cards without a ZIP. The category counts are now
  verified_site 15, organization_location 33, home_based 6, unknown 10 (CHS records without a role site moved from
  unknown to organization_location), town_only 0.
- **Sorting:** the frontend's `sortByDistance` and the agent's `_distance_key` both sort one list on `sort_miles`
  (null last, stable). The separate "Other leads" group was removed. Town limits are unchanged: they use the role's
  own published town, never the organization's location.
- **Tested:** 190 backend tests (14 new or rewritten location tests), geo validation, 62/62 browser checks without AI,
  14/14 real-AI Find my fit checks, 42/42 + 44/44 + 46/46 earlier suites.

## Owner-testing fixes (2026-10-26)

Found in manual testing by the project owner (not a prospective-user test).
- **Corrections and explicit clearing** (`tools.withdraw_fields`, `tools.detect_withdrawals`, `update_profile`):
  corrections and withdrawals must be quoted from the current message (`AgentDeps.current_message`); they apply
  to form-confirmed answers too (`confirmed_overrides`). Withdrawn fields become the field's default (unknown),
  hours and hours period are cleared together, and `withdrawn_fields` round-trips through the browser so history
  can't restore them. Deterministic detection runs after the earlier facts are re-verified and before the model
  runs; `assess_profile(cleared_fields=…)` lets the model clear fields too. A new verified value in the current
  message replaces an earlier chat value.
- **Uncertainty** (`matching._Builder.add`): `met` is only possible for `published_applicable` rules;
  `listed_value_matched` carries the numerical comparison. The overall summary for `needs_confirmation` starts
  "Possible fit — confirm requirements".
- **Evidence** (`matching.dedupe_evidence`, frontend `lib/evidence.ts`): exact repeats and excerpts contained in a
  longer passage from the same source are hidden; distinct sources and conflicts are kept.
- **Age restrictions** (`agent.follow_ups`, instructions step 4): no switching activity or area without asking; a
  deterministic follow-up offers other ways to help after an age or guardian rule rules out every option.
- **Traces:** `AVF_TRACE_DIR` sends saved traces to a run-specific folder.

## Prospective-user feedback fixes (2026-10-26)

- `VolunteerProfile.available_hours_max` keeps a stated range; `matching._hours` decides only when both ends agree.
  `tools.quote_supports`: a range quote can't yield a single chosen number or a session length; `hours_period`
  needs explicit period words; stated day/time words verify `available_days`/`available_times` even if the model
  marked them inferred. `run_assistant` captures a range from the newest message deterministically.
- `profile_facts` shows a stated "no" (has_car False); `AssistantRequest.asked_follow_ups` stops optional questions
  repeating; a new deterministic question asks what an hours amount covers.
- `matching._schedule` adds a "No days or times published" question when the person gave days/times; conflicting
  ages use plain wording; the validator checks card text (why_relevant/why_not) for unhedged uncertain rules.
- `Dataset.filter_values()["towns_by_scope"]`; `Site.public()["directions_url"]` (destination only).

## Safety measures

| Risk | Defense (built) | Evidence |
|---|---|---|
| Prompt injection, user or dataset text | Instructions mark all user, history and tool text as untrusted. The message is wrapped in delimiters. Tools are limited to dataset reads and the matcher (no shell, files, web or forms). | Real run `03b_prompt_injection_subtle__ab609bc8e385`: the model refused the key and approval and kept the deterministic `not_met`. |
| Blatant jailbreak text | Provider content filter (Azure OpenAI, via Portkey), mapped to a clear `content_filtered` error with no recommendations | Real run `03_prompt_injection__3cd46b0bd09a` |
| Key leakage | Key loaded only server-side; never in tools, deps, responses or logs. The output validator rejects any answer containing the key. Responses and traces are scrubbed. Repo scan found 0 files containing the key. | `tests/test_agent_mocked.py::test_mock_secret_in_answer_is_blocked` (mock); real runs' `key_not_in_response` / `key_not_in_trace` checks |
| Model overriding the rules | `stated_fit` must equal the deterministic result. Recommended IDs must have been assessed in this run. IDs and sources must exist. Application steps are built only by code. | Mock tests: override → `invalid_model_output`; invented ID → retried and corrected |
| False approval claims | Regex check on "you are approved/accepted", "guarantee a spot", "submitted your application" | `test_mock_approval_claim_is_blocked` (mock) |
| Invented facts | Only tool data is used. The answer never generates transit, remote options or shifts. Distances come only from `geo.py` and must match a tool's text exactly (Session 10). Checklists are deterministic. | Real-run answers; `tests/test_location_agent.py` |
| Location over-collection | ZIP is optional, five digits, never in URLs, redacted from saved traces, and never inferred from landmarks. No street address is asked for. | `tests/test_geo.py::test_saved_traces_redact_zip_codes`; `test_town_zip_and_transport_need_the_persons_own_words` |
| Loops and overspending | Per call: ≤8 model requests, ≤14 tool calls, ≤120k tokens, ≤4,000 output tokens per response, 60 s per request, 180 s per run, 2 output retries. Per client: 6 assistant calls a minute, 2 concurrent runs. Message ≤2,000 characters; history ≤10 turns. | `backend/config.py`; real runs used 3–6 requests |
| Model or credential failures | Clear error codes: `credentials_missing`, `credentials_rejected`, `model_unavailable`, `rate_limited`, `timeout`, `content_filtered`, `usage_limit_exceeded`, `invalid_model_output`. Never fake recommendations. | `test_assistant_without_credentials_gives_clear_error`; failed trace `4028abafd695` |
| Over-collecting personal data | The profile has only matching fields (age in years, town, hours and so on). Extra fields such as birth date, address or medical history are rejected with 422. API runs log metrics only, to gitignored `local_data/`. | `test_assess_route_and_profile_privacy` |

## Evidence locations

- **Real runs:** `output/agent_runs/` (traces, `runs_index.jsonl`, and a `README.md` with the usage table).
- **Usage:** mean over 6 successful synthetic runs: 21,575 input tokens (14,333 cached), 1,279 output
  tokens, 4.2 requests, 13.6 s. API-reported; see the provenance note in each trace. One real API call
  (`8c18f82ac5aa`) used 48,330 input (37,565 cached) and 1,883 output tokens.
- **Cost:** **pending**. No verified gpt-6-luna price has been recorded, and the provider returned no cost.
- **Tests:**
  - `tests/`: 51 pytest tests (37, plus 14 Session 4 regression tests in `tests/test_regressions.py`). The matching and API tests use the real dataset with synthetic profiles;
    the agent tests use a **mocked** model.
  - `scripts/test_validate_data.py`: 36 data-validator self-tests.

- **Real run after the Session 4 corrections:** `output/agent_runs/01_normal_match__9f57e5508031.json`.
  4 requests, 28,708 input tokens (17,720 cached), 1,077 output tokens, 16.8 s. All 12 automated checks
  pass.

## Known limitations at this checkpoint

- **Ports:** on this machine another project's server occupies port 8000. Testing used port 8001; the
  documented default is 8000.
- **Model rewording:** the model still rephrases deterministic results in its own words. The structured
  cards beside the reply show the actual results.

- **Provenance labels come from the model.** In the post-fix run it labelled
  `commitment_preference: recurring` as user-stated, although the person never said it. Code can't
  verify whether a fact was stated or inferred.
- **Older traces predate Session 4.** Cases 02–05 were not re-run under the new code.

- **Schedules:** the matcher doesn't auto-judge free-text schedules, and the model sometimes comments on
  schedule fit in prose (for example "weekday afternoons fit Mon–Sat 12:30–4:30"). The deterministic
  item stays `needs_confirmation`.
- **Search breadth:** the agent may search narrowly, for example only the person's town, and miss nearby
  towns. *(Session 10: approximate straight-line distances now exist for the 15 roles at verified sites;
  the other 49 records show "Distance unavailable".)*
- **Distances (Session 10):** straight-line only, from a ZIP area's internal point, not from anyone's home.
  No routing, travel time or transit data. Interpolated site coordinates can be off by tens to a few
  hundred metres. Values near a rounding boundary can round either way.
- **Profile extraction:** facts are taken from free text by the model (for example, "weekday afternoons"
  becomes Mon–Fri afternoons). Fields the app supplies take precedence.
- **Token use and caching:** usage varies (16k–48k input tokens per run). Prompt caching is automatic
  (14k cached on average); no deliberate cost optimization has been done or measured yet.
