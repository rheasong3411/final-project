"""Agent tools. Every tool reads only the in-memory dataset and the deterministic matcher.

No tool can run shell commands, read files, browse the web, submit forms or contact anyone.
Tools return compact, structured dicts with stable IDs; dataset text inside them is
data, not instructions.

Profile handling within one run (one consistent profile, see `update_profile`):
- `deps.profile` is the single profile used for assessments.
- Values from the request's `profile` were confirmed by the person in the form: status
  "confirmed" (the trusted path). Chat never overrides them; a conflicting chat value is
  recorded as "conflicts_with_confirmed" so the person can decide.
- Values the model extracts from chat need a supporting quote. The quote must appear verbatim
  in the person's own messages (this turn or history) and, for numbers, contain the number;
  enum/boolean fields need a matching keyword. Then the status is "from_message" (used, but
  shown for confirmation). The model's own provenance labels are never trusted on their own.
- Anything else is "suggested". For eligibility fields (age, guardian, hours, hours period,
  commitment months, session length) a suggestion is NOT used in any assessment until the
  person confirms it. Other suggestions (interests, days, scope...) may guide search and are
  labelled.
- An existing "from_message" value is replaced by a different verified value when the model marks the
  field in corrected_fields, or when the new quote comes from the person's CURRENT message (the latest
  statement wins); otherwise the new value is kept as a suggestion.
- Corrections and withdrawals (see `withdraw_fields`) must be quoted from the CURRENT message. They may change
  even a form-confirmed answer: the person's newest words win, and the page drops that field from its confirmed
  answers (`confirmed_overrides`). A withdrawn field is cleared (unknown, never a guessed replacement) and stays
  cleared: older messages in the history can never restore it; only a value written in a later message can.
- Whenever the profile changes, every stored assessment is recomputed with the new profile,
  so `deps.assessed` always reflects the current profile (checked by fingerprint).
This reduces extraction errors; it cannot eliminate them (a verbatim quote can still be
misread), which is why from_message facts are shown to the person for confirmation.

Location (see backend/geo.py): where the person lives (town, zip_code), how they travel (has_car,
wants_nearby) and where they will volunteer (volunteer_only_in, nearby_towns_ok) are separate fields.
A ZIP must be written by the person (the quote must contain the five digits), so it can never be
inferred from a landmark. An explicit volunteer_only_in limit is enforced in every search.
Distances come only from geo.py; the model is never asked to compute one.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from pydantic_ai import RunContext

from .config import MAX_SEARCH_RESULTS
from .data import Dataset
from .geo import ZIP_RE, get_geo
from .matching import assess, checklist, find_alternatives
from .schemas import ActivityTag, Assessment, VolunteerProfile

MAX_ASSESS_PER_CALL = 4
BROADER_OPTIONS = 5


CRITICAL_FIELDS = ("age", "guardian_available", "available_hours", "available_hours_max", "hours_period",
                   "commitment_months", "max_session_hours")
# Location facts that must also come from the person's own words: a guessed ZIP would fabricate distances,
# a guessed town would trigger residence rules, and a guessed area limit would hide valid options.
VERIFIED_ONLY_FIELDS = CRITICAL_FIELDS + ("town", "zip_code", "volunteer_only_in", "commitment_required")
_NUMERIC = {"age", "available_hours", "available_hours_max", "commitment_months", "max_session_hours"}
# "2–3 hours", "2-3 hrs", "2 to 3 hours": a stated RANGE. Its ends are kept as available_hours / available_hours_max;
# a single number is never picked from it, and a range alone says nothing about the period or a single session.
HOURS_RANGE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:[–—-]|to)\s*(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\b", re.I)
# An explicit period only: "per week", "a week", "each week", "weekly" (never "weekend"); likewise for months.
_HOURS_FIELDS = ("available_hours", "available_hours_max", "hours_period", "max_session_hours")
_PERIOD_WORDS = {"week": re.compile(r"\b(?:per|a|each|every|/)\s*week\b|\bweekly\b|\bhours?/week\b|\bhrs?/wk\b", re.I),
                 "month": re.compile(r"\b(?:per|a|each|every|/)\s*month\b|\bmonthly\b|\bhours?/month\b", re.I)}
_SESSION_WORDS = re.compile(r"\b(per|each|a|every)\s+(visit|session|shift|time)\b|\bat a time\b|\bin one (go|sitting|session|day)\b"
                            r"|\b(in )?total\b|\bmax(imum)?\b", re.I)
# Stated day and time words are verifiable like keywords (they are the person's words, not a derivation).
_DAY_WORDS = {"mon": r"mon(day)?s?", "tue": r"tue(s|sday)?s?", "wed": r"wed(nesday)?s?", "thu": r"thu(rs|rsday)?s?",
              "fri": r"fri(day)?s?", "sat": r"sat(urday)?s?|weekends?", "sun": r"sun(day)?s?|weekends?"}
_TIME_WORDS = {"morning": r"mornings?", "afternoon": r"afternoons?", "evening": r"evenings?|nights?"}
_GUARDIAN_WORDS = re.compile(r"\b(parent|parents|mom|mother|dad|father|guardian|family|grand(ma|pa|parent))\b", re.I)
_ONE_TIME = re.compile(r"\b(one[- ]time|one[- ]off|once|single|one day|one afternoon|one morning)\b", re.I)
_ONGOING = re.compile(r"\b(ongoing|regular(ly)?|weekly|every week|monthly|long[- ]term|recurring)\b", re.I)
_ONLY = re.compile(r"\b(only|just|can'?t|cannot|can not|won'?t|no more than|not able to)\b", re.I)
_KEYWORDS = {  # boolean location/travel facts need a matching word in the person's own text
    "has_car": re.compile(r"\b(car|cars|drive|driving|driver|vehicle)\b", re.I),
    "wants_nearby": re.compile(r"\b(close|closer|near|nearby|walk|walking|local|around here|not far)\b", re.I),
    "nearby_towns_ok": re.compile(r"\b(nearby|other|neighbo(u)?ring|towns?|travel|anywhere|further|farther)\b", re.I),
    "prefers_not_to_share_zip": re.compile(r"\b(zip|zipcode|postal)\b", re.I),
}


@dataclass
class AgentDeps:
    dataset: Dataset
    base_profile: VolunteerProfile
    user_texts: list[str] = field(default_factory=list)
    profile: VolunteerProfile | None = None
    provenance: dict[str, str] = field(default_factory=dict)       # confirmed / from_message / suggested
    quotes: dict[str, str] = field(default_factory=dict)
    suggestions: dict[str, dict] = field(default_factory=dict)     # not used for eligibility decisions
    profile_changes: list[dict] = field(default_factory=list)
    assessed: dict[str, Assessment] = field(default_factory=dict)   # always computed with `profile`
    returned_ids: set[str] = field(default_factory=set)              # IDs any tool returned
    searches: list[dict] = field(default_factory=list)
    alternatives_called: bool = False
    declined: set[str] = field(default_factory=set)              # fields the person marked "not right"
    outside_scope_matches: list[dict] = field(default_factory=list)  # hard-filter matches outside the chosen scope
    current_message: str = ""                                    # the person's newest message (corrections must quote it)
    withdrawn: set[str] = field(default_factory=set)             # fields the person withdrew (this or an earlier turn)
    cleared: dict[str, str] = field(default_factory=dict)        # field -> the person's words withdrawing it (this turn)
    confirmed_overrides: set[str] = field(default_factory=set)   # form-confirmed fields changed by the person's words
    asked_follow_ups: list[str] = field(default_factory=list)    # questions already asked this session (not repeated)

    def __post_init__(self):
        if self.profile is None:
            self.profile = self.base_profile
            self.provenance = {f: "confirmed" for f in self.base_profile.model_fields_set}

    @property
    def broad_search_done(self) -> bool:
        """A search with no query and no town filter beyond the person's own explicit area limit."""
        return any((not s["only_in_town"] or s.get("restricted_by_profile")) and not s["query"] for s in self.searches)


