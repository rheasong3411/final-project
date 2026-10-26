import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../api/client";
import type { Assessment, OpportunityDetail as Detail, SourceRef, VolunteerProfile } from "../api/types";
import { AssessmentView, ChecklistView, EvidenceQuotes } from "../components/AssessmentView";
import { EmptyState, ExternalLink, Loading, Notice } from "../components/Common";
import { CompareToggle } from "../components/CompareToggle";
import { IconPin } from "../components/Icons";
import { NextActions } from "../components/FactLines";
import { LocationDetails, useLocationEstimates, ZipField } from "../components/Location";
import { ProfileForm } from "../components/ProfileForm";
import { AppStatusBadge, UncertaintyBadge } from "../components/Status";
import { activityLabel, animalLabel, formatDate, hostOf, RECORD_TYPE_UI, scopeLabel } from "../lib/labels";
import { requirementRows } from "../lib/requirements";
import { effectiveProfile, useAppState } from "../state/AppState";

export function OpportunityDetail() {
  const { id = "" } = useParams();
  const [d, setD] = useState<Detail | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [fit, setFit] = useState<Assessment | null>(null);
  const [fitError, setFitError] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);
  const { confirmed, messageFacts, saveAnswers } = useAppState();

  useEffect(() => {
    const ctl = new AbortController();
    setD(null); setError(null); setFit(null);
    api.opportunity(id, ctl.signal).then(setD).catch((e) => { if (e.name !== "AbortError") setError(e); });
    return () => ctl.abort();
  }, [id]);

  const { browseZip, setBrowseZip } = useAppState();
  const est = useLocationEstimates(useMemo(() => [id], [id]), browseZip);
  const sources = useMemo(() => Object.fromEntries((d?.sources ?? []).map((s) => [s.source_id, s])) as Record<string, SourceRef>, [d]);

  async function checkFit(changes: Partial<VolunteerProfile>, removed: string[]) {
    // Only the answers the person changed here become confirmed; everything else is kept as it was.
    const touched = new Set([...Object.keys(changes), ...removed]);
    const next = { ...confirmed, ...changes } as Record<string, unknown>;
    for (const f of removed) delete next[f];
    const profile = effectiveProfile(next as VolunteerProfile, messageFacts.filter((m) => !touched.has(m.field)));
    if (touched.size) saveAnswers(changes, removed);
    setChecking(true); setFitError(null);
    try { setFit(await api.assess(id, profile)); }
    catch (e) { setFitError((e as Error).message); }
    finally { setChecking(false); }
  }

  if (error) {
    return <div className="container section"><EmptyState title={error.status === 404 ? "We couldn't find that opportunity" : "This page couldn't be loaded"}>
      <p className="muted">{error.message}</p><Link className="btn btn-primary" to="/explore">Back to Explore</Link></EmptyState></div>;
  }
  if (!d) return <div className="container section"><Loading label="Loading opportunity" /></div>;

  const r = d.record;
  const rows = requirementRows(r);

  return (
    <div className="container section-tight">
      <nav aria-label="Breadcrumb" className="small"><Link to="/explore">Explore</Link> <span aria-hidden>›</span> <span className="muted">{r.title}</span></nav>
      <div className="split" style={{ marginTop: 16 }}>
        <div className="stack">
          {RECORD_TYPE_UI[r.record_type] && <p className="chip chip-peach">{RECORD_TYPE_UI[r.record_type].chip}</p>}
          <h1 style={{ fontSize: "clamp(1.9rem, 4vw, 2.7rem)", marginBottom: 4 }}>{r.title}</h1>
          <p className="muted" style={{ fontSize: "1.1rem" }}>{d.organization.name} · {scopeLabel(d.geographic_scope)}</p>
          <div className="row"><AppStatusBadge status={r.application_status} label={d.application_status_label} /></div>
          <p style={{ fontSize: "1.08rem" }}>{r.description}</p>
          {RECORD_TYPE_UI[r.record_type] && <Notice tone="info">{RECORD_TYPE_UI[r.record_type].explain}</Notice>}
          <p className="row" style={{ gap: 8 }}><IconPin size={17} /><span>{r.location_town ?? "Town not published for this role"} · {r.location_description ?? "Location not published"}</span></p>
          <div className="chips">
            {r.activity_tags.map((t) => <span key={t} className="chip">{activityLabel(t)}</span>)}
            {r.animal_tags.map((t) => <span key={t} className="chip chip-outline">{animalLabel(t)}</span>)}
          </div>
        </div>
        <aside className="stack" aria-label="Location, apply and compare">
        <div className="card stack">
          <h2 style={{ fontSize: "1.25rem" }}>Where it takes place</h2>
          <LocationDetails loc={d.location} towns={d.towns}
            distance={est.zipArea?.status === "supported" ? est.estimates[id]?.distance : null} />
          <details className="disclosure">
            <summary>{est.zip ? "Change ZIP code" : "Estimate distance from your ZIP code"}</summary>
            <div className="disclosure-body"><ZipField idPrefix="detail" zip={browseZip} onApply={setBrowseZip} onRemove={() => setBrowseZip(null)} /></div>
          </details>
        </div>
        <div className="card stack">
          <h2 style={{ fontSize: "1.25rem" }}>Next step</h2>
          <p className="small muted" style={{ margin: 0 }}>
            {r.application_status === "explicitly_accepting_applications" ? "The organization's page says it is accepting applications. A place still isn't guaranteed."
              : r.application_status === "explicitly_closed" ? "The organization's page says these applications are closed. Its page may say when they reopen."
              : "The organization's pages don't clearly say whether applications are being accepted. Check its volunteer page or contact it before you apply."}
            {" "}This app never submits applications.</p>
          <NextActions actions={d.next_actions} />
          <div className="stack" style={{ gap: 4 }}>
            <CompareToggle id={r.opportunity_id} title={r.title} />
            <span className="hint">Optional: compare age, hours, commitment and fees side by side.</span>
          </div>
        </div>
        </aside>
      </div>

      <section className="section-tight" aria-labelledby="req-h">
        <h2 id="req-h">Requirements and schedule</h2>
        <p className="muted">From the organization's published pages. Badges mark information that is uncertain or conflicting; expand “Evidence” to see the exact wording and when we checked the page.</p>
        <div className="facts">
          {rows.map((row) => (
            <div key={row.key} className="fact">
              <div className="fact-head"><h3>{row.label}</h3>{row.status && <UncertaintyBadge status={row.status} />}</div>
              <div>{row.content}</div>
              {row.reasons.map((reason, i) => <p key={i} className="small" style={{ margin: 0, color: "var(--q-ink)" }}>{reason}</p>)}
              {row.quotes.length > 0 && <EvidenceQuotes quotes={row.quotes} sources={sources} />}
            </div>
          ))}
        </div>
        {r.unresolved_questions.length > 0 && (
          <div className="card card-peach" style={{ marginTop: 24 }}>
            <h3>Questions to ask the organization</h3>
            <ul style={{ marginBottom: 0 }}>{r.unresolved_questions.map((q, i) => <li key={i}>{q.question}</li>)}</ul>
          </div>
        )}
      </section>

      <section className="split" aria-label="Check my fit and prepare to apply">
        <div className="card stack" id="check-fit">
          <h2>Check my fit</h2>
          <p className="muted">A fixed-rule check against this role's published requirements — no AI involved. Blank answers become “needs confirmation”, never a “no”.</p>
          <ProfileForm confirmed={confirmed} messageFacts={messageFacts} onSave={checkFit} submitLabel="Check my fit" compact idPrefix="fit" submitUnchanged />
          {checking && <Loading label="Checking published requirements" />}
          {fitError && <Notice tone="error" title="The check couldn't be completed.">{fitError}</Notice>}
          {fit && <div aria-live="polite"><AssessmentView a={fit} sources={sources} /></div>}
        </div>
        <div className="stack">
          <div className="card">
            <h2 style={{ fontSize: "1.3rem" }}>Preparing to apply</h2>
            <ChecklistView steps={d.application_checklist} sources={sources} />
          </div>
          <div className="card">
            <h2 style={{ fontSize: "1.3rem" }}>Sources</h2>
            <p className="small muted">A “checked” date is when we viewed the page. It does not mean the organization confirmed the information that day.</p>
            <ul>{d.sources.map((s) => (
              <li key={s.source_id}><ExternalLink href={s.url}>{s.page_title}</ExternalLink><br /><span className="small muted">{hostOf(s.url)} · checked {formatDate(s.accessed_at)}</span></li>
            ))}</ul>
          </div>
        </div>
      </section>
    </div>
  );
}
