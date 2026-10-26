"""Deterministic assessment of a volunteer profile against one opportunity.

Rules (documented in README "Matching rules"):
- Each requirement is `met`, `not_met` or `needs_confirmation`.
- `not_met` is only possible when the requirement's applicability is `published_applicable`, with one
  exception: a CONFLICTING minimum age where every published version is above the person's age (for example
  15 against 18 and 21). Every version excludes them, so the role is not offered, but the conflict is not
  treated as resolved: both versions and their evidence stay, and the person is told to confirm the current
  rule. Meeting some versions but not others (19 against 18 and 21) stays `needs_confirmation`. A guardian
  never overrides an age rule. Otherwise uncertain or conflicting requirements never exclude anyone.
- `met` is only possible for `published_applicable` rules. When a rule's current applicability is uncertain,
  stale or conflicting, the result is `needs_confirmation` even if the person's answer matches every published
  value; `listed_value_matched=True` records that separate numerical comparison.
- Evidence shown for a result is the smallest useful set: exact repeats, and excerpts contained in a longer
  passage from the same source, are dropped (the dataset itself is unchanged).
- A missing profile answer gives `needs_confirmation`, never a failure.
- A requirement the dataset does not publish is not treated as satisfied. It is
  listed in the notes as "not published", and the overall result only ever says
  "meets the published requirements we checked".
- One-time activities never get recurring hours or month minimums.
- Orientation info and dated notices are informational. They are never treated
  as availability or upcoming events.
- Application status, and whether a specific placement or shift exists, are
  reported separately from fit.

Hours conversion (only used when the profile and the requirement use different periods):
  We assume "P hours per week" means about P hours every week. A calendar month
  has between 4 weeks (28 days) and 31/7 ≈ 4.43 weeks.
  * Requirement R per month, profile P per week:
      met if 4·P ≥ R (even the shortest month gives at least 4·P);
      not_met if (31/7)·P < R (even the longest month can't reach R);
      otherwise needs_confirmation.
  * Requirement R per week, profile P per month:
      not_met if P < 4·R (any month needs at least 4·R to give R every week);
      otherwise needs_confirmation (we don't know how the monthly hours are spread).
"""
from __future__ import annotations

import re

from .data import APPLICATION_STATUS_LABELS, RECORD_TYPE_LABELS, Dataset
from .schemas import (ApplicationStatusInfo, Assessment, EvidenceRef, Opportunity, RequirementAssessment,
                      VolunteerProfile)

WEEKS_PER_MONTH_MIN = 4.0
WEEKS_PER_MONTH_MAX = 31 / 7
ADULT_AGE = 18
MAX_QUESTIONS = 6

_AGE_RE = re.compile(r"(over\s+)?(\d{1,2})\s*(?=\+|\s*years|\s*or older)", re.IGNORECASE)


# ---------------------------------------------------------------- helpers
def _evidence(opp: Opportunity, *fields: str) -> list[EvidenceRef]:
    return [EvidenceRef(source_id=e.source_id, quote=e.evidence) for e in opp.field_evidence if e.field in fields]


def _norm_quote(q: str) -> str:
    q = q.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", re.sub(r"^[\s*•\-\u2013\u2014\"']+|[\s\"'.;,:]+$", "", q)).strip().lower()


def dedupe_evidence(items: list[EvidenceRef]) -> list[EvidenceRef]:
    """Smallest useful set of passages: drops exact repeats and any excerpt contained in a longer passage from the
    SAME source. Passages from different sources (including conflicting ones) are always kept. Order is preserved."""
    norm = [_norm_quote(e.quote) for e in items]
    keep = []
    for i, e in enumerate(items):
        redundant = any(
            j != i and items[j].source_id == e.source_id and norm[i] in norm[j]
            and (len(norm[j]) > len(norm[i]) or j < i)          # contained in a longer one, or an earlier exact repeat
            for j in range(len(items)))
        if not redundant:
            keep.append(e)
    return keep