def _norm(t: str) -> str:
    t = t.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", t).strip().lower()


def quote_supports(deps: AgentDeps, fld: str, value, quote: str | None) -> tuple[bool, str]:
    """Check a supporting quote against the person's own messages (verbatim) and the value."""
    if not quote or len(quote.strip()) < 2:
        return False, "no supporting text from your messages"
    nq = _norm(quote)
    if not any(nq in _norm(u) for u in deps.user_texts):
        return False, "the supporting text was not found in your messages"
    if fld in _NUMERIC:
        nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", nq)]
        if not isinstance(value, (int, float)) or float(value) not in nums:
            return False, "the number is not written in the supporting text"
        rng = HOURS_RANGE.search(nq)
        if rng and fld in ("available_hours", "available_hours_max", "max_session_hours"):
            lo, hi = float(rng.group(1)), float(rng.group(2))
            if fld == "available_hours" and float(value) != lo:
                return False, "a range was stated; keep its lower end here and the upper end in available_hours_max"
            if fld == "available_hours_max" and float(value) != hi:
                return False, "the upper end of the stated range differs"
            if fld == "max_session_hours" and not (_SESSION_WORDS.search(nq) and float(value) == hi):
                return False, "a range of hours doesn't say how long one visit is; ask instead of choosing a number"
    if fld == "available_hours_max" and not HOURS_RANGE.search(nq):
        return False, "no range of hours is written in the supporting text"
    if fld == "hours_period" and not (value in _PERIOD_WORDS and _PERIOD_WORDS[value].search(nq)):
        return False, f"no explicit 'per {value}' is written in the supporting text (a weekend day is not a period)"
    if fld == "available_days" and not (isinstance(value, list) and value and all(
            re.search(rf"\b({_DAY_WORDS.get(d, '$^')})\b", nq) for d in value)):
        return False, "the days are not written in the supporting text"
    if fld == "available_times" and not (isinstance(value, list) and value and all(
            re.search(rf"\b({_TIME_WORDS.get(t, '$^')})\b", nq) for t in value)):
        return False, "the times of day are not written in the supporting text"
    if fld == "guardian_available" and not _GUARDIAN_WORDS.search(nq):
        return False, "the supporting text does not mention a parent or guardian"
    if fld == "zip_code" and (not isinstance(value, str) or not re.search(rf"(?<!\d){re.escape(value)}(?!\d)", nq)):
        return False, "the ZIP code is not written in the supporting text"
    if fld in ("town", "volunteer_only_in") and (not isinstance(value, str) or _norm(value) not in nq):
        return False, f"'{value}' is not written in the supporting text"
    if fld in _KEYWORDS and not _KEYWORDS[fld].search(nq):
        return False, "the supporting text does not say this"
    if fld == "commitment_required":
        kind = _ONE_TIME if value == "one_time" else _ONGOING
        if not (kind.search(nq) and _ONLY.search(nq)):
            return False, "the supporting text does not say this is the only kind of commitment possible"
    return True, ""


