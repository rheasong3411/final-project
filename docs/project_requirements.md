# MGT409 Final Project — original requirements (faithful summary)

**Authoritative source:** `Final Project/Rubrics.pdf` (11 pages). It is a browser print of
<https://zlisto.github.io/mgt_409_fa26/project_requirements.html>, printed 10/25/26 3:41 PM,
© 2026 Tauhid Zaman. Text was extracted with `pypdf` and read in full on 2026-10-25.
This file summarizes that PDF. If anything here disagrees with the PDF, the PDF wins.

> **Path note:** the setup prompt said the PDF is in a `Rubrics/` folder. There is no such folder;
> the assignment is the single file `Final Project/Rubrics.pdf`.

## Deadline

**Monday, October 26, 2026 at 6:00 PM, on Canvas.** (Setup was done on Sunday, Oct 25, 2026, the day before.)

## The task

Build an AI agent app that does something useful for real people, then show how it works, what it
costs, and how you kept it safe. It should bring together the semester's skills: tools, structured
outputs, chat websites, multi-agent teams, caching and prompt-injection defenses. It does not have to
make money, but it has to make a difference. Solo project.

## What to submit (on Canvas)

| What | Format | Details |
|---|---|---|
| GitHub repo | Link (submitted in Canvas's website-URL field) | All app code plus a README explaining how to run it. **Public, or private with GitHub user `zlisto` added as a collaborator.** |
| Report | `report.html` | A single HTML file, **10–15 pages when printed** |
| Slide deck | `slides.html` | A single HTML file, **10 slides max** |
| Demo video | Optional | A 2–3 minute screen recording of you using the app |

**Self-contained HTML:** both HTML files must open by double-clicking on any computer, with every
screenshot showing. Images are embedded inside the file.

## Report (10–15 printed pages)

Written for a smart manager who has never seen the app. Use these sections, **in this order**, with
screenshots wherever they help. AI help with writing is allowed, but you are responsible for every word
and number, and they must match what the app actually does.

1. **Title + links:** project name, your name, the GitHub repo link (the same one submitted on Canvas),
   the app link if it is online, and one sentence on what the app does.
2. **Motivation:** who has the problem, how they deal with it today, what that costs them in money,
   time or frustration, and why anyone should care.
3. **What is new here:** look around first at what exists (apps, startups, ChatGPT itself). What does
   this project do that they don't? Be honest. If something close exists, say what you do differently
   and why it matters.
4. **The agents:** each agent and what it does; the tools each agent can use; if there is more than one
   agent, how they are organized and who hands work to whom (**draw a diagram**); which model(s) and
   why; and **one real run walked through step by step with screenshots**.
5. **Tokenomics:** tokens for one typical run (**input, cached input, output**), measured from real
   runs; cost per run and **per user per month**; cost at **100 and 10,000 users**; what you did to keep
   cost down; and **whether cost cutting made the app worse, with evidence**.
6. **Safety:** what could go wrong and what you built to stop it. Examples: attacks (prompt injection,
   attempts to leak data or cause misbehavior), agent malfunction (invented facts, wrong actions,
   endless loops), protecting the user, and overspending (what stops a bug or bad actor from burning
   the token budget). **Show at least one defense actually working, with a screenshot or a test.**
7. **Impact:** put numbers on it (money saved, hours saved, faster turnaround, better quality, more
   people served, or something newly possible), and say where the numbers come from (your tests, a pilot
   user, public data, a careful estimate). The strongest evidence is a real user trying it.
8. **Limits + next steps:** what doesn't work yet, and what you would build with another month.

Page count assumes normal letter-size pages, regular font, screenshots included. Real detail beats
filler, and **filler costs points**.

## Slide deck

HTML deck, **10 slides max**, telling the story in a few minutes. It must use **reveal.js** (loaded
from a CDN is fine), be a single HTML file, move with arrow keys and go full screen with F.
Screenshots and the diagram are embedded in the file. Suggested order: (1) Title, name and one-line
pitch; (2) problem and who has it; (3) what is new; (4) how the agents work (diagram); (5) demo
screenshots; (6) cost to run; (7) safety; (8) impact numbers; (9) what's next. Big text, clean design,
same colors as the app.

## GitHub repo

- All the code needed to run the app.
- A `README.md` that says what the app is and how to run it step by step (or the link, if it is online).
- A `.env.example` listing the keys needed, with no real values. **Never commit the real `.env` or the
  `PORTKEY_API_KEY`.**

## Model + budget

- **Course key:** `PORTKEY_API_KEY` with **`gpt-6-luna` only. No other models on the course key.**
- **Own key:** for a different model, use your own paid key. An OpenAI key must be named `OPENAI_API_KEY`.

## Testing the app (choose one)

1. **Online:** link at the top of the README and the report, kept up until final grades are posted.
   Free hosts often sleep, so check the link on submission day.
2. **Local from a fresh clone:** staff clone the repo and follow the README. Keep setup simple; if the
   app needs unusual software, a big database or many services, put it online instead.

**10-minute rule:** if the app is not running after 10 minutes of following the README, "The teaching
staff can run it" gets 0 points.

### Where the app finds API keys

Repos are cloned side by side into a `submissions/` folder, and the staff's `.env` sits **one level
above the repo**. The app must look for `.env` **first in the repo's own folder, then in the folder
above it**. Test this by moving your `.env` up one folder. The staff `.env` has exactly two keys,
`PORTKEY_API_KEY` and `OPENAI_API_KEY`; the app must use one of those exact names and list every key it
needs in `.env.example`. If the app needs any other key, put it online and consult the professor.

### Big data

If the app uses a large dataset, include a small test dataset so it runs locally, and explain in the
README how to switch between the two.

## Demo video (optional backup)

A 2–3 minute recording of the app running on your computer on a real example, start to finish, with
narration. If the app won't run for staff, the video can still earn the "It works" and "Look + feel"
points, but **not** the 5 points for "The teaching staff can run it."

## Before submitting

Dry run: clone into a brand-new folder, put `.env` one level above, follow the README and use the app.

## Grading (100 points)

**Tiers:** Tier 1 *It works* (runs and does what it says; familiar idea; report thin on numbers, cost
or safety). Tier 2 *It's clever and new* (plus a new idea or a smart new spin, thoughtfully designed
agents, a complete report with measured token costs, a real safety defense and screenshots). Tier 3
*It makes a difference* (plus a very clever idea that clearly helps real people and could really be
used, with evidence: a real user tried it, time or quality measured against today's approach, and cost
thought through for a whole organization; helping a nonprofit counts as much as saving money).

