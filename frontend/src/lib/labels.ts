// Human-readable labels for dataset vocabularies. Unknown values fall back to a tidied version.
import type { ApplicabilityStatus, AssessmentStatus, CommitmentType, OverallStatus, VolunteerProfile } from "../api/types";

const ACTIVITY: Record<string, string> = {
  dog_walking: "Dog walking", animal_socialization: "Socializing animals", animal_care_cleaning: "Animal care & cleaning",
  laundry: "Laundry", fostering: "Fostering", transport: "Transport", events: "Events", fundraising: "Fundraising",
  administrative: "Administrative", grant_writing: "Grant writing", communications_marketing: "Communications",
  maintenance_trades: "Maintenance & trades", gardening_grounds: "Gardening & grounds",
  education_outreach: "Education & outreach", supply_drives: "Supply drives", crafts: "Crafts",
  adoption_support: "Adoption support", tnr_feral_care: "Feral cat care (TNR)", dog_training: "Dog training",
  youth_program: "Youth program", group_project: "Group project",
};
const ANIMAL: Record<string, string> = {
  dogs: "Dogs", cats: "Cats", small_animals: "Small animals", not_applicable: "No animal contact", unspecified: "Animals not specified",
};
// Explore's commitment filter offers exactly these four choices; "unknown" records stay under "Any commitment".
export const COMMITMENT_FILTER: [string, string][] = [["", "Any commitment"], ["one_time", "One-time"],
  ["recurring", "Ongoing"], ["variable", "Flexible / varies"]];
const COMMITMENT: Record<CommitmentType, string> = {
  recurring: "Ongoing", one_time: "One-time", variable: "Flexible / varies", unknown: "Time commitment: ask organization",
};
const SCOPE: Record<string, string> = { greater_new_haven: "Greater New Haven", wider_connecticut: "Other Connecticut location" };

/** Everyday-language labels for the non-standard record types (the record types themselves are unchanged). */
export const RECORD_TYPE_UI: Record<string, { chip: string; explain: string }> = {
  interest_area_only: {
    chip: "Ask about this activity",
    explain: "The organization mentions this activity on an application form but hasn't published a full role description. Ask whether help is needed; it isn't a confirmed placement.",
  },
  independent_support_activity: {
    chip: "Help on your own",
    explain: "Something you organize yourself, such as a supply drive, pet beds or a fundraiser. It isn't a staffed shelter shift.",
  },
};

export const tidy = (s: string) => s.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
export const activityLabel = (t: string) => ACTIVITY[t] ?? tidy(t);
export const animalLabel = (t: string) => ANIMAL[t] ?? tidy(t);
export const commitmentLabel = (t: CommitmentType) => COMMITMENT[t] ?? tidy(t);
export const scopeLabel = (t: string) => SCOPE[t] ?? tidy(t);

export const FIT_LABEL: Record<AssessmentStatus, string> = {
  met: "Meets this published requirement",
  not_met: "Does not meet this published requirement",
  needs_confirmation: "Needs confirmation",
};
export const OVERALL_LABEL: Record<OverallStatus, string> = {
  meets_published_requirements_checked: "Meets the published requirements we checked",
  needs_confirmation: "Possible fit — confirm requirements",
  not_met: "Does not meet a published requirement",
};
export const APPLICABILITY_LABEL: Record<ApplicabilityStatus | "not_published", string> = {
  published_applicable: "Published requirement",
  needs_confirmation: "Uncertain — confirm with organization",
  conflicting: "Sources conflict — confirm with organization",
  not_published: "Not published",
};

export const REQUIREMENT_LABEL: Record<string, string> = {
  minimum_age: "Minimum age", guardian_requirement: "Parent or guardian", minimum_hours: "Hours",
  minimum_commitment_months: "Commitment length", time_commitment: "Time commitment", session_length: "Session length",
  recurring_schedule: "Schedule", other_requirements: "Other requirement", commitment_type: "Commitment type",
  training_requirements: "Training", fees: "Fees",
};
export const requirementLabel = (r: string) => REQUIREMENT_LABEL[r] ?? tidy(r);

export const PROFILE_FIELD_LABEL: Record<keyof VolunteerProfile, string> = {
  age: "Age", guardian_available: "Parent or guardian can attend", town: "Town where you live",
  include_wider_connecticut: "Include other Connecticut locations", interests: "Interests", animal_preferences: "Animals",
  prefers_no_animal_contact: "Prefers no animal contact", available_hours: "Available hours", available_hours_max: "Up to (hours)", hours_period: "Hours per",
  commitment_months: "Months you can commit", commitment_preference: "Commitment preference",
  available_days: "Days", available_times: "Times of day", max_session_hours: "Longest single session (hours)",
  zip_code: "ZIP code", prefers_not_to_share_zip: "Prefers not to share a ZIP code", has_car: "Has a car",
  wants_nearby: "Needs something close to home", nearby_towns_ok: "Can travel to nearby towns",
  volunteer_only_in: "Only volunteer in", commitment_required: "Can only do",
};

const DAY: Record<string, string> = { mon: "Mon", tue: "Tue", wed: "Wed", thu: "Thu", fri: "Fri", sat: "Sat", sun: "Sun" };

export function formatProfileValue(field: string, value: unknown): string {
  if (value === null || value === undefined) return "Not sure";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value)) {
    if (field === "interests") return value.map((v) => activityLabel(String(v))).join(", ");
    if (field === "animal_preferences") return value.map((v) => animalLabel(String(v))).join(", ");
    if (field === "available_days") return value.map((v) => DAY[String(v)] ?? String(v)).join(", ");
    return value.map((v) => tidy(String(v))).join(", ");
  }
  if (field === "commitment_preference" || field === "commitment_required") return tidy(String(value)).replace("One time", "One-time").replace("Recurring", "Ongoing");
  return String(value);
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "Not recorded";
  // A bare YYYY-MM-DD is a calendar date: parse it as local, not UTC midnight (which shows the previous day).
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  const d = m ? new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])) : new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
}

export function hostOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}
