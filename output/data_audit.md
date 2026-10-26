# Data audit — animal-volunteer dataset (schema v2, after the correction pass)

**Prepared:** 2026-10-25 (America/New_York). First version was written around 16:06 EDT; this
revision follows the correction pass (around 16:20 EDT).

**Sources:** 34 sources were fetched 15:50–15:53 EDT, and one recheck
(`chs_newington_openings_recheck`) was fetched at 16:15:56 EDT.

**Not claimed:** this audit does not show that every record is complete, that any opportunity is
open now, or that meeting the published rules makes anyone eligible. Organizations make those
decisions.

## 0. What changed in the correction pass

| Change | Result |
|---|---|
| Guardian rules | 31 `guardian_requirement` values that said "not required" only because the minimum age was 18+ were set to **`null`**, and their 31 `Derived:` evidence entries were removed. Minimum ages were kept. Only the **3 explicitly published** guardian rules remain: Branford general (under 16), PAWS Families for Felines (13–17) and PAWS Reading to Rescues (parent attends). The validator now rejects derived guardian values. |
| Requirement applicability | New `requirement_applicability` object: 168 field assessments (125 `published_applicable`, 33 `needs_confirmation`, 10 `conflicting`), each with source IDs and a reason. |
| Animal Haven possibly-legacy form | The 12-month commitment (11 roles), dog-walking 2 hrs/week and morning cleaning availability are **kept as published claims** but marked `needs_confirmation`. Source `ah_application` is flagged `possibly_superseded`. Dog-walking age 21 stays `published_applicable` because both pages agree. |
| Schedules | `published_schedule` was replaced by `recurring_schedule` (10 records), `orientation_info` (17) and `dated_notices` (2). Branford's "Sunday, October 11" notices are now dated notices with `stated_year: null` and `timing_assessment: appears_past_year_not_stated`. |
| Record types | New `record_type`: 51 `described_volunteer_role`, 4 `interest_area_only`, 9 `independent_support_activity`. No records were deleted. |
| Commitment types | New `commitment_type` (12 recurring, 1 one-time, 4 variable, 47 unknown) and `time_commitment`, which keeps the published wording, ranges and units. |
| CHS Newington group project | Rechecked live at 16:15 EDT; the page is unchanged. It is now `one_time` ("3-4 hours, one time"), with **no six-month minimum**. The general 6-month rule is kept in the evidence and noted as overridden for this role. It is no longer recorded as a conflict. |
| Non-requirements | New `notes_for_applicants` field. Animal Haven's allergy advisory, its "requested" skills, and "which form / whom to contact" notes moved here from `other_requirements`, so they can't act as eligibility rules. |
| Sources | `reliability_flags` added; 1 recheck source added (35 total). |
| Validation | The validator was rewritten for the new schema and given a `--data-dir` option. Self-tests and the quote check are now repo scripts (§7, §10). |

## 1. Counts

| | Count |
|---|---|
| Organizations | **8** (5 Greater New Haven, 3 wider Connecticut) |
| Opportunity records | **64** (IDs unchanged) |
| Sources | **35** (34 original fetches and 1 recheck) |
| `field_evidence` entries | 328 (organizations and opportunities) |
| Passages checked by the quote script | 389 (`field_evidence` plus the published wording stored in schedules, notices and commitments) |
| Unresolved questions | 160 |

Records per organization: Animal Haven 11, Branford Compassion Club 11, Cat Tales 10, PAWS 9, CHS 8,
Friends of the New Haven Animal Shelter 7, Greater New Haven Cat Project 6, Dan Cosgrove (Branford) 2.

## 2. Counts by scope, status, record type and commitment type

**Application status**

| Scope | explicitly_accepting_applications | explicitly_closed | needs_confirmation | Total |
|---|---|---|---|---|
| greater_new_haven (default view) | **0** | 3 | 34 | 37 |
| wider_connecticut (separate scope) | 10 | 2 | 15 | 27 |
| **Total** | 10 | 5 | 49 | 64 |

**Record type**

| record_type | Greater New Haven | Wider CT | Total | Application status |
|---|---|---|---|---|
| described_volunteer_role | 28 | 23 | **51** | 10 accepting, 5 closed, 36 needs confirmation |
| interest_area_only | 4 | 0 | **4** | all needs confirmation (Animal Haven checkbox areas) |
| independent_support_activity | 5 | 4 | **9** | all needs confirmation |

