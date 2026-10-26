# Location and distance evidence (Session 10, 2026-10-25)

All inputs are synthetic. ZIP 06511 (the public ZIP of Yale SOM's area) and 06513 are **test values**, used
here to show what the app calculates; no real person's ZIP is recorded anywhere.

## Files

- `ui_location_test_report.json`: browser results against the production build. Explore and detail 48/48 (no AI); the
  real-AI conversation 118/119 (12 fresh gpt-6-luna runs; one wording-regex miss, with the manual review recorded
  next to it); the earlier non-AI suite 42/42.
- `independent_distance_check.json`: the app's haversine distances compared with a WGS84 ellipsoidal geodesic
  computed by a separate library (`pyproj` 3.8.0).
- Screenshots: `output/screenshots/session10/` (desktop 1440 px, mobile 390 px).

## Data sources

| What | Source | Licence / permission | Date | Notes |
|---|---|---|---|---|
| ZIP areas | U.S. Census Bureau, 2026 Gazetteer Files, ZIP Code Tabulation Areas (`2026_Gaz_zcta_national.zip`) | U.S. Government work, public domain in the U.S. (17 U.S.C. 105); no key or account | File Last-Modified 2026-09-08; downloaded 2026-10-25 | **Census ZCTAs, not postal ZIP boundaries.** Coordinates are each ZCTA's internal point. 289 Connecticut rows kept (`data/geo/`). |
| Volunteering addresses | Official organization pages (fetched again 2026-10-25) | Short quotes only; snapshots stay local | Access time per quote in `data/volunteer_locations.json` | 30/30 quotes found in the page snapshots. Mailing addresses and P.O. boxes are never used. |
| Site coordinates | U.S. Census Geocoder REST API (`onelineaddress`, benchmark `Public_AR_Current`) | Public Census service, no key; results are U.S. Government works | Geocoded 2026-10-25 | Exactly one match per address. Interpolated along TIGER address ranges, so approximate. |
| Maps links | Google Maps URLs (`/maps/search/?api=1&query=<address>`) | Documented; no API key needed | — | Sends only the organization's address; the person picks the starting point. |

## Representative distances (test ZIP 06511)

| Role | Verified site | Shown as |
|---|---|---|
| `fnhas_dog_handler` | Robin I. Kroogman New Haven Animal Shelter, 81 Fournier Street, New Haven, CT 06511 | Approx. 1 mile from your ZIP area |
| `ah_dog_walking` | The Animal Haven shelter, 89 Mill Road, North Haven, CT 06473 | Approx. 6 miles from your ZIP area |
| `bcc_shelter_care` | Branford Compassion Club Feline Rescue and Adoption Center, 2037 Foxon Road, North Branford, CT 06471 | Approx. 9 miles from your ZIP area |
| `branford_general_volunteer` | Dan Cosgrove Animal Shelter, 749 East Main Street, Branford, CT 06405 | Approx. 9 miles from your ZIP area |
| `chs_newington_group_trails` | CHS Newington adoption center, 701 Russell Road, Newington, CT 06111 | Approx. 29 miles from your ZIP area |
| `paws_cat_volunteer` | PAWS shelter, 504 Main Avenue, Norwalk, CT 06851 | Approx. 28 miles from your ZIP area |

Changing the ZIP to 06513 re-estimates them (for example the New Haven shelter goes from "Approx. 1 mile" to
"Approx. 3.5 miles"), with no AI call. Roles without a verified site show "Distance unavailable" with the reason
("the organization doesn't say where this role takes place", "this role takes place in your own home", or "no
verified volunteering location"); they are never dropped, and "Closest estimated location" lists them last.

## Independent check

Over 18 ZIP-to-site pairs (06511 and 06513 to all nine sites), the app's spherical haversine (radius 3,958.8 miles)
and the WGS84 geodesic differ by at most **0.10 mile** (0.25% at 42 miles). 17 of 18 rounded labels match. The
exception sits on a rounding boundary: 06513 to the New Haven shelter is 3.747 miles (app) vs 3.756 miles
(geodesic), shown as "3.5" vs "4" miles. Hand check: 06511's internal point (41.31727, −72.926373) to 89 Mill Road,
North Haven (41.371340, −72.840054) gives 5.83 miles by the formula and 5.84 miles geodesic, shown as "Approx. 6
miles".

## Limitations

- **From the ZIP area's center, not the person's home.** Large ZIP areas can put someone several miles from the point used.
- **Straight line only.** No driving, walking or transit routing, travel times or walkability claims.
- **Interpolated site coordinates** can be off by tens to a few hundred metres; a large property (The Animal Haven's
  seven acres) is one point. Rounding to at least half a mile is coarser than that error.
- **Coverage:** Connecticut ZCTAs only. P.O. Box-only and single-organization ZIPs (e.g. 06501, 06520) have no area.
- **Only 15 of 64 records** have a verified volunteering site. Events, fostering, field work and most office or
  remote-unclear roles have no distance.
- **Closeness is separate from fit and status.** A closed role 1 mile away stays closed and is never recommended.
