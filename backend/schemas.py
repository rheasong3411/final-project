"""Typed models.

Part 1 mirrors the existing dataset (data/*.json, schema v2) field for field, with
extra="forbid", so any drift between the JSON and the backend fails loudly at
startup instead of producing a second, incompatible copy of the data.

Part 2 is the volunteer profile. Part 3 is the deterministic assessment. Part 4
is the agent's structured output and the API's assistant response.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ---------------------------------------------------------------- shared vocabularies
Scope = Literal["organization", "program", "role"]
ApplicationStatus = Literal["explicitly_accepting_applications", "explicitly_closed", "needs_confirmation"]
RecordType = Literal["described_volunteer_role", "interest_area_only", "independent_support_activity"]
CommitmentType = Literal["recurring", "one_time", "variable", "unknown"]
ApplicabilityStatus = Literal["published_applicable", "needs_confirmation", "conflicting"]
GeographicScope = Literal["greater_new_haven", "wider_connecticut"]
ActivityTag = Literal[
    "dog_walking", "animal_socialization", "animal_care_cleaning", "laundry", "fostering", "transport",
    "events", "fundraising", "administrative", "grant_writing", "communications_marketing",
    "maintenance_trades", "gardening_grounds", "education_outreach", "supply_drives", "crafts",
    "adoption_support", "tnr_feral_care", "dog_training", "youth_program", "group_project",
]
AnimalTag = Literal["dogs", "cats", "small_animals", "not_applicable", "unspecified"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


# ---------------------------------------------------------------- 1) dataset
class Source(_Strict):
    source_id: str
    organization_id: str
    url: str
    page_title: str
    accessed_at: str
    access_result: str
    published_update_date: str | None
    reliability_flags: list[str]
    evidence_notes: str
    conflicts_or_stale_information: list[str]


class Evidence(_Strict):
    field: str
    source_id: str
    evidence: str
    scope: Scope
    conflict: bool | None = None
    note: str | None = None


class Location(_Strict):
    label: str
    address: str
    town: str | None = None
    source_id: str


class Organization(_Strict):
    organization_id: str
    name: str
    official_website: str
    physical_address: str | None
    town: str | None
    geographic_scope: GeographicScope
    latitude: float | None
    longitude: float | None
    contact_page_url: str
    source_ids: list[str]
    locations: list[Location]
    notes: str | None
    field_evidence: list[Evidence]


class GuardianRequirement(_Strict):
    required: bool
    applies_under_age: int | None
    details: str
    scope: Scope


class TimeCommitment(_Strict):
    published_text: str
    source_id: str
    scope: Scope
    hours_min: float | None
    hours_max: float | None
    hours_per: Literal["week", "month", "session"] | None
    duration_months_min: float | None
    duration_months_max: float | None
    duration_is_typical_not_minimum: bool
    note: str | None


class ScheduleItem(_Strict):
    original_text: str
    summary: str
    source_id: str
    scope: Scope
    note: str | None = None


class DatedNotice(_Strict):
    original_text: str
    stated_date_text: str
    stated_year: int | None
    timing_assessment: Literal["appears_past_year_not_stated", "past", "upcoming", "unknown"]
    assessed_on: str
    note: str | None
    source_id: str
    scope: Scope


class TrainingRequirement(_Strict):
    type: str
    description: str
    scope: Scope
    source_id: str


class Fee(_Strict):
    amount: float
    currency: str
    applies_when: str
    payment_terms: str | None
    covers: str | None
    source_id: str


class OtherRequirement(_Strict):
    requirement: str
    scope: Scope
    source_id: str


class ApplicantNote(_Strict):
    note: str
    type: Literal["advisory", "preferred_skill", "process_note"]
    scope: Scope
    source_id: str


class Applicability(_Strict):
    status: ApplicabilityStatus
    source_ids: list[str]
    reason: str


class UnresolvedQuestion(_Strict):
    field: str | None
    question: str


class Opportunity(_Strict):
    opportunity_id: str
    organization_id: str
    record_type: RecordType
    title: str
    description: str
    activity_tags: list[ActivityTag]
    animal_tags: list[AnimalTag]
    location_description: str | None
    location_town: str | None
    minimum_age: int | None
    guardian_requirement: GuardianRequirement | None
    commitment_type: CommitmentType
    minimum_hours: float | None
    hours_period: Literal["week", "month"] | None
    minimum_commitment_months: float | None
    time_commitment: list[TimeCommitment] | None
    recurring_schedule: list[ScheduleItem] | None
    orientation_info: list[ScheduleItem] | None
    dated_notices: list[DatedNotice] | None
    training_requirements: list[TrainingRequirement] | None
    fees: list[Fee] | None
    other_requirements: list[OtherRequirement] | None
    notes_for_applicants: list[ApplicantNote] | None
    requirement_applicability: dict[str, Applicability]
    application_status: ApplicationStatus
    application_or_information_url: str | None
    source_ids: list[str]
    field_evidence: list[Evidence]
    unresolved_questions: list[UnresolvedQuestion]


# ---------------------------------------------------------------- 2) volunteer profile
Weekday = Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DayPart = Literal["morning", "afternoon", "evening"]


class VolunteerProfile(BaseModel):
    """Only what matching needs. Every field is optional: a missing answer is never a failure.

    Deliberately NOT collected: name, birth date, street address, contact details,
    medical history (including allergies), or anything else not used by a rule.
    """

    model_config = ConfigDict(extra="forbid")

    age: int | None = Field(None, ge=5, le=110, description="Age in whole years (not a birth date).")
    guardian_available: bool | None = Field(
        None, description="For minors: can a parent or guardian attend with them? null = not asked yet.")
    town: str | None = Field(None, max_length=60, description="Town where the person lives (no street address).")
    zip_code: str | None = Field(
        None, pattern=r"^\d{5}$", description="Optional 5-digit ZIP of where they live, kept as a string so leading "
                                               "zeros survive. Only used to estimate distances.")
    prefers_not_to_share_zip: bool | None = Field(None, description="True if the person declined to give a ZIP.")
    has_car: bool | None = Field(None, description="How they travel: false = no car. null = not said.")
    wants_nearby: bool | None = Field(None, description="True if they said they need something close to home.")
    nearby_towns_ok: bool | None = Field(
        None, description="Answer to 'Do you need to stay within <town>, or can you travel to nearby towns?' "
                          "true = nearby towns are fine. Says nothing about distance or transit.")
    volunteer_only_in: str | None = Field(
        None, max_length=60, description="Set ONLY if the person explicitly limits where they will volunteer to one "
                                         "town ('I need to stay in New Haven'). Where they live does not set this.")
    include_wider_connecticut: bool = Field(
        False, description="Greater New Haven is the default; true adds the separate wider-Connecticut scope.")
    interests: list[ActivityTag] = Field(default_factory=list, max_length=10)
    animal_preferences: list[Literal["dogs", "cats", "small_animals"]] = Field(default_factory=list, max_length=3)
    prefers_no_animal_contact: bool | None = None
    available_hours: float | None = Field(None, ge=0, le=168, description="Hours they can give (the LOWER end of a "
                                                                       "stated range such as '2–3 hours').")
    available_hours_max: float | None = Field(
        None, ge=0, le=168, description="Upper end of a stated range ('2–3 hours' -> available_hours=2, "
                                        "available_hours_max=3). Never pick one number from a range.")
    hours_period: Literal["week", "month"] | None = None
    commitment_months: float | None = Field(None, ge=0, le=120, description="How many months they can commit.")
    commitment_preference: Literal["one_time", "recurring", "either"] | None = Field(
        None, description="A PREFERENCE only; it never filters results.")
    commitment_required: Literal["one_time", "recurring"] | None = Field(
        None, description="A HARD constraint, only when the person says they can ONLY do this kind (\"I can only do a "
                          "one-time project\"). Records whose published commitment type differs, or is unknown, are "
                          "not matches.")
    available_days: list[Weekday] = Field(default_factory=list, max_length=7)
    available_times: list[DayPart] = Field(default_factory=list, max_length=3)
    max_session_hours: float | None = Field(
        None, ge=0, le=24, description="Longest single continuous block the person can attend, in hours "
                                        "(for one-time sessions). Weekly/monthly hours do not answer this.")

    @model_validator(mode="after")
    def _range(self):
        if self.available_hours_max is not None and (self.available_hours is None
                                                     or self.available_hours_max < self.available_hours):
            raise ValueError("available_hours_max needs available_hours (the lower end) and must not be smaller")
        if self.available_hours_max == self.available_hours and self.available_hours_max is not None:
            object.__setattr__(self, "available_hours_max", None)  # "3–3" is just 3
        return self

    @field_validator("town", "volunteer_only_in")
    @classmethod
    def _clean_town(cls, v: str | None) -> str | None:
        return v.strip() or None if isinstance(v, str) else v

    def fingerprint(self) -> str:
        """Stable hash of the fields requirement checks use; every assessment records the fingerprint it was
        computed with. Location and travel fields never change fit, so changing them doesn't stale assessments."""
        import hashlib
        import json
        data = self.model_dump(mode="json", exclude=set(LOCATION_FIELDS))
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:12]


