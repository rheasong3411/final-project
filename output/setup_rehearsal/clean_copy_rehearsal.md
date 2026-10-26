# Grader setup: clean-copy rehearsal (2026-10-25)

**This is a clean-copy rehearsal, not a fresh GitHub clone.** No GitHub repository exists yet. Repeat
this from the real clone before submitting (checklist C3/C4/G9 stay pending until then).

**How it was run:** `python scripts/clean_copy_rehearsal.py --port 8001` (results in
`clean_copy_rehearsal.json`; first attempt in `clean_copy_rehearsal_attempt1.json`).

## What the rehearsal did

- **Copied** the 141 files that would be committed into a new temporary
  `submissions/animal-volunteer/`. It respected `.gitignore`: no `.venv`, `node_modules`,
  `local_data` (private snapshots) or `.env`. The built website `frontend/dist/` was included.
- **Used no** existing virtual environment, `node_modules` or shell credential: `PORTKEY_API_KEY` was
  removed from the server's environment.
- **Ran on port 8001.** The unrelated server on port 8000 was left running.

## Timings (automated)

| Step | Time |
|---|---|
| Copy files | 0.3 s |
| `python3 -m venv .venv` (Python 3.14.7) | 2.1 s |
| `pip install -r requirements.txt` | 7.1 s (pip download cache available); **12.4 s with `--no-cache-dir`** (measured separately) |
| Server start | 0.8–1.3 s |
| **Total automated run** (including 2 real assistant requests) | **33.3 s** |
| Manual credential placement (create one `.env` file) | not timed; the script wrote the file. Allow about 1–2 minutes for a person. |

## Results

| Credential location | Health check | Pages (`/`, `/explore`, an opportunity detail, `/find-my-fit`) | One real assistant request |
|---|---|---|---|
| None | `credentials_present: false` | all 200, website loads | `credentials_missing`, a clear error, no fake answer |
| `animal-volunteer/.env` (repo root) | source `project .env` | all 200 | ok, `gpt-6-luna-global`, 11.6 s, 24,049 input / 977 output tokens |
| `submissions/.env` (one folder above) | source `parent-folder .env` | all 200 | ok, `gpt-6-luna-global`, 8.7 s, 15,829 input / 893 output tokens |

- The temporary `.env` files were deleted afterwards.
- The key was never printed or written to the results (the script asserts this).
- **Attempt 1:** both stages sent the same message, so the parent-folder request (0.8 s, identical usage)
  was a Portkey gateway-cache replay. It proved the credential path but not fresh generation. Attempt 2
  uses a distinct message per stage, and both requests were fresh.

## Build check

`frontend/dist/` is byte-identical to a fresh `vite build` of the current source (14 files compared by
SHA-256). Rebuild with `cd frontend && npm ci && npm run build`. Node is only needed to rebuild.

## Not tested yet

- A real clone from GitHub.
- A machine without Python 3.14. The pinned packages were installed on 3.14.7; older Python versions
  are untested.
- Windows.
