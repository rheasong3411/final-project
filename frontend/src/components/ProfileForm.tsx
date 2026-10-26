// Optional profile form. Blank means "Not sure": nothing defaults to zero, "no guardian", or eligible.
// It shows the CURRENT effective answers (confirmed ones and those taken from chat, marked "from chat"). Opening it
// confirms nothing. Saving confirms only the fields the person changed; clearing a filled field and saving removes
// that answer. Answers that arrive from a new reply update untouched fields without overwriting unsaved edits.
import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import type { DayPart, MessageFact, VolunteerProfile, Weekday } from "../api/types";
import { activityLabel, animalLabel } from "../lib/labels";
import { effectiveProfile } from "../state/AppState";

const ACTIVITIES = ["dog_walking", "animal_socialization", "animal_care_cleaning", "fostering", "events", "fundraising",
  "administrative", "transport", "education_outreach", "supply_drives", "crafts", "gardening_grounds", "tnr_feral_care",
  "adoption_support", "grant_writing", "communications_marketing", "maintenance_trades", "dog_training", "laundry"];
const ANIMALS = ["dogs", "cats", "small_animals"];
const DAYS: [Weekday, string][] = [["mon", "Mon"], ["tue", "Tue"], ["wed", "Wed"], ["thu", "Thu"], ["fri", "Fri"], ["sat", "Sat"], ["sun", "Sun"]];
const TIMES: [DayPart, string][] = [["morning", "Morning"], ["afternoon", "Afternoon"], ["evening", "Evening"]];

type Draft = Record<string, string | string[] | boolean>;

function toDraft(p: VolunteerProfile): Draft {
  const s = (v: unknown) => (v === null || v === undefined ? "" : String(v));
  return {
    age: s(p.age), town: s(p.town), guardian: p.guardian_available === true ? "yes" : p.guardian_available === false ? "no" : "",
    interests: p.interests ?? [], animals: p.animal_preferences ?? [],
    noContact: p.prefers_no_animal_contact === true ? "yes" : p.prefers_no_animal_contact === false ? "no" : "",
    hours: s(p.available_hours), hoursMax: s(p.available_hours_max), period: s(p.hours_period), months: s(p.commitment_months),
    pref: s(p.commitment_required ?? p.commitment_preference), mustPref: !!p.commitment_required,
    prefOnly: s(p.commitment_preference),  // a stated preference, kept apart from a hard "only" limit
    days: p.available_days ?? [], times: p.available_times ?? [], session: s(p.max_session_hours),
    wider: !!p.include_wider_connecticut,
    zip: s(p.zip_code), car: p.has_car === true ? "yes" : p.has_car === false ? "no" : "",
    area: p.volunteer_only_in ? "only" : p.nearby_towns_ok ? "nearby" : "", onlyIn: s(p.volunteer_only_in || p.town),
    // not shown as form fields, but kept so saving the form doesn't erase them
    nearby: p.wants_nearby === true ? "yes" : p.wants_nearby === false ? "no" : "",
    noZip: p.prefers_not_to_share_zip ? "yes" : "",
  };
}

const num = (v: string) => (v.trim() === "" ? undefined : Number(v));
const tri = (v: string) => (v === "yes" ? true : v === "no" ? false : undefined);

function fromDraft(d: Draft): VolunteerProfile {
  const p: VolunteerProfile = {
    age: num(d.age as string), town: (d.town as string).trim() || undefined, guardian_available: tri(d.guardian as string),
    interests: d.interests as string[], animal_preferences: d.animals as string[],
    prefers_no_animal_contact: tri(d.noContact as string), available_hours: num(d.hours as string),
    available_hours_max: num(d.hours as string) !== undefined ? num(d.hoursMax as string) : undefined,
    hours_period: ((d.period as string) || undefined) as VolunteerProfile["hours_period"],
    commitment_months: num(d.months as string),
    // With "I can only do this kind" ticked, the choice is a hard limit; a preference is kept only if one was stated.
    commitment_preference: ((d.mustPref ? d.prefOnly : d.pref) as string || undefined) as VolunteerProfile["commitment_preference"],
    // A hard constraint only when ticked ("I can only do this kind"); otherwise it's a preference that never filters.
    commitment_required: d.mustPref && (d.pref === "one_time" || d.pref === "recurring")
      ? (d.pref as VolunteerProfile["commitment_required"]) : undefined,
    available_days: d.days as Weekday[], available_times: d.times as DayPart[], max_session_hours: num(d.session as string),
    include_wider_connecticut: d.wider as boolean,
    zip_code: (d.zip as string).trim() || undefined, has_car: tri(d.car as string),
    volunteer_only_in: d.area === "only" ? (d.onlyIn as string).trim() || undefined : undefined,
    nearby_towns_ok: d.area === "nearby" ? true : undefined,
    wants_nearby: tri(d.nearby as string),
    prefers_not_to_share_zip: d.noZip === "yes" && !(d.zip as string).trim() ? true : undefined,
  };
  for (const k of Object.keys(p) as (keyof VolunteerProfile)[]) if (p[k] === undefined) delete p[k];
  return p;
}