# Where someone lives (town, zip_code), how they travel (has_car) and where they will volunteer
# (volunteer_only_in, nearby_towns_ok) are kept apart. None of these except `town` feeds a requirement check
# (town matters for residence-based rules such as fees for non-residents).
LOCATION_FIELDS = ("zip_code", "prefers_not_to_share_zip", "has_car", "wants_nearby", "nearby_towns_ok",
                   "volunteer_only_in")


# ---------------------------------------------------------------- 3) deterministic assessment
AssessmentStatus = Literal["met", "not_met", "needs_confirmation"]
OverallStatus = Literal["not_met", "needs_confirmation", "meets_published_requirements_checked"]


class EvidenceRef(BaseModel):
    source_id: str
    quote: str


class RequirementAssessment(BaseModel):
    opportunity_id: str
    requirement: str
    published_requirement: str
    applicability: ApplicabilityStatus | Literal["not_published"]
    status: AssessmentStatus
    profile_fields_used: dict[str, object]
    explanation: str
    source_ids: list[str]
    evidence: list[EvidenceRef]
    uncertainty_note: str | None = Field(None, description="Short note shown beside the fact when applicability "
                                                            "is needs_confirmation or conflicting.")
    listed_value_matched: bool | None = Field(
        None, description="True when the person's answer matches the listed value but the rule's current "
                          "applicability is uncertain or conflicting, so the status stays needs_confirmation.")