def _applicability(opp: Opportunity, field: str):
    a = opp.requirement_applicability.get(field)
    return (a.status, list(a.source_ids), a.reason) if a else ("not_published", [], "")


def _fmt_hours(h: float, period: str) -> str:
    return f"{h:g} hours per {period}"


def _claimed_age_thresholds(opp: Opportunity, strict: bool = True) -> list[int]:
    """Age thresholds stated in minimum_age evidence. strict: "over 18" is read as 19 (used to decide that someone
    meets EVERY version); lenient: read as 18 (used to decide that EVERY version is above someone's age)."""
    out = []
    for e in opp.field_evidence:
        if e.field != "minimum_age":
            continue
        for over, num in _AGE_RE.findall(e.evidence):
            out.append(int(num) + (1 if over and strict else 0))
    return out


class _Builder:
    def __init__(self, opp: Opportunity, flags: dict[str, list[str]] | None = None):
        self.opp = opp
        self.flags = flags or {}  # source_id -> reliability flags, for short uncertainty notes
        self.items: list[RequirementAssessment] = []
        self.notes: list[str] = []
        self.questions: list[str] = []

    def add(self, requirement: str, published: str, applicability: str, status: str, used: dict,
            explanation: str, source_ids: list[str], evidence: list[EvidenceRef], below_all_versions: bool = False) -> None:
        if status == "not_met" and applicability != "published_applicable" and not (
                below_all_versions and requirement == "minimum_age" and applicability == "conflicting"):
            raise AssertionError("not_met is only allowed for published_applicable requirements (or a conflicting "
                                 "minimum age whose every version is above the person's age)")
        matched = None
        if status == "met" and applicability != "published_applicable":
            # The person's answer matches the listed value, but the rule itself may be outdated or conflicting:
            # amber, never green. The comparison is kept separately.
            status, matched = "needs_confirmation", True
        sids = list(dict.fromkeys(source_ids + [e.source_id for e in evidence]))
        self.items.append(RequirementAssessment(
            opportunity_id=self.opp.opportunity_id, requirement=requirement, published_requirement=published,
            applicability=applicability, status=status, profile_fields_used=used, explanation=explanation,
            source_ids=sids, evidence=dedupe_evidence(evidence), uncertainty_note=self._note(applicability, sids),
            listed_value_matched=matched))

    def _note(self, applicability: str, sids: list[str]) -> str | None:
        """One short line to show beside the fact; the full reason stays in the record."""
        if applicability == "conflicting":
            return "Sources disagree; confirm with the organization."
        if applicability != "needs_confirmation":
            return None
        if any("possibly_superseded" in self.flags.get(s, []) for s in sids):
            return "Listed on an older application form; needs confirmation."
        return "Current applicability unclear; needs confirmation."


