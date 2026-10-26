# Comparison with existing services (sources accessed 2026-10-25)

**Method:** I read each product's own public pages. "Not found" means the pages I inspected did not
describe the feature. It does **not** mean the product lacks it. I did not create accounts or use
logged-in features.

## Sources

| Product | Pages inspected (accessed 2026-10-25) |
|---|---|
| Idealist (includes VolunteerMatch since early 2025) | https://www.idealist.org/en/volunteer ; https://www.idealist.org/en/help/how-do-i-search-for-volunteer-opportunities-on-idealist ; https://www.idealist.org/volunteermatch |
| Samaritan Scout | https://www.samaritanscout.org/ ; https://www.samaritanscout.org/about (the `/faq` URL returned 404) |
| General-purpose AI chat assistants (e.g. ChatGPT) | Not inspected as a product page. Compared only at the level of design: they are not tied to a fixed, dated, quoted dataset. |

## Feature comparison

| Feature | Idealist / VolunteerMatch | Samaritan Scout | Animal Volunteer Finder (ours) |
|---|---|---|---|
| Geographic coverage | National, with a radius of 5–100 miles or "Entire Country"; "100,000+ unique ways to volunteer", "more than 200,000 organizations" | Not stated. Aims to "scale Scout to serve the entire United States" | **Narrow by design:** 8 animal organizations (5 in Greater New Haven by default, 3 elsewhere in CT as a labelled opt-in), 64 records |
| Search and filters | Keyword, location and radius, on-site/hybrid/remote, date, cause areas, skills | A search engine for opportunities and organizations; filters not described | Town of the role, activity, animal, organization, commitment type, application status, record type |
| Matching | A "Best Match" sort based on the selected filters | "AI-guided search engine platform with an automated data pipeline" | One AI agent that searches the dataset, plus **fixed-rule** checks of the person's answers against each published requirement |
| Requirement evidence (age, guardian, hours, commitment) | Not found as structured fields or filters on the help page | Not found | Each requirement stored with a short quote, source URL and page-check date (376 quotes verified against saved page snapshots) |
| Conflicting or uncertain information | Not found | Not found | Conflicts kept, not resolved (e.g. Animal Haven 18+ vs 21+). Uncertain rules never count against a person and become questions to ask. |
| Eligibility explanation | Not found | Not found | "Meets / does not meet / needs confirmation", requirement by requirement, with the answers used and the evidence |
| Application preparation | "How to Apply" section on each listing; apply through Idealist, email or an external site | Not found | A checklist built from the data (link, orientation, fees, questions to ask). Applications always happen on the organization's own site. |
| Application status | Not found | Not found | Three labels ("Accepting applications (placement not guaranteed)", "Applications closed", "Confirm with organization"), kept separate from fit |

## What we can and cannot claim

- **Not new:** AI-assisted volunteer search and matching already exist. Samaritan Scout describes an
  AI-guided volunteer search engine, and Idealist offers best-match sorting at national scale.
- **Our specific contribution** is narrower. For one local cause (animal volunteering in Greater New
  Haven), the app checks a person against each **published, sourced** requirement with fixed rules.
  It:
  - keeps conflicting and outdated information visible instead of guessing;
  - refuses to turn uncertainty into a yes or no;
  - separates "do I meet the rules?" from "is the organization taking applications?";
  - prepares the person for the organization's own application.
- **The trade-off is coverage:** large platforms list far more opportunities and causes than our
  64-record dataset.
- **Not compared:** we did not run a side-by-side user test against these products.