def in_current_message(deps: AgentDeps, quote: str | None) -> bool:
    return bool(quote) and len(quote.strip()) >= 2 and _norm(quote) in _norm(deps.current_message)


# Fields that only make sense together are cleared together (hours without a period are meaningless).
_CLEAR_GROUPS = {"available_hours": ("available_hours", "hours_period"), "hours_period": ("available_hours", "hours_period")}


def withdraw_fields(deps: AgentDeps, fields: list[str], quotes: dict[str, str] | str | None) -> list[dict]:
    """Explicitly clear facts the person withdrew in their CURRENT message ("I can't commit weekly or for 12 months").

    The cleared field becomes unknown (never a guessed replacement such as 0 or another number). This also applies to
    form-confirmed answers, which are then reported in `confirmed_overrides` so the page drops them. Withdrawn fields
    stay withdrawn for the rest of the session unless the person states a new value in a later message."""
    events, changed = [], False
    data = deps.profile.model_dump()
    defaults = {f: info.get_default(call_default_factory=True) for f, info in VolunteerProfile.model_fields.items()}
    for f in fields:
        quote = quotes if isinstance(quotes, str) or quotes is None else quotes.get(f)
        if f not in VolunteerProfile.model_fields:
            events.append({"field": f, "applied": False, "status": "unknown_field"})
            continue
        if not in_current_message(deps, quote):
            events.append({"field": f, "applied": False, "status": "not_withdrawn",
                           "reason": "a withdrawal must quote the person's current message"})
            continue
        for g in _CLEAR_GROUPS.get(f, (f,)):
            deps.withdrawn.add(g)
            deps.cleared.setdefault(g, quote)
            deps.suggestions.pop(g, None)
            prev = deps.provenance.pop(g, None)
            deps.quotes.pop(g, None)
            if prev == "confirmed":
                deps.confirmed_overrides.add(g)
            if data.get(g) != defaults[g] or prev is not None:
                events.append({"field": g, "old": data.get(g), "new": None, "applied": True, "status": "cleared",
                               "supporting_text": quote, **({"was": "confirmed"} if prev == "confirmed" else {})})
                data[g] = defaults[g]
                changed = True
    if changed:
        deps.profile = VolunteerProfile.model_validate(data)
        for oid in list(deps.assessed):
            deps.assessed[oid] = assess(deps.dataset, deps.dataset.opportunities[oid], deps.profile)
    deps.profile_changes.extend(events)
    return events


_NEGATION = r"(?:can'?t|cannot|can not|won'?t|will not|unable to|not able to|no longer|don'?t want to|do not want to)"
_WEEKLY = re.compile(_NEGATION + r"(?:\s+[\w'-]+){0,6}?\s+(?:weekly|every week|each week|per week|a week|regular(?:ly)?|"
                     r"ongoing|recurring|monthly|every month|per month|a month)\b", re.I)
_MONTHS = re.compile(_NEGATION + r"(?:\s+[\w'-]+){0,8}?\s+(?:for\s+)?(?:\d+|a|one|six|twelve)[\s-]*(?:months?|years?)\b",
                     re.I)


def detect_withdrawals(message: str, profile: VolunteerProfile) -> list[tuple[list[str], str]]:
    """Conservative, deterministic withdrawals in the person's own words (the model may miss them):
    "I can't commit weekly" clears recurring hours; "I can't commit ... for 12 months" clears months.
    Only fields that currently hold a value are affected; nothing is replaced with a guess."""
    out = []
    m = _WEEKLY.search(message)
    if m and profile.available_hours is not None:
        word = m.group(0).lower()
        period = "month" if re.search(r"month", word) else "week" if re.search(r"week", word) else None
        if period is None or profile.hours_period in (None, period):
            out.append((["available_hours", "hours_period"], m.group(0)))
    m = _MONTHS.search(message)
    if m and profile.commitment_months is not None:
        out.append((["commitment_months"], m.group(0)))
    return out


