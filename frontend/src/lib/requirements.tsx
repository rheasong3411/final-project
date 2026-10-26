// Builds the requirement rows shown on detail and compare pages from the real record.
// Missing values say "Not published"; uncertain ones carry the applicability status and reason.
import type { ReactNode } from "react";
import type { ApplicabilityStatus, OpportunityRecord } from "../api/types";
import { dedupeQuotes } from "./evidence";
import { commitmentLabel, formatDate } from "./labels";

export interface ReqRow {
  key: string;
  label: string;
  content: ReactNode;
  status: ApplicabilityStatus | "not_published" | null;
  reasons: string[];
  quotes: { source_id: string; quote: string }[];
}

const RANK: Record<string, number> = { conflicting: 3, needs_confirmation: 2, published_applicable: 1 };

function worst(r: OpportunityRecord, fields: string[]): { status: ApplicabilityStatus | null; reasons: string[] } {
  let status: ApplicabilityStatus | null = null;
  const reasons: string[] = [];
  for (const f of fields) {
    const a = r.requirement_applicability[f];
    if (!a) continue;
    if (!status || RANK[a.status] > RANK[status]) status = a.status;
    if (a.status !== "published_applicable" && !reasons.includes(a.reason)) reasons.push(a.reason);
  }
  return { status, reasons };
}

function quotes(r: OpportunityRecord, fields: string[], extra: { source_id: string; quote: string }[] = []) {
  const q = r.field_evidence.filter((e) => fields.includes(e.field)).map((e) => ({ source_id: e.source_id, quote: e.evidence }));
  return dedupeQuotes([...q, ...extra]);
}

const NP = <span className="muted">Not published</span>;

export function requirementRows(r: OpportunityRecord): ReqRow[] {
  const rows: ReqRow[] = [];
  const add = (key: string, label: string, content: ReactNode, fields: string[], extra: { source_id: string; quote: string }[] = [], empty = false) => {
    const w = worst(r, fields);
    rows.push({ key, label, content, status: empty && !w.status ? "not_published" : w.status, reasons: w.reasons, quotes: quotes(r, fields, extra) });
  };

  // Age
  const ageApp = r.requirement_applicability.minimum_age?.status;
  add("age", "Minimum age",
    r.minimum_age === null
      ? (ageApp === "conflicting" ? "Sources conflict — confirm with organization"
        : ageApp === "needs_confirmation" ? "Unclear — confirm with organization" : NP)
      : r.minimum_age === 0 ? "All ages welcome (see guardian rule)" : `${r.minimum_age} or older`,
    ["minimum_age"], [], r.minimum_age === null && !ageApp);

  // Guardian
  add("guardian", "Parent or guardian",
    r.guardian_requirement ? r.guardian_requirement.details
      : <span className="muted">Not published (this doesn't mean a guardian isn't required)</span>,
    ["guardian_requirement"], [], !r.guardian_requirement);

  // Time
  const tc = r.time_commitment ?? [];
  const timeParts: ReactNode[] = [];
  if (r.minimum_hours !== null && r.hours_period) timeParts.push(`At least ${r.minimum_hours} hours per ${r.hours_period}`);
  for (const t of tc.filter((t) => t.hours_per === "session")) {
    const range = t.hours_min !== null && t.hours_max !== null && t.hours_min !== t.hours_max ? `${t.hours_min}–${t.hours_max}` : `${t.hours_min ?? t.hours_max}`;
    timeParts.push(`One session of ${range} hours`);
  }
  add("time", "Time commitment",
    <>
      <span className="chip" style={{ marginBottom: 6 }}>{commitmentLabel(r.commitment_type)}</span>
      {timeParts.length ? <ul style={{ margin: "6px 0 0" }}>{timeParts.map((t, i) => <li key={i}>{t}</li>)}</ul>
        : <div className="muted">No minimum hours published (not the same as no minimum)</div>}
    </>,
    ["minimum_hours", "hours_period", "commitment_type", "time_commitment"],
    tc.map((t) => ({ source_id: t.source_id, quote: t.published_text })));

  // Length
  const typical = tc.filter((t) => t.duration_is_typical_not_minimum);
  const varies = r.commitment_type === "variable" ? tc.filter((t) => !t.duration_is_typical_not_minimum) : [];
  add("length", "Commitment length",
    r.minimum_commitment_months !== null ? `At least ${r.minimum_commitment_months} months`
      : typical.length ? `Usually ${typical[0].duration_months_min}–${typical[0].duration_months_max} months (typical, not a stated minimum)`
        : varies.length ? `Varies: “${varies[0].published_text}”`
          : r.commitment_type === "one_time" ? "One-time; no minimum length applies" : NP,
    ["minimum_commitment_months"], [], r.minimum_commitment_months === null && !typical.length && !varies.length && r.commitment_type !== "one_time");

  // Schedule (recurring only)
  const sched = r.recurring_schedule ?? [];
  add("schedule", "Recurring schedule",
    sched.length ? <ul style={{ margin: 0 }}>{sched.map((s, i) => <li key={i}>{s.summary}</li>)}</ul> : NP,
    ["recurring_schedule"], sched.map((s) => ({ source_id: s.source_id, quote: s.original_text })), !sched.length);

  // Orientation (process info, not dates)
  const ori = r.orientation_info ?? [];
  add("orientation", "Orientation",
    ori.length ? <ul style={{ margin: 0 }}>{ori.map((s, i) => <li key={i}>{s.summary}</li>)}</ul> : NP,
    ["orientation_info"], ori.map((s) => ({ source_id: s.source_id, quote: s.original_text })), !ori.length);

  // Historical notices
  const notices = r.dated_notices ?? [];
  if (notices.length) {
    add("notices", "Past notices",
      <ul style={{ margin: 0 }}>{notices.map((n, i) => (
        <li key={i}><strong>Not an upcoming date.</strong> The page said “{n.stated_date_text}”{n.stated_year ? ` ${n.stated_year}` : " (no year given)"}; when checked on {formatDate(n.assessed_on)} this appeared to be in the past.</li>
      ))}</ul>,
      ["dated_notices"], notices.map((n) => ({ source_id: n.source_id, quote: n.original_text })));
  }

  // Training
  const tr = r.training_requirements ?? [];
  add("training", "Training and steps",
    tr.length ? <ul style={{ margin: 0 }}>{tr.map((t, i) => <li key={i}>{t.description}</li>)}</ul> : NP,
    ["training_requirements"], [], !tr.length);

  // Fees
  const fees = r.fees ?? [];
  add("fees", "Fees",
    fees.length ? <ul style={{ margin: 0 }}>{fees.map((f, i) => <li key={i}>${f.amount} {f.currency} — {f.applies_when}{f.payment_terms ? `. ${f.payment_terms}` : ""}</li>)}</ul>
      : <span className="muted">Not published (not the same as free)</span>,
    ["fees"], [], !fees.length);

  // Other requirements
  const other = r.other_requirements ?? [];
  if (other.length) add("other", "Other requirements", <ul style={{ margin: 0 }}>{other.map((o, i) => <li key={i}>{o.requirement}</li>)}</ul>, ["other_requirements"]);

  // Notes (not requirements)
  const notes = r.notes_for_applicants ?? [];
  if (notes.length) add("notes", "Good to know", <ul style={{ margin: 0 }}>{notes.map((n, i) => <li key={i}>{n.note}</li>)}</ul>, ["notes_for_applicants"]);

  return rows;
}
