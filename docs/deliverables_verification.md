# Verification record: report.html and slides.html drafts (2026-10-25, Session 7)

Both files are **drafts**. User-test findings, the GitHub link and the fresh-clone test are still
pending. Regenerate both with `python scripts/build_slides.py` (it also rebuilds `report.html`; needs
`pillow`). All numbers are read from the evidence files at build time.

## report.html

| Check | Result | How checked |
|---|---|---|
| Printed length | **14 US Letter pages** after the Session 8 citation pass (13 before; target 10–15) | Chrome print to PDF (`emulate_media("print")`, Letter); `output/deliverables_check/report_print_check.pdf` |
| Self-contained | **0 external requests**; 8 screenshots and the diagram embedded (base64 JPEG and inline SVG); system fonts with fallbacks | Request log while loading; scan of `src`/`href` |
| Section order | 1 Title + links → 2 Motivation → 3 What is new here → 4 The agents → 5 Tokenomics → 6 Safety → 7 Impact → 8 Limits + next steps: **matches the rubric** | Parsed `<h2>` order |
| Links | No external hyperlinks. The GitHub URL is marked **Pending**, with no fake links. The app is noted as not hosted. | `href` scan; "Pending" markers |
| Pending items visible | Impact: "Prospective-user testing: PENDING", with a fill-in box. Limits: GitHub link and fresh clone pending. | Text search |
| Claims | No "first", "proven", "verified bill" or time-saved claims. Costs labelled "modeled … not a bill". Optimization reported as "no regression detected by our checks in this small sample". The clean-copy rehearsal is never called a fresh clone. | Phrase scan plus reading |
| Numbers match evidence | Per-run $0.00128, per user $0.0051, 100 users $0.51, 10,000 users $51.12, baseline $0.00190, 54/54 vs 54/54, −33%: all generated from `output/cost_eval/tokenomics.json` and `results.json`. The walkthrough tokens come from trace `ui_integrated__af1ced1eab65`. | Build script reads the files |
| Visual inspection | All 13 pages viewed as a contact sheet; pages 6, 9 and 11 viewed at 100 dpi. Fixed: two-image rows splitting across pages, an oversized phone image, forced page breaks (16 → 13 pages), and a provider-filter crop that showed the wrong area. Remaining: some white space where tables avoid splitting. | PDF rendered to PNG (PyMuPDF) |

**Screenshot correction found during this check:** the Session 6 provider-filter screenshot did not show
the notice. It was retaken (`safety_provider_filter_blatant_injection.png`, run
`ui_integrated__d2bdc37e7df6`), and the old file was kept as
`safety_provider_filter_attempt1_notice_not_visible.png`.

## slides.html

| Check | Result | How checked |
|---|---|---|
| Slide count | **10** (maximum 10) | `Reveal.getTotalSlides()` |
| reveal.js | Loaded from the jsDelivr CDN (`reveal.js@5.1.0`), as the course's slide instructions suggest. **Needs internet** for that library only. | Request log: only the 2 CDN files |
| Embedded assets | 5 screenshots and the diagram embedded (base64 and inline SVG) | `src` scan |
| Overflow | No element extends past the 1280×720 slide on any slide | Bounding-box check per slide (`output/deliverables_check/slides_check.json`) |
| Navigation | The right arrow moves to slide 2; controls and slide numbers shown; no console errors | Playwright keyboard test |
| Readability | Body text 24–32 px, smallest footnotes 21 px. All slides viewed (contact sheet plus slide 6 at full size). Fixed: content stuck in the top half, small type, and screenshots cropped at the right edge. | Screenshots in `output/deliverables_check/slides/` |
| Pending shown honestly | The Impact slide says "Prospective-user test: PENDING"; the GitHub link and fresh clone are marked pending on slides 1 and 10 | Reading |

## Still needed before finalizing

1. **User-test findings:**
   - the participant description they approved;
   - task completion and times for T1–T4;
   - main confusions;
   - one quote they agreed to;
   - suggested improvements;
   - optionally, the manual-search baseline time and the order of tasks.
2. **The GitHub repository URL**, and a timed fresh clone from it (replacing "Pending" in both files).
3. Optionally, a confirmed course or Azure billing basis, if actual dollars are wanted rather than
   modeled costs.

## Session 8: accuracy and citation pass (2026-10-25)

Both generators (`scripts/build_report.py`, `scripts/build_slides.py`) were changed, so the corrections
survive a rebuild.

