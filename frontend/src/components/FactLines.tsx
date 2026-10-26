// One labelled line per fact, rendered from the backend's structured results (never from the model's prose):
// location, estimated distance, minimum age, guardian, hours, commitment, application status and fit.
// The person's own answer is shown next to the requirement when known; nothing is invented when it isn't.
import type { Assessment, DistanceEstimate, NextAction, Recommendation, RequirementAssessment } from "../api/types";
import { hostOf, scopeLabel } from "../lib/labels";
import { PlaceLine } from "./Location";
import { ExternalLink } from "./Common";
import { AppStatusBadge, OverallBadge } from "./Status";

const STATUS_TEXT: Record<string, string> = {
  met: "Meets requirement", not_met: "Doesn't meet requirement", needs_confirmation: "Needs confirmation",
};

const ROWS: { label: string; keys: string[] }[] = [
  { label: "Minimum age", keys: ["minimum_age"] },
  { label: "Parent or guardian", keys: ["guardian_requirement"] },
  { label: "Hours", keys: ["minimum_hours", "time_commitment", "session_length"] },
  { label: "Commitment", keys: ["minimum_commitment_months"] },
];

function published(r: RequirementAssessment): string {
  const t = r.published_requirement;
  const age = /^Minimum age (\d+)$/.exec(t);
  if (age) return `${age[1]}+`;
  return t.replace(/^Minimum commitment of /, "").replace(/^Published versions: /, "Sources say ")
    .replace(/ \(published minimums differ\)$/, "");  // the note beside it already says the sources differ
}

const DAYS: Record<string, string> = { mon: "Mon", tue: "Tue", wed: "Wed", thu: "Thu", fri: "Fri", sat: "Sat", sun: "Sun" };
const hoursText = (lo: unknown, hi: unknown) => (hi !== null && hi !== undefined ? `${lo}–${hi}` : String(lo));

/** Directions to the place the estimate is about, labelled when it is only the organization's address. */
function Directions({ loc }: { loc: NonNullable<Recommendation["location"]> }) {
  const [url, text] = loc.kind === "verified_site" && loc.site?.directions_url ? [loc.site.directions_url, "Directions"]
    : loc.kind === "organization_location" && loc.organization_site?.directions_url
      ? [loc.organization_site.directions_url, "Directions to the organization's address"]
      : loc.kind === "home_based" && loc.related_site?.directions_url
        ? [loc.related_site.directions_url, `Directions to ${loc.related_site.label}`] : [null, null];
  if (!url) return null;
  return <span className="place-note"><ExternalLink href={url} arrow label={`${text} (opens Google Maps in a new tab; you enter your starting point)`}>{text}</ExternalLink></span>;
}

/** The person's answer the rule was checked against, or "not given yet". Never guessed. */
function yourAnswer(r: RequirementAssessment): string {
  const u = r.profile_fields_used as Record<string, unknown>;
  const has = (k: string) => u[k] !== null && u[k] !== undefined;
  if ("age" in u) return has("age") ? String(u.age) : "not given yet";
  if ("guardian_available" in u) return has("guardian_available") ? (u.guardian_available ? "can come" : "can't come") : "not given yet";
  if ("available_hours" in u) return has("available_hours")
    ? `${hoursText(u.available_hours, u.available_hours_max)} hours${u.hours_period ? ` per ${u.hours_period}` : " (week, month or visit not said yet)"}`
    : "not given yet";
  if ("available_days" in u || "available_times" in u) {
    const d = ((u.available_days as string[]) ?? []).map((x) => DAYS[x] ?? x).join(", ");
    const t = ((u.available_times as string[]) ?? []).join(", ");
    return [d, t].filter(Boolean).join(" · ") || "not given yet";
  }
  if ("max_session_hours" in u) return has("max_session_hours") ? `up to ${u.max_session_hours} hours per session` : "not given yet";
  if ("commitment_months" in u) return has("commitment_months") ? `${u.commitment_months} months` : "not given yet";
  return "";
}