**Overdone ideas are capped at Tier 1 on the idea unless there is a real twist:** resume or cover-letter
reviewer; **chat with a PDF or a pile of documents**; trip planner; email or meeting summarizer; recipe
or meal planner; generic study buddy or flashcards; anything built in class or homework without a real
addition.

**Evidence rule:** in each report row, a section without the listed evidence gets **at most half** of
that row's points.

| Component | Pts | Top of range / evidence |
|---|---|---|
| **The idea:** Novelty + real-world value | 21 | Very clever, clearly new, solves a real problem, usable. Overdone ideas without a twist are capped at Tier 1. |
| **The app:** It works | 15 | Real end-to-end work: agents use real tools and real data and produce useful results without crashing. Clean repo, no secrets committed. |
| **The app:** Teaching staff can run it | 5 | Works online, or runs locally from a fresh clone via the README with `.env` one folder up; test dataset included if the real one is large. Not running after 10 minutes = 0. |
| **The app:** Look + feel | 10 | Clean layout, clear buttons and screens; a first-time user can figure it out. |
| **Report:** Motivation + what is new | 8 | Clear problem with a real person; honest look at what exists. *Evidence: named existing products compared against.* |
| **Report:** Agent design | 10 | Each agent and tool explained, clear diagram, smart organization. *Evidence: one real run traced step by step with screenshots of what each agent did.* |
| **Report:** Tokenomics | 8 | Cost per run, per user, at scale; concrete cost cuts and whether they hurt performance. *Evidence: real token counts from runs, in logs or app screenshots (the app can display its own usage). Estimates alone get half.* |
| **Report:** Safety | 8 | Risks that matter, with built defenses. *Evidence: a screenshot or test of a defense stopping an attack or malfunction. Describing a defense gets half.* |
| **Report:** Impact + metrics | 5 | Believable, sourced numbers; honest limits and next steps. *Evidence: a real user tried it (quote, screenshot or before/after time). Guesses alone get half.* |
| **Report:** Design | 2 | Clean, readable, sharp and well-placed screenshots and diagrams. |
| **Slides:** Content | 6 | Whole story in a few minutes, with a diagram, screenshots and key numbers. |
| **Slides:** Design | 2 | Big readable text, consistent style, visuals that carry the story. |
| **Total** | **100** | |

## Tips from the assignment

Start with a person, then the tech. Talk to a real user (even one 15-minute conversation). Take
screenshots as you go, including good runs, bad runs and safety catches. Ship something that works first,
then make it clever.

---

## Implementation notes vs. these requirements (updated 2026-10-25, backend stage)

This section is our own status note, not part of the assignment.

- **Model:** the backend calls only `gpt-6-luna`, using the course `PORTKEY_API_KEY` through Portkey's
  documented base URL. Every real response reported `gpt-6-luna-global`. No `OPENAI_API_KEY` or other
  model is used.
- **Keys:** the app looks for `.env` in the repo root and then the folder above it, and never overrides
  an existing environment variable. This matches "Where your app finds the API keys". `.env.example`
  lists `PORTKEY_API_KEY` with no value.
- **Data:** the dataset is small (64 records), so no separate test dataset is needed. The backend reads
  `data/` with relative paths.
- **Still open:** hosted vs. local delivery; the timed 10-minute fresh-clone dry run (not yet done);
  report; slides; demo video; real-user evidence; cost figures.
- **Discrepancies found in our planning documents:** none new at this stage. The checklist wording
  "API-reported usage" is stricter than the PDF ("real token counts ... in your logs or screenshots");
  the saved traces meet both readings.