# ---------------------------------------------------------------- individual rules
def _age(b: _Builder, p: VolunteerProfile) -> None:
    o = b.opp
    app, sids, reason = _applicability(o, "minimum_age")
    ev = _evidence(o, "minimum_age")
    used = {"age": p.age}
    if o.minimum_age is None and app == "not_published":
        if p.age is not None and p.age < ADULT_AGE:
            b.add("minimum_age", "No minimum age published", "not_published", "needs_confirmation", used,
                  f"The organization does not publish a minimum age for this {o.record_type.replace('_', ' ')}. "
                  "Because you are under 18, ask whether minors can take part and under what conditions.",
                  [], [])
        else:
            b.notes.append("No minimum age is published for this record (not the same as 'no age limit').")
        return
    if app == "published_applicable":
        req = o.minimum_age
        published = "All ages welcome" if req == 0 else f"Minimum age {req}"
        if p.age is None:
            b.add("minimum_age", published, app, "needs_confirmation", used,
                  f"The published minimum age is {req}. Your age is needed to check this.", sids, ev)
        elif p.age >= req:
            b.add("minimum_age", published, app, "met", used,
                  f"You are {p.age}; the published minimum is {req}." if req else "The organization says all ages are welcome.",
                  sids, ev)
        else:
            b.add("minimum_age", published, app, "not_met", used,
                  f"The published minimum age is {req} and you are {p.age}.", sids, ev)
        return
    # needs_confirmation or conflicting: never exclude
    thresholds = _claimed_age_thresholds(o)
    strict = max(thresholds) if thresholds else None
    lenient_all = sorted(set(_claimed_age_thresholds(o, strict=False)))
    label = "conflicting published ages" if app == "conflicting" else "age rule that needs confirmation"
    published = (f"Published versions: {', '.join(str(t) for t in sorted(set(thresholds)))}+ ({label})"
                 if thresholds else f"Unclear age rule ({label})")
    if app == "conflicting" and len(lenient_all) >= 2:
        # Plain wording; the conflicting values and their sources stay in the evidence details.
        published = f"{' or '.join(f'{t}+' for t in lenient_all)} (published minimums differ)"
        both = "both" if len(lenient_all) == 2 else "all"
        if p.age is None:
            b.add("minimum_age", published, app, "needs_confirmation", used,
                  f"The published minimums differ ({' and '.join(f'{t}+' for t in lenient_all)}). Your age is needed; "
                  "confirm the organization's current rule.", sids, ev)
        elif p.age >= max(lenient_all) and (strict is None or p.age >= strict):
            b.add("minimum_age", published, app, "met", used,
                  f"Your age meets {both} published minimums; confirm the organization's current rule.", sids, ev)
        elif p.age < lenient_all[0]:
            which = "Both published age requirements are" if both == "both" else "All published age requirements are"
            b.add("minimum_age", published, app, "not_met", used,
                  f"{which} above your age; confirm the current rule with the organization.", sids, ev,
                  below_all_versions=True)
        else:
            met = [t for t in lenient_all if p.age >= t]
            unmet = [t for t in lenient_all if p.age < t]
            b.add("minimum_age", published, app, "needs_confirmation", used,
                  f"Your age meets {'one published minimum' if len(met) == 1 else 'some published minimums'} "
                  f"({', '.join(f'{t}+' for t in met)}) but not {'the other' if len(unmet) == 1 else 'others'} "
                  f"({', '.join(f'{t}+' for t in unmet)}); confirm the organization's current rule.", sids, ev)
        return
    if p.age is None:
        b.add("minimum_age", published, app, "needs_confirmation", used,
              f"{reason} Your age is needed, and the organization should confirm which rule applies.", sids, ev)
    elif strict is not None and p.age >= strict:
        b.add("minimum_age", published, app, "met", used,
              f"You are {p.age}, which meets even the strictest published version ({strict}). {reason}", sids, ev)
    elif app == "conflicting" and (lenient := sorted(set(_claimed_age_thresholds(o, strict=False)))) \
            and p.age < lenient[0]:
        # Every published version is above the person's age: not offered, but the conflict stays unresolved.
        which = ("Both published age requirements are" if len(lenient) == 2
                 else "All published age requirements are" if len(lenient) > 2 else "The published age requirement is")
        b.add("minimum_age", published, app, "not_met", used,
              f"{which} above your age; confirm the current rule with the organization. (You are {p.age}; the "
              f"conflicting published versions are {' and '.join(f'{t}+' for t in lenient)}, and the conflict is not "
              "resolved.)", sids, ev, below_all_versions=True)
    else:
        b.add("minimum_age", published, app, "needs_confirmation", used,
              f"You are {p.age}. {reason} This is not treated as a rejection; ask the organization which age rule applies.",
              sids, ev)


