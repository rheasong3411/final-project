// Thin fetch wrapper. All requests go to same-origin /api (Vite proxies it in development;
// FastAPI serves both in production). No credentials ever live in the browser.
import type {
  Assessment, AssistantResponse, ChatTurn, FilterValues, Health, LocationEstimates, MessageFact, OpportunityDetail,
  OpportunityList, VolunteerProfile,
} from "./types";

export class ApiError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, init?: RequestInit & { timeoutMs?: number }): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), init?.timeoutMs ?? 20000);
  if (init?.signal) init.signal.addEventListener("abort", () => controller.abort());
  let res: Response;
  try {
    res = await fetch(path, { ...init, signal: controller.signal, headers: { "content-type": "application/json" } });
  } catch (e) {
    clearTimeout(timer);
    if ((e as Error).name === "AbortError") {
      if (init?.signal?.aborted) throw e;
      throw new ApiError(0, "client_timeout", "The request took too long. Please try again.");
    }
    throw new ApiError(0, "backend_unavailable", "The app's server could not be reached. Is the backend running?");
  }
  clearTimeout(timer);
  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : "";
    } catch {
      /* non-JSON error body */
    }
    const code = res.status === 429 ? "rate_limited" : res.status === 422 ? "invalid_input" : res.status === 404 ? "not_found" : "server_error";
    throw new ApiError(res.status, code, detail || `Request failed (HTTP ${res.status}).`);
  }
  return (await res.json()) as T;
}

/** Drops unanswered fields so "not sure" is sent as absent, never as zero/false. */
export function cleanProfile(p: VolunteerProfile): VolunteerProfile {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(p)) {
    if (v === null || v === undefined || v === "") continue;
    if (Array.isArray(v) && v.length === 0) continue;
    if (k === "include_wider_connecticut" && v === false) continue;
    out[k] = v;
  }
  return out as VolunteerProfile;
}

export type ListParams = Record<string, string | string[] | undefined>;

function query(params: ListParams): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === "") continue;
    (Array.isArray(v) ? v : [v]).forEach((x) => q.append(k, x));
  }
  const s = q.toString();
  return s ? `?${s}` : "";
}

export const api = {
  health: (signal?: AbortSignal) => request<Health>("/api/health", { signal }),
  filters: (signal?: AbortSignal) => request<FilterValues>("/api/filters", { signal }),
  opportunities: (params: ListParams, signal?: AbortSignal) =>
    request<OpportunityList>(`/api/opportunities${query(params)}`, { signal }),
  opportunity: (id: string, signal?: AbortSignal) =>
    request<OpportunityDetail>(`/api/opportunities/${encodeURIComponent(id)}`, { signal }),
  assess: (id: string, profile: VolunteerProfile, signal?: AbortSignal) =>
    request<Assessment>(`/api/opportunities/${encodeURIComponent(id)}/assess`, {
      method: "POST", body: JSON.stringify({ profile: cleanProfile(profile) }), signal,
    }),
  /** POST, so a ZIP never appears in a URL, browser history or server access log. */
  locationEstimates: (zip_code: string, opportunity_ids: string[], signal?: AbortSignal) =>
    request<LocationEstimates>("/api/location/estimates", {
      method: "POST", body: JSON.stringify({ zip_code, opportunity_ids }), signal,
    }),
  assistant: (body: { message: string; profile: VolunteerProfile; message_facts: MessageFact[]; history: ChatTurn[];
                      declined_fields: string[]; earlier_user_messages: string[]; withdrawn_fields: string[]; asked_follow_ups: string[] },
              signal?: AbortSignal) =>
    request<AssistantResponse>("/api/assistant", {
      method: "POST", body: JSON.stringify({ ...body, profile: cleanProfile(body.profile) }), signal,
      timeoutMs: 200000, // the backend run limit is 180 s
    }),
};
