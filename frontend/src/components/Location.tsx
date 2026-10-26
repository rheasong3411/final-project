// Location, optional ZIP and approximate distances. Distances come only from the backend
// (Census ZIP areas + verified sites); the browser never calculates or guesses one.
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { DistanceEstimate, LocationInfo, LocationEstimates, ZipArea } from "../api/types";
import { effectiveProfile, useAppState } from "../state/AppState";
import { ExternalLink } from "./Common";
import { IconPin } from "./Icons";

export const ZIP_HELP = "Used to estimate which locations are closer. No street address needed.";
/** Shown once near results, never repeated per option. */
export const DISTANCE_NOTE = "Distances are straight-line estimates from your ZIP area. For some activities, the distance is to the organization; the activity location may differ.";
export const ACCEPTING_NOTE = "“Accepting applications” doesn't guarantee a placement or a particular shift.";
export const MAPS_NOTE = "Maps and directions links open Google Maps with only the destination filled in. Your ZIP isn't sent; you enter your own starting point and choose how to travel. This app doesn't check travel times or transit routes.";

/** The ZIP currently in this session (confirmed in a form, or taken from the person's own message). */
export function useSessionZip(): string | null {
  const { confirmed, messageFacts } = useAppState();
  const z = effectiveProfile(confirmed, messageFacts).zip_code;
  return typeof z === "string" && z ? z : null;
}

/** Fetches straight-line estimates for `ids` whenever the given ZIP or the ids change (POST; ZIP never in a URL).
 *  Explore and detail pages pass the browsing ZIP; Find my fit passes the ZIP from its own answers. */
export function useLocationEstimates(ids: string[], zip: string | null) {
  const key = ids.join(",");
  const [state, setState] = useState<{ key: string; data: LocationEstimates | null; error: boolean }>({ key: "", data: null, error: false });
  useEffect(() => {
    if (!zip) return;
    const ctl = new AbortController();
    api.locationEstimates(zip, ids, ctl.signal)
      .then((data) => setState({ key: `${zip}|${key}`, data, error: false }))
      .catch((e) => { if (e.name !== "AbortError") setState({ key: `${zip}|${key}`, data: null, error: true }); });
    return () => ctl.abort();
  }, [zip, key]); // eslint-disable-line react-hooks/exhaustive-deps
  const fresh = zip && state.key === `${zip}|${key}`;
  return {
    zip,
    zipArea: fresh ? state.data?.zip_area ?? null : null,
    estimates: fresh ? state.data?.estimates ?? {} : {},
    loading: !!zip && !fresh,
    error: fresh ? state.error : false,
  };
}

/** "Distance: nearest first": ONE list, ordered by the backend's unrounded `sort_miles` (volunteering site, else the
 *  organization's verified location). Records without a distance follow, in their original order (stable sort). */
export function sortByDistance<T>(items: T[], idOf: (t: T) => string, estimates: Record<string, { distance: DistanceEstimate }>) {
  const key = (t: T) => estimates[idOf(t)]?.distance?.sort_miles ?? Infinity;
  return [...items].sort((a, b) => key(a) - key(b));
}

/** The one place/distance line for a record, from structured fields only:
 *  "North Haven · About 6 miles away"; "Organization: New Haven · About 2 miles away" + "Activity location may differ";
 *  "Help from your home" (+ a clearly labelled secondary distance). Without a ZIP: the place only. */
export function PlaceLine({ loc, d }: { loc: LocationInfo | null | undefined; d?: DistanceEstimate | null }) {
  if (!loc) return null;
  const est = d && d.status === "estimated" && d.label ? d : null;
  if (loc.kind === "home_based") {
    return (
      <span className="place-line">
        <strong>Help from your home</strong>
        {est && <span className="place-note">{est.label}{est.type === "organization_reference" ? " (for reference; no travel is stated)" : ""}</span>}
      </span>
    );
  }
  const note = est ? est.secondary : loc.place_note;
  return (
    <span className="place-line">
      <strong>{est ? est.label : loc.place_label}</strong>
      {note && <span className="place-note">{note}</span>}
    </span>
  );
}

function Site({ s, label }: { s: { label: string; address: string; maps_url: string | null; directions_url?: string | null }; label: string }) {
  return (
    <span>{label}: <strong>{s.label}</strong>, {s.address}
      {s.maps_url && <> · <ExternalLink href={s.maps_url}>Check location in maps</ExternalLink></>}
      {s.directions_url && <> · <ExternalLink href={s.directions_url}>Directions</ExternalLink></>}</span>
  );
}

