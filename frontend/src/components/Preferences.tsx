// "Your answers": one compact summary. Facts taken from the person's messages (with a verified quote) are
// already used, provisionally, and marked "from chat"; one action confirms them all, and each can be edited.
// Unverified suggestions are listed separately and never confirmed automatically. Answers the person withdrew
// ("I can't commit weekly") are listed as removed, so a cleared field is distinguishable from an unchanged one.
import { useState, type FormEvent } from "react";
import type { MessageFact, ProfileFact, VolunteerProfile } from "../api/types";
import { formatProfileValue, PROFILE_FIELD_LABEL } from "../lib/labels";

const NUMBER = new Set(["age", "available_hours", "commitment_months", "max_session_hours"]);
const BOOL = new Set(["guardian_available", "has_car", "wants_nearby", "nearby_towns_ok", "prefers_no_animal_contact",
  "prefers_not_to_share_zip", "include_wider_connecticut"]);
const ENUM: Record<string, [string, string][]> = {
  hours_period: [["week", "Week"], ["month", "Month"]],
  commitment_preference: [["one_time", "One-time"], ["recurring", "Ongoing"], ["either", "Either"]],
};

type Row = { field: string; value: unknown; source: "confirmed" | "chat"; quote: string | null };

const label = (f: string) => PROFILE_FIELD_LABEL[f as keyof VolunteerProfile] ?? f;
// A stated "no" is an answer worth keeping (e.g. "no car"); only unset/default values are hidden.
const FALSE_IS_DEFAULT = new Set(["include_wider_connecticut", "prefers_not_to_share_zip"]);
const shown = (v: unknown, field?: string) => v !== undefined && v !== null && !(v === false && (!field || FALSE_IS_DEFAULT.has(field)))
  && !(Array.isArray(v) && v.length === 0);

function EditValue({ field, value, onSave, onCancel }: { field: string; value: unknown; onSave: (v: unknown) => void; onCancel: () => void }) {
  const [draft, setDraft] = useState(value === null || value === undefined ? "" : String(value));
  const [error, setError] = useState<string | null>(null);
  const id = `edit-${field}`;
  function save(e: FormEvent) {
    e.preventDefault();
    let v: unknown = draft.trim();
    if (NUMBER.has(field)) {
      const n = Number(draft);
      if (draft.trim() === "" || Number.isNaN(n) || n < 0) { setError("Enter a number."); return; }
      if (field === "age" && (!Number.isInteger(n) || n < 5 || n > 110)) { setError("Age in whole years (5–110)."); return; }
      v = n;
    } else if (BOOL.has(field)) v = draft === "true";
    else if (field === "zip_code" && !/^\d{5}$/.test(draft.trim())) { setError("Five digits, for example 06511."); return; }
    else if (v === "") { setError("Enter a value, or use Remove."); return; }
    onSave(v);
  }
  return (
    <form className="row pref-edit" onSubmit={save} noValidate style={{ gap: 6 }}>
      <label htmlFor={id} className="visually-hidden">{label(field)}</label>
      {BOOL.has(field) ? (
        <select id={id} value={draft} onChange={(e) => setDraft(e.target.value)}><option value="true">Yes</option><option value="false">No</option></select>
      ) : ENUM[field] ? (
        <select id={id} value={draft} onChange={(e) => setDraft(e.target.value)}>{ENUM[field].map(([v, t]) => <option key={v} value={v}>{t}</option>)}</select>
      ) : (
        <input id={id} value={draft} onChange={(e) => setDraft(e.target.value)} inputMode={NUMBER.has(field) || field === "zip_code" ? "numeric" : undefined}
          maxLength={field === "zip_code" ? 5 : 60} style={{ maxWidth: 160 }} aria-invalid={!!error} />
      )}
      <button className="btn btn-primary btn-small" type="submit">Save</button>
      <button className="btn btn-ghost btn-small" type="button" onClick={onCancel}>Cancel</button>
      {error && <span className="hint" role="alert" style={{ color: "var(--no-ink)", width: "100%" }}>{error}</span>}
    </form>
  );
}

