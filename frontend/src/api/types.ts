// Types mirror the FastAPI responses (backend/schemas.py and backend/data.py summary/details dicts).
// Keep in sync with the backend; do not add fields the API does not return.

export type ApplicationStatus = "explicitly_accepting_applications" | "explicitly_closed" | "needs_confirmation";
export type RecordType = "described_volunteer_role" | "interest_area_only" | "independent_support_activity";
export type CommitmentType = "recurring" | "one_time" | "variable" | "unknown";
export type ApplicabilityStatus = "published_applicable" | "needs_confirmation" | "conflicting";
export type GeographicScope = "greater_new_haven" | "wider_connecticut";
export type AssessmentStatus = "met" | "not_met" | "needs_confirmation";
export type OverallStatus = "not_met" | "needs_confirmation" | "meets_published_requirements_checked";

export interface OpportunitySummary {
  opportunity_id: string;
  title: string;
  organization_id: string;
  organization_name: string;
  geographic_scope: GeographicScope;
  towns: string[];
  record_type: RecordType;
  record_type_label: string;
  activity_tags: string[];
  animal_tags: string[];
  commitment_type: CommitmentType;
  minimum_age: number | null;
  minimum_age_status: ApplicabilityStatus | "not_published";
  uncertain_requirements: string[];
  application_status: ApplicationStatus;
  application_status_label: string;
  short_description: string;
  source_checked_on: string | null;
  /** Present on list and detail routes. */
  location?: LocationInfo;
  next_actions?: NextAction[];
}

/** Where a record takes place (official pages, verified 2026-10-25). No distance here. */
export type LocationKind = "verified_site" | "organization_location" | "town_only" | "home_based" | "unknown";
export interface SiteRef { site_id: string; label: string; address: string; town: string; maps_url: string | null;
  /** Google Maps directions with only the destination filled in (the person enters their start and how they travel). */
  directions_url?: string | null }

/** Where a record takes place: exactly one of five categories (backend/geo.py). No distance here. */
export interface LocationInfo {
  kind: LocationKind;
  headline: string;
  /** Short card text without a ZIP ("North Haven", "Organization: New Haven", "Help from your home"…). */
  place_label: string;
  /** Small note under the place, e.g. "Activity location may differ". */
  place_note: string | null;
  location_status: "verified_site" | "candidate_site_unconfirmed" | "volunteer_home" | "not_published";
  note: string | null;
  /** The role's own published town only; never inferred from the organization. */
  role_town: string | null;
  site: SiteRef | null;
  organization_site: SiteRef | null;
  related_site: (SiteRef & { purpose: string }) | null;
  other_sites: SiteRef[];
  town_reference: { town: string; source: string } | null;
  travel_note: string | null;
  evidence: { source_id: string; url: string; quote: string; accessed_at: string }[];
  maps_url: string | null;
  coordinates_verified: boolean;
}

export interface DistanceEstimate {
  status: "estimated" | "unavailable" | "no_zip_area";
  /** The destination measured: the volunteering site, else the organization's verified location (or its nearest
   *  named site), a town reference point, a sourced home-activity travel site, or a home-activity reference. */
  type: "volunteering_site" | "organization_location" | "organization_nearest_site" | "town_reference" | "related_site"
    | "organization_reference" | null;
  /** Rounded value shown to people. */
  miles: number | null;
  /** Unrounded distance, for sorting only. */
  sort_miles: number | null;
  display: string | null;
  /** "North Haven" / "Organization: New Haven" / "Nearest organization site: CHS Wilton"… */
  place_label: string | null;
  /** place_label · display, as shown on cards. */
  label: string | null;
  secondary: string | null;
  destination_label: string | null;
  explanation: string;
}

export type ZipStatus = "supported" | "invalid_format" | "not_in_dataset" | "outside_coverage" | "not_provided" | "declined";
export interface ZipArea { status: ZipStatus; message: string }

export interface LocationEstimates {
  zip_area: ZipArea;
  estimates: Record<string, LocationInfo & { distance: DistanceEstimate }>;
  method: string;
}

export interface OpportunityList {
  count: number;
  scope: string;
  record_types: RecordType[];
  results: OpportunitySummary[];
  /** Records left out because their applications are explicitly closed. */
  closed_hidden: number;
  note: string | null;
}