def update_profile(deps: AgentDeps, supplied: VolunteerProfile | None, supporting_quotes: dict[str, str] | None = None,
                   corrected_fields: list[str] | None = None, inferred_fields: list[str] | None = None) -> list[dict]:
    """Merge chat-derived facts into the single run profile; recompute assessments if it changed."""
    if supplied is None:
        return []
    quotes, corrected, inferred = supporting_quotes or {}, set(corrected_fields or []), set(inferred_fields or [])
    # "Saturday or Sunday mornings" -> sat, sun, morning is reading the person's words, not a guess: if the words are
    # in the quote, it is verified even when the model listed the field as inferred.
    inferred -= {f for f in ("available_days", "available_times") if f in inferred
                 and quote_supports(deps, f, getattr(supplied, f), quotes.get(f))[0]}
    data = deps.profile.model_dump()
    events, changed = [], False
    for f in sorted(supplied.model_fields_set):
        new, prev = getattr(supplied, f), deps.provenance.get(f)
        quote = quotes.get(f)
        if new is None:  # an explicit null is not a statement; withdrawals use cleared_fields with a quote
            continue
        if f in deps.declined and prev != "confirmed":
            events.append({"field": f, "new": new, "applied": False, "status": "declined_by_person"})
            continue
        current = in_current_message(deps, quote)
        if f in deps.withdrawn and not current:
            # Withdrawn by the person; older messages in the history can never restore it.
            events.append({"field": f, "new": new, "applied": False, "status": "withdrawn_earlier",
                           "reason": "you withdrew this earlier; only a value from your newest message replaces it"})
            continue
        if prev == "confirmed" and new != data.get(f) and current and f in corrected and f not in inferred \
                and quote_supports(deps, f, new, quote)[0]:
            # The person corrected a form-confirmed answer in their newest message: their latest words win.
            events.append({"field": f, "old": data.get(f), "new": new, "applied": True, "status": "replaced_confirmed",
                           "supporting_text": quote})
            data[f], deps.provenance[f], deps.quotes[f] = new, "from_message", quote
            deps.confirmed_overrides.add(f)
            deps.suggestions.pop(f, None)
            deps.withdrawn.discard(f)
            changed = True
            continue
        if prev == "confirmed":
            if new != data.get(f):
                deps.suggestions[f] = {"value": new, "supporting_text": quote, "status": "conflicts_with_confirmed",
                                       "note": "differs from your confirmed answer; your confirmed answer is used"}
                events.append({"field": f, "new": new, "applied": False, "status": "conflicts_with_confirmed"})
            continue
        ok, why = (False, "derived by the assistant, not written by you") if f in inferred else \
            quote_supports(deps, f, new, quote)
        status = "from_message" if ok else "suggested"
        if f in VERIFIED_ONLY_FIELDS and status == "suggested" and f in _HOURS_FIELDS and quote and (
                HOURS_RANGE.search(_norm(quote)) or f == "hours_period"):
            # A misreading of a stated range, or a period that wasn't said: not used, and not offered back as a
            # "suggestion" either (the page asks what the hours mean instead).
            events.append({"field": f, "new": new, "applied": False, "status": "rejected", "reason": why})
            continue
        if f in VERIFIED_ONLY_FIELDS and status == "suggested":
            deps.suggestions[f] = {"value": new, "supporting_text": quote, "status": "suggested",
                                   "note": f"{why}; not used until you confirm it"}
            events.append({"field": f, "new": new, "applied": False, "status": "suggested", "reason": why})
            continue
        if new == data.get(f) and prev is not None:
            if prev == "suggested" and status == "from_message":
                deps.provenance[f], deps.quotes[f] = status, quote
            continue
        newer = current and not in_current_message(deps, deps.quotes.get(f))
        if prev in (None, "suggested") or (prev == "from_message" and status == "from_message" and (f in corrected or newer)):
            events.append({"field": f, "old": data.get(f) if prev else None, "new": new, "applied": True,
                           "status": status, **({"reason": why} if why else {})})
            data[f] = new
            deps.provenance[f] = status
            if quote:
                deps.quotes[f] = quote
            deps.suggestions.pop(f, None)
            deps.withdrawn.discard(f)
            changed = True
        else:
            deps.suggestions[f] = {"value": new, "supporting_text": quote, "status": "suggested",
                                   "note": "differs from what you said earlier; not applied unless you confirm it"}
            events.append({"field": f, "new": new, "applied": False, "status": "suggested",
                           "reason": "conflicts with an earlier answer from your messages"})
    if changed:
        deps.profile = VolunteerProfile.model_validate(data)
        for oid in list(deps.assessed):  # invalidate: recompute everything under the new profile
            deps.assessed[oid] = assess(deps.dataset, deps.dataset.opportunities[oid], deps.profile)
    deps.profile_changes.extend(events)
    return events


def profile_facts(deps: AgentDeps) -> list[dict]:
    """Every profile fact with its status, for the 'Your preferences' panel."""
    out = []
    for f, status in deps.provenance.items():
        v = getattr(deps.profile, f)
        if v is None or v == [] or (v is False and status != "from_message" and status != "confirmed"):
            continue  # unstated defaults aren't shown; a stated "no" (e.g. no car) is, so it is kept across turns
        out.append({"field": f, "value": getattr(deps.profile, f), "status": status,
                    "supporting_text": deps.quotes.get(f), "used_in_assessment": True,
                    "note": "Please confirm this answer." if status == "from_message" else
                            ("Assistant suggestion; please confirm." if status == "suggested" else None)})
    for f, sug in deps.suggestions.items():
        out.append({"field": f, "value": sug["value"], "status": sug["status"],
                    "supporting_text": sug.get("supporting_text"), "used_in_assessment": False, "note": sug["note"]})
    for f, quote in deps.cleared.items():  # removed at the person's request in this message
        if f not in deps.provenance:
            out.append({"field": f, "value": None, "status": "cleared", "supporting_text": quote,
                        "used_in_assessment": False, "note": "Removed because you withdrew it."})
    return out


