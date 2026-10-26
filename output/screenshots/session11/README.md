# Session 11 screenshots (2026-10-25)

Production build served by FastAPI, Playwright + Chrome at 1440 × 900 and 390 × 844. **Synthetic inputs**; the ZIP shown
(06511) is a test value.

- `s11_final_*`: **final** captures after all spacing fixes (real gpt-6-luna turn, run `ui_s11_screens__*`):
  reply top, one option card with its labelled fact lines, the "Your answers" summary, full page.
  The mobile option-card capture is partly covered by the sticky header at the top (a capture artifact of a tall
  element); the full-page mobile capture shows it unobstructed.
- `s11_fmf_*`, `s11_preferences_summary_*`: the tested five-turn conversation and decline case. These were taken
  just before a small layout fix (the "Confirms only…" hint beside the Confirm button now sits on its own line).
- `s11_explore_*`, `s11_detail_*`: Explore (commitment filter expanded in place with `size="4"`, because native
  drop-down pop-ups don't appear in screenshots; ZIP sorting) and detail pages with the next-step buttons.
- `s11_compare_*`, `s11_home_*`: current Compare and Home pages.
