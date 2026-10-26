# Screenshots overwritten during Session 16 (2026-10-25)

While re-running the earlier browser check scripts against the Session 16 build, the following files were
re-captured in place by mistake. **They show the Session 16 interface, not the session named by their folder or
caption.** The original captures could not be recovered (no backup copy was found). Results of those earlier
sessions remain documented in their JSON reports and in `AI_prompts.md`; the files below are not evidence of how
the earlier builds looked.

Root folder (written by `scripts/ui_check.py`, which saves here by default; one real assistant turn on the
gpt-6-luna server at port 8001 was also sent, untraced, before the script stopped on an outdated selector):
`desktop_explore.png`, `desktop_opportunity_detail.png`, `desktop_compare.png`, `desktop_home.png`,
`desktop_find_my_fit_error_state_simulated.png`, `desktop_keyboard_focus_visible.png`,
`desktop_explore_empty_state.png`, `desktop_find_my_fit_real_reply.png`, `desktop_check_my_fit_missing_info.png`.

`session13/` (written by the Session 13 check script): `s13_compare_desktop.png`, `s13_compare_mobile.png`,
`s13_explore_two_selected_desktop.png`, `s13_explore_two_selected_mobile.png`, `s13_card_explanation_desktop.png`,
`s13_card_explanation_mobile.png`, `s13_explore_cards_desktop.png`, `s13_explore_cards_mobile.png`.

`session15/` (written by the Session 15 check script): `s15_explore_after_clear_desktop.png`,
`s15_explore_after_clear_mobile.png`, `s15_explore_sort_zip_desktop.png`, `s15_explore_sort_zip_mobile.png`.

Later re-runs write to a scratch folder instead (`UI_CHECK_OUT`), so no other files were affected.

## Recovery (2026-10-25, after Session 16)

**Outcome: all 21 historical screenshots restored to their original paths.** The note above described the
situation before recovery and is kept unchanged as a record of the mistake.

- **Source:** an earlier project ZIP provided by Rhea, saved as `Final Project/backup.zip` (502 entries). Its copies of
  the 21 files carry their original times (root files 17:53–17:54, `session13/` 22:39, `session15/` 22:32–22:33),
  all before the overwrite at about 23:11–23:12.
- **Method:** the ZIP was extracted into a temporary folder outside the project. The recaptured Session 16 images were
  first copied to `session16/recaptured_overwrites/` (same relative paths, with a README); then only these 21 files
  were copied back. No code, data, frontend build, report or slides were replaced.
- **Verification:** SHA-256 of each restored file equals the hash of the same member read directly from `backup.zip`
  and of the extracted copy: **21/21 byte-identical**. Full hashes: `session16/recaptured_overwrites/recovery_sha256.json`.
- 19 of the 21 recaptures differed from the originals; 2 (`desktop_keyboard_focus_visible.png`,
  `session13/s13_explore_cards_mobile.png`) happened to be byte-identical to them.
- The report and slides use none of these 21 files (they use `session16/s16_*`, `session11`, `session12`,
  `mobile_home.png` and the two safety screenshots), so they were not rebuilt.
- Prevention: `scripts/ui_check.py` and `scripts/ui_safety_demo.py` now write every run to a new
  `output/screenshots/runs/<script>_<date-time>/` folder by default.

| Restored file | SHA-256 (first 16 hex) | Identical to backup |
|---|---|---|
| `desktop_explore.png` | `2c4e9e2e378ac79d…` | yes |
| `desktop_opportunity_detail.png` | `72a1f2b54b75fd67…` | yes |
| `desktop_compare.png` | `28002a7ba2e31b98…` | yes |
| `desktop_home.png` | `24015ee00c4942be…` | yes |
| `desktop_find_my_fit_error_state_simulated.png` | `f94be557eb3d17d6…` | yes |
| `desktop_keyboard_focus_visible.png` | `85c141c29d18b827…` | yes |
| `desktop_explore_empty_state.png` | `bdb4e32296df0e9d…` | yes |
| `desktop_find_my_fit_real_reply.png` | `d58d3a49fd38d01c…` | yes |
| `desktop_check_my_fit_missing_info.png` | `4f437530dd4915e2…` | yes |
| `session13/s13_compare_desktop.png` | `c494039e7a2db8c0…` | yes |
| `session13/s13_compare_mobile.png` | `c40fd9e4e79a0db1…` | yes |
| `session13/s13_explore_two_selected_desktop.png` | `594efcd5bf5cf63e…` | yes |
| `session13/s13_explore_two_selected_mobile.png` | `b139417be77c3623…` | yes |
| `session13/s13_card_explanation_desktop.png` | `0ee7289be74ee569…` | yes |
| `session13/s13_card_explanation_mobile.png` | `fe434082c711aeb6…` | yes |
| `session13/s13_explore_cards_desktop.png` | `e6a8d58fa1367c17…` | yes |
| `session13/s13_explore_cards_mobile.png` | `290636600f68c096…` | yes |
| `session15/s15_explore_after_clear_desktop.png` | `8bd0104f12b8a312…` | yes |
| `session15/s15_explore_after_clear_mobile.png` | `70fa5f23f5449287…` | yes |
| `session15/s15_explore_sort_zip_desktop.png` | `a36f859d0e73b5d0…` | yes |
| `session15/s15_explore_sort_zip_mobile.png` | `cabbc976b08c095a…` | yes |