The independent support activities are: BCC bake sales, BCC crafting, BCC youth supply drives, BCC
youth art for advocacy, BCC youth kindness education, Cat Tales under-15 school fundraiser, CHS
collection drive, CHS craft projects and the PAWS Junior Volunteer Program.

**Commitment type**

| commitment_type | Greater New Haven | Wider CT | Total |
|---|---|---|---|
| recurring | 9 | 3 | **12** |
| one_time | 0 | 1 | **1** (CHS group project) |
| variable | 1 | 3 | **4** (BCC foster; CHS fosters ×3) |
| unknown | 27 | 20 | **47** |

**No Greater New Haven record says on its page that it is accepting applications right now.**
Following decision 6, these records will be labeled "Confirm with organization," not "Open now."

## 3. Coverage of each proposed filter

"Usable for a mismatch" counts requirements that are `published_applicable`. Everything else can only
raise a confirmation question.

| Field | Populated (all / GNH) | Usable for a mismatch (all / GNH) | Notes |
|---|---|---|---|
| Role-level town (`location_town`) | 17 / 9 | n/a | Organization town is known for 6 of 8 organizations; town filter only |
| Activity tags | 64 / 37 | n/a | Our classification |
| Animal tags (specific) | 62 / 35 | n/a | 2 `unspecified` |
| Minimum age | 24 / 17 | 24 / 17 | Plus 10 conflicting (Animal Haven) and 5 needs confirmation with a null value (BCC feral/foster, CHS fosters) |
| Guardian rule (stated) | 3 / 1 | 3 / 1 | Was 34 "known" before; 31 were inferences and are now null |
| Minimum hours + period | 12 / 9 | 10 / 7 | Animal Haven dog walking (legacy form) and New Haven foster (how hours are counted) need confirmation |
| Minimum commitment (months) | 20 / 18 | 9 / 7 | The 11 Animal Haven values need confirmation |
| Commitment wording (`time_commitment`) | 28 / 20 | — | Keeps ranges ("2-3 hours", "3-4 hours, one time", "usually 2 to 4 month") |
| Recurring schedule | 10 / 6 | 9 / 5 | Animal Haven morning availability needs confirmation. CHS open shifts can change. |
| Orientation info | 17 / 9 | — | Process descriptions; no upcoming dates |
| Dated notices | 2 / 2 | never used | Both Branford, both appear past, year not stated |
| Training requirements | 20 / 9 | 20 / 9 | |
| Fees | 2 / 2 | 2 / 2 | Branford non-resident $50 only; other fees are `null` (not stated), not "free" |
| Explicit application status | 15 / 3 | — | Shown separately from fit (decision 5) |

## 4. Missing fields and inaccessible sources

**Missing everywhere:** coordinates (`null` by decision 3), public-transit information, live shift
availability and published update dates.

**Frequently missing:** hours (52 of 64 `null`), commitment length (44 `null`), recurring schedule (54
`null`), guardian rules (61 `null`, meaning not stated), and age for non-direct-care roles.

**Sources we could not fully read** (nothing was submitted or bypassed):

| Source | Result | Effect |
|---|---|---|
| Animal Haven POINT sign-up | JavaScript-rendered; title only | Can't tell whether POINT's rules settle the age conflict or replace the on-site form's terms |
| Branford Volgistics forms ×2 | JavaScript-rendered | Form-level requirements unknown |
| GNHCP Airtable application | JavaScript-rendered | Form-level requirements unknown |
| Cat Tales shelter application | Form body not rendered | Same |
| BCC Shelterluv form | First step only | Later steps not seen |
| Animal Haven `/foster/` | 404 | The foster link is a form with no role description, so no record was created |

**Not inspected:** the PAWS foster page and junior brochure, CHS Waterford and Wilton opportunity
pages, the City of New Haven shelter page, and Cat Tales' managerial/clerical application.

## 5. Contradictory and uncertain rules