class ApplicationStatusInfo(BaseModel):
    status: ApplicationStatus
    label: str
    explanation: str
    source_ids: list[str]


class Assessment(BaseModel):
    opportunity_id: str
    title: str
    organization_name: str
    record_type: RecordType
    record_type_label: str
    overall_status: OverallStatus
    overall_summary: str
    requirements: list[RequirementAssessment]
    notes: list[str]
    costs: list[str]
    application_status: ApplicationStatusInfo
    placement_or_shift_availability: str
    questions_for_organization: list[str]
    profile_fingerprint: str = ""


# ---------------------------------------------------------------- 4) agent output + assistant response
class AgentRecommendation(BaseModel):
    opportunity_id: str = Field(description="Must be an ID returned by the tools.")
    stated_fit: OverallStatus = Field(description="Must equal overall_status from assess_profile for this ID.")
    why_relevant: str = Field(max_length=300, description="One short sentence.")


class AgentNonMatch(BaseModel):
    opportunity_id: str = Field(description="A role discussed to explain why it does not fit or is closed.")
    stated_fit: OverallStatus = Field(description="Must equal overall_status from the latest assessment.")
    why_not: str = Field(max_length=300)


class AgentOutput(BaseModel):
    """What the model must return. The server adds the deterministic details."""

    answer: str = Field(max_length=1200, description="Brief opening (1-3 short sentences). Per-option facts are "
                                                     "rendered by the page from the tool results.")
    recommendations: list[AgentRecommendation] = Field(
        default_factory=list, max_length=3,
        description="Suitable options only: assessed, and overall_status is not 'not_met'.")
    alternative_ids: list[str] = Field(
        default_factory=list, max_length=3,
        description="Suitable alternatives only: assessed, not 'not_met', applications not explicitly closed.")
    non_matches: list[AgentNonMatch] = Field(
        default_factory=list, max_length=3,
        description="Assessed roles you explain as not fitting (not_met) or closed. Never presented as options.")
    ask_about_ids: list[str] = Field(
        default_factory=list, max_length=3,
        description="Only with a hard commitment constraint (commitment_required): suitable records whose commitment is "
                    "unknown or varies, offered separately as activities to ask about, never as matches.")
    outside_area_ids: list[str] = Field(
        default_factory=list, max_length=3,
        description="Only when the person limited where they volunteer (volunteer_only_in): suitable records outside "
                    "that town (or with no confirmed location), offered only if they choose to expand the area.")
    follow_up_questions: list[str] = Field(default_factory=list, max_length=4, description="At most 2 are shown.")
    cited_source_ids: list[str] = Field(default_factory=list, max_length=15)
    checklist_for_ids: list[str] = Field(default_factory=list, max_length=3,
                                         description="IDs whose application checklist should be shown.")


