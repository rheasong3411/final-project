// Renders the backend's deterministic Assessment. Fit and application status are shown separately.
import type { Assessment, ChecklistStep, RequirementAssessment, SourceRef } from "../api/types";
import { formatDate, formatProfileValue, PROFILE_FIELD_LABEL, requirementLabel } from "../lib/labels";
import { ExternalLink } from "./Common";
import { dedupeQuotes } from "../lib/evidence";
import { AppStatusBadge, FitBadge, OverallBadge, UncertaintyBadge } from "./Status";

export function RequirementResults({ items, sources }: { items: RequirementAssessment[]; sources?: Record<string, SourceRef> }) {
  if (!items.length) return <p className="muted">No published requirements to check for this record.</p>;
  return (
    <ul className="req-list">
      {items.map((r, i) => {
        const used = Object.entries(r.profile_fields_used).filter(([, v]) => !(Array.isArray(v) && v.length === 0));
        return (
          <li key={i} className="req-item">
            <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
              <h4>{requirementLabel(r.requirement)}</h4>
              <FitBadge status={r.status} />
            </div>
            <p style={{ margin: "4px 0" }}><span className="muted small">Published: </span>{r.published_requirement}</p>
            <div className="row" style={{ margin: "6px 0" }}><UncertaintyBadge status={r.applicability} /></div>
            <p style={{ margin: "6px 0" }}>{r.explanation}</p>
            {r.listed_value_matched && r.requirement !== "minimum_age" && <p className="small muted" style={{ margin: "0 0 6px" }}>Your answer matches the listed value, but this rule may be outdated or the sources conflict, so it still needs confirmation.</p>}
            {used.length > 0 && (
              <p className="small muted" style={{ margin: 0 }}>
                Your answers used: {used.map(([k, v]) => `${PROFILE_FIELD_LABEL[k as keyof typeof PROFILE_FIELD_LABEL] ?? k}: ${formatProfileValue(k, v)}`).join(" · ")}
              </p>
            )}
            {r.evidence.length > 0 && <EvidenceQuotes quotes={r.evidence} sources={sources} />}
          </li>
        );
      })}
    </ul>
  );
}

export function EvidenceQuotes({ quotes, sources, label = "Evidence" }:
  { quotes: { source_id: string; quote: string }[]; sources?: Record<string, SourceRef>; label?: string }) {
  const shown = dedupeQuotes(quotes);  // the count always matches the passages shown
  if (!shown.length) return null;
  return (
    <details className="disclosure" style={{ marginTop: 10 }}>
      <summary>{label} ({shown.length})</summary>
      <div className="disclosure-body">
        {shown.map((q, i) => {
          const s = sources?.[q.source_id];
          return (
            <div key={i} style={{ marginTop: 8 }}>
              <blockquote>“{q.quote}”</blockquote>
              <p className="small muted" style={{ margin: 0 }}>
                {s ? <><ExternalLink href={s.url}>{s.page_title}</ExternalLink> · page checked {formatDate(s.accessed_at)}</> : <>Source: {q.source_id}</>}
              </p>
            </div>
          );
        })}
      </div>
    </details>
  );
}

export function AssessmentView({ a, sources }: { a: Assessment; sources?: Record<string, SourceRef> }) {
  return (
    <div className="stack">
      <div className="row" style={{ gap: 10 }}>
        <span className="badge-label">Fit:</span><OverallBadge status={a.overall_status} />
      </div>
      <p>{a.overall_summary}</p>
      <div className="row" style={{ gap: 10 }}>
        <span className="badge-label">Application status (separate from fit):</span>
        <AppStatusBadge status={a.application_status.status} label={a.application_status.label} />
      </div>
      <p className="small muted">{a.placement_or_shift_availability}</p>
      <h4>Requirement by requirement</h4>
      <RequirementResults items={a.requirements} sources={sources} />
      {a.costs.length > 0 && (<><h4>Costs</h4><ul>{a.costs.map((c, i) => <li key={i}>{stripSourceTags(c)}</li>)}</ul></>)}
      {a.notes.length > 0 && (<><h4>Notes</h4><ul>{a.notes.map((n, i) => <li key={i}>{stripSourceTags(n)}</li>)}</ul></>)}
      {a.questions_for_organization.length > 0 && (
        <><h4>Questions to ask the organization</h4><ul>{a.questions_for_organization.map((q, i) => <li key={i}>{q}</li>)}</ul></>
      )}
    </div>
  );
}

export function ChecklistView({ steps, sources }: { steps: ChecklistStep[]; sources?: Record<string, SourceRef> }) {
  return (
    <ol>
      {steps.map((s, i) => (
        <li key={i} style={{ marginBottom: 10 }}>
          <Linkified text={s.step} />
          {s.source_ids.length > 0 && sources && (
            <span className="small muted"> — source: {s.source_ids.map((id) => sources[id]?.page_title ?? id).join(", ")}</span>
          )}
        </li>
      ))}
    </ol>
  );
}

/** Turns bare https URLs in backend text into safe external links (no HTML parsing). */
export function Linkified({ text }: { text: string }) {
  const parts = text.split(/(https?:\/\/[^\s)]+)/g);
  return <>{parts.map((p, i) => (/^https?:\/\//.test(p) ? <ExternalLink key={i} href={p.replace(/[.,]$/, "")}>{p.replace(/[.,]$/, "")}</ExternalLink> : p))}</>;
}

export const stripSourceTags = (s: string) => s.replace(/\s*\[[a-z0-9_]+\]\s*$/i, "");