export interface FilterValues {
  geographic_scopes: { default: string; values: string[] };
  towns: string[];
  /** Town options for each scope: Greater New Haven only, or all (with other Connecticut locations). */
  towns_by_scope?: { greater_new_haven: string[]; all: string[] };
  organizations: { organization_id: string; name: string; geographic_scope: GeographicScope }[];
  activity_tags: string[];
  animal_tags: string[];
  record_types: { value: RecordType; label: string }[];
  application_statuses: { value: ApplicationStatus; label: string }[];
  commitment_types: CommitmentType[];
  notes: string;
}

export interface Evidence {
  field: string;
  source_id: string;
  evidence: string;
  scope: string;
  conflict?: boolean | null;
  note?: string | null;
}

export interface ScheduleItem { original_text: string; summary: string; source_id: string; scope: string; note?: string | null }
export interface DatedNotice {
  original_text: string; stated_date_text: string; stated_year: number | null;
  timing_assessment: string; assessed_on: string; note: string | null; source_id: string; scope: string;
}
export interface TimeCommitment {
  published_text: string; source_id: string; scope: string;
  hours_min: number | null; hours_max: number | null; hours_per: "week" | "month" | "session" | null;
  duration_months_min: number | null; duration_months_max: number | null;
  duration_is_typical_not_minimum: boolean; note: string | null;
}
export interface Applicability { status: ApplicabilityStatus; source_ids: string[]; reason: string }

export interface OpportunityRecord {
  opportunity_id: string;
  organization_id: string;
  record_type: RecordType;
  title: string;
  description: string;
  activity_tags: string[];
  animal_tags: string[];
  location_description: string | null;
  location_town: string | null;
  minimum_age: number | null;
  guardian_requirement: { required: boolean; applies_under_age: number | null; details: string; scope: string } | null;
  commitment_type: CommitmentType;
  minimum_hours: number | null;
  hours_period: "week" | "month" | null;
  minimum_commitment_months: number | null;
  time_commitment: TimeCommitment[] | null;
  recurring_schedule: ScheduleItem[] | null;
  orientation_info: ScheduleItem[] | null;
  dated_notices: DatedNotice[] | null;
  training_requirements: { type: string; description: string; scope: string; source_id: string }[] | null;
  fees: { amount: number; currency: string; applies_when: string; payment_terms: string | null; covers: string | null; source_id: string }[] | null;
  other_requirements: { requirement: string; scope: string; source_id: string }[] | null;
  notes_for_applicants: { note: string; type: string; scope: string; source_id: string }[] | null;
  requirement_applicability: Record<string, Applicability>;
  application_status: ApplicationStatus;
  application_or_information_url: string | null;
  source_ids: string[];
  field_evidence: Evidence[];
  unresolved_questions: { field: string | null; question: string }[];
}

export interface SourceRef { source_id: string; organization_id: string; page_title: string; url: string; accessed_at: string }
export interface ChecklistStep { step: string; source_ids: string[] }

export interface OpportunityDetail extends OpportunitySummary {
  record: OpportunityRecord;
  organization: {
    organization_id: string; name: string; official_website: string; physical_address: string | null;
    town: string | null; geographic_scope: GeographicScope; contact_page_url: string;
    locations: { label: string; address: string; town: string | null; source_id: string }[]; notes: string | null;
  };
  sources: SourceRef[];
  application_checklist: ChecklistStep[];
  next_actions: NextAction[];
}

export interface RequirementAssessment {
  opportunity_id: string;
  requirement: string;
  published_requirement: string;
  applicability: ApplicabilityStatus | "not_published";
  status: AssessmentStatus;
  profile_fields_used: Record<string, unknown>;
  explanation: string;
  source_ids: string[];
  evidence: { source_id: string; quote: string }[];
  /** Short note shown beside the fact when applicability is needs_confirmation or conflicting. */
  uncertainty_note?: string | null;
  /** The person's answer matches the listed value, but the rule's current applicability is uncertain, so the
   *  status stays "needs_confirmation" (amber), never green. */
  listed_value_matched?: boolean | null;
}

/** Official-page links, labelled by what the destination is (backend Dataset.next_actions). */
export interface NextAction { label: string; url: string; kind: "volunteer_page" | "application" | "contact" }