class SourceRef(BaseModel):
    source_id: str
    organization_id: str
    page_title: str
    url: str
    accessed_at: str


class ChecklistStep(BaseModel):
    step: str
    source_ids: list[str]


class ApplicationChecklist(BaseModel):
    opportunity_id: str
    title: str
    steps: list[ChecklistStep]


class DistanceEstimate(BaseModel):
    status: Literal["estimated", "unavailable", "no_zip_area"]
    type: Literal["volunteering_site", "organization_location", "organization_nearest_site", "town_reference",
                  "related_site", "organization_reference"] | None = Field(
        None, description="What the estimate measures. Only volunteering_site is a distance to where you volunteer.")
    place_label: str | None = Field(None, description="e.g. 'North Haven', 'Organization: New Haven'.")
    label: str | None = Field(None, description="place_label · display, as shown on cards.")
    miles: float | None = Field(None, description="Rounded value shown to people.")
    sort_miles: float | None = Field(None, description="Unrounded distance, for sorting only.")
    display: str | None = None
    secondary: str | None = Field(None, description="e.g. 'Activity location may differ'.")
    destination_label: str | None = None
    explanation: str


class LocationEstimate(BaseModel):
    """Where a record takes place (one of five categories) and, with a supported ZIP, a labelled straight-line
    estimate. Kept apart from the assessment (fit) and the application status. See backend/geo.py."""
    towns: list[str] = Field(description="Shown towns: the role's own town, else the organization's town.")
    geographic_scope: GeographicScope
    kind: Literal["verified_site", "organization_location", "town_only", "home_based", "unknown"]
    headline: str
    place_label: str = Field("", description="Short card text without a ZIP, e.g. 'Organization: New Haven'.")
    place_note: str | None = Field(None, description="Small note under the place, e.g. 'Activity location may differ'.")
    location_status: Literal["verified_site", "candidate_site_unconfirmed", "volunteer_home", "not_published"]
    role_town: str | None = Field(None, description="Only the role's own published town; never inferred.")
    site: dict | None = None
    organization_site: dict | None = None
    related_site: dict | None = None
    other_sites: list[dict] = []
    town_reference: dict | None = None
    travel_note: str | None = None
    evidence: list[dict] = []
    maps_url: str | None = None
    coordinates_verified: bool = False
    note: str | None = None
    distance: DistanceEstimate | None = None
    in_chosen_area: bool | None = Field(None, description="null when the person set no volunteering-area limit.")


