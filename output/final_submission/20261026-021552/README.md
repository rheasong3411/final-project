# Final submission checks (2026-10-26)

Repository: **https://github.com/rheasong3411/final-project** (public). The app is not hosted; it runs locally.

## Fresh clone from GitHub (tested commit `c3f1e0a`)

Followed only the README quick start, in a new temporary folder outside the project, with a new virtual environment:
`git clone` → `cd final-project` → `python3 -m venv .venv` → `source .venv/bin/activate` → `pip install -r requirements.txt`
→ `.env` (PORTKEY_API_KEY) one folder above → `uvicorn backend.api:app --port 8011`.

- **Environment:** macOS 14.7.3 (arm64), Python 3.14.7, pip 26.2.1. **pip cache disabled** to imitate a machine without
  cached downloads. `PORTKEY_API_KEY` was unset in the shell, so the key could only come from a `.env` file. Port 8011
  because 8000 and 8001 were in use by other servers.
- **Time (commands only):** clone 5.4 s, venv 7.5 s, pip done 21.6 s, server ready 23.2 s, home page served **23.3 s**
  (cumulative). A person's reading and typing time is extra. Well inside the 10-minute rule. Log: `setup_log.txt`.
- **.env loading:** `../.env` → "parent-folder .env"; `./.env` → "project .env". The key copies were deleted after.
- **App checks** (`fresh_clone_checks_script.py`): pages (Home, Explore, About, Find my fit, detail), an animal filter
  and scope-matched town options, ZIP distances and Explore Clear all (ZIP, sort, filters reset), a two-role comparison,
  no overflow or errors, desktop and mobile.
  - `fresh_clone/`: first attempt; the real reply arrived, then the script stopped on a Playwright checkbox call (script bug).
  - `fresh_clone_run2/`: **25/25**, but its Find my fit reply was a **gateway cache replay** of the first attempt's
    identical request (same usage to the token), so it is not counted as a fresh call.
  - `fresh_clone_run3_fresh_call/`: **25/25**, server restarted with `AVF_CACHE_FORCE_REFRESH=1` and trace saving (test
    settings only; no installed files changed). Gateway status `REFRESH, REFRESH, REFRESH, REFRESH`: a fresh call.
- **Real Find my fit (run `fresh_clone__e0d3f9c8f4da`), gpt-6-luna via Portkey, returned `gpt-6-luna-global`:**
  tools `update_location_preferences → search_opportunities → assess_profile → final_result`; profile {"age": 25, "town": "New Haven", "has_car": false, "animal_preferences": ["cats"], "available_hours": 2.0, "available_hours_max": 3.0, "available_days": ["sat"], "available_times": ["morning"]};
  API-reported usage 4 requests, 32,754 input tokens (27,959 cached reads,
  4,291 cache writes, 504 uncached), 1,503 output tokens.
  The two earlier calls used 34,364 input / 2,320 output tokens each (the second being the replay).

## Report and slides (renders of this version were removed as outdated; see `../20261026-031300_last_pass/`)

- `report.html`: **15** US Letter pages (Chrome print), 7 embedded images, 0 external requests, sections in the required
  order (Title + links → Limits + next steps). Every page rendered and inspected (`report_page_*.png`).
- `slides.html`: **10** reveal.js slides (reveal.js from a CDN, as the assignment suggests), the architecture diagram and
  5 embedded screenshots, no overflow. Every slide rendered and inspected. Three slide labels were corrected after
  inspection (`slide_*_after_label_fix.png`): "Session 16 build" instead of "final build", "mostly synthetic testing plus
  one informal user test", and the location row.
- All 26 external links returned HTTP 200. No placeholders remain. Older screenshots are captioned with their build.
- Feedback (paraphrased, one informal user), developer retesting, automated tests and real-run evidence are kept
  separate; no participant quotes, timings or approval are claimed.

Later commits after `c3f1e0a` changed only documentation, README text and the regenerated report/slides.
