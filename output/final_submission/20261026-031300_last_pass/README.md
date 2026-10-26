# Last pass before submission (2026-10-26)

- **Python compatibility:** a fresh clone with Python 3.10 failed. `pydantic-ai-slim` 2.61 requires Python 3.11+, but
  the README said 3.10+. The README and requirements now say **3.11 or newer**, and the quick start checks the version.
  Two report/setup scripts used Python 3.12-only f-string syntax; they were made compatible.
- **Find my fit on phones:** the comparison bar no longer covers the chat. It is hidden on Find my fit, and the
  "Compare (N)" menu link stays. Checked on desktop and mobile (`find_my_fit_no_tray_*.png`).
- **Slide 9:** shows the measured numbers (13 pages across 5 organizations; median 22 s).
- **Report:** the setup line is commit-neutral.
- **Checks:** 245 tests, data validation 0 errors, UI suite 42/42 (`ui_check/`); report 15 pages, slides 10, no
  overflow (all rendered here).