def zip_status(deps: AgentDeps) -> dict:
    p = deps.profile
    if p.zip_code is None and p.prefers_not_to_share_zip:
        return {"status": "declined", "message": "The person chose not to share a ZIP code. Don't ask again."}
    return get_geo().check_zip(p.zip_code).public()


def location_context(deps: AgentDeps) -> dict:
    """The location facts the agent must respect, kept as separate fields. Never includes the ZIP digits."""
    p = deps.profile
    return {
        "lives_in_town": p.town,
        "zip_area": zip_status(deps),
        "has_car": p.has_car,
        "wants_nearby": p.wants_nearby,
        "nearby_towns_ok": p.nearby_towns_ok,
        "volunteer_only_in": p.volunteer_only_in,
        "rules": "Distances are straight-line estimates from the ZIP area, rendered on each option by the page. Never "
                 "write a distance, travel time, walkability or transit claim yourself.",
    }


def travel_info(deps: AgentDeps, opportunity_id: str) -> dict:
    """Compact location + distance for one record (no fit information)."""
    geo = get_geo()
    loc = geo.location_of(opportunity_id)
    o = deps.dataset.opportunities[opportunity_id]
    # kind: verified_site | organization_location | town_only | home_based | unknown (see backend/geo.py)
    out = {"location_kind": loc["kind"], "role_town": loc["role_town"] or "not published",
           "organization_town": deps.dataset.org(o).town}
    if deps.profile.volunteer_only_in:
        out["in_chosen_area"] = deps.dataset.confirmed_in_town(o, deps.profile.volunteer_only_in)
    zc = geo.check_zip(deps.profile.zip_code)
    if zc.status == "supported":
        d = geo.distance(opportunity_id, zc)
        if d["label"]:
            out["distance_shown_on_page"] = d["label"] + (f" ({d['secondary']})" if d["secondary"] else "")
    return out


def _compact_assessment(a: Assessment) -> dict:
    return {
        "opportunity_id": a.opportunity_id,
        "title": a.title,
        "organization_name": a.organization_name,
        "record_type_label": a.record_type_label,
        "overall_status": a.overall_status,
        "overall_summary": a.overall_summary,
        "requirements": [{"requirement": r.requirement, "published": r.published_requirement,
                          "applicability": r.applicability, "status": r.status, "explanation": r.explanation,
                          "source_ids": r.source_ids} for r in a.requirements],
        "application_status": a.application_status.label,
        "placement_or_shift_availability": a.placement_or_shift_availability,
        "costs": a.costs,
        "notes": a.notes[:6],
        "questions_for_organization": a.questions_for_organization[:4],
    }


def _current_statuses(deps: AgentDeps) -> dict:
    return {oid: a.overall_status for oid, a in deps.assessed.items()}


def _distance_key(deps: AgentDeps, oid: str) -> float:
    """Unrounded distance to the chosen destination (volunteering site, else the organization); none sorts last."""
    zc = get_geo().check_zip(deps.profile.zip_code)
    d = get_geo().distance(oid, zc)
    return d["sort_miles"] if d.get("sort_miles") is not None else float("inf")