/** Which form control holds each profile field (used for "from chat" marks and change tracking). */
const DRAFT_KEYS: Record<string, string[]> = {
  age: ["age"], town: ["town"], guardian_available: ["guardian"], interests: ["interests"], animal_preferences: ["animals"],
  prefers_no_animal_contact: ["noContact"], available_hours: ["hours"], available_hours_max: ["hoursMax"], hours_period: ["period"], commitment_months: ["months"],
  commitment_preference: ["pref"], commitment_required: ["pref", "mustPref"], available_days: ["days"], available_times: ["times"],
  max_session_hours: ["session"], include_wider_connecticut: ["wider"], zip_code: ["zip"], has_car: ["car"],
  volunteer_only_in: ["area", "onlyIn"], nearby_towns_ok: ["area"], wants_nearby: ["nearby"], prefers_not_to_share_zip: ["noZip"],
};
const isEmpty = (v: unknown) => v === undefined || v === null || v === false || v === "" || (Array.isArray(v) && v.length === 0);
const same = (a: unknown, b: unknown) => (isEmpty(a) && isEmpty(b)) || JSON.stringify(a) === JSON.stringify(b);

/** Fields the person changed (new or different values) and fields they emptied (removed), relative to `before`. */
export function diffAnswers(before: VolunteerProfile, after: VolunteerProfile): { changes: Partial<VolunteerProfile>; removed: string[] } {
  const b = before as Record<string, unknown>, a = after as Record<string, unknown>;
  const changes: Record<string, unknown> = {}, removed: string[] = [];
  for (const k of new Set([...Object.keys(b), ...Object.keys(a)])) {
    if (same(b[k], a[k])) continue;
    if (isEmpty(a[k])) { if (!isEmpty(b[k])) removed.push(k); } else changes[k] = a[k];
  }
  return { changes: changes as Partial<VolunteerProfile>, removed };
}

function FromChat({ on }: { on: boolean }) {
  return on ? <span className="pref-tag pref-tag-chat form-source">from chat</span> : null;
}

function Checks({ name, options, value, onChange }: { name: string; options: [string, string][]; value: string[]; onChange: (v: string[]) => void }) {
  return (
    <div className="checks">
      {options.map(([v, label]) => (
        <label key={v} className="check">
          <input type="checkbox" name={name} value={v} checked={value.includes(v)}
            onChange={(e) => onChange(e.target.checked ? [...value, v] : value.filter((x) => x !== v))} />
          <span>{label}</span>
        </label>
      ))}
    </div>
  );
}