def _guardian(b: _Builder, p: VolunteerProfile, age_not_met: bool) -> None:
    o, g = b.opp, b.opp.guardian_requirement
    used = {"age": p.age, "guardian_available": p.guardian_available}
    if g is None:
        if p.age is not None and p.age < ADULT_AGE and not age_not_met:
            b.add("guardian_requirement", "No guardian rule published", "not_published", "needs_confirmation", used,
                  "The organization does not publish a parent/guardian rule for this record. That does not mean a "
                  "guardian is not required. Ask before applying.", [], [])
        return
    app, sids, _ = _applicability(o, "guardian_requirement")
    ev = _evidence(o, "guardian_requirement")
    published = g.details
    applies = g.applies_under_age
    if applies is not None:
        if p.age is None:
            b.add("guardian_requirement", published, app, "needs_confirmation", used,
                  f"A guardian is required under age {applies}. Your age is needed to check this.", sids, ev)
            return
        if p.age >= applies:
            b.add("guardian_requirement", published, app, "met", used,
                  f"The guardian rule applies under age {applies}; you are {p.age}.", sids, ev)
            return
    if p.guardian_available is True:
        status, why = "met", "You said a parent or guardian can take part as required."
    elif p.guardian_available is False:
        status = "not_met" if app == "published_applicable" else "needs_confirmation"
        why = "The organization requires a parent or guardian, and you said one is not available."
    else:
        status, why = "needs_confirmation", "A parent or guardian is required. Can one attend with you? (not answered yet)"
    b.add("guardian_requirement", published, app, status, used, f"{why} Published rule: {published}", sids, ev)


def _compare_hours(req: float, req_period: str, have: float, have_period: str) -> tuple[str, str]:
    """Return (raw_status, explanation) where raw_status is met / unmet / unclear."""
    if req_period == have_period:
        return ("met" if have >= req else "unmet",
                f"You have {_fmt_hours(have, have_period)}; the published minimum is {_fmt_hours(req, req_period)}.")
    if req_period == "month":  # profile weekly
        low, high = have * WEEKS_PER_MONTH_MIN, have * WEEKS_PER_MONTH_MAX
        if low >= req:
            return "met", (f"{_fmt_hours(have, 'week')} is at least {low:g} hours in any month (4-week lower bound), "
                           f"which meets the published {_fmt_hours(req, 'month')}.")
        if high < req:
            return "unmet", (f"{_fmt_hours(have, 'week')} is at most about {high:.1f} hours in a month, "
                             f"below the published {_fmt_hours(req, 'month')}.")
        return "unclear", (f"{_fmt_hours(have, 'week')} gives {low:g}–{high:.1f} hours a month depending on the "
                           f"month; the published minimum is {_fmt_hours(req, 'month')}.")
    # requirement weekly, profile monthly
    if have < req * WEEKS_PER_MONTH_MIN:
        return "unmet", (f"{_fmt_hours(have, 'month')} cannot cover {_fmt_hours(req, 'week')} every week "
                         f"(that needs at least {req * WEEKS_PER_MONTH_MIN:g} hours a month).")
    return "unclear", (f"{_fmt_hours(have, 'month')} could cover {_fmt_hours(req, 'week')} only if spread "
                       "across every week; confirm your weekly availability.")


def _hours(b: _Builder, p: VolunteerProfile) -> None:
    o = b.opp
    if o.commitment_type == "one_time":
        return  # one-time activities never inherit recurring hours
    if o.minimum_hours is None or o.hours_period is None:
        if o.commitment_type in ("unknown", "variable"):
            b.notes.append("No minimum hours are published (not the same as 'no minimum').")
        return
    app, sids, reason = _applicability(o, "minimum_hours")
    ev = _evidence(o, "minimum_hours", "hours_period")
    published = _fmt_hours(o.minimum_hours, o.hours_period)
    used = {"available_hours": p.available_hours, "hours_period": p.hours_period,
            **({"available_hours_max": p.available_hours_max} if p.available_hours_max is not None else {})}
    if p.available_hours is None or p.hours_period is None:
        b.add("minimum_hours", published, app, "needs_confirmation", used,
              f"The published minimum is {published}. Tell us your available hours and whether that is per week or per month.",
              sids, ev)
        return
    raw, why = _compare_hours(o.minimum_hours, o.hours_period, p.available_hours, p.hours_period)
    if p.available_hours_max is not None:  # a stated range: decided only when both ends agree
        raw_hi, _ = _compare_hours(o.minimum_hours, o.hours_period, p.available_hours_max, p.hours_period)
        stated = f"You said {p.available_hours:g}–{p.available_hours_max:g} hours per {p.hours_period}"
        if raw == raw_hi == "met":
            why = f"{stated}; even the lower end meets the published minimum of {published}."
        elif raw == raw_hi == "unmet":
            why = f"{stated}; even the upper end is below the published minimum of {published}."
        else:
            raw, why = "unclear", f"{stated}; part of that range meets the published minimum of {published}, so confirm."

    if raw == "met":
        status = "met"
    elif raw == "unmet" and app == "published_applicable":
        status = "not_met"
    else:
        status = "needs_confirmation"
    if app != "published_applicable":
        why += f" {reason}"
    b.add("minimum_hours", published, app, status, used, why, sids, ev)