async def search_opportunities(ctx: RunContext[AgentDeps], query: str | None = None,
                               only_in_town: str | None = None,
                               activities: list[ActivityTag] | None = None,
                               animals: list[str] | None = None,
                               include_wider_connecticut: bool = False,
                               include_other_ways_to_help: bool = False,
                               commitment: Literal["one_time", "recurring", "variable"] | None = None,
                               organization_id: str | None = None,
                               sort_by_closest: bool = False,
                               include_closed: bool = False) -> dict:
    """Search the volunteer dataset with the SAME rules as the Explore page (backend Dataset.search).

    Explicit filters are hard: results never relax them. Closed roles are left out.
    only_in_town: set ONLY when the person explicitly says they will volunteer only in that town (matches the
    role's own published town). A home town alone is not a restriction. The profile's volunteer_only_in limit
    is always applied.
    commitment: "one_time", "recurring" or "variable" keeps only records whose PUBLISHED commitment type is
    exactly that (unknown never matches). The profile's commitment_required is always applied. Never infer a
    commitment from words like event, fundraiser or project.
    query: optional substring of title, description or organization name. animals: dogs, cats, small_animals,
    or not_applicable for no animal contact. Greater New Haven only unless include_wider_connecticut is true
    (only when the person asked for it). include_other_ways_to_help adds interest-area-only records and
    independent support activities (labelled, never placements).
    include_closed: true ONLY when the person asks about a specific role or organization by name, to explain
    its status. A closed role is never a recommendation or alternative.
    sort_by_closest: with a supported ZIP, order by distance to the volunteering site, else the organization
    (records without a distance last). The page labels which one each distance measures.
    Returns `results` (the matches), `matches_outside_scope` (same filters in other Connecticut locations, when
    you did not include them: mention and offer to expand, never expand yourself) and, with a commitment
    filter, `commitment_unknown_leads` (same filters except commitment, commitment unknown or varies: only for
    ask_about_ids, clearly as needing confirmation).
    """
    deps = ctx.deps
    ds = deps.dataset
    limit = deps.profile.volunteer_only_in
    town = limit or only_in_town
    required = deps.profile.commitment_required
    commitment = required or commitment
    types = ["described_volunteer_role"] + (["interest_area_only", "independent_support_activity"]
                                            if include_other_ways_to_help else [])
    kw = dict(include_wider_connecticut=include_wider_connecticut, town=town, activities=activities, animals=animals,
              record_types=types, query=query, organization_id=organization_id, commitment_type=commitment)
    hits = ds.search(**kw, include_closed=include_closed)
    hidden_closed = 0 if include_closed else len(ds.search(**kw, include_closed=True)) - len(hits)
    if sort_by_closest:
        hits.sort(key=lambda o: _distance_key(deps, o.opportunity_id))
    hits.sort(key=lambda o: o.application_status == "explicitly_closed")  # stable: non-closed first
    total = len(hits)
    results = [{**ds.summary(o), "travel": travel_info(deps, o.opportunity_id)} for o in hits[:MAX_SEARCH_RESULTS]]
    deps.searches.append({"query": query, "only_in_town": town, "restricted_by_profile": bool(limit),
                          "activities": activities, "animals": animals, "wider": include_wider_connecticut,
                          "commitment": commitment, "count": total})
    deps.returned_ids.update(r["opportunity_id"] for r in results)
    out = {"count": total, "results": results,
           "scope": "greater_new_haven + wider_connecticut" if include_wider_connecticut else "greater_new_haven",
           "location_filter": town or "none (all towns in scope)",
           "commitment_filter": commitment or "none",
           "closed_matches_left_out": hidden_closed,
           "location_context": location_context(deps), "note": None, "broader_options": []}
    if not include_wider_connecticut:
        wider = [o for o in ds.search(**{**kw, "include_wider_connecticut": True}) if ds.scope_of(o) == "wider_connecticut"]
        out["matches_outside_scope"] = [{"opportunity_id": o.opportunity_id, "title": o.title,
                                         "organization_name": ds.org(o).name, "towns": ds.towns_of(o)} for o in wider[:3]]
        out["matches_outside_scope_count"] = len(wider)
        if wider and total == 0:
            deps.outside_scope_matches = out["matches_outside_scope"]
    if commitment:
        leads = [o for o in ds.search(**{**kw, "commitment_type": None}) if o.commitment_type in ("unknown", "variable")]
        out["commitment_unknown_leads"] = [{**ds.summary(o), "commitment_note": "commitment not published or varies: "
                                            "NOT a confirmed match"} for o in leads[:BROADER_OPTIONS]]
        deps.returned_ids.update(o.opportunity_id for o in leads[:BROADER_OPTIONS])
    if limit and only_in_town and only_in_town.strip().lower() != limit.lower():
        out["note"] = f"The person limited volunteering to {limit}; that limit was applied instead of {only_in_town}."
    if total == 0 and not commitment:
        broader = ds.search(include_wider_connecticut=include_wider_connecticut, animals=animals,
                            record_types=types, town=limit)[:BROADER_OPTIONS]
        out["broader_options"] = [{**ds.summary(o), "travel": travel_info(deps, o.opportunity_id)} for o in broader]
        deps.returned_ids.update(o.opportunity_id for o in broader)
        out["note"] = ("Nothing matches these filters. broader_options drops the query"
                       + (f" but keeps the person's limit to {limit}" if limit else " and town filter")
                       + " within the same scope. Assess them or call find_alternatives before saying nothing "
                         "suitable exists.")
    elif total == 0:
        out["note"] = (f"No record in this scope publishes a '{commitment}' commitment with these filters. Say so plainly. "
                       "commitment_unknown_leads may go only in ask_about_ids; matches_outside_scope may be offered "
                       "only as an option to expand the area.")
    elif total > len(results):
        out["note"] = f"{total} matched; showing the first {len(results)}. Narrow the filters to see others."
    return out