| Correction | What changed |
|---|---|
| Matching rule | "Not met requires both sources to agree" was replaced. A definite "not met" is allowed only for a requirement marked `published_applicable`; conflicting or needs-confirmation requirements are not enforced as exclusions. The safety example now says why its 21+ rule is `published_applicable`. |
| Profile confirmation | Checked against `backend/tools.py`. The wording now matches the code: confirmed form answers; chat facts with verified quotations; inferred age, guardian, hours, hours period, commitment and session length stay suggestions until confirmed. Other inferred preferences can guide search, and the foster town-list check can use an inferred town. A quotation check shows the words were written, not that they were interpreted correctly. "Only confirmed facts count" was removed from the slides, and the diagram now says "form answers". |
| Citations | 18 numbered references with clickable links and access dates (organization pages use their actual page-check timestamps). The report has 17 citation points; every reference is cited at least once. Slides 2, 3 and 7 have visible source lines. All 10 slides have speaker notes (the reveal.js notes plugin comes from the same CDN). |
| Kinds of checks | The report now separates structural validation, quotation matching, automated output checks and factual verification, and says none proves every sentence is accurate. Safety adds that the defenses reduce risk but don't guarantee every attack is blocked. |
| Provider usage | "No tokens" became "the provider reported no usage". Exclusions say we don't assume filtered requests cost nothing. |
| Other absolutes | "Every rule" became "each published rule in the dataset". "Never shows fake recommendations" became "the response contains an error and no recommendations". "Fit labels cannot be overridden" became "must match the results computed by code". "Verified against the message" became "quotations found (quotation check)". A scan of the remaining "never/always/guarantee/verified/prove" uses found them accurate. |
| Reference check | Portkey's Responses API page, previously seen only in search results, was opened and confirmed to say the OpenAI SDK works with `https://api.portkey.ai/v1`. |

**Re-verification:**
- **Report:** 14 Letter pages, 0 external requests on load, and 40 clickable links in the PDF. Pages 4
  (matching and profile text) and 13–14 (references) were inspected and are readable.
- **Slides:** 10 slides, no overflow, no console errors, and arrow navigation works. Every slide was
  inspected after the changes.
- **Bug found and fixed:** slides 3 and 10 showed raw template text (`{srcline(...)}`), because two
  slide strings were not f-strings.

**Still pending:** user-test findings, the GitHub link, and the fresh clone from it.

## Session 11 rebuild (2026-10-25)

- `report.html`: printed to Letter in Chrome (Playwright `page.pdf`) → **15 pages** (limit 10–15); 0 external
  requests; 7 embedded images; 24 numbered references. Section 1 states Claude Code as the implementation
  assistant and GPT-6 Luna via Portkey as the runtime AI. Tokenomics shows the measured current agent first and
  keeps the Session 6 experiment as historical, with its tested configuration named.
- `slides.html`: **10 slides**; no slide content taller than 720 px at 1280 × 720; reveal.js and its notes plugin
  from the CDN (course instruction). Renders: `output/deliverables_check/slides/slide_01.png` … `slide_10.png`.
- Still pending inside both: prospective-user findings, the GitHub link and the timed fresh clone.

## Session 12 rebuild (2026-10-25)

- `report.html`: 15 Letter pages, 0 external requests, 7 embedded images; no "Approx" or old status labels in its text.
  Section 4 has a location-category table computed from the data; tests list Sessions 10–12 results separately.
- `slides.html`: 10 slides, no overflow. Pending items unchanged (user test, GitHub link, fresh clone).

## Session 14 rebuild (2026-10-25): current interface in the drafts

- **Generators updated** (`scripts/build_report.py`, `scripts/build_slides.py`):
  - **Wording:** "Availability not confirmed", shown as information with a keyboard-accessible explanation; "Visit volunteer page ↗" and "Contact organization ↗"; "Apply on organization's website ↗" only for real application pages that aren't closed (no current link is one); "Compare requirements" / "Added to comparison" and the comparison bar.
  - **Removed from both files:** "Ask about availability", "Check application details" and "Approx".
- **Screenshots (current interface):** the final Session 13 build. Report: option card (`s13_fmf_card_desktop`), Explore sorted by closest verified site (`s13_explore_zip_closest_desktop`), comparison bar (`s13_explore_two_selected_desktop`). Slides: detail panel (`s13_detail_organization_only_desktop`), Compare (`s13_compare_desktop`), option card. The Explore-by-ZIP and detail captures were taken from the unchanged Session 13 build for this rebuild; no features were added. The answers panel (`s12_final_preferences_desktop`) and the home hero (`s11_home_desktop`) are unchanged interface areas.
- **Historical, labelled:** the Session 6 safety-run screenshot and the Session 7 provider-filter retake (captions now say they are historical); the slide-6 run steps are Session 11, with the card from another synthetic query.
- **Checks:**
  - `report.html`: 15 Letter pages (Chrome print), 0 external requests, 7 embedded images.
  - `slides.html`: 10 slides, no overflow after reducing slide 5's image height (a first rebuild overflowed at 754 px).
  - Crops were inspected for readability; the comparison-bar crop was widened so "2 opportunities selected" isn't cut off.