class Recommendation(BaseModel):
    opportunity_id: str
    title: str
    organization_name: str
    record_type: RecordType
    record_type_label: str
    why_relevant: str
    assessment: Assessment
    location: LocationEstimate | None = None
    next_actions: list[dict] = Field(default_factory=list, description="Official-page links: 'Visit volunteer page' (or "
                                                                       "'Apply on organization's website') and 'Contact organization'.")


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=2000)


class MessageFact(BaseModel):
    """A profile fact taken from the person's own chat text in an earlier turn (not yet confirmed).

    The server re-verifies that `supporting_text` appears in the person's messages before using it.
    """
    model_config = ConfigDict(extra="forbid")
    field: str = Field(max_length=40)
    value: object
    supporting_text: str = Field(min_length=1, max_length=300)


class AssistantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=2000)
    profile: VolunteerProfile | None = Field(
        None, description="Answers the person explicitly confirmed in the form (the trusted path).")
    message_facts: list[MessageFact] = Field(default_factory=list, max_length=20)
    declined_fields: list[str] = Field(
        default_factory=list, max_length=20,
        description="Profile fields the person marked 'not right'; chat values for them are never applied.")
    history: list[ChatTurn] = Field(default_factory=list, max_length=10)
    asked_follow_ups: list[str] = Field(
        default_factory=list, max_length=40,
        description="Questions already shown this session; the server doesn't repeat its own optional questions.")
    withdrawn_fields: list[str] = Field(
        default_factory=list, max_length=30,
        description="Fields the person withdrew in an earlier turn. They stay unknown: older messages can't restore "
                    "them; only a value written in the current message can.")
    earlier_user_messages: list[str] = Field(
        default_factory=list, max_length=40,
        description="The person's own messages from before `history` (not sent to the model). Used only to "
                    "re-verify quotes behind remembered facts, so memory survives long conversations.")

    @field_validator("earlier_user_messages")
    @classmethod
    def _cap(cls, v: list[str]) -> list[str]:
        return [m[:2000] for m in v]


class ProfileFact(BaseModel):
    field: str
    value: object
    status: Literal["confirmed", "from_message", "suggested", "conflicts_with_confirmed", "cleared"]
    supporting_text: str | None = None
    used_in_assessment: bool
    note: str | None = None


class UsageRecord(BaseModel):
    requests: int
    input_tokens: int | None
    cached_input_tokens: int | None
    cache_write_input_tokens: int | None = None
    uncached_input_tokens: int | None
    output_tokens: int | None
    provenance: str


class AssistantResponse(BaseModel):
    run_id: str
    ok: bool
    answer: str
    recommendations: list[Recommendation] = []
    alternatives: list[Recommendation] = []
    explained_non_matches: list[Recommendation] = []
    outside_area_suggestions: list[Recommendation] = []
    ask_about: list[Recommendation] = Field(default_factory=list, description="'Other activities to ask about': they "
                                            "relax a hard constraint, named in each why_relevant.")
    location_context: dict = {}
    requirement_assessments: list[RequirementAssessment] = []
    follow_up_questions: list[str] = []
    sources: list[SourceRef] = []
    application_checklists: list[ApplicationChecklist] = []
    profile_used: VolunteerProfile | None = None
    profile_provenance: dict[str, str] = {}
    profile_facts: list[ProfileFact] = []
    profile_changes: list[dict] = []
    withdrawn_fields: list[str] = Field(default_factory=list, description="All fields withdrawn so far (send back next turn).")
    confirmed_overrides: list[str] = Field(
        default_factory=list, description="Form-confirmed fields the person corrected or withdrew in this message; the "
                                          "page removes them from its confirmed answers.")
    requested_model: str
    returned_models: list[str] = []
    usage: UsageRecord | None = None
    error: str | None = None
    disclaimer: str = ("This assistant helps you prepare to apply. It does not approve volunteers, confirm openings, "
                       "or guarantee placement or shifts. Organizations make all decisions.")