async def update_location_preferences(ctx: RunContext[AgentDeps], lives_in_town: str | None = None,
                                      zip_code: str | None = None,
                                      prefers_not_to_share_zip: bool | None = None,
                                      has_car: bool | None = None, wants_nearby: bool | None = None,
                                      nearby_towns_ok: bool | None = None, volunteer_only_in: str | None = None,
                                      supporting_quotes: dict[str, str] | None = None,
                                      corrected_fields: list[str] | None = None) -> dict:
    """Record where the person lives, how they travel and where they will volunteer. Call it whenever they
    mention any of these. Pass only what they said, with supporting_quotes[field] = their exact words
    (field names: town, zip_code, prefers_not_to_share_zip, has_car, wants_nearby, nearby_towns_ok,
    volunteer_only_in).

    lives_in_town: where they live ("I live in New Haven"). Not a limit on where they volunteer.
    zip_code: only five digits the person typed. Never infer a ZIP from a landmark, street or institution.
    has_car=false for "I don't have a car"; wants_nearby=true for "I need something close".
    nearby_towns_ok: their answer to "Do you need to stay within <town>, or can you travel to nearby towns?"
    volunteer_only_in: ONLY for an explicit limit ("I need to stay in New Haven").
    Returns the ZIP status (supported / invalid_format / not_in_dataset / outside_coverage) to explain.
    """
    deps = ctx.deps
    quotes = dict(supporting_quotes or {})
    if "lives_in_town" in quotes and "town" not in quotes:
        quotes["town"] = quotes.pop("lives_in_town")
    values = {"town": lives_in_town, "prefers_not_to_share_zip": prefers_not_to_share_zip, "has_car": has_car,
              "wants_nearby": wants_nearby, "nearby_towns_ok": nearby_towns_ok, "volunteer_only_in": volunteer_only_in}
    zip_problem = None
    if zip_code is not None:
        z = zip_code.strip()
        if ZIP_RE.fullmatch(z):
            values["zip_code"] = z
        else:
            zip_problem = get_geo().check_zip(z).public()  # invalid format: never stored
    supplied = {k: v for k, v in values.items() if v is not None}
    changes = []
    if supplied:
        changes = update_profile(deps, VolunteerProfile.model_validate(supplied), quotes, corrected_fields)
    return {"profile_changes": changes, "location_context": location_context(deps),
            **({"zip_input_problem": zip_problem} if zip_problem else {})}


async def get_opportunity_details(ctx: RunContext[AgentDeps], opportunity_id: str) -> dict:
    """Full requirements, applicability, evidence quotes, schedules, notes and source links for one record."""
    ds = ctx.deps.dataset
    o = ds.opportunities.get(opportunity_id)
    if o is None:
        return {"error": f"Unknown opportunity_id '{opportunity_id}'. Use IDs returned by search_opportunities."}
    ctx.deps.returned_ids.add(opportunity_id)
    rec = o.model_dump(exclude={"field_evidence", "source_ids"})
    return {
        **ds.summary(o),
        "record": rec,
        "evidence": [{"field": e.field, "source_id": e.source_id, "quote": e.evidence, "scope": e.scope,
                      **({"conflict": True} if e.conflict else {})} for e in o.field_evidence],
        "sources": [ds.source_ref(s) for s in o.source_ids],
    }


async def get_opportunity_details_compact(ctx: RunContext[AgentDeps], opportunity_id: str,
                                          include_evidence: bool = False) -> dict:
    """Record details for one opportunity: description, location, schedules, orientation, past notices,
    training, fees, other requirements, notes, application link and source links.

    assess_profile already returns each requirement's published wording, applicability (including
    conflicts), explanation, source IDs and questions for the organization, so it is not repeated here.
    Set include_evidence=true only when you need the exact quoted wording from the sources.
    """
    ds = ctx.deps.dataset
    o = ds.opportunities.get(opportunity_id)
    if o is None:
        return {"error": f"Unknown opportunity_id '{opportunity_id}'. Use IDs returned by search_opportunities."}
    ctx.deps.returned_ids.add(opportunity_id)
    rec = o.model_dump(exclude={"field_evidence", "source_ids", "requirement_applicability", "unresolved_questions",
                                "opportunity_id", "organization_id", "activity_tags", "animal_tags",
                                "record_type", "application_status"})
    out = {"opportunity_id": o.opportunity_id, "title": o.title, "organization_name": ds.org(o).name,
           "towns": ds.towns_of(o), "application_status_label": ds.summary(o)["application_status_label"],
           "record": rec, "sources": [ds.source_ref(s) for s in o.source_ids]}
    if include_evidence:
        out["evidence"] = [{"field": e.field, "source_id": e.source_id, "quote": e.evidence,
                            **({"conflict": True} if e.conflict else {})} for e in o.field_evidence]
    return out


