# Final consistency and visual check (2026-10-26)

All of the following were actually run on the regenerated `report.html` and `slides.html`.

## Fixes
- **Slide 4 speaker notes** now state the exception to "not met only for `published_applicable`": when every conflicting
  published minimum age is above the person's age, the role is kept out of recommendations and alternatives, and the
  source conflict stays visible.
- **The app's About page** said uncertain or conflicting rules "never count against you". It now states the same
  exception, and that such rules are never marked as met. Frontend rebuilt (`index-BxocqyZG.js`) and the text checked in
  the running app.
- The report already stated the exception (§4), as did README.md and docs/backend_design.md. Historical records weren't
  edited.
- **Report test count:** 244 → 245 (re-counted). **Slide 7** now labels the $0.00185 mean as Session 11 and shows the
  final-build spot check ($0.00160, 10 runs).
- **Print layout, report page 8:**
  - The option card's "Possible fit" badge was cut off; the crop and the print height cap for paired images were adjusted.
  - The older Session 16 Explore screenshot printed too small and started mid-heading, so it was removed. The location
    table covers the same content.
  - "Run details" is now its own figure.
  - The "Your answers" caption was corrected to match the taller crop.

## Checks
- **`report.html`:** 15 US Letter pages (Chrome print); sections in the required order (Title + links → Limits + next
  steps, then References); 6 images, all embedded as data URIs and loading from `file://`; 0 external requests.
- **`slides.html`:** 10 slides; reveal.js loads from the CDN (the course's suggested setup), so it needs internet; 5
  embedded images, all loading from `file://`; 1 SVG diagram; arrow keys move between slides; no element overflows a
  slide.
- **Links:** all 26 external links returned HTTP 200.
- **Facts checked against the code and data:**
  - tools: 6, and their names;
  - model: gpt-6-luna, returned as gpt-6-luna-global;
  - limits: 8 requests, 14 tool calls, 120k tokens, 60 s and 180 s timeouts, 2 retries, 6 calls a minute;
  - data: 8 organizations, 64 records, 37 sources, 9 sites, 6 closed roles, 37 Greater New Haven records (4 closed, 0
    accepting);
  - tests: 245 backend, 52 validator.
- **Visual check:** every report page and slide was rendered and inspected (`report_page_*.png`, `slide_*.png`).
- **Tests:** 245 passed; data validation 0 errors.