def _months(b: _Builder, p: VolunteerProfile) -> None:
    o = b.opp
    if o.commitment_type == "one_time":
        for tc in o.time_commitment or []:
            b.notes.append(f"One-time activity: \"{tc.published_text}\". No recurring hours or minimum months apply.")
        return
    if o.minimum_commitment_months is None:
        typical = [tc for tc in (o.time_commitment or []) if tc.duration_is_typical_not_minimum]
        for tc in typical:
            if p.commitment_months is not None and tc.duration_months_min and p.commitment_months < tc.duration_months_min:
                b.add("time_commitment", tc.published_text, _applicability(o, "time_commitment")[0], "needs_confirmation",
                      {"commitment_months": p.commitment_months},
                      f"The typical commitment is {tc.duration_months_min:g}–{tc.duration_months_max:g} months (not a stated "
                      f"minimum); you said {p.commitment_months:g}. Ask whether a shorter commitment works.",
                      [tc.source_id], _evidence(o, "time_commitment"))
        if o.commitment_type == "variable":
            for tc in o.time_commitment or []:
                b.notes.append(f"Commitment varies: \"{tc.published_text}\"")
        elif not typical:
            b.notes.append("No minimum commitment length is published (not the same as 'no minimum').")
        return
    app, sids, reason = _applicability(o, "minimum_commitment_months")
    ev = _evidence(o, "minimum_commitment_months")
    need = o.minimum_commitment_months
    published = f"Minimum commitment of {need:g} months"
    used = {"commitment_months": p.commitment_months}
    if p.commitment_months is None:
        b.add("minimum_commitment_months", published, app, "needs_confirmation", used,
              f"{published} is published. How many months can you commit?", sids, ev)
    elif p.commitment_months >= need:
        b.add("minimum_commitment_months", published, app, "met", used,
              f"You can commit {p.commitment_months:g} months; the published minimum is {need:g}."
              + (f" {reason}" if app != "published_applicable" else ""), sids, ev)
    else:
        status = "not_met" if app == "published_applicable" else "needs_confirmation"
        b.add("minimum_commitment_months", published, app, status, used,
              f"You can commit {p.commitment_months:g} months; the published minimum is {need:g}."
              + (f" {reason}" if app != "published_applicable" else ""), sids, ev)


def _sessions(b: _Builder, p: VolunteerProfile) -> None:
    """Published single-session lengths (e.g. "3-4 hours, one time") vs. the longest block the person can attend.

    Weekly/monthly availability never answers this. A published range is not turned into a
    minimum of its maximum: meeting the top of the range is `met`; falling below the bottom is
    `not_met` (only if applicable); anything in between needs confirmation.
    """
    o = b.opp
    app, sids, reason = _applicability(o, "time_commitment")
    for tc in o.time_commitment or []:
        if tc.hours_per != "session":
            continue
        lo, hi = tc.hours_min, tc.hours_max
        rng = (f"{lo:g}–{hi:g} hours" if lo is not None and hi is not None and lo != hi
               else f"{(lo if lo is not None else hi):g} hours")
        published = f"One session of {rng} (\"{tc.published_text}\")"
        used = {"max_session_hours": p.max_session_hours}
        ev = [EvidenceRef(source_id=tc.source_id, quote=tc.published_text)]
        have = p.max_session_hours
        if have is None:
            status, why = "needs_confirmation", (f"This is a single session of {rng}. Can you attend one continuous "
                                                 "block of that length? Weekly or monthly availability doesn't answer this.")
        elif hi is not None and have >= hi:
            status, why = "met", f"You can attend up to {have:g} hours in one session; the session is {rng}."
        elif lo is not None and have < lo:
            status = "not_met" if app == "published_applicable" else "needs_confirmation"
            why = f"You can attend up to {have:g} hours in one session; the published session is {rng}."
        else:
            status, why = "needs_confirmation", (f"You can attend up to {have:g} hours; the session is {rng}. Ask "
                                                 "whether a shorter stay works.")
        if app != "published_applicable" and reason:
            why += f" {reason}"
        b.add("session_length", published, app, status, used, why, [tc.source_id], ev)