async def assess_profile(ctx: RunContext[AgentDeps], opportunity_ids: list[str], profile: VolunteerProfile,
                         supporting_quotes: dict[str, str] | None = None,
                         corrected_fields: list[str] | None = None,
                         inferred_fields: list[str] | None = None,
                         cleared_fields: list[str] | None = None) -> dict:
    """Deterministically assess the person against up to 4 opportunities. Call this before any fit claim.

    profile: only facts the person gave (leave unknown fields out; never guess).
    supporting_quotes: for EVERY field you pass, the exact words from the person's message that state it
    (copied verbatim, e.g. {"age": "I'm 26"}). Facts without a verifiable quote stay unconfirmed
    suggestions; eligibility fields (age, guardian, hours, hours period, commitment months, session length)
    are then not used until the person confirms them, so ask a follow-up question.
    inferred_fields: fields you derived (e.g. days from "weekday afternoons"); kept as suggestions.
    corrected_fields: fields the person explicitly corrected in their own words ("actually I'm 17").
    cleared_fields: fields the person WITHDREW without giving a new value ("I can't commit weekly or for 12
    months" -> available_hours, hours_period, commitment_months), each with supporting_quotes[field] copied from
    their CURRENT message. Cleared fields become unknown; never invent a replacement value.
    Answers confirmed in the form win, except when the person corrects or withdraws them in their current message
    (list the field in corrected_fields or cleared_fields). Earlier assessments are recomputed when the profile
    changes. Use the `current_statuses` returned here as the only valid fit labels.
    """
    deps = ctx.deps
    changes = withdraw_fields(deps, list(cleared_fields or []), supporting_quotes or {}) if cleared_fields else []
    changes += update_profile(deps, profile, supporting_quotes, corrected_fields, inferred_fields)
    out, errors = [], []
    for oid in opportunity_ids[:MAX_ASSESS_PER_CALL]:
        o = deps.dataset.opportunities.get(oid)
        if o is None:
            errors.append(f"Unknown opportunity_id '{oid}'")
            continue
        deps.assessed[oid] = assess(deps.dataset, o, deps.profile)
        deps.returned_ids.add(oid)
        out.append(_compact_assessment(deps.assessed[oid]))
    if len(opportunity_ids) > MAX_ASSESS_PER_CALL:
        errors.append(f"Only the first {MAX_ASSESS_PER_CALL} IDs were assessed.")
    return {"profile_used": deps.profile.model_dump(exclude_defaults=True, exclude={"zip_code"}),
            "profile_changes": changes,
            "unconfirmed_not_used": {f: s["value"] for f, s in deps.suggestions.items()},
            "withdrawn_fields": sorted(deps.withdrawn),
            "assessments": out, "current_statuses": _current_statuses(deps),
            "travel_separate_from_fit": {a["opportunity_id"]: travel_info(deps, a["opportunity_id"]) for a in out},
            "errors": errors}


async def find_alternatives_tool(ctx: RunContext[AgentDeps], profile: VolunteerProfile | None = None,
                                 activities: list[ActivityTag] | None = None,
                                 exclude_opportunity_id: str | None = None,
                                 supporting_quotes: dict[str, str] | None = None,
                                 corrected_fields: list[str] | None = None,
                                 inferred_fields: list[str] | None = None) -> dict:
    """Other ways to help that are not a definite mismatch and not explicitly closed (any record type, labelled).

    Every returned alternative is assessed under the current profile and may be offered as a suitable option.
    """
    deps = ctx.deps
    ds = deps.dataset
    changes = update_profile(deps, profile, supporting_quotes, corrected_fields, inferred_fields)
    deps.alternatives_called = True
    limit = deps.profile.volunteer_only_in
    alts = find_alternatives(ds, deps.profile, exclude_id=exclude_opportunity_id, activities=activities,
                             limit=64 if (limit or deps.profile.commitment_required) else 5)
    required = deps.profile.commitment_required
    relaxed = []
    if required:  # a hard commitment constraint is never relaxed silently
        relaxed = [a for a in alts if ds.opportunities[a["opportunity_id"]].commitment_type in ("unknown", "variable")][:3]
        alts = [a for a in alts if ds.opportunities[a["opportunity_id"]].commitment_type == required]
        if not limit:
            alts = alts[:5]
    outside = []
    if limit:
        inside = [a for a in alts if ds.confirmed_in_town(ds.opportunities[a["opportunity_id"]], limit)]
        outside = [a for a in alts if a not in inside][:3]
        alts = inside[:5]
    for a in alts + outside:
        a["travel"] = travel_info(deps, a["opportunity_id"])
        deps.returned_ids.add(a["opportunity_id"])
        deps.assessed[a["opportunity_id"]] = assess(ds, ds.opportunities[a["opportunity_id"]], deps.profile)
    note = None if alts else "No alternatives found in this scope."
    if limit:
        note = ((f"No suitable alternative is confirmed in {limit}. " if not alts else "")
                + f"outside_area_candidates are outside {limit} or their own location isn't published as {limit}: "
                  "offer them only as "
                  "outside_area_ids, asking whether the person wants to widen the area.")
    for a in relaxed:
        a["commitment_note"] = "commitment not published or varies: NOT a confirmed match; only for ask_about_ids"
        deps.returned_ids.add(a["opportunity_id"])
        deps.assessed[a["opportunity_id"]] = assess(ds, ds.opportunities[a["opportunity_id"]], deps.profile)
    if required:
        note = (note or "") + (f" Only records with a published '{required}' commitment are alternatives; "
                               "commitment_unknown_leads need confirmation.")
    return {"profile_used": deps.profile.model_dump(exclude_defaults=True, exclude={"zip_code"}),
            "profile_changes": changes, "alternatives": alts,
            **({"commitment_unknown_leads": relaxed} if required else {}),
            **({"outside_area_candidates": outside} if limit else {}),
            "current_statuses": _current_statuses(deps), "note": note}


async def get_application_checklist(ctx: RunContext[AgentDeps], opportunity_id: str) -> dict:
    """Application steps taken only from the dataset. Applications happen on the organization's own site."""
    ds = ctx.deps.dataset
    o = ds.opportunities.get(opportunity_id)
    if o is None:
        return {"error": f"Unknown opportunity_id '{opportunity_id}'."}
    ctx.deps.returned_ids.add(opportunity_id)
    return {"opportunity_id": opportunity_id, "steps": checklist(ds, o)}