| Records | Issue | Handling |
|---|---|---|
| 10 Animal Haven roles (all except dog walking) | Volunteer page says **21+** for all volunteering; on-site form says **18+** (21+ for dog walking) | `minimum_age` null, applicability `conflicting`, both quotes kept, question raised |
| 11 Animal Haven roles | Commitment (12 months), dog-walking hours (2/week) and morning cleaning availability appear **only on the on-site form**, which the current page seems to have replaced with POINT | Values kept as published claims, applicability `needs_confirmation`, questions raised. Not used to accept or reject anyone. |
| `chs_newington_group_trails` | The general CHS "6-month commitment to the organization" vs. this role's "3-4 hours, one time" | **Resolved by scope:** a clearly stated role-specific exception overrides the general rule for this role only. `commitment_type: one_time`, no minimum months; both statements kept in the evidence. Rechecked at 16:15 EDT. |
| CHS fosters ×3 | "Must be **over** 18" could mean 18+ or 19+ | `minimum_age` null, `needs_confirmation` |
| CHS fosters ×3 | Does the organization-wide 6-month rule apply to fostering ("a few days to several months")? | `commitment_type: variable`; question raised; no minimum recorded |
| BCC feral feeding, BCC foster | 18+ applies to "direct care" / working "directly with our cats". Do these roles count? | `minimum_age` null, `needs_confirmation` |
| New Haven foster | 8 hours/month applies to all volunteers, but how hours are counted for fosters isn't stated | `minimum_hours` value kept, `needs_confirmation` |
| PAWS cat volunteer and dog walker | 18+ comes from an **undated** flyer linked on the current page | `published_applicable`, with the reason noting the flyer is undated. Families for Felines (13–17 with a guardian) is a stated program exception. |
| PAWS (all) | "**Most** volunteer positions require ... 2 hours per week" | Not applied to any specific role; question raised |
| GNHCP | Testimonials describe the old New Haven center; the center moved to Northford in 2025 | Source flagged `partially_outdated`; testimonials aren't used as facts |

## 6. Stale dates and application-status limitations

