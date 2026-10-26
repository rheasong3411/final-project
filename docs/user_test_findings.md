# Prospective-user test findings (one informal test)

**What this is:** one informal test of the app by one prospective user, separate from the owner's own testing and
from the automated tests. It does **not** establish broad usability, adoption or measured time savings.

## Participant (anonymous)

A 25-year-old graduate student in New Haven who likes cats, has no car, and can volunteer for 2–3 hours on weekend
mornings.

## Session details

| Item | Recorded? |
|---|---|
| Date and app build used | Not recorded |
| Tasks attempted and completion (T1–T4 in `docs/user_test_guide.md`) | Not recorded |
| Task times | Not recorded |
| Ease and trust ratings (1–5) | Not recorded |
| Verbatim quotes | Four short quotes, provided by Rhea on 2026-10-26 (below); the rest of the feedback is paraphrased |
| Manual-search baseline | Not done, so no time-saving claim is made |

## Quotes (verbatim, as provided by Rhea)

- “Every requirement shows where it came from.”
- “The design is calm, readable and looks trustworthy.”
- “I did say them, so that made the assistant seem broken.” (Placed by us with the answers the assistant didn't use,
  weekend availability and no car; the quote itself doesn't name them.)
- “I'd still have to visit three websites and probably email them.”

## Feedback (paraphrased, not a verbatim quote)

- **What they liked:** the website is cute and easy to read; the sources help them trust the information; the
  cat-related suggestions were useful.
- **Their answers:** the assistant didn't use their weekend availability, and later seemed to forget that they don't
  have a car.
- **Requirements:** the chat and the card explained Animal Haven's one-year commitment differently; they should give
  the same explanation.
- **Getting there:** distance estimates and directions links would help them decide which places they could reach
  without a car.
- **What could be clearer:** simpler age requirements, a check of the town filter, and fewer repeated warnings (while
  keeping the important ones).

## Reported vs. reproduced (developer retesting, not the participant)

The participant's situation was re-enacted with a synthetic message through the real app with real gpt-6-luna calls
(via Portkey), followed by questions about requirements and getting there. Evidence: `output/user_feedback_retest/20261026-013842/`.

| Reported by the participant | What our retest found | Status |
|---|---|---|
| Weekend availability not used | **Reproduced.** Saturday, Sunday and mornings were stored only as unverified "suggestions" (the model marked them as derived), so "Your answers" listed them as *not used*. | Fixed |
| Later seemed to forget "no car" | **Partly reproduced.** "No car" was used in the checks and kept in our runs, but "Your answers" hid it (a "no" was filtered out), so it wasn't visible or reliably carried forward. | Fixed |
| One-year commitment explained differently in chat and card | **Not reproduced** in our runs: the chat described it as listed on an older form and needing confirmation, as the card did. A gap was found: the short text on cards wasn't checked for this. | Check added |
| Wanted distances and directions | Distance estimates already existed but need an optional ZIP; the app asks for it optionally. **No directions links existed.** | Directions added |
| Age requirements hard to read | **Reproduced:** "Sources say 18, 21+ (conflicting published ages) … (your answer matches the listed value) ⚠ Sources disagree". | Simplified |
| Town filter | **Reproduced:** the town options included Newington and Norwalk (wider Connecticut) when only Greater New Haven was selected. | Fixed |
| Repeated warnings | **Reproduced:** the optional ZIP and "stay within New Haven?" questions repeated on every turn; one older-form note repeated on two lines of a card; the detail page explained a matched age twice. | Reduced |
| — (found by us) | "2–3 hours" was dropped in turn 1, and in turn 2 a 3-hour single-session limit appeared that the person never stated. | Fixed |

**What worked in the retest:** age, town, cats and "no car" were captured and kept across turns; no ZIP was invented;
no bus routes or travel times were claimed; Animal Haven's commitment was described as needing confirmation.

## Changes made

- **Profile:** stated days and times ("Saturday or Sunday mornings") count as the person's words; "2–3 hours" is kept
  as a range (`available_hours` 2, `available_hours_max` 3) and checked at both ends; a period is taken only from
  explicit words ("per week"; "weekend" is not "per week"); a single-visit length is not chosen from a range; the app
  asks "When you say 2–3 hours, is that each week, each month, or for a single visit?". "Has a car: No" is shown and
  carried forward. Correction, withdrawal and confirmation behaviour is unchanged.
- **Cards:** a Schedule line shows the person's days and times against the published schedule (or "No days or times
  published", as a question); a note shared by several lines is shown once.
- **Consistency:** the short text on each card must describe an uncertain rule (such as the one-year commitment) the
  way the card does, or the answer is sent back to the model.
- **Age wording:** "Your age meets both published minimums; confirm the organization's current rule." Between
  minimums: "Your age meets one published minimum (18+) but not the other (21+)…". Below every minimum: still not
  recommended. The conflicting values and sources stay in the evidence. A guardian never overrides an age rule.
- **Locations:** town options follow the selected scope (a wider-Connecticut town is cleared when that scope is
  turned off). Directions links open Google Maps with only the destination filled in (the person enters their start
  and chooses how to travel); organization-address fallbacks are labelled. No bus access or travel times are claimed.
- **Repetition:** optional questions (ZIP, area, hours period) are asked once per session.

## Verification (developer retesting — the participant has not retested or approved these changes)

- Before the fixes: 25/34 checks. After: 34/34. Final screens, desktop and mobile:
  23/23. Backend: 244 tests (13 new in `tests/test_user_feedback_fixes.py`). Earlier UI suite 42/42.
- API-reported usage (real gpt-6-luna calls): before 11 requests; 88,050 input tokens (74,903 cached reads, 11,761 cache writes, 1,386 uncached); 4,829 output tokens; after
  10 requests; 79,165 input tokens (62,243 cached reads, 15,662 cache writes, 1,260 uncached); 4,751 output tokens; final screens 8 requests; 66,759 input tokens (56,784 cached reads, 8,967 cache writes, 1,008 uncached); 3,076 output tokens. Total 29 requests; 233,974 input tokens (193,930 cached reads, 36,390 cache writes, 3,654 uncached); 12,656 output tokens.

## Remaining limits

- One informal session; four short quotes, but no recorded tasks, times or ratings.
- The one-year-commitment mismatch wasn't reproduced, so the new check addresses a likely cause, not a confirmed one.
- Distances still need an optional ZIP and are straight lines; directions are only links; transit is not checked.
- Model behaviour varies between runs; the fixes above are enforced by code where possible.
- The participant's own words point to a limit the app doesn't remove: “I'd still have to visit three websites and
  probably email them.” The app prepares people to apply; confirming openings still means contacting organizations.