/** Fuller location block (detail page, expandable section): addresses, maps links, travel notes, evidence. */
export function LocationDetails({ loc, distance }: { loc: LocationInfo | null | undefined; distance?: DistanceEstimate | null; towns?: string[] }) {
  if (!loc) return null;
  return (
    <div className="location-block stack" style={{ gap: 6 }}>
      <p className="row" style={{ gap: 8, margin: 0, alignItems: "flex-start" }}>
        <IconPin size={17} />
        <span><strong>{loc.headline}</strong></span>
      </p>
      {loc.kind === "verified_site" && loc.site && <p className="small" style={{ margin: 0 }}><Site s={loc.site} label="Volunteering site" /></p>}
      {loc.kind === "organization_location" && loc.organization_site && (
        <p className="small" style={{ margin: 0 }}><Site s={loc.organization_site} label="Organization location (the activity location may differ)" /></p>)}
      {loc.role_town && loc.kind !== "verified_site" && <p className="small" style={{ margin: 0 }}>Published town for this role: {loc.role_town}</p>}
      {loc.kind === "home_based" && loc.related_site && (
        <p className="small" style={{ margin: 0 }}><Site s={loc.related_site} label={`For ${loc.related_site.purpose.toLowerCase()}`} /></p>)}
      {loc.travel_note && <p className="small" style={{ margin: 0 }}>{loc.travel_note}</p>}
      {loc.other_sites.length > 0 && (
        <div className="small">The organization's sites (which one applies isn't stated):
          <ul style={{ margin: "4px 0 0" }}>{loc.other_sites.map((s) => <li key={s.site_id}><Site s={s} label={s.town} /></li>)}</ul></div>)}
      {loc.note && loc.kind !== "verified_site" && <p className="small muted" style={{ margin: 0 }}>{loc.note}</p>}
      {distance && distance.status === "estimated" && distance.label && (
        <p className="small" style={{ margin: 0 }}>Estimated distance: <strong>{distance.label}</strong>{distance.secondary && ` (${distance.secondary})`}</p>)}
      {loc.maps_url || loc.organization_site?.maps_url || loc.related_site?.maps_url || loc.other_sites.some((x) => x.maps_url) ? <p className="hint" style={{ margin: 0 }}>{MAPS_NOTE}</p> : null}
      {loc.evidence.length > 0 && (
        <details className="disclosure">
          <summary>Location evidence ({loc.evidence.length})</summary>
          <div className="disclosure-body">
            {loc.evidence.map((e, i) => (
              <div key={i} style={{ marginTop: 8 }}>
                <blockquote>“{e.quote}”</blockquote>
                <p className="small muted" style={{ margin: 0 }}><ExternalLink href={e.url}>{e.source_id}</ExternalLink> · checked {e.accessed_at.slice(0, 10)}</p>
              </div>))}
          </div>
        </details>
      )}
    </div>
  );
}

const STATUS_TONE: Record<string, string> = { supported: "badge-met", invalid_format: "badge-no", not_in_dataset: "badge-q", outside_coverage: "badge-q" };

/** Optional ZIP field. Stored only in this tab's memory as a confirmed answer; editable and removable. */
/** Optional browsing ZIP (Explore, detail pages). Controlled by the page: `zip` is the applied value. To reset the
 *  typed draft and any validation message, the page remounts it with a new `key`. */
export function ZipField({ idPrefix = "zip", compact = false, zip, onApply, onRemove }: {
  idPrefix?: string; compact?: boolean; zip: string | null; onApply: (z: string) => void; onRemove: () => void;
}) {
  const [draft, setDraft] = useState(zip ?? "");
  const [error, setError] = useState<string | null>(null);
  const [area, setArea] = useState<ZipArea | null>(null);
  useEffect(() => { setDraft(zip ?? ""); }, [zip]);
  useEffect(() => {
    if (!zip) { setArea(null); return; }
    const ctl = new AbortController();
    api.locationEstimates(zip, [], ctl.signal).then((r) => setArea(r.zip_area)).catch(() => undefined);
    return () => ctl.abort();
  }, [zip]);
  const id = `${idPrefix}-zip`;

  function save(e: FormEvent) {
    e.preventDefault();
    const z = draft.trim();
    if (!/^\d{5}$/.test(z)) { setError("A ZIP code is exactly five digits, for example 06511."); return; }
    setError(null);
    onApply(z);
  }
  function remove() { onRemove(); setDraft(""); setError(null); }

  return (
    <form className="field" onSubmit={save} noValidate aria-describedby={`${id}-help`}>
      <label htmlFor={id}>ZIP code {compact ? "(optional)" : <span className="muted small">(optional)</span>}</label>
      <div className="row" style={{ flexWrap: "nowrap" }}>
        <input id={id} type="text" inputMode="numeric" autoComplete="postal-code" maxLength={5} value={draft}
          onChange={(e) => setDraft(e.target.value)} placeholder="e.g. 06511" aria-invalid={!!error} />
        <button className="btn btn-secondary btn-small" type="submit">Use</button>
      </div>
      <span id={`${id}-help`} className="hint">{ZIP_HELP} Used for browsing only; it doesn't change your Find my fit answers.</span>
      {error && <span className="hint" role="alert" style={{ color: "var(--no-ink)" }}>{error}</span>}
      {zip && area && (
        <span className="small" role="status">
          <span className={`badge ${STATUS_TONE[area.status] ?? "badge-q"}`}>{area.status === "supported" ? `ZIP ${zip}: distance estimates on` : `ZIP ${zip}: no estimates`}</span>
          {area.status !== "supported" && <><br />{area.message}</>}
        </span>
      )}
      {zip && <button type="button" className="link-button small" onClick={remove} style={{ alignSelf: "flex-start" }}>Remove ZIP code</button>}
    </form>
  );
}

/** Small helper for components that only need "is a supported ZIP in use?". */
export function useSupportedZip(ids: string[], zip: string | null) {
  const est = useLocationEstimates(ids, zip);
  return useMemo(() => ({ ...est, supported: est.zipArea?.status === "supported" }), [est]);
}