def _schedule(b: _Builder, p: VolunteerProfile) -> None:
    o = b.opp
    for item in o.recurring_schedule or []:
        app, sids, reason = _applicability(o, "recurring_schedule")
        used = {"available_days": p.available_days, "available_times": p.available_times}
        stated = ", ".join(p.available_days + p.available_times) or "not given"
        b.add("recurring_schedule", item.summary, app, "needs_confirmation", used,
              f"Published schedule: \"{item.original_text}\". Your stated availability: {stated}. Schedules are "
              "free text in the sources, so the app does not auto-judge them. Check this against your availability."
              + (f" {reason}" if app != "published_applicable" else ""),
              [item.source_id], [EvidenceRef(source_id=item.source_id, quote=item.original_text)])
    if not o.recurring_schedule and (p.available_days or p.available_times) \
            and o.record_type != "independent_support_activity" and "fostering" not in o.activity_tags:
        # The person's days/times are used even when the role publishes none: shown as a question, never as a fit.
        days = {"mon": "Monday", "tue": "Tuesday", "wed": "Wednesday", "thu": "Thursday", "fri": "Friday",
                "sat": "Saturday", "sun": "Sunday"}
        stated = " or ".join(days.get(d, d) for d in p.available_days) or "your days"
        if p.available_times:
            stated += " " + " or ".join(t + "s" for t in p.available_times)
        b.add("recurring_schedule", "No days or times published", "not_published", "needs_confirmation",
              {"available_days": p.available_days, "available_times": p.available_times},
              f"No days or times are published for this role. Ask whether {stated} are possible.", [], [])
    for item in o.orientation_info or []:
        b.notes.append(f"Orientation (process, not a scheduled date): {item.summary}")
    for n in o.dated_notices or []:
        b.notes.append(f"Past notice, not an upcoming date (year not stated): \"{n.original_text}\"")


def _other(b: _Builder, p: VolunteerProfile) -> None:
    o = b.opp
    app, sids, reason = _applicability(o, "other_requirements")
    for req in o.other_requirements or []:
        ev = [EvidenceRef(source_id=e.source_id, quote=e.evidence) for e in o.field_evidence
              if e.field == "other_requirements" and e.source_id == req.source_id]
        if req.requirement.startswith("Live in one of:"):
            towns = [t.strip().lower() for t in req.requirement.split(":", 1)[1].split("(")[0].split(",")]
            used = {"town": p.town}
            if p.town and p.town.strip().lower() in towns:
                b.add("other_requirements", req.requirement, app, "met", used, f"You live in {p.town}, a listed town.",
                      [req.source_id], ev[:1])
            else:
                b.add("other_requirements", req.requirement, app, "needs_confirmation", used,
                      ("Your town is not given." if not p.town else f"{p.town} is not in the listed towns.")
                      + " The organization says out-of-area placement is considered for special-needs cats, so ask.",
                      [req.source_id], ev[:1])
            continue
        b.add("other_requirements", req.requirement, app, "needs_confirmation", {},
              "Self-check: the app does not ask about this. Confirm you can meet it.", [req.source_id], ev[:1])