- **Still pending:** user-test findings, the GitHub link and the actual fresh-clone test.

## Session 15 rebuild (2026-10-25)

- Report wording: the comparison table's search row (role's own town; organization and closest-site sorting; the
  removed status filter dropped), the search tool's shared-filter description, and a "Hard constraints versus
  preferences" bullet describing the one-time behavior. Slides: the contribution line and the how-it-works notes.
  No screenshots needed replacing (the visible interface areas in them are unchanged).
- `report.html`: 15 Letter pages, 0 external requests. `slides.html`: 10 slides; a first rebuild overflowed slide 3 by
  5 px and the added sentence was shortened. User test, GitHub link and fresh clone remain pending.

## Session 16 rebuild (2026-10-25)

- Report: the location table (destination order, new labels, counts from code), the sorting bullet ("Distance:
  nearest first", one list), the comparison-table search and location rows, the limits bullet, and a Session 16 test
  line. Slides: the working-app sentence and image alt text.
- **Screenshots (current interface):** Session 16 build. Report: option card (`s16_fmf_card_desktop`, real
  gpt-6-luna turn), Explore sorted by distance (`s16_explore_sorted_boundary_desktop`), comparison bar
  (`s16_explore_two_selected_desktop`). Slides: detail panel (`s16_detail_organization_desktop`), Compare
  (`s16_compare_three_desktop`), option card. The answers panel and home hero are unchanged interface areas.
- 21 earlier screenshots were accidentally overwritten while re-running old check scripts; see
  `output/screenshots/RECAPTURED_SESSION16.md`. None of them is used in the report or slides. They were then restored from a backup
  (21/21 SHA-256 identical); the report and slides did not need rebuilding.
- `report.html`: 15 Letter pages, 0 external requests. `slides.html`: 10 slides, no overflow. User test, GitHub link
  and fresh clone remain pending.

## Owner-testing fixes (2026-10-26): not rebuilt

- `report.html` and `slides.html` were **not** rebuilt; nothing in them is contradicted. The report's option-card
  image (Session 16 build) shows the earlier overall badge text "Needs confirmation" (now "Possible fit — confirm
  requirements"). Rebuild pending the owner's review.

## Conflicting-age fix (2026-10-26): report rebuilt

- One sentence in `scripts/build_report.py` now states the exception: a role is not offered when every conflicting
  minimum-age version is above the person's age. `report.html`: 15 Letter pages, 0 external requests.
  `slides.html`: 10 slides, no overflow. Screenshots unchanged.

## Prospective-user feedback (2026-10-26): report and slides rebuilt

- Report §7 Impact: the PENDING boxes were replaced by the participant profile, paraphrased feedback, a
  reported-vs-reproduced table and the changes, with limits (one informal test; no times, ratings or measured
  savings). Slide 9 likewise. Limits wording adjusted; the backend test count updated to 244.
- To stay within 15 pages: a smaller table font, two older test-result lines merged, and the cost and setup bullets
  removed from Impact (they remain in Tokenomics and Limits).
- `report.html`: 15 Letter pages, 0 external requests, section order unchanged. `slides.html`: 10 slides, no overflow.
- Still pending: GitHub link and timed fresh clone (marked in both).

## Final submission (2026-10-26)

- Repository: https://github.com/rheasong3411/final-project (public). GitHub placeholders replaced in README, report
  and slides; the app is described as not hosted (runs locally), never as a public localhost link.
- Fresh clone from GitHub verified: about 23 s of setup commands (pip cache off), both `.env` locations, app checks
  25/25, one fresh real gpt-6-luna Find my fit run. Evidence: `output/final_submission/`.
- `report.html` 15 Letter pages, required section order, self-contained; `slides.html` 10 slides, no overflow; every
  page and slide visually inspected; 26 links returned 200; three slide labels corrected.

## Participant quotes added (2026-10-26)

- Four verbatim quotes from the informal prospective user (provided by Rhea) added to report §7 and §8 and slide 9;
  one quote's placement (answers the assistant didn't use) is our reading. To stay at 15 pages: the evidence-index
  paragraph was shortened, a sentence repeated elsewhere was removed, the Tokenomics limits became one paragraph, and
  the feedback table may now split across pages (its header repeats).
- `report.html`: 15 Letter pages, 0 external requests; `slides.html`: 10 slides, no overflow. Renders: `output/final_submission/20261026-023428_participant_quotes/`.
