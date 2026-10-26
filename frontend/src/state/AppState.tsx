// In-memory app state only (no localStorage/sessionStorage/cookies). Reloading the page or using
// "Clear my session" erases the profile, conversation and comparison selection.
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import type { Assessment, AssistantResponse, MessageFact, ProfileFact, VolunteerProfile } from "../api/types";

export const MAX_COMPARE = 3;

export type Turn =
  | { role: "user"; content: string }
  | { role: "assistant"; content: string; response: AssistantResponse; refreshed?: Record<string, Assessment>; refreshedAt?: string };

interface AppState {
  compareIds: string[];
  toggleCompare: (id: string) => void;
  removeCompare: (id: string) => void;
  clearCompare: () => void;

  /** Answers the person explicitly confirmed in a form: the trusted path. */
  confirmed: VolunteerProfile;
  setConfirmed: (p: VolunteerProfile) => void;
  /** Facts taken from the person's own chat text (re-verified by the server every turn). */
  messageFacts: MessageFact[];
  setMessageFacts: (f: MessageFact[]) => void;
  /** Latest fact list from the server (confirmed / from_message / suggested / conflicts). */
  facts: ProfileFact[];
  setFacts: (f: ProfileFact[]) => void;
  /** Bumped only when the PERSON changes preferences (form, confirm, remove), so results can be refreshed. */
  profileVersion: number;
  bumpPreferences: () => void;
  declined: string[];
  setDeclined: (d: string[]) => void;
  /** Fields the person withdrew or removed. Sent with every message so older messages can't restore them; a value
   *  the person states later (or saves in the form) replaces the withdrawal. */
  withdrawn: string[];
  setWithdrawn: (w: string[]) => void;
  /** Questions already shown this session, so optional questions (ZIP, area) aren't repeated every turn. */
  asked: string[];
  addAsked: (q: string[]) => void;
  /** The one way the person's own edits are saved (form, confirm, remove): only the fields they changed become
   *  confirmed; unrelated answers (confirmed or from chat) are kept; removed fields become unknown. */
  saveAnswers: (changes: Partial<VolunteerProfile>, removed: string[]) => void;
  /** Applies the server's report that the person corrected or withdrew confirmed answers in chat (no re-check
   *  notice: the new reply already reflects it). */
  dropConfirmed: (fields: string[]) => void;

  turns: Turn[];
  setTurns: (fn: (t: Turn[]) => Turn[]) => void;
  resetSession: () => void;

  /** ZIP used only for browsing (Explore and detail pages). Separate from Find my fit's answers, so clearing
   *  Explore never erases a confirmed answer or the conversation. */
  browseZip: string | null;
  setBrowseZip: (z: string | null) => void;
}

const Ctx = createContext<AppState | null>(null);

/** The current effective answers: confirmed answers win over facts from chat text. */
export function effectiveProfile(confirmed: VolunteerProfile, messageFacts: MessageFact[]): VolunteerProfile {
  const fromChat: Record<string, unknown> = {};
  for (const f of messageFacts) fromChat[f.field] = f.value;
  const out: Record<string, unknown> = { ...fromChat };
  for (const [k, v] of Object.entries(confirmed)) if (v !== undefined && v !== null) out[k] = v;
  return out as VolunteerProfile;
}

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const [confirmed, setConfirmedState] = useState<VolunteerProfile>({});
  const [messageFacts, setMessageFactsState] = useState<MessageFact[]>([]);
  const [facts, setFacts] = useState<ProfileFact[]>([]);
  const [turns, setTurnsState] = useState<Turn[]>([]);
  const [profileVersion, setProfileVersion] = useState(0);
  const [browseZip, setBrowseZip] = useState<string | null>(null);

  const toggleCompare = useCallback((id: string) => {
    setCompareIds((ids) => (ids.includes(id) ? ids.filter((x) => x !== id) : ids.length >= MAX_COMPARE ? ids : [...ids, id]));
  }, []);
  const removeCompare = useCallback((id: string) => setCompareIds((ids) => ids.filter((x) => x !== id)), []);
  const clearCompare = useCallback(() => setCompareIds([]), []);

  const setConfirmed = useCallback((p: VolunteerProfile) => { setConfirmedState(p); setProfileVersion((v) => v + 1); }, []);
  const setMessageFacts = useCallback((f: MessageFact[]) => setMessageFactsState(f), []);
  const bumpPreferences = useCallback(() => setProfileVersion((v) => v + 1), []);
  const [declined, setDeclined] = useState<string[]>([]);
  const [withdrawn, setWithdrawn] = useState<string[]>([]);
  const [asked, setAsked] = useState<string[]>([]);
  const addAsked = useCallback((q: string[]) => setAsked((a) => [...new Set([...a, ...q])].slice(-40)), []);
  const saveAnswers = useCallback((changes: Partial<VolunteerProfile>, removed: string[]) => {
    const touched = new Set([...Object.keys(changes), ...removed]);
    setConfirmedState((c) => {
      const next = { ...c, ...changes } as Record<string, unknown>;
      for (const f of removed) delete next[f];
      return next as VolunteerProfile;
    });
    setMessageFactsState((m) => m.filter((x) => !touched.has(x.field)));
    setFacts((fs) => [
      ...fs.filter((f) => !touched.has(f.field)),
      ...Object.entries(changes).map(([field, value]) => ({ field: field as keyof VolunteerProfile, value, status: "confirmed" as const,
        supporting_text: null, used_in_assessment: true, note: null })),
    ]);
    setWithdrawn((w) => [...new Set([...w.filter((f) => !(f in changes)), ...removed])]);
    setDeclined((d) => d.filter((f) => !(f in changes)));
    setProfileVersion((v) => v + 1);
  }, []);
  const dropConfirmed = useCallback((fields: string[]) => {
    if (!fields.length) return;
    setConfirmedState((c) => {
      const next = { ...c } as Record<string, unknown>;
      for (const f of fields) delete next[f];
      return next as VolunteerProfile;
    });
  }, []);
  const setTurns = useCallback((fn: (t: Turn[]) => Turn[]) => setTurnsState(fn), []);
  const resetSession = useCallback(() => {
    setConfirmedState({}); setMessageFactsState([]); setFacts([]); setTurnsState([]); setCompareIds([]); setDeclined([]); setWithdrawn([]); setAsked([]);
    setBrowseZip(null);
    setProfileVersion((v) => v + 1);
  }, []);

  const value = useMemo<AppState>(() => ({
    compareIds, toggleCompare, removeCompare, clearCompare, confirmed, setConfirmed, messageFacts, setMessageFacts,
    facts, setFacts, profileVersion, bumpPreferences, declined, setDeclined, withdrawn, setWithdrawn, saveAnswers, dropConfirmed,
    asked, addAsked, turns, setTurns, resetSession, browseZip, setBrowseZip,
  }), [compareIds, toggleCompare, removeCompare, clearCompare, confirmed, setConfirmed, messageFacts, setMessageFacts,
    facts, profileVersion, bumpPreferences, declined, withdrawn, saveAnswers, dropConfirmed, asked, addAsked, turns, setTurns, resetSession, browseZip]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAppState(): AppState {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAppState must be used inside AppStateProvider");
  return v;
}