export function Preferences({ confirmed, messageFacts, facts, onConfirm, onConfirmAll, onDismiss, onRemove, onEditInForm }: {
  confirmed: VolunteerProfile;
  messageFacts: MessageFact[];
  facts: ProfileFact[];
  onConfirm: (field: string, value: unknown) => void;
  onConfirmAll: (items: { field: string; value: unknown }[]) => void;
  onDismiss: (field: string) => void;
  onRemove: (field: string) => void;
  onEditInForm?: () => void;
}) {
  const [editing, setEditing] = useState<string | null>(null);
  const conf = confirmed as Record<string, unknown>;
  const rows: Row[] = Object.entries(conf).filter(([f, v]) => shown(v, f)).map(([field, value]) => ({ field, value, source: "confirmed", quote: null }));
  const chat = new Map<string, Row>();
  for (const f of facts) if (f.status === "from_message" && !(f.field in conf)) chat.set(f.field, { field: f.field, value: f.value, source: "chat", quote: f.supporting_text });
  for (const m of messageFacts) if (!(m.field in conf) && !chat.has(m.field)) chat.set(m.field, { field: m.field, value: m.value, source: "chat", quote: m.supporting_text });
  const chatRows = [...chat.values()].filter((r) => shown(r.value, r.field));
  const all = [...chatRows, ...rows];
  // Hours and their period read as one answer ("3 per week"); edited in the form, removed together.
  const period = all.find((r) => r.field === "hours_period")?.value;
  const upTo = all.find((r) => r.field === "available_hours_max")?.value;
  const hasHours = all.some((r) => r.field === "available_hours");
  const display = all.filter((r) => !((r.field === "hours_period" || r.field === "available_hours_max") && hasHours));
  const rowLabel = (f: string) => (f === "available_hours" ? "Hours you can give" : label(f));
  const rowValue = (r: Row) => r.field !== "available_hours" ? formatProfileValue(r.field, r.value)
    : `${formatProfileValue(r.field, r.value)}${upTo != null ? `–${upTo}` : ""}${period ? ` per ${period}` : " (week, month or visit not said yet)"}`;
  const suggestions = facts.filter((f) => (f.status === "suggested" && !(f.field in conf) && !chat.has(f.field)) || f.status === "conflicts_with_confirmed");
  const shownFields = new Set(all.map((r) => r.field));
  // Hours and their period are cleared together; list them once ("Hours you can give").
  const cleared = facts.filter((f) => f.status === "cleared" && !shownFields.has(f.field)
    && !(f.field === "hours_period" && facts.some((g) => g.status === "cleared" && g.field === "available_hours")));
  const clearedQuotes = [...new Set(cleared.map((f) => f.supporting_text).filter((q): q is string => !!q))]
    .filter((q, _, all) => !all.some((o) => o !== q && o.includes(q)));  // drop a quote contained in a longer one

  if (!all.length && !suggestions.length && !cleared.length) {
    return <p className="muted small">Nothing yet. Tell the assistant about yourself, or fill in the form below — every answer is optional.</p>;
  }
  return (
    <div className="stack" style={{ gap: 12 }}>
      {all.length > 0 && (
        <>
          <dl className="pref-summary">
            {display.map((r) => (
              <div key={`${r.source}-${r.field}`} className="pref-row">
                <dt>{rowLabel(r.field)}</dt>
                <dd>
                  {editing === r.field ? (
                    <EditValue field={r.field} value={r.value} onCancel={() => setEditing(null)}
                      onSave={(v) => { onConfirm(r.field, v); setEditing(null); }} />
                  ) : (
                    <>
                      <span className="pref-value">{rowValue(r)}</span>{" "}
                      <span className={`pref-tag ${r.source === "chat" ? "pref-tag-chat" : "pref-tag-confirmed"}`}>{r.source === "chat" ? "from chat" : "confirmed"}</span>
                      <span className="pref-actions">
                        <button className="link-button small" onClick={() => (Array.isArray(r.value) || r.field === "available_hours" ? onEditInForm?.() : setEditing(r.field))}>
                          Edit<span className="visually-hidden"> {rowLabel(r.field)}</span></button>
                        <button className="link-button small" onClick={() => { onRemove(r.field); if (r.field === "available_hours") { if (period) onRemove("hours_period"); if (upTo != null) onRemove("available_hours_max"); } }}>
                          Remove<span className="visually-hidden"> {rowLabel(r.field)}</span></button>
                      </span>
                    </>
                  )}
                </dd>
              </div>
            ))}
          </dl>
          {chatRows.length > 0 && (
            <div className="stack" style={{ gap: 6 }}>
              <button className="btn btn-primary btn-small" style={{ alignSelf: "flex-start" }}
                onClick={() => onConfirmAll(chatRows.map((r) => ({ field: r.field, value: r.value })))}>
                Confirm these details ({chatRows.length})
              </button>
              <p className="hint" style={{ margin: 0 }}>Confirms only the answers marked “from chat”. Use Edit first if anything is wrong.</p>
            </div>
          )}
          {chatRows.some((r) => r.quote) && (
            <details className="disclosure">
              <summary>Where the chat answers came from</summary>
              <div className="disclosure-body">
                <ul className="small" style={{ margin: 0 }}>
                  {chatRows.filter((r) => r.quote).map((r) => <li key={r.field}><strong>{label(r.field)}:</strong> you wrote “{r.quote}”</li>)}
                </ul>
              </div>
            </details>
          )}
        </>
      )}
      {cleared.length > 0 && (
        <div className="pref-cleared" role="status">
          <p className="small" style={{ margin: 0 }}><strong>Removed at your request:</strong> {cleared.map((f) => f.field === "available_hours" ? "Hours you can give" : label(f.field)).join(", ")}.
            {" "}These are now unknown, not replaced with a guess.</p>
          {clearedQuotes.map((q) => (
            <p key={q} className="small muted" style={{ margin: "2px 0 0" }}>You wrote “{q}”</p>))}
        </div>
      )}
      {suggestions.length > 0 && (
        <div className="pref-suggestions stack" style={{ gap: 8 }}>
          <h3 style={{ fontSize: "1rem", margin: 0 }}>Suggestions, not used</h3>
          <p className="hint" style={{ margin: 0 }}>The assistant couldn't match these to your own words (or they differ from a confirmed answer), so they aren't used until you choose them.</p>
          <ul className="pref-list">
            {suggestions.map((f) => (
              <li key={`s-${f.field}-${f.status}`} className="pref-item">
                <strong>{label(f.field)}: {formatProfileValue(f.field, f.value)}</strong>
                {f.status === "conflicts_with_confirmed" && <span className="small muted"> (differs from your confirmed answer)</span>}
                <div className="row" style={{ gap: 8, marginTop: 6 }}>
                  <button className="btn btn-secondary btn-small" onClick={() => onConfirm(f.field, f.value)}>Use this<span className="visually-hidden"> {label(f.field)}</span></button>
                  <button className="btn btn-ghost btn-small" onClick={() => onDismiss(f.field)}>Dismiss<span className="visually-hidden"> {label(f.field)}</span></button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