export function ProfileForm({ confirmed, messageFacts, onSave, submitLabel = "Save my changes", compact = false, idPrefix = "pf",
  submitUnchanged = false }: {
  confirmed: VolunteerProfile; messageFacts: MessageFact[];
  onSave: (changes: Partial<VolunteerProfile>, removed: string[]) => void;
  submitLabel?: string; compact?: boolean; idPrefix?: string;
  /** Call onSave even when nothing changed (e.g. "Check my fit" re-runs the check with the current answers). */
  submitUnchanged?: boolean;
}) {
  const current = useMemo(() => effectiveProfile(confirmed, messageFacts), [confirmed, messageFacts]);
  const chatFields = useMemo(() => new Set(messageFacts.map((m) => m.field).filter((f) => !(f in confirmed))), [confirmed, messageFacts]);
  const [d, setD] = useState<Draft>(() => toDraft(current));
  const dirty = useRef(new Set<string>());
  const base = useRef(current);   // the answers the draft was built from (the "before" of a save)
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState<string | null>(null);
  const set = (k: string, v: string | string[] | boolean) => { dirty.current.add(k); setSaved(null); setD((x) => ({ ...x, [k]: v })); };
  // New answers (a reply, a confirmation elsewhere) refresh only the fields the person hasn't edited here.
  const key = JSON.stringify(current);
  useEffect(() => {
    const fresh = toDraft(current);
    setD((x) => Object.fromEntries(Object.keys(fresh).map((k) => [k, dirty.current.has(k) ? x[k] : fresh[k]])) as Draft);
    const kept = Object.fromEntries(Object.entries(base.current).filter(([f]) => (DRAFT_KEYS[f] ?? []).some((k) => dirty.current.has(k))));
    base.current = { ...current, ...kept } as VolunteerProfile;
  }, [key]); // eslint-disable-line react-hooks/exhaustive-deps
  const chat = (f: string) => chatFields.has(f) && !(DRAFT_KEYS[f] ?? []).some((k) => dirty.current.has(k));
  const id = (s: string) => `${idPrefix}-${s}`;
  const ageNum = num(d.age as string);
  const showGuardian = ageNum === undefined || ageNum < 18;

  function submit(e: FormEvent) {
    e.preventDefault();
    const p = fromDraft(d);
    for (const [k, v] of Object.entries(p)) {
      if (typeof v === "number" && (Number.isNaN(v) || v < 0)) { setError(`Please enter a valid number for ${k.replace(/_/g, " ")}, or leave it blank.`); return; }
    }
    if (p.age != null && (p.age < 5 || p.age > 110 || !Number.isInteger(p.age))) { setError("Age should be a whole number of years (5–110), or blank."); return; }
    if (p.available_hours !== undefined && !p.hours_period) { setError("Please choose whether your hours are per week or per month."); return; }
    if (p.available_hours_max != null && p.available_hours != null && p.available_hours_max < p.available_hours) { setError("The “up to” hours can't be less than the first number."); return; }
    if (p.available_hours_max !== undefined && p.available_hours_max === p.available_hours) delete p.available_hours_max;
    if (p.zip_code && !/^\d{5}$/.test(p.zip_code)) { setError("A ZIP code is exactly five digits, for example 06511 — or leave it blank."); return; }
    if (d.area === "only" && !p.volunteer_only_in) { setError("Please enter the town you'll volunteer in, or choose another option."); return; }
    setError(null);
    const { changes, removed } = diffAnswers(base.current, p);
    const n = Object.keys(changes).length + removed.length;
    if (!n && !submitUnchanged) { setSaved("Nothing changed, so nothing was saved."); return; }
    dirty.current.clear();
    onSave(changes, removed);
    setSaved(n ? `Saved ${n} ${n === 1 ? "change" : "changes"}. Your other answers are unchanged.` : null);
  }

  return (
    <form onSubmit={submit} className="stack" noValidate aria-describedby={id("intro")}>
      <p id={id("intro")} className="hint" style={{ margin: 0 }}>All questions are optional. Leave anything blank if you're not sure — blank answers are never treated as "no" or "zero". Answers marked “from chat” came from your messages; saving confirms only what you change. To remove an answer, clear it and save. We don't ask for your name, birth date, address or contact details.</p>
      <div className="form-grid">
        <div className="field"><label htmlFor={id("age")}>Age <FromChat on={chat("age")} /></label>
          <input id={id("age")} type="number" inputMode="numeric" min={5} max={110} value={d.age as string} onChange={(e) => set("age", e.target.value)} placeholder="Not sure" /></div>
        <div className="field"><label htmlFor={id("town")}>Town where you live <FromChat on={chat("town")} /></label>
          <input id={id("town")} type="text" value={d.town as string} onChange={(e) => set("town", e.target.value)} placeholder="e.g. Hamden" />
          <span className="hint">Where you live. It doesn't limit where you volunteer.</span></div>
        {!compact && (
          <div className="field"><label htmlFor={id("zip")}>ZIP code <FromChat on={chat("zip_code")} /></label>
            <input id={id("zip")} type="text" inputMode="numeric" autoComplete="postal-code" maxLength={5} value={d.zip as string}
              onChange={(e) => set("zip", e.target.value)} placeholder="Optional, e.g. 06511" />
            <span className="hint">Used to estimate which locations are closer. No street address needed.</span></div>
        )}
        {showGuardian && (
          <div className="field"><label htmlFor={id("guardian")}>Can a parent or guardian come with you? <FromChat on={chat("guardian_available")} /></label>
            <select id={id("guardian")} value={d.guardian as string} onChange={(e) => set("guardian", e.target.value)}>
              <option value="">Not sure / not answered</option><option value="yes">Yes</option><option value="no">No</option>
            </select><span className="hint">Some programs require this for younger volunteers.</span></div>
        )}
      </div>
      {!compact && (
        <>
          <fieldset><legend>What would you like to do? <FromChat on={chat("interests")} /></legend>
            <Checks name="interests" options={ACTIVITIES.map((a) => [a, activityLabel(a)])} value={d.interests as string[]} onChange={(v) => set("interests", v)} /></fieldset>
          <fieldset><legend>Animals you'd like to work with <FromChat on={chat("animal_preferences")} /></legend>
            <Checks name="animals" options={ANIMALS.map((a) => [a, animalLabel(a)])} value={d.animals as string[]} onChange={(v) => set("animals", v)} /></fieldset>
        </>
      )}
      <div className="form-grid">
        <div className="field"><label htmlFor={id("hours")}>Hours you can give <FromChat on={chat("available_hours")} /></label>
          <input id={id("hours")} type="number" min={0} max={168} step="0.5" value={d.hours as string} onChange={(e) => set("hours", e.target.value)} placeholder="Not sure" /></div>
        <div className="field"><label htmlFor={id("hoursMax")}>Up to (optional)</label>
          <input id={id("hoursMax")} type="number" min={0} max={168} step="0.5" value={d.hoursMax as string} onChange={(e) => set("hoursMax", e.target.value)} placeholder="For a range, e.g. 2–3" /></div>
        <div className="field"><label htmlFor={id("period")}>Per <FromChat on={chat("hours_period")} /></label>
          <select id={id("period")} value={d.period as string} onChange={(e) => set("period", e.target.value)}>
            <option value="">Not sure</option><option value="week">Week</option><option value="month">Month</option></select></div>
        <div className="field"><label htmlFor={id("months")}>Months you can commit <FromChat on={chat("commitment_months")} /></label>
          <input id={id("months")} type="number" min={0} max={120} value={d.months as string} onChange={(e) => set("months", e.target.value)} placeholder="Not sure" /></div>
        <div className="field"><label htmlFor={id("session")}>Longest single session (hours) <FromChat on={chat("max_session_hours")} /></label>
          <input id={id("session")} type="number" min={0} max={24} step="0.5" value={d.session as string} onChange={(e) => set("session", e.target.value)} placeholder="Not sure" />
          <span className="hint">For one-time events, e.g. a 3–4 hour project.</span></div>
      </div>
      {!compact && (
        <>
          <div className="form-grid">
            <div className="field"><label htmlFor={id("pref")}>Commitment preference <FromChat on={chat("commitment_preference") || chat("commitment_required")} /></label>
              <select id={id("pref")} value={d.pref as string} onChange={(e) => set("pref", e.target.value)}>
                <option value="">Not sure</option><option value="recurring">Ongoing / recurring</option>
                <option value="one_time">One-time</option><option value="either">Either</option></select>
              {(d.pref === "one_time" || d.pref === "recurring") && (
                <label className="check" style={{ marginTop: 6 }}><input type="checkbox" checked={d.mustPref as boolean} onChange={(e) => set("mustPref", e.target.checked)} />
                  <span>I can only do this kind (other commitments aren't matches)</span></label>)}</div>
            <div className="field"><label htmlFor={id("contact")}>Prefer no direct animal contact?</label>
              <select id={id("contact")} value={d.noContact as string} onChange={(e) => set("noContact", e.target.value)}>
                <option value="">Not sure</option><option value="yes">Yes</option><option value="no">No</option></select></div>
          </div>
          <fieldset><legend>Days you're usually free</legend>
            <Checks name="days" options={DAYS} value={d.days as string[]} onChange={(v) => set("days", v)} /></fieldset>
          <fieldset><legend>Times of day</legend>
            <Checks name="times" options={TIMES} value={d.times as string[]} onChange={(v) => set("times", v)} /></fieldset>
          <div className="form-grid">
            <div className="field"><label htmlFor={id("car")}>Do you have a car? <FromChat on={chat("has_car")} /></label>
              <select id={id("car")} value={d.car as string} onChange={(e) => set("car", e.target.value)}>
                <option value="">Not sure / rather not say</option><option value="yes">Yes</option><option value="no">No</option></select>
              <span className="hint">How you travel. We don't estimate travel times or transit.</span></div>
            <div className="field"><label htmlFor={id("area")}>Where will you volunteer?</label>
              <select id={id("area")} value={d.area as string} onChange={(e) => set("area", e.target.value)}>
                <option value="">Anywhere in the area I'm browsing</option>
                <option value="nearby">My town or nearby towns</option>
                <option value="only">Only in one town</option></select></div>
            {d.area === "only" && (
              <div className="field"><label htmlFor={id("onlyIn")}>Town you'll volunteer in</label>
                <input id={id("onlyIn")} type="text" value={d.onlyIn as string} onChange={(e) => set("onlyIn", e.target.value)} placeholder="e.g. New Haven" />
                <span className="hint">Only roles published in this town are recommended.</span></div>
            )}
          </div>
          <label className="toggle"><input type="checkbox" checked={d.wider as boolean} onChange={(e) => set("wider", e.target.checked)} />
            <span>Include other Connecticut locations<br /><span className="hint">Expand beyond Greater New Haven.</span></span></label>
        </>
      )}
      {error && <p className="notice notice-error" role="alert">{error}</p>}
      {saved && <p className="hint" role="status" style={{ margin: 0 }}>{saved}</p>}
      <div className="row"><button type="submit" className="btn btn-primary">{submitLabel}</button></div>
    </form>
  );
}