def _costs(o: Opportunity, p: VolunteerProfile) -> list[str]:
    out = []
    for f in o.fees or []:
        base = f"{f.amount:g} {f.currency} fee"
        cond = f.applies_when
        if "not a Branford resident" in cond and p.town:
            if p.town.strip().lower() == "branford":
                out.append(f"{base} applies to non-Branford residents. You said Branford, so it should not apply. [{f.source_id}]")
                continue
            out.append(f"{base} applies because you said {p.town} (not Branford)." + (f" {f.payment_terms}" if f.payment_terms else "")
                       + f" [{f.source_id}]")
            continue
        out.append(f"{base} when: {cond}." + (f" {f.payment_terms}" if f.payment_terms else "") + f" [{f.source_id}]")
    if o.fees is None:
        out.append("No fee information is published (not the same as free).")
    return out


def _application_status(ds: Dataset, o: Opportunity) -> ApplicationStatusInfo:
    ev = _evidence(o, "application_status")
    if o.application_status == "explicitly_accepting_applications":
        why = "The source says it is accepting applications for this. That does not guarantee placement or a shift."
    elif o.application_status == "explicitly_closed":
        why = "The source says applications for this category are closed."
    else:
        why = ("No source explicitly says applications are open or closed. A description or an application link "
               "does not prove there is an opening.")
    return ApplicationStatusInfo(status=o.application_status, label=APPLICATION_STATUS_LABELS[o.application_status],
                                 explanation=why + (f" Evidence: \"{ev[0].quote}\"" if ev else ""),
                                 source_ids=list(dict.fromkeys(e.source_id for e in ev)))


def _placement(o: Opportunity) -> str:
    listed = [s.original_text for s in (o.recurring_schedule or []) if "open shift" in s.original_text.lower()]
    if listed:
        return (f"The role page lists \"{listed[0]}\". Listed shifts can change and are not a booking. Confirm with the "
                "organization.")
    return "Not published: no source lists specific open placements or shifts. Confirm with the organization."


# ---------------------------------------------------------------- public API
def assess(ds: Dataset, opp: Opportunity, profile: VolunteerProfile) -> Assessment:
    b = _Builder(opp, {sid: s.reliability_flags for sid, s in ds.sources.items()})
    _age(b, profile)
    age_not_met = any(i.requirement == "minimum_age" and i.status == "not_met" for i in b.items)
    _guardian(b, profile, age_not_met)
    _hours(b, profile)
    _months(b, profile)
    _sessions(b, profile)
    _schedule(b, profile)
    _other(b, profile)

    if opp.record_type != "described_volunteer_role":
        b.notes.insert(0, RECORD_TYPE_LABELS[opp.record_type] + ". Not a confirmed placement.")
    for t in opp.training_requirements or []:
        b.notes.append(f"Required step: {t.description} [{t.source_id}]")
    for n in opp.notes_for_applicants or []:
        b.notes.append(f"Note ({n.type.replace('_', ' ')}): {n.note} [{n.source_id}]")
    if profile.commitment_preference == "one_time" and opp.commitment_type == "recurring":
        b.notes.append("Preference note: you prefer one-time help, and this role has a recurring commitment.")
    if profile.commitment_preference == "recurring" and opp.commitment_type == "one_time":
        b.notes.append("Preference note: you want ongoing help, and this is a one-time activity.")

    statuses = [i.status for i in b.items]
    if "not_met" in statuses:
        overall = "not_met"
        unmet = [i for i in b.items if i.status == "not_met"]
        if all(i.applicability == "published_applicable" for i in unmet):
            summary = ("Does not meet a clearly applicable published requirement: "
                       f"{', '.join(i.requirement.replace('_', ' ') for i in unmet)}.")
        else:
            summary = ("Every published version of the minimum age is above your age (the sources conflict, so "
                       "confirm the current rule with the organization).")
    elif "needs_confirmation" in statuses:
        overall = "needs_confirmation"
        summary = (f"Possible fit — confirm requirements: {statuses.count('needs_confirmation')} requirement(s) need "
                   "confirmation or more information; none is a definite mismatch.")
    else:
        overall = "meets_published_requirements_checked"
        summary = ("Meets the published requirements we checked, subject to the organization's confirmation. "
                   "This is not approval or a guaranteed placement.")

    questions = [q.question for q in opp.unresolved_questions][:MAX_QUESTIONS]
    return Assessment(
        opportunity_id=opp.opportunity_id, title=opp.title, organization_name=ds.org(opp).name,
        record_type=opp.record_type, record_type_label=RECORD_TYPE_LABELS[opp.record_type],
        overall_status=overall, overall_summary=summary, requirements=b.items, notes=b.notes,
        costs=_costs(opp, profile), application_status=_application_status(ds, opp),
        placement_or_shift_availability=_placement(opp), questions_for_organization=questions,
        profile_fingerprint=profile.fingerprint())