export interface Assessment {
  opportunity_id: string;
  title: string;
  organization_name: string;
  record_type: RecordType;
  record_type_label: string;
  overall_status: OverallStatus;
  overall_summary: string;
  requirements: RequirementAssessment[];
  notes: string[];
  costs: string[];
  application_status: { status: ApplicationStatus; label: string; explanation: string; source_ids: string[] };
  placement_or_shift_availability: string;
  questions_for_organization: string[];
  profile_fingerprint: string;
}

export type Weekday = "mon" | "tue" | "wed" | "thu" | "fri" | "sat" | "sun";
export type DayPart = "morning" | "afternoon" | "evening";

/** Mirrors backend VolunteerProfile. Every field optional: missing means "not sure / not answered". */
export interface VolunteerProfile {
  age?: number | null;
  guardian_available?: boolean | null;
  town?: string | null;
  /** Five digits, kept as a string so a leading zero survives. Only used to estimate distances. */
  zip_code?: string | null;
  prefers_not_to_share_zip?: boolean | null;
  has_car?: boolean | null;
  wants_nearby?: boolean | null;
  nearby_towns_ok?: boolean | null;
  volunteer_only_in?: string | null;
  include_wider_connecticut?: boolean;
  interests?: string[];
  animal_preferences?: string[];
  prefers_no_animal_contact?: boolean | null;
  available_hours?: number | null;
  /** Upper end of a stated range ("2–3 hours"). */
  available_hours_max?: number | null;
  hours_period?: "week" | "month" | null;
  commitment_months?: number | null;
  commitment_preference?: "one_time" | "recurring" | "either" | null;
  /** Hard constraint ("I can only do one-time"); a preference never filters. */
  commitment_required?: "one_time" | "recurring" | null;
  available_days?: Weekday[];
  available_times?: DayPart[];
  max_session_hours?: number | null;
}

export interface Recommendation {
  opportunity_id: string;
  title: string;
  organization_name: string;
  record_type: RecordType;
  record_type_label: string;
  why_relevant: string;
  assessment: Assessment;
  location: (LocationInfo & {
    towns: string[]; geographic_scope: GeographicScope; distance: DistanceEstimate | null; in_chosen_area: boolean | null;
  }) | null;
  next_actions: NextAction[];
}

export interface LocationContext {
  lives_in_town: string | null;
  zip_area: ZipArea;
  has_car: boolean | null;
  wants_nearby: boolean | null;
  nearby_towns_ok: boolean | null;
  volunteer_only_in: string | null;
}

export interface ProfileFact {
  field: keyof VolunteerProfile;
  value: unknown;
  status: "confirmed" | "from_message" | "suggested" | "conflicts_with_confirmed" | "cleared";
  supporting_text: string | null;
  used_in_assessment: boolean;
  note: string | null;
}

export interface AssistantResponse {
  run_id: string;
  ok: boolean;
  answer: string;
  recommendations: Recommendation[];
  alternatives: Recommendation[];
  explained_non_matches: Recommendation[];
  outside_area_suggestions: Recommendation[];
  /** "Other activities to ask about": relax a hard constraint, named on each card. */
  ask_about?: Recommendation[];
  location_context: LocationContext | Record<string, never>;
  requirement_assessments: RequirementAssessment[];
  follow_up_questions: string[];
  sources: SourceRef[];
  application_checklists: { opportunity_id: string; title: string; steps: ChecklistStep[] }[];
  profile_used: VolunteerProfile | null;
  profile_provenance: Record<string, string>;
  profile_facts: ProfileFact[];
  profile_changes: Record<string, unknown>[];
  /** Every field withdrawn so far; sent back next turn so older messages can't restore them. */
  withdrawn_fields?: string[];
  /** Form-confirmed fields the person corrected or withdrew in this message (dropped from confirmed answers). */
  confirmed_overrides?: string[];
  requested_model: string;
  returned_models: string[];
  usage: {
    requests: number; input_tokens: number | null; cached_input_tokens: number | null;
    cache_write_input_tokens?: number | null;
    uncached_input_tokens: number | null; output_tokens: number | null; provenance: string;
  } | null;
  error: string | null;
  disclaimer: string;
}

export interface MessageFact { field: string; value: unknown; supporting_text: string }
export interface ChatTurn { role: "user" | "assistant"; content: string }

export interface Health {
  status: string;
  data: { organizations: number; opportunities: number; sources: number };
  assistant: { model: string; provider: string; credentials_present: boolean; credential_source: string | null };
}
