import { Link } from "react-router-dom";
import { Sprig } from "../components/Illustrations";
import { useAppState } from "../state/AppState";

export function About() {
  const { resetSession } = useAppState();
  return (
    <div className="container section-tight" style={{ maxWidth: 860 }}>
      <p className="eyebrow">About</p>
      <h1 style={{ fontSize: "clamp(1.9rem, 4vw, 2.7rem)" }}>How Animal Volunteer Finder works</h1>
      <p style={{ fontSize: "1.15rem" }} className="muted">A student project for MGT409 (AI Foundations for Managers) that helps people in Greater New Haven find animal-volunteering roles and understand what each one asks of them before applying.</p>

      <section className="section-tight stack">
        <h2>What it covers</h2>
        <p>The main view covers five Greater New Haven organizations: Friends of the New Haven Animal Shelter, The Animal Haven (North Haven), Branford Compassion Club (North Branford), the Dan Cosgrove Animal Shelter (Town of Branford), and The Greater New Haven Cat Project (Northford). Three organizations elsewhere in Connecticut appear only when you turn on “Include other Connecticut locations”. Each result shows its published town and is labelled “Other Connecticut location”.</p>
        <p>The project is not affiliated with or endorsed by any of these organizations.</p>

        <h2>How the information was gathered</h2>
        <p>Each role, requirement and application link was compiled from the organizations' public web pages. Each requirement keeps a short quote and the date we checked the page. Where pages disagree — for example, two different minimum ages — both versions are kept and the requirement is marked as conflicting rather than picking one. A checked date tells you when we looked at a page, not that the organization confirmed anything that day.</p>

        <h2>How requirement checks and AI recommendations work</h2>
        <p><strong>Requirement checks use fixed rules, not AI.</strong> When you check your fit, the app compares your answers with each published requirement and labels it “meets this published requirement”, “does not meet this published requirement”, or “needs confirmation”. A rule that is uncertain or conflicting becomes a question to ask, and is never marked as met. The one exception: if every published version of a conflicting minimum age is above your age, the role isn't suggested, and both versions stay visible. A blank answer is never treated as “no”.</p>
        <p><strong>The assistant</strong> (Find my fit) uses an AI model to understand your message, search this dataset, run those same fixed-rule checks, and explain the results in plain language. It cannot change the check results, and its suggestions about your answers stay unconfirmed until you confirm them.</p>

        <h2>Locations and distances</h2>
        <p>Every listing says what is actually known about where it happens: a <strong>verified volunteering site</strong> (an official page places the role at a street address, checked October 25, 2026, with coordinates from the U.S. Census Geocoder); only the <strong>organization's location</strong> (the activity location may differ); a <strong>published town</strong> only; <strong>help from your home</strong> (with any supported travel, such as picking up supplies); or <strong>location: ask organization</strong>. Mailing addresses and P.O. boxes are never used, and an organization's address never counts as the place a role happens.</p>
        <p>With an optional ZIP code, each listing shows one distance: to its verified volunteering site (“North Haven · About 6 miles away”); if the activity site is unknown, to the organization's verified physical location (“Organization: New Haven · About 1 mile away”, with “Activity location may differ”), or, for an organization with several sites and none named for the role, to its nearest site, by name. Otherwise no distance is shown. Activities done from home say “Help from your home”; they are never ranked as 0 miles. Distances are straight-line estimates from your ZIP area (U.S. Census ZIP Code Tabulation Areas, 2026), not driving, walking or transit distances. “Distance: nearest first” sorts the whole list by these estimates, with listings that have no distance last. Closeness never changes fit or application status. Maps links open the address without sending your ZIP.</p>

        <h2>What it can't do</h2>
        <ul>
          <li>It can't tell you whether a role is open right now. Most listings say “Availability not confirmed”. Roles whose pages say applications are closed aren't listed, but their detail pages still work.</li>
          <li>It doesn't approve volunteers, guarantee placement, book shifts, or submit applications.</li>
          <li>It has no live shift schedules, travel times or public-transit information, and it can't tell you whether a place is walkable. Distances are rough straight-line estimates only.</li>
          <li>The information can change after the dates shown. Always confirm with the organization.</li>
        </ul>

        <h2>Privacy</h2>
        <p>We only ask for what the checks need (for example your age in years and your town, never your birth date or address). A ZIP code is optional and only used to estimate distances. Your answers and conversation live in this browser tab's memory and are not saved to your device. When you use the assistant, your message is sent to our server and to the AI model provider to produce an answer; the server keeps only technical run statistics (such as timing and token counts), not your messages or ZIP code. Distance requests send your ZIP in the request body, never in a web address. Reloading the page clears everything, or you can clear it now.</p>
        <p><button className="btn btn-secondary" onClick={() => { resetSession(); }}>Clear my session now</button></p>
        <p className="small muted">The assistant and requirement checks are aids, not advice. <Link to="/explore">Explore opportunities</Link> or <Link to="/find-my-fit">find your fit</Link>.</p>
      </section>
      <div aria-hidden style={{ display: "flex", justifyContent: "flex-end", opacity: 0.8 }}><Sprig className="" /></div>
    </div>
  );
}