def checklist(ds: Dataset, opp: Opportunity) -> list[dict]:
    """Application steps built only from the dataset (the model cannot add steps)."""
    org = ds.org(opp)
    steps: list[dict] = []
    status = APPLICATION_STATUS_LABELS[opp.application_status]
    if opp.application_status == "explicitly_closed":
        steps.append({"step": f"Applications are currently closed ({status}). Check {org.name}'s page for when they reopen.",
                      "source_ids": [e.source_id for e in opp.field_evidence if e.field == "application_status"][:1]})
    elif opp.application_or_information_url:
        steps.append({"step": f"Read and apply on {org.name}'s own website: {opp.application_or_information_url} "
                              f"(status: {status}).", "source_ids": opp.source_ids[:1]})
    for n in opp.notes_for_applicants or []:
        if n.type == "process_note":
            steps.append({"step": n.note, "source_ids": [n.source_id]})
    for t in opp.training_requirements or []:
        steps.append({"step": f"Complete required step: {t.description}", "source_ids": [t.source_id]})
    for o in opp.orientation_info or []:
        steps.append({"step": f"Orientation: {o.summary}", "source_ids": [o.source_id]})
    for f in opp.fees or []:
        steps.append({"step": f"Fee: {f.amount:g} {f.currency} when {f.applies_when.lower()}."
                              + (f" {f.payment_terms}" if f.payment_terms else ""), "source_ids": [f.source_id]})
    for r in opp.other_requirements or []:
        steps.append({"step": f"Be ready to show or confirm: {r.requirement}", "source_ids": [r.source_id]})
    for q in opp.unresolved_questions[:4]:
        steps.append({"step": f"Ask the organization: {q.question}", "source_ids": []})
    steps.append({"step": f"Contact or more information: {org.contact_page_url}", "source_ids": []})
    return steps


def find_alternatives(ds: Dataset, profile: VolunteerProfile, *, exclude_id: str | None = None,
                      activities: list[str] | None = None, limit: int = 5) -> list[dict]:
    """Records (any record type) that are not a definite mismatch, in the profile's scope.

    Ranking: shared activity tags first, then fewer unresolved requirements. Independent
    support activities and interest areas are labelled as such.
    """
    want = set(activities or profile.interests)
    candidates = ds.search(include_wider_connecticut=profile.include_wider_connecticut,
                           record_types=["described_volunteer_role", "interest_area_only", "independent_support_activity"])
    scored = []
    for o in candidates:
        if o.opportunity_id == exclude_id or o.application_status == "explicitly_closed":
            continue
        a = assess(ds, o, profile)
        if a.overall_status == "not_met":
            continue
        overlap = len(want & set(o.activity_tags)) if want else 0
        if profile.age is not None and profile.age < ADULT_AGE and "youth_program" in o.activity_tags:
            overlap += 1  # minors: prefer programs explicitly aimed at young people
        unresolved = sum(1 for r in a.requirements if r.status == "needs_confirmation")
        scored.append((-overlap, unresolved, o.opportunity_id, a))
    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    return [{**ds.summary(ds.opportunities[oid]), "overall_status": a.overall_status,
             "overall_summary": a.overall_summary} for _, _, oid, a in scored[:limit]]
