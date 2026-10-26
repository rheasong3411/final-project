import { useEffect, useMemo, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../api/client";
import type { Assessment, AssistantResponse, ChatTurn, ChecklistStep, DistanceEstimate, LocationContext, Recommendation, SourceRef } from "../api/types";
import { AssessmentView, ChecklistView } from "../components/AssessmentView";
import { ExternalLink, Notice, SafeText } from "../components/Common";
import { HeroIllustration } from "../components/Illustrations";
import { FactLines, NextActions } from "../components/FactLines";
import { ACCEPTING_NOTE, DISTANCE_NOTE, LocationDetails, sortByDistance, useLocationEstimates, useSessionZip } from "../components/Location";
import { Preferences } from "../components/Preferences";
import { ProfileForm } from "../components/ProfileForm";
import { formatDate, hostOf, RECORD_TYPE_UI } from "../lib/labels";
import { effectiveProfile, useAppState, type Turn } from "../state/AppState";

const ERROR_TEXT: Record<string, { title: string; body: string }> = {
  credentials_missing: { title: "The assistant isn't set up on this server.", body: "Its API key hasn't been configured. Browsing, details and “Check my fit” on each opportunity still work." },
  credentials_rejected: { title: "The assistant's AI service rejected the server's credentials.", body: "Please try again later. Browsing and fit checks still work." },
  model_unavailable: { title: "The AI service is unavailable right now.", body: "Please try again in a moment." },
  model_http_error: { title: "The AI service returned an error.", body: "Please try again in a moment." },
  rate_limited: { title: "Too many requests in a short time.", body: "Please wait about a minute, then send your message again." },
  timeout: { title: "The assistant took too long to answer.", body: "Please try again, perhaps with a shorter question." },
  client_timeout: { title: "The assistant took too long to answer.", body: "Please try again, perhaps with a shorter question." },
  content_filtered: { title: "The AI provider's safety filter blocked this message.", body: "Please rephrase your question about volunteering." },
  usage_limit_exceeded: { title: "This request hit a safety limit.", body: "Please ask a narrower question." },
  invalid_model_output: { title: "The assistant's answer didn't pass our checks, so it wasn't shown.", body: "No recommendations were made up in its place. Please try again or rephrase." },
  backend_unavailable: { title: "The app's server couldn't be reached.", body: "Check that the backend is running, then try again." },
  invalid_input: { title: "That message couldn't be sent.", body: "Messages can be up to 2,000 characters." },
  internal_error: { title: "Something went wrong on the server.", body: "Please try again." },
  server_error: { title: "Something went wrong on the server.", body: "Please try again." },
};

const EXAMPLES = [
  "I'm 24, live in Hamden, and can give about 3 hours a week. I'd love to help with cats.",
  "I'm 15 and want to help dogs. My dad can come with me on weekends.",
  "I can only do a one-time project of a few hours with my coworkers.",
];

function RecCard({ rec, assessment, sources, kind, distance, showDistance, limit, checklist }: {
  rec: Recommendation; assessment: Assessment; sources: Record<string, SourceRef>; kind: "rec" | "alt" | "non" | "out" | "ask";
  distance: DistanceEstimate | null | undefined; showDistance: boolean; limit: string | null; checklist?: ChecklistStep[];
}) {
  const loc = rec.location;
  return (
    <article className="card stack option-card" aria-labelledby={`rc-${kind}-${rec.opportunity_id}`}>
      <div>
        {RECORD_TYPE_UI[rec.record_type] && <p className="chip chip-peach" style={{ marginBottom: 8 }} title={RECORD_TYPE_UI[rec.record_type].explain}>{RECORD_TYPE_UI[rec.record_type].chip}</p>}
        <h3 id={`rc-${kind}-${rec.opportunity_id}`} style={{ marginBottom: 2 }}><Link to={`/opportunities/${rec.opportunity_id}`}>{rec.title}</Link></h3>
        <p className="small muted" style={{ margin: 0 }}>{rec.organization_name}</p>
      </div>
      {rec.why_relevant && <p style={{ margin: 0 }} className={kind === "ask" ? "relaxed-note" : undefined}>{kind === "non" ? "Why it doesn't fit right now: " : ""}{rec.why_relevant}</p>}
      {limit && loc && loc.in_chosen_area !== null && (
        <p style={{ margin: 0 }}><span className={`badge ${loc.in_chosen_area ? "badge-met" : "badge-q"}`}>{loc.in_chosen_area ? `In ${limit}` : loc.towns.length && !loc.towns.includes(limit) ? `Outside ${limit}` : `Not confirmed in ${limit}`}</span></p>
      )}
      <FactLines rec={rec} assessment={assessment} distance={distance} showDistanceRow={showDistance} />
      <NextActions actions={rec.next_actions} />
      {loc && (loc.evidence.length > 0 || loc.kind !== "unknown") && (
        <details className="disclosure">
          <summary>Location details{loc.evidence.length ? " and evidence" : ""}</summary>
          <div className="disclosure-body"><LocationDetails loc={loc} /></div>
        </details>
      )}
      <details className="disclosure">
        <summary>Requirement details and evidence</summary>
        <div className="disclosure-body"><AssessmentView a={assessment} sources={sources} /></div>
      </details>
      {checklist && checklist.length > 0 && (
        <details className="disclosure"><summary>Preparing to apply</summary>
          <div className="disclosure-body"><ChecklistView steps={checklist} sources={sources} /></div></details>
      )}
    </article>
  );
}

function RunDetails({ r }: { r: AssistantResponse }) {
  return (
    <details className="disclosure" style={{ marginTop: 12 }}>
      <summary>Run details</summary>
      <div className="disclosure-body small">
        <p style={{ margin: "6px 0" }}>Run ID: <code>{r.run_id}</code><br />Requested model: {r.requested_model}<br />
          Returned model: {r.returned_models.length ? r.returned_models.join(", ") : "not reported"}</p>
        {r.usage && (
          <p style={{ margin: 0 }}>API-reported usage: {r.usage.requests} model requests · {r.usage.input_tokens ?? "n/a"} input tokens
            ({r.usage.cached_input_tokens ?? "n/a"} cached reads{r.usage.cache_write_input_tokens != null ? `, ${r.usage.cache_write_input_tokens} cache writes` : ""}) · {r.usage.output_tokens ?? "n/a"} output tokens. Cost is not calculated here.</p>
        )}
      </div>
    </details>
  );
}

function contextLine(c: LocationContext | Record<string, never>): string | null {
  if (!c || !("zip_area" in c)) return null;
  const parts: string[] = [];
  if (c.lives_in_town) parts.push(`lives in ${c.lives_in_town}`);
  if (c.zip_area.status === "supported") parts.push("ZIP area used for distance estimates");
  else if (c.zip_area.status === "declined") parts.push("no ZIP (your choice)");
  else if (c.zip_area.status !== "not_provided") parts.push("ZIP not usable for estimates");
  if (c.has_car === false) parts.push("no car");
  if (c.has_car === true) parts.push("has a car");
  if (c.wants_nearby) parts.push("wants something close");
  if (c.volunteer_only_in) parts.push(`volunteering only in ${c.volunteer_only_in}`);
  else if (c.nearby_towns_ok) parts.push("nearby towns are OK");
  return parts.length ? parts.join(" · ") : null;
}

function AssistantTurn({ turn, latest }: { turn: Extract<Turn, { role: "assistant" }>; latest: boolean }) {
  const r = turn.response;
  const sources = useMemo(() => Object.fromEntries(r.sources.map((s) => [s.source_id, s])) as Record<string, SourceRef>, [r]);
  const cur = (rec: Recommendation) => (latest && turn.refreshed?.[rec.opportunity_id]) || rec.assessment;
  const all = [...r.recommendations, ...r.alternatives, ...r.explained_non_matches, ...(r.outside_area_suggestions ?? []),
    ...(r.ask_about ?? [])];
  // Latest reply: distances follow the ZIP currently in this session (re-estimated when it changes).
  const profileZip = useSessionZip();   // Find my fit uses its own answers' ZIP, never the Explore browsing ZIP
  const est = useLocationEstimates(useMemo(() => (latest ? all.map((x) => x.opportunity_id) : []), [latest, r]), profileZip); // eslint-disable-line react-hooks/exhaustive-deps
  const supported = est.zipArea?.status === "supported";
  const [closest, setClosest] = useState(false);
  const dist = (rec: Recommendation): DistanceEstimate | null | undefined =>
    latest ? (supported ? est.estimates[rec.opportunity_id]?.distance : null) : rec.location?.distance;
  const sorting = latest && closest && supported;
  const limit = "volunteer_only_in" in r.location_context ? r.location_context.volunteer_only_in : null;
  const ctx = contextLine(r.location_context);
  const checklists = Object.fromEntries(r.application_checklists.map((c) => [c.opportunity_id, c.steps]));
  const showDistance = latest ? supported : all.some((x) => x.location?.distance);
  const section = (title: string, list: Recommendation[], kind: "rec" | "alt" | "non" | "out" | "ask", intro?: string) => list.length > 0 && (
    <>
      <h3>{title}</h3>
      {intro && <p className="small muted" style={{ marginTop: -8 }}>{intro}</p>}
      <div className="grid">{(sorting ? sortByDistance(list, (x) => x.opportunity_id, est.estimates) : list).map((x) =>
        <RecCard key={x.opportunity_id} rec={x} assessment={cur(x)} sources={sources} kind={kind} distance={dist(x)}
          showDistance={showDistance} limit={limit} checklist={kind === "non" ? undefined : checklists[x.opportunity_id]} />)}</div>
    </>
  );
  return (
    <div className="bubble bubble-assistant stack" aria-label={latest ? "Latest assistant reply" : "Earlier assistant reply"}>
      {!latest && <p className="small muted" style={{ margin: 0 }}>Earlier reply — its results may not reflect your latest preferences.</p>}
      <SafeText text={r.answer} />
      {ctx && <p className="small muted" style={{ marginBottom: 0 }}><strong>Location details used:</strong> {ctx}</p>}
      {latest && turn.refreshedAt && (
        <Notice tone="info">Requirement results below were re-checked with your updated preferences at {turn.refreshedAt}. The written reply above was based on your earlier answers — send a message for an updated reply.</Notice>
      )}
      {latest && supported && all.length > 1 && (
        <div className="row" role="group" aria-label="Sort these results" style={{ gap: 8 }}>
          <span className="small">Sort:</span>
          <button className={`btn btn-small ${closest ? "btn-ghost" : "btn-secondary"}`} aria-pressed={!closest} onClick={() => setClosest(false)}>Assistant's order</button>
          <button className={`btn btn-small ${closest ? "btn-secondary" : "btn-ghost"}`} aria-pressed={closest} onClick={() => setClosest(true)}>Distance: nearest first</button>
        </div>
      )}
      {latest && supported && <p className="small muted" style={{ marginBottom: 0 }}>{DISTANCE_NOTE} Closeness doesn't change fit or application status.</p>}
      {all.some((x) => cur(x).application_status.status === "explicitly_accepting_applications") && <p className="small muted" style={{ marginBottom: 0 }}>{ACCEPTING_NOTE}</p>}
      {section("Options to consider", r.recommendations, "rec")}
      {section("Other ways to help", r.alternatives, "alt")}
      {section(limit ? `Outside ${limit} or not confirmed there — only if you choose to widen the area` : "Outside your chosen area", r.outside_area_suggestions ?? [], "out",
        limit ? `You said you need to stay in ${limit}. These are elsewhere, or their own location isn't published as ${limit}. They're shown only so you can decide whether to widen the area.` : undefined)}
      {section("Other activities to ask about", r.ask_about ?? [], "ask",
        "Optional. These don't confirm what you said you need; each card names what still needs confirming.")}
      {section("Roles that don't fit right now", r.explained_non_matches, "non")}
      {r.follow_up_questions.length > 0 && (
        <div className="card card-peach"><h3 style={{ fontSize: "1.05rem" }}>The assistant would like to know</h3>
          <ul style={{ marginBottom: 0 }}>{r.follow_up_questions.map((q, i) => <li key={i}>{q}</li>)}</ul></div>
      )}
      {r.sources.length > 0 && (
        <details className="disclosure"><summary>Sources ({r.sources.length})</summary>
          <div className="disclosure-body"><p className="small muted">Checked dates show when we viewed each page, not when an organization confirmed anything.</p>
            <ul>{r.sources.map((s) => <li key={s.source_id}><ExternalLink href={s.url}>{s.page_title}</ExternalLink> <span className="small muted">({hostOf(s.url)}, checked {formatDate(s.accessed_at)})</span></li>)}</ul></div></details>
      )}
      <p className="small muted" style={{ margin: 0 }}>{r.disclaimer}</p>
      <RunDetails r={r} />
    </div>
  );
}

export function FindMyFit() {
  const s = useAppState();
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState<string | null>(null); // message being answered right now
  const [error, setError] = useState<{ title: string; body: string } | null>(null);
  const [showLast, setShowLast] = useState(false); // after a failure: reopen the last successful results
  const [sendFailed, setSendFailed] = useState(false);
  const [confirmReset, setConfirmReset] = useState(false);
  const currentRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLDetailsElement>(null);
  const lastVersion = useRef(s.profileVersion);
  const sending = pending !== null;

  const latestIdx = s.turns.map((t) => t.role).lastIndexOf("assistant");

  // When the person changes preferences, re-check the latest results deterministically (no AI call).
  useEffect(() => {
    if (s.profileVersion === lastVersion.current) return;
    lastVersion.current = s.profileVersion;
    const t = s.turns[latestIdx];
    if (!t || t.role !== "assistant" || !t.response.ok) return;
    const r = t.response;
    const ids = [...r.recommendations, ...r.alternatives, ...r.explained_non_matches, ...(r.outside_area_suggestions ?? [])].map((x) => x.opportunity_id);
    if (!ids.length) return;
    const profile = effectiveProfile(s.confirmed, s.messageFacts);
    Promise.all(ids.map((id) => api.assess(id, profile))).then((results) => {
      const refreshed = Object.fromEntries(results.map((a) => [a.opportunity_id, a]));
      const at = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
      s.setTurns((turns) => turns.map((x, i) => (i === latestIdx && x.role === "assistant" ? { ...x, refreshed, refreshedAt: at } : x)));
    }).catch(() => setError({ title: "Your results couldn't be re-checked.", body: "They may not reflect your latest preferences. Try sending a message." }));
  }, [s.profileVersion]); // eslint-disable-line react-hooks/exhaustive-deps

  // Bring the new answer (or the "updating" notice) to the top of the screen, below the sticky header.
  useEffect(() => {
    if (s.turns.length || sending) currentRef.current?.scrollIntoView({ block: "start", behavior: "smooth" });
  }, [s.turns.length, sending]);

  async function send(e?: FormEvent) {
    e?.preventDefault();
    const message = draft.trim();
    if (!message || sending) return;
    setPending(message); setError(null); setShowLast(false); setSendFailed(false);
    // The model sees the last 10 turns. Older messages are sent only so remembered facts can be re-verified
    // against the person's own words; collapsing the display never removes anything from this memory.
    const history: ChatTurn[] = s.turns.slice(-10).map((t) => ({ role: t.role, content: t.content.slice(0, 2000) }));
    const earlier = s.turns.slice(0, -10).filter((t) => t.role === "user").map((t) => t.content.slice(0, 2000)).slice(-40);
    try {
      const r = await api.assistant({ message, profile: s.confirmed, message_facts: s.messageFacts, history,
                                      declined_fields: s.declined, earlier_user_messages: earlier,
                                      withdrawn_fields: s.withdrawn, asked_follow_ups: s.asked });
      if (!r.ok) {
        setError(ERROR_TEXT[r.error ?? ""] ?? { title: "The assistant couldn't answer.", body: r.answer });
        setSendFailed(true);
        return; // keep the draft; no fake recommendations
      }
      // The server's profile is the current one: withdrawn facts are gone (and stay gone), corrected confirmed
      // answers are dropped from the confirmed set, and the replacement (if any) arrives as a chat fact.
      s.dropConfirmed(r.confirmed_overrides ?? []);
      s.setWithdrawn(r.withdrawn_fields ?? s.withdrawn);
      s.addAsked(r.follow_up_questions);
      s.setMessageFacts(r.profile_facts.filter((f) => f.status === "from_message" && f.supporting_text)
        .map((f) => ({ field: f.field, value: f.value, supporting_text: f.supporting_text! })));
      s.setFacts(r.profile_facts);
      s.setTurns((t) => [...t, { role: "user", content: message }, { role: "assistant", content: r.answer, response: r }]);
      setDraft("");
    } catch (err) {
      const code = err instanceof ApiError ? err.code : "backend_unavailable";
      setError(ERROR_TEXT[code] ?? { title: "Something went wrong.", body: (err as Error).message });
      setSendFailed(true);
    } finally {
      setPending(null);
    }
  }

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };

  // Confirm, edit and remove all go through saveAnswers, so they behave the same way everywhere.
  const confirmFact = (field: string, value: unknown) => s.saveAnswers({ [field]: value }, []);
  const confirmAll = (items: { field: string; value: unknown }[]) =>
    s.saveAnswers(Object.fromEntries(items.map((i) => [i.field, i.value])), []);
  /** "Dismiss" an unverified suggestion: never applied from chat again. */
  function dismissFact(field: string) {
    s.setDeclined([...new Set([...s.declined, field])]);
    s.setFacts(s.facts.filter((f) => !(f.field === field && (f.status === "suggested" || f.status === "conflicts_with_confirmed"))));
  }
  /** "Remove" an answer (from chat or confirmed): it becomes unknown and older messages can't restore it. */
  const removeField = (field: string) => s.saveAnswers({}, [field]);

  // Only the latest exchange is shown by default; everything earlier is collapsed (never deleted).
  // After a failed send, the last successful exchange is collapsed too until the person reopens it.
  const failedSend = sendFailed && !sending;
  const hideLatest = sending || (failedSend && !showLast);
  const splitAt = latestIdx >= 0 ? Math.max(0, latestIdx - 1) : s.turns.length;
  const previous = hideLatest ? s.turns : s.turns.slice(0, splitAt);
  const current = hideLatest ? [] : s.turns.slice(splitAt);

  return (
    <div className="container section-tight">
      <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-end" }}>
        <div style={{ maxWidth: 720 }}>
          <p className="eyebrow">Find my fit</p>
          <h1 style={{ fontSize: "clamp(1.9rem, 4vw, 2.7rem)" }}>Tell us a little, and we'll check the requirements with you</h1>
          <p className="muted">The assistant searches this guide's Greater New Haven listings and runs fixed-rule requirement checks. It can't see live openings, and it never applies on your behalf.</p>
        </div>
        <div className="row">
          {!confirmReset
            ? <button className="btn btn-secondary btn-small" onClick={() => setConfirmReset(true)}>Clear my session</button>
            : <span className="row" role="group" aria-label="Confirm clearing">
                <span className="small">Clear your answers and conversation?</span>
                <button className="btn btn-primary btn-small" onClick={() => { s.resetSession(); setDraft(""); setError(null); setShowLast(false); setSendFailed(false); setConfirmReset(false); }}>Yes, clear</button>
                <button className="btn btn-ghost btn-small" onClick={() => setConfirmReset(false)}>Cancel</button>
              </span>}
        </div>
      </div>

      <div className="split" style={{ marginTop: 24 }}>
        <section aria-label="Conversation" className="stack">
          {s.turns.length === 0 && !sending && (
            <div className="card card-quiet stack" style={{ alignItems: "center", textAlign: "center" }}>
              <HeroIllustration className="" />
              <p style={{ maxWidth: 520 }}>Say what you'd like to do, roughly how much time you have, and anything else that matters to you. You can also fill in the optional form instead.</p>
              <div className="stack" style={{ width: "100%", maxWidth: 560 }}>
                {EXAMPLES.map((ex) => <button key={ex} className="btn btn-secondary btn-small" style={{ whiteSpace: "normal", textAlign: "left" }} onClick={() => setDraft(ex)}>{ex}</button>)}
              </div>
            </div>
          )}
          {previous.length > 0 && (
            <details className="disclosure previous-conversation">
              <summary>Previous conversation ({previous.filter((t) => t.role === "user").length} earlier {previous.filter((t) => t.role === "user").length === 1 ? "message" : "messages"})</summary>
              <div className="disclosure-body chat">
                <p className="small muted" style={{ margin: 0 }}>Still part of this session: the assistant keeps using what you said here. Use “Clear my session” to delete it.</p>
                {previous.map((t, i) => t.role === "user"
                  ? <div key={i} className="bubble bubble-user"><span className="visually-hidden">You said: </span>{t.content}</div>
                  : <AssistantTurn key={i} turn={t} latest={false} />)}
              </div>
            </details>
          )}
          <div ref={currentRef} className="current-turn chat" aria-live="polite">
            {sending && (
              <>
                <div className="bubble bubble-user"><span className="visually-hidden">You said: </span>{pending}</div>
                <div className="card updating" role="status">
                  <p className="loading" style={{ margin: 0 }}><span className="spinner" aria-hidden />Updating your results… this can take up to a minute.</p>
                  {latestIdx >= 0 && <p className="small muted" style={{ margin: "8px 0 0" }}>Your earlier results are under “Previous conversation” and may not reflect this message.</p>}
                </div>
              </>
            )}
            {failedSend && error && (
              <div className="stack">
                <Notice tone="error" title={error.title}><p>{error.body} Your message is still in the box below.</p></Notice>
                {latestIdx >= 0 && !showLast && (
                  <button className="btn btn-secondary btn-small" style={{ alignSelf: "flex-start" }} onClick={() => setShowLast(true)}>Show my last results (based on earlier answers)</button>
                )}
              </div>
            )}
            {!sending && current.length > 0 && (
              <>
                {failedSend && <Notice tone="warn" title="Based on your earlier answers">Your latest message hasn't been answered yet, so these results don't reflect it.</Notice>}
                {current.map((t, i) => t.role === "user"
                  ? <div key={i} className="bubble bubble-user"><span className="visually-hidden">You said: </span>{t.content}</div>
                  : <AssistantTurn key={i} turn={t} latest />)}
              </>
            )}
          </div>
          <form className="composer stack" onSubmit={send} aria-label="Send a message">
            {error && !failedSend && <Notice tone="error" title={error.title}><p>{error.body}</p></Notice>}
            <label htmlFor="msg" className="visually-hidden">Your message</label>
            <textarea id="msg" value={draft} onChange={(e) => setDraft(e.target.value)} onKeyDown={onKey} maxLength={2000}
              placeholder="e.g. I'm 19, live in West Haven, and want to help with cats on weekends." disabled={sending} />
            <div className="row" style={{ justifyContent: "space-between" }}>
              <span className="hint">Press Enter to send, Shift+Enter for a new line. Please don't include names, addresses or contact details.</span>
              <button className="btn btn-primary" type="submit" disabled={sending || !draft.trim()}>{sending ? "Sending…" : "Send"}</button>
            </div>
          </form>
        </section>

        <aside aria-labelledby="prefs-h" className="stack">
          <div className="card stack">
            <h2 id="prefs-h" style={{ fontSize: "1.3rem" }}>Your answers</h2>
            <p className="small muted" style={{ margin: 0 }}>Answers marked “from chat” were taken from your own words and are already used, provisionally, in the checks. Confirming them lets you correct anything first. Suggestions the assistant couldn't match to your words are kept apart and not used.</p>
            <Preferences confirmed={s.confirmed} messageFacts={s.messageFacts} facts={s.facts}
              onConfirm={confirmFact} onConfirmAll={confirmAll} onDismiss={dismissFact} onRemove={removeField}
              onEditInForm={() => { if (formRef.current) { formRef.current.open = true; formRef.current.scrollIntoView({ block: "start", behavior: "smooth" }); } }} />
          </div>
          <details ref={formRef} className="disclosure" style={{ background: "var(--surface)", scrollMarginTop: 92 }}>
            <summary>Add or edit your answers (optional)</summary>
            <div className="disclosure-body">
              <ProfileForm confirmed={s.confirmed} messageFacts={s.messageFacts} onSave={s.saveAnswers} submitLabel="Save my changes" idPrefix="mf" />
            </div>
          </details>
        </aside>
      </div>
    </div>
  );
}