- **Branford orientation and Tails to Trails:** both "October 11" notices print **no year**. They are
  stored as `dated_notices` with `stated_year: null` and `timing_assessment:
  appears_past_year_not_stated`, assessed on 2026-10-25. The validator blocks `upcoming` without a
  printed year and blocks calendar dates inside recurring schedules or orientation info. The recurring
  pattern ("orientations every month throughout the spring and the fall"; links "posted one month
  prior") is kept separately in `orientation_info`.
- **New Haven (Friends):** dog-handler, cat-handler and foster applications are explicitly closed. No
  application link is posted for other roles.
- **CHS:** the "current openings" and foster statuses can change at any time. The September 30 banner
  closure had already passed.
- **BCC "closed to new intakes"** refers to animals, not volunteers. **GNHCP's TNR hold** applies to
  assistance requests; any effect on volunteer TNR work is unknown.
- `explicitly_accepting_applications` means the page invites applications. It does **not** mean a
  vacancy, placement or shift for any individual.

## 7. Records and constraints checked against sources

Three checks, separate from the structural validator:

1. **Quote check (reproducible locally).** `python scripts/check_evidence_quotes.py` looks for every
   quoted passage (split on `...`, bracketed notes removed, whitespace, quotes and dashes normalized)
   in the saved snapshot of the cited page.
   - *Previously reported result reproduced:* the first audit said 297 of 297 quoted passages were
     found verbatim, plus 44 derived or label entries. Running the new script on the **pre-correction
     data** with the **same original snapshots** gives exactly **297 found, 44 derived or label, 0 not
     found**.
   - *Current data (16:21 EDT):* **389 passages examined: 376 found verbatim, 13 labels or derived
     statements (reviewed by hand), 0 not found, 0 without a snapshot.** The derived count dropped
     because the 31 guardian inferences were removed.
   - The snapshots are **unchanged byte-for-byte copies of the original fetches**: page text extracted
     at fetch time plus the raw HTML or PDF, listed in `MANIFEST.json` with SHA-256 checksums. They
     were not re-fetched or recreated. The only new fetch is the clearly separate CHS recheck. They
     live in the gitignored `local_data/source_snapshots/2026-10-25/` because they are full copies of
     third-party pages. **On a fresh clone the quote check can't be reproduced**: the script exits
     with code 2 and says so.
2. **Manual review** of the normalized values against their quotes for every record. In this pass it
   specifically covered: every `needs_confirmation` and `conflicting` assessment (§5); the CHS group
   project against the live page; the scope of each rule (organization, program or role); and the 13
   non-quote entries (4 Animal Haven interest-area labels and 9 Cat Tales "apply using" process notes).
3. **Live recheck:** the CHS Newington page fetched at 16:15:56 EDT has a role section identical to
   the 15:52 fetch.

The quote check shows the text appeared on the page **as fetched on 2026-10-25**. It does not show
the page is still current or that the organization still applies the rule.

Per-record fields checked by the quote script (current data):

| Record | Fields with quotes found verbatim | Fields with derived statements or labels (manual review) |
|---|---|---|
| `fnhas` | notes, physical_address | — |
| `animal_haven` | physical_address | — |
| `bcc` | physical_address | — |
| `branford_shelter` | physical_address | — |
| `gnhcp` | physical_address | — |
| `paws` | physical_address | — |
| `fnhas_dog_handler` | application_status, commitment_type, hours_period, location_description, minimum_age, minimum_commitment_months, minimum_hours, orientation_info, other_requirements, recurring_schedule, time_commitment, training_requirements | — |
| `fnhas_cat_handler` | application_status, commitment_type, hours_period, location_description, minimum_age, minimum_commitment_months, minimum_hours, orientation_info, other_requirements, recurring_schedule, time_commitment, training_requirements | — |
| `fnhas_foster` | application_status, commitment_type, hours_period, minimum_age, minimum_commitment_months, minimum_hours, orientation_info, other_requirements, time_commitment, training_requirements | — |
| `fnhas_adoption_events` | application_status, commitment_type, hours_period, minimum_age, minimum_commitment_months, minimum_hours, orientation_info, other_requirements, recurring_schedule, time_commitment, training_requirements | — |
| `fnhas_dog_bathing` | application_status, commitment_type, hours_period, minimum_age, minimum_commitment_months, minimum_hours, orientation_info, other_requirements, recurring_schedule, time_commitment, training_requirements | — |
| `fnhas_transport_rescue` | application_status, commitment_type, description, hours_period, minimum_age, minimum_commitment_months, minimum_hours, orientation_info, other_requirements, time_commitment, training_requirements | — |
| `fnhas_fundraising_education` | application_status, commitment_type, description, hours_period, minimum_age, minimum_commitment_months, minimum_hours, orientation_info, other_requirements, time_commitment, training_requirements | — |
| `ah_dog_walking` | application_status, commitment_type, hours_period, location_description, minimum_age, minimum_commitment_months, minimum_hours, notes_for_applicants, time_commitment | — |
| `ah_cat_socializing` | application_status, location_description, minimum_age, minimum_commitment_months, notes_for_applicants, time_commitment | — |
| `ah_shelter_cleaning` | application_status, location_description, minimum_age, minimum_commitment_months, notes_for_applicants, recurring_schedule, time_commitment | — |
| `ah_fundraising_events` | application_status, description, minimum_age, minimum_commitment_months, notes_for_applicants, time_commitment | — |
| `ah_administrative` | application_status, minimum_age, minimum_commitment_months, notes_for_applicants, time_commitment | — |
| `ah_building_maintenance` | application_status, minimum_age, minimum_commitment_months, notes_for_applicants, time_commitment | — |
| `ah_gardening` | application_status, location_description, minimum_age, minimum_commitment_months, notes_for_applicants, time_commitment | — |
| `ah_grant_writing` | application_status, minimum_age, minimum_commitment_months, notes_for_applicants, time_commitment | description |
| `ah_communications_marketing` | application_status, minimum_age, minimum_commitment_months, notes_for_applicants, time_commitment | description |
| `ah_food_supply_drives` | application_status, minimum_age, minimum_commitment_months, notes_for_applicants, time_commitment | description |
| `ah_adoption_awareness_events` | application_status, minimum_age, minimum_commitment_months, notes_for_applicants, time_commitment | description |
| `bcc_shelter_care` | application_status, location_description, minimum_age, recurring_schedule | — |
| `bcc_shy_cat_socializing` | application_status, description, minimum_age | — |
| `bcc_feral_colony_feeding` | application_status, description | — |
| `bcc_foster` | application_status, other_requirements, time_commitment | — |
| `bcc_fundraising` | application_status, description | — |
| `bcc_bake_sales` | application_status, description | — |
| `bcc_offsite_events` | application_status, description | — |
| `bcc_crafting` | application_status, description | — |
| `bcc_youth_supply_drives` | application_status, description, notes_for_applicants | — |
| `bcc_youth_art_advocacy` | application_status, description, notes_for_applicants | — |
| `bcc_youth_kindness_education` | application_status, description, notes_for_applicants | — |
| `branford_general_volunteer` | commitment_type, dated_notices, fees, guardian_requirement, hours_period, location_description, minimum_age, minimum_hours, orientation_info, other_requirements, time_commitment, training_requirements | — |
| `branford_tails_to_trails` | dated_notices, description, fees, orientation_info, other_requirements, training_requirements | — |
| `gnhcp_direct_care` | application_status, description, location_description, minimum_age | — |
| `gnhcp_grant_writing` | application_status, description, minimum_age | — |
| `gnhcp_event_organizing` | application_status, description, minimum_age | — |
| `gnhcp_awareness_outreach` | application_status, description, minimum_age | — |
| `gnhcp_food_drives_workshops` | application_status, description, minimum_age | — |
| `gnhcp_rescue_tnr` | application_status, context, description, minimum_age | — |
| `cattales_shelter_care` | application_status, commitment_type, description, hours_period, minimum_age, minimum_hours, time_commitment | notes_for_applicants |
| `cattales_foster` | application_status, description | notes_for_applicants |
| `cattales_feral_feeding` | application_status, description | notes_for_applicants |
| `cattales_vet_transport` | application_status, description | notes_for_applicants |
| `cattales_trades` | application_status, description | notes_for_applicants |
| `cattales_adoption_appointments` | application_status, description | notes_for_applicants |
| `cattales_donor_correspondence` | application_status, description | notes_for_applicants |
| `cattales_fundraiser_help` | application_status, description | notes_for_applicants |
| `cattales_phone_line` | application_status, description | notes_for_applicants |
| `cattales_youth_school_fundraiser` | application_status, description | — |
| `chs_newington_group_trails` | application_status, commitment_type, location_description, minimum_age, notes_for_applicants, other_requirements, recurring_schedule, time_commitment | — |
| `chs_newington_laundry` | application_status, commitment_type, hours_period, location_description, minimum_age, minimum_commitment_months, minimum_hours, orientation_info, other_requirements, recurring_schedule, time_commitment, training_requirements | — |
| `chs_newington_dog_trainer` | application_status, commitment_type, hours_period, location_description, minimum_age, minimum_commitment_months, minimum_hours, orientation_info, other_requirements, recurring_schedule, time_commitment, training_requirements | — |
| `chs_foster_newington` | application_status, commitment_type, minimum_age, other_requirements, time_commitment, training_requirements | — |
| `chs_foster_waterford` | application_status, commitment_type, minimum_age, other_requirements, time_commitment, training_requirements | — |
| `chs_foster_wilton` | application_status, commitment_type, minimum_age, other_requirements, time_commitment, training_requirements | — |
| `chs_collection_drive` | description | — |
| `chs_craft_projects` | description | — |
| `paws_cat_volunteer` | application_status, description, minimum_age, minimum_hours, orientation_info, training_requirements | — |
| `paws_dog_walker` | application_status, description, minimum_age, minimum_hours, orientation_info, training_requirements | — |
| `paws_families_for_felines` | application_status, description, guardian_requirement, minimum_age, minimum_hours, orientation_info, training_requirements | — |
| `paws_adoption_counselor` | application_status, description, minimum_hours, orientation_info, training_requirements | — |
| `paws_fundraising` | application_status, description, minimum_hours, orientation_info, training_requirements | — |
| `paws_office_admin` | application_status, description, minimum_hours, orientation_info, training_requirements | — |
| `paws_foster` | description, minimum_hours | — |
| `paws_junior_volunteer` | description, minimum_hours | — |
| `paws_reading_to_rescues` | description, guardian_requirement, minimum_hours, other_requirements, recurring_schedule, time_commitment | — |

## 8. Features this dataset supports (with the matching rules in README "Planned matching behavior")

| Planned feature | Support | Notes |
|---|---|---|
| Town / location filter | **Partial** | By town only (decision 3). Organization level for 6 of 8 organizations; role level for 17 roles. Many roles say "location not stated." |
| Animal and activity preferences | **Yes** | Tags on all 64 records |
| Published age and guardian rules | **Partial** | 24 ages are usable for a mismatch; 15 more raise confirmation questions. Only 3 guardian rules are published. "Not stated" must never be shown as "not required." |
| Weekly / monthly hours | **Partial** | 10 usable, 2 need confirmation |
| Minimum commitment length | **Partial** | 9 usable, 11 need confirmation (Animal Haven). One-time and variable commitments are now represented correctly. |
| Published schedule requirements | **Limited** | 9 usable recurring schedules. Dated notices are history only. |
| Application status | **Yes, three-way** | Shown separately from fit; "Confirm with organization" for `needs_confirmation` |
| Evidence-backed explanations and checklists | **Yes** | Each requirement has an applicability status, sources and a reason. 63 of 64 records have questions to ask the organization. |
| "Another way to help" suggestions | **Yes** | 9 independent support activities and several non-direct-care roles. They must be presented as self-organized help, not shelter shifts. |
| Record-type labelling | **Yes** | 4 interest-area-only records must be labelled "listed as an interest area; ask whether this help is needed" |

## 9. Features that need more information (do not promise these)

- **Exact shifts, live vacancies, acceptance or placement:** not in any source.
- **Public transit, distance and "near me":** postponed (decision 3). Coordinates are `null`.
- **Remote work:** not published as an option for any role.
- **Fees outside Branford:** unknown, not zero.
- **"Open now" in Greater New Haven:** nothing is confirmed open.
- **Upcoming orientations:** none with a published date. Only the past Branford notices exist.
- **Novelty claim:** compare with existing services such as **Idealist** and **Samaritan Scout** (and
  others, for example VolunteerMatch, general chatbots and the shelters' own pages) before finalizing.
  AI-assisted volunteer search already exists, so **do not call this project first or unique** without
  evidence.

## 10. Validation, self-tests and their actual results

Run from `animal-volunteer/` at 2026-10-25 16:23 EDT:

```
$ python scripts/validate_data.py
Data folder: …/animal-volunteer/data
Loaded 35 sources, 8 organizations, 64 opportunities.
Opportunities by application_status: explicitly_accepting_applications=10, explicitly_closed=5, needs_confirmation=49
Opportunities by geographic_scope: greater_new_haven=37, wider_connecticut=27
Opportunities by record_type: described_volunteer_role=51, independent_support_activity=9, interest_area_only=4
Opportunities by commitment_type: one_time=1, recurring=12, unknown=47, variable=4
Opportunities by requirement applicability: conflicting=10, needs_confirmation=33, published_applicable=125
WARNING  opportunities[branford_general_volunteer]: minimum_age is 0 (a published 'all ages' rule); check that the guardian requirement is shown to users

Result: 0 error(s), 1 warning(s).
Note: passing validation means the data is structurally consistent, not that it is factually accurate.
```

Exit code 0. The one warning is intentional (Branford's published "All ages are welcome," stored with
its under-16 guardian rule).

```
$ python scripts/test_validate_data.py
....................................
----------------------------------------------------------------------
Ran 36 tests in 0.277s

OK
```

The 36 tests are: 1 check that the real data passes; the **21 original self-tests** (now reproducible
as code and updated for schema v2; the "empty fee list" case now expects the stricter "must be null
rather than an empty list" error); and **14 new tests** for the correction-pass rules: derived
guardian rejected, legacy-only rule marked applicable, conflict marked applicable, uncertain rule
without a question, populated requirement without applicability, past date in a recurring schedule,
"upcoming" without a printed year, one-time project with 6 months, recurring without hours, unknown
record type, unknown commitment type, interest area marked open, typical duration copied as a minimum,
and independent activity given a shift schedule.

*Earlier result, for the record:* the first audit reported 21 of 21 self-tests passing with an ad-hoc
harness run from the session scratchpad. That harness targeted schema v1, which no longer exists, so
its exact run can't be repeated. Its cases are carried forward in `scripts/test_validate_data.py`.

```
$ python scripts/check_evidence_quotes.py
Passages examined: 389
  quoted and found verbatim in the cited snapshot: 376
  derived statements / labels (manual review, not string-checkable): 13
  cited source has no text snapshot: 0
  NOT FOUND: 0
```

## 11. Decisions recorded and remaining questions

**Recorded decisions (2026-10-25):** Greater New Haven is the default view; wider Connecticut is a
separate labeled scope; town filtering only, with coordinates null and distance/transit postponed;
check dates and uncertainty always shown; application status shown separately from fit; uncertain
roles say "Confirm with organization," not "Open now"; applications stay on organizations' own
sites; no visual theme chosen yet; `animal-volunteer/` is the planned repo root (no Git found in it
or any parent folder); the real `.env` was not moved or copied.

**Remaining questions for Rhea:**

1. **Deadline:** the PDF says **Mon Oct 26, 2026, 6:00 PM**. Should the build be scoped to fit?
2. **`.env` placement:** when the backend is connected, a `.env` will be needed in
   `animal-volunteer/` (gitignored) or `Final Project/`. The current one in `MGT409 AI/` is two levels
   up and won't be found. Which do you prefer?
3. **Theme:** the workspace instructions (`agents.md`) default websites to black and pink unless you
   say otherwise. You asked not to pick a theme yet, so none is applied. Choose one when we build the UI.
4. **Interest-area-only records** (4) are kept and labelled. Show them in Explore, or only as "other
   ways to help"?
5. **Freshness:** re-fetch before submission? Any re-fetch should be stored as new recheck sources,
   not as replacements.
6. **Optional follow-ups not done:** PAWS foster page and junior brochure, CHS Waterford/Wilton pages,
   the City of New Haven shelter page.

## Session 11 application recheck (2026-10-25)

Read-only recheck of the five Greater New Haven organizations' volunteer pages and the application systems they link
to. Pages were rendered in a browser (Playwright, Chrome); nothing was clicked, submitted or signed into, and no
organization was contacted. Visible text is saved locally in
`local_data/source_snapshots/2026-10-25/application_recheck/` (gitignored).

| Organization | What the pages say now (access time) | Change to the data |
|---|---|---|
| Friends of the New Haven Animal Shelter | "Applications for dog handlers, cat handlers and fosters have been closed." Enrollment links are posted only during an enrollment period (2026-10-25T20:29:37-04:00). | None: still closed for those 3 roles; others still "confirm with organization". |
| The Animal Haven | Volunteer page: "please apply to volunteer today" (general invitation). The POINT sign-up link now redirects to a sign-in page (2026-10-25T20:30:37-04:00), so it was not opened further. | None. A general invitation and a form are not a statement that applications are being accepted for a role. |
| Branford Compassion Club | No accepting/closed statement on the volunteer page or the Shelterluv form. The foster page says "We need fosters now more than ever before!" | None to status. The foster appeal is now recorded as evidence on `bcc_foster` (undated appeal, not an explicit "accepting applications"). |
| Dan Cosgrove Animal Shelter (Branford) | General application form (Volgistics): "This application form is currently disabled" and the "Sunday, October 11, 2026" orientation "is full"; next sign-ups to be posted (2026-10-25T20:31:15-04:00). Tails to Trails form: open; requires age 25 and your own transportation, 3 Dog Handling and Safety Classes and a kennel cleaning session, at least 4 hours a month, lifting 50 pounds, license and insurance uploads; offers a Sunday, Nov 15, 2026 orientation (2026-10-25T20:32:02-04:00). | `branford_general_volunteer` → **explicitly_closed** (role scope, with the quote). `branford_tails_to_trails`: minimum age 25, 4 hours a month (recurring), own-transportation and lifting requirements, training, the upcoming orientation as a dated notice; status stays "confirm with organization" because an open form is not evidence of a vacancy. Two new source records (`*_recheck`); the original records are unchanged. |
| The Greater New Haven Cat Project | No accepting/closed statement on the volunteer page; the Airtable application form showed "your browser version is not supported" and was not read further. | None. |

Result: no Greater New Haven record is "explicitly accepting applications". 4 are explicitly closed (3 FNHAS, 1 Branford)
and 33 need confirmation. Quote check after the change: 391/391 found (`scripts/check_evidence_quotes.py`); the two
new snapshots were added to the local manifest with a note that they were rendered, not part of the original fetch.
