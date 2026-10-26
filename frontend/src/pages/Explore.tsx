import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import type { FilterValues, OpportunityList } from "../api/types";
import { EmptyState, Loading, Notice } from "../components/Common";
import { ACCEPTING_NOTE, DISTANCE_NOTE, sortByDistance, useLocationEstimates, ZipField } from "../components/Location";
import { useAppState } from "../state/AppState";
import { OpportunityCard } from "../components/OpportunityCard";
import { activityLabel, animalLabel, COMMITMENT_FILTER } from "../lib/labels";

const MULTI = ["activity", "animal"] as const;
const SINGLE = ["q", "town", "organization_id", "commitment_type"] as const;

export function Explore() {
  const [params, setParams] = useSearchParams();
  const [filters, setFilters] = useState<FilterValues | null>(null);
  const [data, setData] = useState<OpportunityList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [qDraft, setQDraft] = useState(params.get("q") ?? "");

  const COMMITMENT_VALUES = COMMITMENT_FILTER.map(([v]) => v);
  const commitment = params.get("commitment_type") ?? "";
  const sortParam = params.get("sort") ?? "";
  const sortClosest = sortParam === "closest";
  const sortOrg = sortParam === "org";
  const { browseZip, setBrowseZip } = useAppState();
  const [zipFieldKey, setZipFieldKey] = useState(0);   // bumping it remounts the ZIP field: draft and errors cleared

  // "Commitment not published" is no longer a filter: an old link or URL with it (or any unknown value)
  // falls back to "Any commitment", which still includes records whose commitment isn't published.
  // The application-status filter was removed (closed roles are left out by the backend). Old links that still
  // carry it, or the removed "unknown" commitment value, fall back to the defaults.
  useEffect(() => {
    const badCommitment = commitment && !COMMITMENT_VALUES.includes(commitment);
    if (badCommitment || params.has("application_status")) {
      const n = new URLSearchParams(params);
      if (badCommitment) n.delete("commitment_type");
      n.delete("application_status");
      setParams(n, { replace: true });
    }
  }, [commitment, params.has("application_status")]); // eslint-disable-line react-hooks/exhaustive-deps

  const wider = params.get("wider") === "1";
  const includeInterest = params.get("interest") === "1";
  const includeIndependent = params.get("independent") === "1";

  useEffect(() => {
    const ctl = new AbortController();
    api.filters(ctl.signal).then(setFilters).catch((e) => { if (e.name !== "AbortError") setError(e.message); });
    return () => ctl.abort();
  }, []);

  const apiParams = useMemo(() => {
    const p: Record<string, string | string[] | undefined> = { scope: wider ? "all" : "greater_new_haven" };
    for (const k of SINGLE) p[k] = params.get(k) ?? undefined;
    if (p.commitment_type && !COMMITMENT_VALUES.includes(p.commitment_type as string)) p.commitment_type = undefined;
    for (const k of MULTI) p[k] = params.getAll(k);
    p.record_type = ["described_volunteer_role", ...(includeInterest ? ["interest_area_only"] : []),
      ...(includeIndependent ? ["independent_support_activity"] : [])];
    return p;
  }, [params, wider, includeInterest, includeIndependent]);

  useEffect(() => {
    const ctl = new AbortController();
    setData(null); setError(null);
    api.opportunities(apiParams, ctl.signal).then(setData).catch((e) => { if (e.name !== "AbortError") setError(e.message); });
    return () => ctl.abort();
  }, [apiParams]);

  const update = (fn: (p: URLSearchParams) => void) => { const n = new URLSearchParams(params); fn(n); setParams(n, { replace: true }); };
  const setSingle = (k: string, v: string) => update((p) => (v ? p.set(k, v) : p.delete(k)));
  const toggleMulti = (k: string, v: string) => update((p) => {
    const cur = p.getAll(k); p.delete(k);
    (cur.includes(v) ? cur.filter((x) => x !== v) : [...cur, v]).forEach((x) => p.append(k, x));
  });
  const toggleFlag = (k: string) => update((p) => (p.get(k) === "1" ? p.delete(k) : p.set(k, "1")));
  // Clears every browsing setting: search, filters, optional record types, wider Connecticut, sorting and the browsing
  // ZIP (typed draft, applied value, messages and derived distances). Find my fit answers are untouched.
  const clearAll = () => {
    setQDraft(""); setParams(new URLSearchParams(), { replace: true });
    setBrowseZip(null); setZipFieldKey((k) => k + 1);
  };

  const orgName = (id: string) => filters?.organizations.find((o) => o.organization_id === id)?.name ?? id;
  const active: { label: string; remove: () => void }[] = [];
  if (params.get("q")) active.push({ label: `Search: “${params.get("q")}”`, remove: () => { setQDraft(""); setSingle("q", ""); } });
  if (params.get("town")) active.push({ label: `Volunteering in: ${params.get("town")}`, remove: () => setSingle("town", "") });
  params.getAll("activity").forEach((a) => active.push({ label: activityLabel(a), remove: () => toggleMulti("activity", a) }));
  params.getAll("animal").forEach((a) => active.push({ label: animalLabel(a), remove: () => toggleMulti("animal", a) }));
  if (params.get("organization_id")) active.push({ label: orgName(params.get("organization_id")!), remove: () => setSingle("organization_id", "") });
  const commitmentText = COMMITMENT_FILTER.find(([v]) => v === commitment)?.[1];
  if (commitment && commitmentText) active.push({ label: commitmentText, remove: () => setSingle("commitment_type", "") });
  if (wider) active.push({ label: "Including other Connecticut locations", remove: () => toggleFlag("wider") });
  if (includeInterest) active.push({ label: "Showing additional volunteer interests", remove: () => toggleFlag("interest") });
  if (includeIndependent) active.push({ label: "Showing ways to help on your own", remove: () => toggleFlag("independent") });

  const orgs = filters?.organizations.filter((o) => wider || o.geographic_scope === "greater_new_haven") ?? [];
  // Town options follow the selected scope: other Connecticut towns only when that scope is on.
  const townOptions = (wider ? filters?.towns_by_scope?.all : filters?.towns_by_scope?.greater_new_haven) ?? filters?.towns ?? [];
  const townParam = params.get("town");
  useEffect(() => {  // a town from the wider scope is cleared when the scope narrows (no silent empty results)
    if (filters && townParam && !townOptions.includes(townParam)) setSingle("town", "");
  }, [filters, wider, townParam]); // eslint-disable-line react-hooks/exhaustive-deps

  const ids = useMemo(() => (data?.results ?? []).map((o) => o.opportunity_id), [data]);
  const est = useLocationEstimates(ids, browseZip);
  const zipSupported = est.zipArea?.status === "supported";
  const sorting = sortClosest && zipSupported;
  // One list, one count. Distance order uses the backend's unrounded sort_miles; records without a distance go last.
  const listed = !data ? [] : sorting ? sortByDistance(data.results, (o) => o.opportunity_id, est.estimates)
    : sortOrg ? [...data.results].sort((a, b) => a.organization_name.localeCompare(b.organization_name) || a.title.localeCompare(b.title))
    : data.results;
  const canClear = active.length > 0 || !!browseZip || !!sortParam;
  const card = (o: OpportunityList["results"][number]) => (
    <OpportunityCard key={o.opportunity_id} o={o} showScope={wider} distance={zipSupported ? est.estimates[o.opportunity_id]?.distance : null} />);

  return (
    <div className="container section-tight">
      <p className="eyebrow">Explore</p>
      <h1 style={{ fontSize: "clamp(2rem, 4vw, 2.8rem)" }}>Animal-volunteering opportunities</h1>
      <p className="muted" style={{ maxWidth: 760 }}>Showing roles described by organizations in <strong>{wider ? "Greater New Haven and other Connecticut locations" : "Greater New Haven"}</strong>. Roles whose applications are closed aren't listed (you can still open them from a direct link). Each card says what is known about where it happens and links to the organization's own volunteer page. {ACCEPTING_NOTE}</p>

      <div className="explore-layout" style={{ marginTop: 28 }}>
        <aside aria-label="Filters" className="filters">
          <form role="search" onSubmit={(e) => { e.preventDefault(); setSingle("q", qDraft.trim()); }} className="field">
            <label htmlFor="q">Search</label>
            <div className="row" style={{ flexWrap: "nowrap" }}>
              <input id="q" type="search" value={qDraft} onChange={(e) => setQDraft(e.target.value)} placeholder="e.g. cats, fundraising" />
              <button className="btn btn-secondary btn-small" type="submit">Search</button>
            </div>
          </form>
          <div className="field">
            <label htmlFor="town">Volunteering location</label>
            <select id="town" value={params.get("town") ?? ""} onChange={(e) => setSingle("town", e.target.value)}>
              <option value="">All towns in this area</option>
              {townOptions.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            <span className="hint">Only roles whose own published location is in this town (the same rule the assistant uses). An organization's address doesn't count; use “Organization” to see everything it lists. This isn't where you live.</span>
            <label className="toggle" style={{ marginTop: 8 }}><input type="checkbox" checked={wider} onChange={() => toggleFlag("wider")} />
              <span>Include other Connecticut locations<br /><span className="hint">Expand beyond Greater New Haven.</span></span></label>
          </div>
          <div className="stack" style={{ gap: 8 }}>
            <ZipField key={zipFieldKey} idPrefix="ex" zip={browseZip} onApply={setBrowseZip} onRemove={() => setBrowseZip(null)} />
            <div className="field">
              <label htmlFor="sort">Sort results</label>
              <select id="sort" value={sortOrg ? "org" : sortClosest && zipSupported ? "closest" : ""} onChange={(e) => setSingle("sort", e.target.value)}
                aria-describedby="sort-help">
                <option value="">Default order</option>
                <option value="org">Organization name A–Z</option>
                <option value="closest" disabled={!zipSupported}>Distance: nearest first{zipSupported ? "" : " (needs a ZIP code)"}</option>
              </select>
              <span id="sort-help" className="hint">{zipSupported
                ? "Listings without a distance are shown last."
                : "Add a supported Connecticut ZIP code above to sort by distance."}</span>
            </div>
          </div>
          <fieldset>
            <legend>Activity</legend>
            <div className="checks">
              {filters?.activity_tags.map((a) => (
                <label key={a} className="check"><input type="checkbox" checked={params.getAll("activity").includes(a)} onChange={() => toggleMulti("activity", a)} /><span>{activityLabel(a)}</span></label>
              ))}
            </div>
          </fieldset>
          <fieldset>
            <legend>Animals</legend>
            <div className="checks">
              {["dogs", "cats", "small_animals", "not_applicable"].map((a) => (
                <label key={a} className="check"><input type="checkbox" checked={params.getAll("animal").includes(a)} onChange={() => toggleMulti("animal", a)} /><span>{animalLabel(a)}</span></label>
              ))}
            </div>
          </fieldset>
          <div className="field">
            <label htmlFor="org">Organization</label>
            <select id="org" value={params.get("organization_id") ?? ""} onChange={(e) => setSingle("organization_id", e.target.value)}>
              <option value="">All organizations</option>
              {orgs.map((o) => <option key={o.organization_id} value={o.organization_id}>{o.name}</option>)}
            </select>
          </div>
          <div className="field">
            <label htmlFor="ct">Commitment type</label>
            <select id="ct" value={COMMITMENT_VALUES.includes(commitment) ? commitment : ""} onChange={(e) => setSingle("commitment_type", e.target.value)}>
              {COMMITMENT_FILTER.map(([v, label]) => <option key={v || "any"} value={v}>{label}</option>)}
            </select>
            <span className="hint">“Any commitment” also includes listings that don't publish one.</span>
          </div>
          <fieldset className="stack">
            <legend>More ways to help</legend>
            <label className="toggle"><input type="checkbox" checked={includeIndependent} onChange={() => toggleFlag("independent")} />
              <span>Show ways to help on your own<br /><span className="hint">Organize a supply drive, make pet beds or bandanas, or start a fundraiser.</span></span></label>
            <label className="toggle"><input type="checkbox" checked={includeInterest} onChange={() => toggleFlag("interest")} />
              <span>Show additional volunteer interests<br /><span className="hint">Activities mentioned on application forms, with details to ask the organization about.</span></span></label>
          </fieldset>
          <button className="btn btn-secondary" onClick={clearAll} disabled={!canClear}>Clear all filters</button>
        </aside>

        <section aria-labelledby="results-heading">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <h2 id="results-heading" style={{ fontSize: "1.3rem", margin: 0 }} aria-live="polite">
              {data ? `${data.count} ${data.count === 1 ? "result" : "results"}` : "Results"}
            </h2>
            {canClear && <button className="link-button" onClick={clearAll}>Clear all</button>}
          </div>
          {active.length > 0 && (
            <div className="active-filters" style={{ margin: "12px 0" }} aria-label="Active filters">
              {active.map((f) => (
                <button key={f.label} className="chip remove-chip" onClick={f.remove} aria-label={`Remove filter: ${f.label}`}>{f.label} <span aria-hidden>×</span></button>
              ))}
            </div>
          )}
          {error && <Notice tone="error" title="We couldn't load opportunities.">{error}</Notice>}
          {!data && !error && <div className="grid grid-3" style={{ marginTop: 16 }}>{[0, 1, 2].map((i) => <div key={i} className="skeleton" />)}</div>}
          {data && data.closed_hidden > 0 && (
            <p className="small muted" style={{ margin: "8px 0 0" }}>{data.closed_hidden} {data.closed_hidden === 1 ? "role matching these filters has" : "roles matching these filters have"} closed applications and {data.closed_hidden === 1 ? "isn't" : "aren't"} shown.</p>
          )}
          {data && data.count === 0 && (
            <div style={{ marginTop: 16 }}>
              <EmptyState title="No matching opportunities to show">
                <p className="muted">Nothing that isn't closed matches all of these filters. Try removing a filter, choosing “All towns in this area”, including other Connecticut locations, or showing ways to help on your own.</p>
                <button className="btn btn-primary" onClick={clearAll}>Clear all filters</button>
              </EmptyState>
            </div>
          )}
          {data && data.count > 0 && zipSupported && <p className="small muted" style={{ margin: "12px 0 0" }}>{DISTANCE_NOTE}</p>}
          {data && data.count > 0 && <div className="grid grid-3" style={{ marginTop: 16 }}>{listed.map(card)}</div>}
          {!data && !error && <Loading label="Loading results" />}
        </section>
      </div>
    </div>
  );
}
