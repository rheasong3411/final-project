# Prospective-user test guide (for Rhea to run with one real person)

**Status: one informal test conducted (2026-10-26); findings in `docs/user_test_findings.md`. Task times,
ratings and a verbatim quote were not recorded; use this guide for any further session.** Automated browser checks and the owner's own testing are not user testing.
Don't report any findings until a real session has happened. A pre-session readiness walkthrough (synthetic, not a
user test) is in `output/user_test_readiness/`.

## Who to invite

- **One adult (18+)** who might actually look for animal-volunteering opportunities in Greater New
  Haven, for example a student, neighbour or coworker who likes animals. Using an adult avoids needing
  a guardian's consent.
- Ideally someone who hasn't seen the app.
- **You contact them yourself.** The assistant does not contact anyone.

## Before the session (5 minutes)

1. Start the app from `animal-volunteer/`:
   `.venv/bin/uvicorn backend.api:app --host 127.0.0.1 --port 8001`. Port 8000 is used by another app on this Mac.
   - Don't set `AVF_SAVE_TRACES` (it's for synthetic tests only). Normal runs save only a metrics line, with no
     message text, in `local_data/api_run_metrics.jsonl`.
   - Check `http://127.0.0.1:8001/api/health`: the model should be `gpt-6-luna`, with `credentials_present: true`.
   - Open `http://127.0.0.1:8001` in a **new private window**. Everything is kept in memory, so a fresh window
     starts empty. If the window was used before, click **Clear my session** on Find my fit.
   - Use a laptop or desktop at a normal window size. The phone layout works, but a Compare selection bar can sit
     over part of the page until you scroll.
2. Have a stopwatch ready, plus the private notes template: copy
   `docs/user_test_record_template.md` to `local_data/user_test/notes.md`. `local_data/` is
   gitignored, so raw notes never enter the submission.
3. Read the consent script below and note the answers.

**Consent script:** "I'm testing a class project that helps people find animal-volunteering
opportunities. It takes about 20 minutes. I'll time a few tasks and take notes, but I won't record your
name or anything that identifies you. Please don't type your name, address or contact details into the
app. What you type into Find my fit is sent to an AI model (OpenAI's model, through the course's Portkey
gateway) to write the replies. The app doesn't save your messages, but the AI service may keep its own logs, so
please only share what you're comfortable with, such as your age and the time you have. You can stop at any time.
May I quote something you say, anonymously, in my class report? And may I describe you only as, for example,
'a graduate student in New Haven who likes cats'?"

## Tasks (think aloud; don't help unless they're stuck for 2 minutes)

| # | Task, read aloud | Done when |
|---|---|---|
| T1 | "Find one animal-volunteering opportunity in Greater New Haven that interests you." | They open a detail page they say interests them |
| T2 | "Compare the requirements of two or three opportunities — age, time and anything you'd need to confirm." | They use Compare (or detail pages) and can state one difference |
| T3 | "Use Find my fit to ask whether something might suit you. Share only what you're comfortable sharing." | They read a reply and the **Your answers** panel; using **Confirm these details** or Edit on at least one answer counts |
| T4 | "What is your next step to actually apply for the one you like best?" | They name the step (for example "open the organization's page", "attend orientation", "ask about the age rule") |

- A Find my fit reply can take up to a minute; don't count that wait as confusion, but note it if it bothers them.
- If the assistant shows an error, note it, let them try once more, then move on. T1, T2 and T4 don't need the AI.

For each task, record:
- **Completion:** done / partly / not done.
- **Time in seconds:** start when you finish reading the task, stop when it is done or abandoned.
- **Confusion:** where they hesitated or misread something.
- Anything they say about trust or uncertainty.

## Debrief (5 minutes)

1. "On a scale of 1–5, how easy was this?" and "How much would you trust the requirement information?"
2. "What was most confusing?" and "What would you change first?"
3. "Would you use this if you were looking to volunteer? Why or why not?"
4. Ask permission again for **one direct quote**, and note it word for word.

## Optional: measuring time saved (only with a baseline)

To claim time saved, run a **comparable manual task**. The person uses an ordinary web search and the
organizations' own websites, without this app, to "find one animal-volunteering role in Greater New
Haven you could do, and write down its minimum age, time commitment, and how to apply". Time it with
the same rules.

- **Order effects:** whichever method goes second benefits from what they learned in the first. With
  one person you can't remove this; say which order you used.
- **Report it honestly:** say "one participant, one task, order X: manual N min vs app M min". Don't
  call it a measured saving in general.
- **Without the manual task, report task times only.** Make no time-saving claim.

## After the session

- Keep raw notes only in `local_data/user_test/` (or on paper).
- Write an **anonymized** summary for the report, only with the participant's permission: role
  description, task results and times, the quote, top confusions and suggested improvements.
- Never include names, contact details or screenshots showing their personal information.