function Row({ label, children, note }: { label: string; children: React.ReactNode; note?: string | null }) {
  return (
    <div className="fact-line">
      <dt>{label}</dt>
      <dd>{children}{note && <span className="fact-note"> ⚠ {note}</span>}</dd>
    </div>
  );
}

export function FactLines({ rec, assessment, distance, showDistanceRow }: {
  rec: Recommendation; assessment: Assessment; distance: DistanceEstimate | null | undefined; showDistanceRow: boolean;
}) {
  const loc = rec.location;
  const byKey = new Map(assessment.requirements.map((r) => [r.requirement, r]));
  const rows = [...ROWS, ...(byKey.has("recurring_schedule") ? [{ label: "Schedule", keys: ["recurring_schedule"] }] : [])]
    .map(({ label, keys }) => ({ label, r: keys.map((k) => byKey.get(k)).find(Boolean) }));
  // A note shared by several rows ("Listed on an older application form…") is shown once, naming those rows.
  const noteRows = new Map<string, string[]>();
  for (const { label, r } of rows) if (r?.uncertainty_note) noteRows.set(r.uncertainty_note, [...(noteRows.get(r.uncertainty_note) ?? []), label]);
  const shared = [...noteRows].filter(([, ls]) => ls.length > 1);
  return (
    <dl className="fact-lines">
      {loc && (
        <Row label="Location">
          <PlaceLine loc={loc} d={showDistanceRow ? distance : null} />
          <Directions loc={loc} />
          {loc.geographic_scope === "wider_connecticut" && <span className="place-note">{scopeLabel(loc.geographic_scope)}</span>}
        </Row>
      )}
      {rows.map(({ label, r }) => {
        if (!r) return <Row key={label} label={label}><span className="muted">Not published</span></Row>;
        const you = yourAnswer(r);
        const note = r.uncertainty_note && (noteRows.get(r.uncertainty_note)?.length ?? 0) > 1 ? null : r.uncertainty_note;
        return (
          <Row key={label} label={label} note={note}>
            {published(r)}
            {you && <> <span className="sep">|</span> You: {you}</>}
            {" "}<span className="sep">|</span> <span className={`fit-word fit-${r.status}`}>{STATUS_TEXT[r.status]}</span>
            {r.listed_value_matched && <span className="small muted">{r.requirement === "minimum_age"
              ? " (your age meets both published minimums)" : " (your answer matches the listed value)"}</span>}
          </Row>
        );
      })}
      {shared.map(([note, labels]) => (
        <div key={note} className="fact-line fact-line-note"><dt className="visually-hidden">Note</dt>
          <dd><span className="fact-note">⚠ {labels.join(" and ")}: {note.charAt(0).toLowerCase() + note.slice(1)}</span></dd></div>
      ))}
      <Row label="Application status">
        <AppStatusBadge status={assessment.application_status.status} label={assessment.application_status.label} />
      </Row>
      <Row label="Your fit"><OverallBadge status={assessment.overall_status} /></Row>
    </dl>
  );
}

/** "Visit volunteer page ↗" (or "Apply on organization's website ↗" for a real application page that isn't closed) and
 *  "Contact organization ↗", linked to the organization's own pages. Nothing is submitted. */
export function NextActions({ actions, compact = false }: { actions: NextAction[] | undefined; compact?: boolean }) {
  if (!actions?.length) return null;
  return (
    <div className={`row next-actions${compact ? " next-actions-compact" : ""}`} style={{ gap: compact ? 6 : 8 }}>
      {actions.map((a) => (
        <ExternalLink key={a.kind} href={a.url} arrow className={a.kind === "contact" ? "text-link" : "btn btn-small btn-secondary"}
          label={`${a.label} (opens ${hostOf(a.url)} in a new tab)`}>{a.label}</ExternalLink>
      ))}
    </div>
  );
}
