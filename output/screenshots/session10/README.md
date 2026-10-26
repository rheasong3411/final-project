# Session 10 screenshots (2026-10-25)

Genuine screenshots of the production build (`frontend/dist/` served by FastAPI), taken with Playwright in
Google Chrome at 1440 × 900 (desktop) and 390 × 844 (mobile). **All inputs are synthetic.** The ZIP codes
visible (06511, 06513, and the invalid or unsupported 6511, 06520, 10001) are test values; 06511 is the public
ZIP of Yale SOM's area.

| File | Shows |
|---|---|
| `s10_explore_commitment_dropdown_expanded_*` | The commitment filter with its four options: Any commitment, One-time, Ongoing, Flexible / varies. **The list is expanded in place with the HTML `size="4"` attribute**, because a native drop-down's pop-up is drawn by the operating system and doesn't appear in browser screenshots. The same four options appear in the normal pop-up. |
| `s10_explore_zip_closest_*` | Explore with a supported ZIP and "Closest estimated location": distance lines, the straight-line note, and listings without a verified location placed last. |
| `s10_detail_location_*` | A verified site with its address, "Approx. … from your ZIP area", the explanation and "Check location in maps". |
| `s10_detail_unverified_location_*` | GNHCP direct care: "Distance unavailable", the reason, a possible (unconfirmed) site, and no maps link. |
| `s10_fmf_t1_*`, `t3`, `t4_zip`, `t5_restricted*` | The real gpt-6-luna conversation (turns 1, 3, 4, 5) with earlier turns collapsed into "Previous conversation". |
| `s10_fmf_loading_t*` | While a request runs: the new message, "Updating your results…", and the earlier answer collapsed. |
| `s10_fmf_previous_open_*` | "Previous conversation" reopened: earlier messages and replies, and the note that they're still part of the session. |
| `s10_fmf_failed_*` / `s10_fmf_failed_reopened_*` | A **simulated** failure (the browser aborted the request): the draft is kept, and "Show my last results (based on earlier answers)" reopens them under a "Based on your earlier answers" notice. |
| `s10_fmf_zip_declined_desktop` | The person declined to give a ZIP: no distances, and no repeated ZIP question. |
| `s10_fmf_loading_t2_decline` | The loading state in the decline-ZIP conversation. |

The Find my fit screenshots were taken just before a small spacing fix: on mobile, the "Location details used"
line and the distance note had no gap between them. The fix changes only that margin.
