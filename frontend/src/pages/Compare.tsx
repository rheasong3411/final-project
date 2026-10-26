import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { OpportunityDetail, SourceRef } from "../api/types";
import { EvidenceQuotes } from "../components/AssessmentView";
import { EmptyState, Loading, Notice } from "../components/Common";
import { NextActions } from "../components/FactLines";
import { AppStatusBadge, UncertaintyBadge } from "../components/Status";
import { RECORD_TYPE_UI, scopeLabel } from "../lib/labels";
import { requirementRows, type ReqRow } from "../lib/requirements";
import { useAppState } from "../state/AppState";

const KEYS: [string, string][] = [["age", "Minimum age"], ["guardian", "Parent or guardian"], ["time", "Time commitment"],
  ["length", "Commitment length"], ["schedule", "Recurring schedule"], ["fees", "Fees"]];

function Cell({ row, sources }: { row?: ReqRow; sources: Record<string, SourceRef> }) {
  if (!row) return <span className="muted">Not published</span>;
  return (
    <div className="stack" style={{ gap: 6 }}>
      <div>{row.content}</div>
      {row.status && row.status !== "published_applicable" && <div><UncertaintyBadge status={row.status} /></div>}
      {row.quotes.length > 0 && <EvidenceQuotes quotes={row.quotes} sources={sources} />}
    </div>
  );
}

/** The same structured place text as the cards (never the HQ town presented as the role's own town). */
function placeLabel(d: OpportunityDetail): string {
  if (!d.location) return d.record.location_town ?? "Location: ask organization";
  return d.location.place_note ? `${d.location.place_label} · ${d.location.place_note}` : d.location.place_label;
}

export function Compare() {
  const { compareIds, removeCompare, clearCompare } = useAppState();
  const [items, setItems] = useState<OpportunityDetail[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!compareIds.length) { setItems([]); return; }
    const ctl = new AbortController();
    setItems(null);
    Promise.all(compareIds.map((id) => api.opportunity(id, ctl.signal)))
      .then(setItems).catch((e) => { if (e.name !== "AbortError") setError(e.message); });
    return () => ctl.abort();
  }, [compareIds]);

  const prepared = useMemo(() => (items ?? []).map((d) => ({
    d, rows: Object.fromEntries(requirementRows(d.record).map((r) => [r.key, r])) as Record<string, ReqRow>,
    sources: Object.fromEntries(d.sources.map((s) => [s.source_id, s])) as Record<string, SourceRef>,
  })), [items]);

  return (
    <div className="container section-tight">
      <p className="eyebrow">Compare</p>
      <h1 style={{ fontSize: "clamp(1.9rem, 4vw, 2.6rem)" }}>Compare opportunities</h1>
      <p className="muted">Compare age, hours, commitment and fees side by side, up to three at a time. Uncertain or conflicting information is flagged in each cell; expand “Evidence” to see the source wording.</p>
      {error && <Notice tone="error" title="Couldn't load the comparison.">{error}</Notice>}
      {compareIds.length === 0 && (
        <EmptyState title="Nothing selected to compare yet">
          <p className="muted">Use “Compare requirements” on any opportunity card or detail page to add it here.</p>
          <Link to="/explore" className="btn btn-primary">Explore opportunities</Link>
        </EmptyState>
      )}
      {compareIds.length > 0 && !items && !error && <Loading label="Loading comparison" />}
      {prepared.length > 0 && (
        <>
          <div className="row" style={{ justifyContent: "flex-end", margin: "12px 0" }}>
            <button className="btn btn-secondary btn-small" onClick={clearCompare}>Remove all</button>
          </div>
          <table className="compare-table">
            <caption className="visually-hidden">Requirements of the selected opportunities, side by side</caption>
            {/* A narrow label column, then equal widths for every opportunity (two or three), whatever the content. */}
            <colgroup><col className="compare-label-col" />{prepared.map(({ d }) => <col key={d.opportunity_id} />)}</colgroup>
            <thead>
              <tr>
                <th scope="col"><span className="visually-hidden">Requirement</span></th>
                {prepared.map(({ d }) => (
                  <th key={d.opportunity_id} scope="col">
                    {RECORD_TYPE_UI[d.record_type] && <div><span className="chip chip-peach" style={{ fontFamily: "var(--font-sans)" }}>{RECORD_TYPE_UI[d.record_type].chip}</span></div>}
                    <Link to={`/opportunities/${d.opportunity_id}`}>{d.title}</Link>
                    <div className="small muted" style={{ fontFamily: "var(--font-sans)", fontWeight: 500 }}>{d.organization_name}</div>
                    <div className="small muted" style={{ fontFamily: "var(--font-sans)", fontWeight: 500 }}>{placeLabel(d)} · {scopeLabel(d.geographic_scope)}</div>
                    <div style={{ fontFamily: "var(--font-sans)", fontWeight: 500, margin: "6px 0" }}><NextActions actions={d.next_actions} compact /></div>
                    <button className="link-button small" onClick={() => removeCompare(d.opportunity_id)}>Remove<span className="visually-hidden"> {d.title}</span></button>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr><th scope="row">Application status</th>{prepared.map(({ d }) => <td key={d.opportunity_id}><AppStatusBadge status={d.application_status} label={d.application_status_label} /></td>)}</tr>
              {KEYS.map(([k, label]) => (
                <tr key={k}><th scope="row">{label}</th>{prepared.map(({ d, rows, sources }) => <td key={d.opportunity_id}><Cell row={rows[k]} sources={sources} /></td>)}</tr>
              ))}
              <tr><th scope="row">Questions to ask</th>{prepared.map(({ d }) => (
                <td key={d.opportunity_id}>{d.record.unresolved_questions.length
                  ? <ul style={{ margin: 0 }}>{d.record.unresolved_questions.slice(0, 4).map((q, i) => <li key={i}>{q.question}</li>)}</ul>
                  : <span className="muted">None recorded</span>}</td>))}</tr>
            </tbody>
          </table>
          <div className="compare-cards">
            {prepared.map(({ d, rows, sources }) => (
              <article key={d.opportunity_id} className="card stack" aria-labelledby={`cc-${d.opportunity_id}`}>
                <div>
                  {RECORD_TYPE_UI[d.record_type] && <p className="chip chip-peach" style={{ marginBottom: 8 }}>{RECORD_TYPE_UI[d.record_type].chip}</p>}
                  <h2 id={`cc-${d.opportunity_id}`} style={{ fontSize: "1.25rem", marginBottom: 2 }}><Link to={`/opportunities/${d.opportunity_id}`}>{d.title}</Link></h2>
                  <p className="small muted" style={{ margin: 0 }}>{d.organization_name}</p>
                  <p className="small muted" style={{ margin: 0 }}>{placeLabel(d)} · {scopeLabel(d.geographic_scope)}</p>
                </div>
                <AppStatusBadge status={d.application_status} label={d.application_status_label} />
                <NextActions actions={d.next_actions} compact />
                <dl className="dl">
                  {KEYS.map(([k, label]) => (<div key={k}><dt>{label}</dt><dd><Cell row={rows[k]} sources={sources} /></dd></div>))}
                  <div><dt>Questions to ask</dt><dd>{d.record.unresolved_questions.length
                    ? <ul style={{ margin: 0 }}>{d.record.unresolved_questions.slice(0, 4).map((q, i) => <li key={i}>{q.question}</li>)}</ul>
                    : <span className="muted">None recorded</span>}</dd></div>
                </dl>
                <button className="btn btn-secondary btn-small" onClick={() => removeCompare(d.opportunity_id)}>Remove from compare</button>
              </article>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
