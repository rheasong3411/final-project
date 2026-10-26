#!/usr/bin/env python3
"""Structural validation for the animal-volunteer dataset (schema v2).

Run from the animal-volunteer/ folder:

    python scripts/validate_data.py                  # validates data/
    python scripts/validate_data.py --data-dir PATH  # validates another copy (used by the self-tests)

Checks structure, types, IDs, references, allowed values, evidence links,
conflict handling, requirement applicability, schedule separation and
commitment types. It cannot check factual accuracy: a record can pass every
check here and still misstate what an organization's page says. Quote checks
against saved page snapshots are in scripts/check_evidence_quotes.py, and the
factual review is in output/data_audit.md.

Exit code 0 means no errors (warnings may still be printed); 1 means errors.
Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- vocabularies (documented in README.md)
GEOGRAPHIC_SCOPES = {"greater_new_haven", "wider_connecticut"}
APPLICATION_STATUSES = {"explicitly_accepting_applications", "explicitly_closed", "needs_confirmation"}
RECORD_TYPES = {"described_volunteer_role", "interest_area_only", "independent_support_activity"}
COMMITMENT_TYPES = {"recurring", "one_time", "variable", "unknown"}
APPLICABILITY_STATUSES = {"published_applicable", "needs_confirmation", "conflicting"}
HOURS_PERIODS = {"week", "month"}
HOURS_PER = {"week", "month", "session"}
TIMING_ASSESSMENTS = {"appears_past_year_not_stated", "past", "upcoming", "unknown"}
ACCESS_RESULTS = {"accessible", "accessible_form_only", "accessible_dynamic_content_not_rendered",
                  "not_found_404", "not_accessible"}
RELIABILITY_FLAGS = {"possibly_superseded", "undated", "partially_outdated"}
SCOPES = {"organization", "program", "role"}
TRAINING_TYPES = {"orientation", "training", "mentorship", "shadowing", "video", "interview", "other"}
NOTE_TYPES = {"advisory", "preferred_skill", "process_note"}
ACTIVITY_TAGS = {
    "dog_walking", "animal_socialization", "animal_care_cleaning", "laundry", "fostering", "transport",
    "events", "fundraising", "administrative", "grant_writing", "communications_marketing",
    "maintenance_trades", "gardening_grounds", "education_outreach", "supply_drives", "crafts",
    "adoption_support", "tnr_feral_care", "dog_training", "youth_program", "group_project",
}
ANIMAL_TAGS = {"dogs", "cats", "small_animals", "not_applicable", "unspecified"}

# Normalized requirement fields. Every populated one needs a requirement_applicability entry.
REQUIREMENT_FIELDS = ["minimum_age", "guardian_requirement", "minimum_hours", "minimum_commitment_months",
                      "commitment_type", "time_commitment", "recurring_schedule", "training_requirements",
                      "fees", "other_requirements"]
# Populated values of these fields must cite field_evidence (list fields with their own
# source_id + original text are checked item by item instead).
EVIDENCED_FIELDS = ["minimum_age", "guardian_requirement", "minimum_hours", "hours_period",
                    "minimum_commitment_months", "training_requirements", "fees", "other_requirements",
                    "notes_for_applicants"]
MAX_EVIDENCE_CHARS = 450  # keep passages short; never copy whole pages
# A month-and-day date inside schedule/orientation text means a dated notice was filed in the wrong place.
DATE_PATTERN = re.compile(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b")

STR, INT, NUM, LIST, DICT, NONE = str, int, (int, float), list, dict, type(None)
SOURCE_FIELDS = {
    "source_id": (STR, True), "organization_id": (STR, True), "url": (STR, True), "page_title": (STR, True),
    "accessed_at": (STR, True), "access_result": (STR, True), "published_update_date": ((STR, NONE), False),
    "reliability_flags": (LIST, False), "evidence_notes": (STR, True), "conflicts_or_stale_information": (LIST, False),
}
ORG_FIELDS = {
    "organization_id": (STR, True), "name": (STR, True), "official_website": (STR, True),
    "physical_address": ((STR, NONE), False), "town": ((STR, NONE), False), "geographic_scope": (STR, True),
    "latitude": ((int, float, NONE), False), "longitude": ((int, float, NONE), False),
    "contact_page_url": (STR, True), "source_ids": (LIST, True), "locations": (LIST, False),
    "notes": ((STR, NONE), False), "field_evidence": (LIST, False),
}
OPP_FIELDS = {
    "opportunity_id": (STR, True), "organization_id": (STR, True), "record_type": (STR, True),
    "title": (STR, True), "description": (STR, True),
    "activity_tags": (LIST, True), "animal_tags": (LIST, True), "location_description": ((STR, NONE), False),
    "location_town": ((STR, NONE), False), "minimum_age": ((INT, NONE), False),
    "guardian_requirement": ((DICT, NONE), False), "commitment_type": (STR, True),
    "minimum_hours": ((int, float, NONE), False), "hours_period": ((STR, NONE), False),
    "minimum_commitment_months": ((int, float, NONE), False), "time_commitment": ((LIST, NONE), False),
    "recurring_schedule": ((LIST, NONE), False), "orientation_info": ((LIST, NONE), False),
    "dated_notices": ((LIST, NONE), False), "training_requirements": ((LIST, NONE), False),
    "fees": ((LIST, NONE), False), "other_requirements": ((LIST, NONE), False),
    "notes_for_applicants": ((LIST, NONE), False), "requirement_applicability": (DICT, False),
    "application_status": (STR, True), "application_or_information_url": ((STR, NONE), False),
    "source_ids": (LIST, True), "field_evidence": (LIST, True), "unresolved_questions": (LIST, False),
}

errors: list[str] = []
warnings: list[str] = []


def err(where: str, msg: str) -> None:
    errors.append(f"{where}: {msg}")


def warn(where: str, msg: str) -> None:
    warnings.append(f"{where}: {msg}")


def type_ok(value, types) -> bool:
    if isinstance(value, bool):  # bool is a subclass of int; never accept it as a number
        return bool in (types if isinstance(types, tuple) else (types,))
    return isinstance(value, types)


def is_num(v) -> bool:
    return type_ok(v, NUM)


def load(data_dir: Path, name: str):
    path = data_dir / f"{name}.json"
    try:
        with path.open(encoding="utf-8") as f:
            rows = json.load(f)
    except FileNotFoundError:
        err(path.name, "file not found")
        return []
    except json.JSONDecodeError as e:
        err(path.name, f"invalid JSON: {e}")
        return []
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        err(path.name, "top level must be an array of objects")
        return []
    return rows


def check_shape(rows, fields, id_field, label):
    ids = Counter()
    for i, r in enumerate(rows):
        rid = r.get(id_field, f"#{i}")
        if not isinstance(rid, str):
            rid = repr(rid)  # keep IDs hashable so a bad ID is reported, not a crash
        where = f"{label}[{rid}]"
        for k in r.keys() - fields.keys():
            err(where, f"unexpected field '{k}'")
        for k, (types, required) in fields.items():
            if k not in r:
                err(where, f"missing field '{k}'")
                continue
            v = r[k]
            if not type_ok(v, types):
                err(where, f"field '{k}' has type {type(v).__name__}")
            elif required and (v is None or v == "" or v == []):
                err(where, f"required field '{k}' is empty")
        ids[rid] += 1
    for rid, n in ids.items():
        if n > 1:
            err(label, f"duplicate {id_field} '{rid}' ({n} times)")
    return {r.get(id_field) for r in rows if isinstance(r.get(id_field), str)}


def check_url(where, field, url, required=True):
    if url is None:
        if required:
            err(where, f"{field} is null")
        return
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc or " " in url:
        err(where, f"{field} is not a valid http(s) URL: {url!r}")


def check_evidence_list(where, items, source_ids_known, record_sources):
    fields_with_evidence = Counter()
    for j, e in enumerate(items):
        w = f"{where}.field_evidence[{j}]"
        if not isinstance(e, dict):
            err(w, "must be an object")
            continue
        for k in ("field", "source_id", "evidence", "scope"):
            if not isinstance(e.get(k), str) or not e.get(k):
                err(w, f"missing or empty '{k}'")
        extra = e.keys() - {"field", "source_id", "evidence", "scope", "conflict", "note"}
        if extra:
            err(w, f"unexpected keys {sorted(extra)}")
        if e.get("scope") not in SCOPES:
            err(w, f"scope must be one of {sorted(SCOPES)}")
        if "conflict" in e and e["conflict"] is not True:
            err(w, "'conflict' must be true when present")
        sid = e.get("source_id")
        if sid not in source_ids_known:
            err(w, f"unknown source_id '{sid}'")
        elif sid not in record_sources:
            err(w, f"source_id '{sid}' is not listed in the record's source_ids")
        if len(e.get("evidence", "")) > MAX_EVIDENCE_CHARS:
            err(w, f"evidence passage longer than {MAX_EVIDENCE_CHARS} chars; use a short excerpt or paraphrase")
        if e.get("field") == "guardian_requirement" and str(e.get("evidence", "")).startswith("Derived:"):
            err(w, "guardian evidence must be a published statement, not a derivation from minimum age")
        fields_with_evidence[e.get("field")] += 1
    return fields_with_evidence


def check_items(where, field, items, required_keys, rec_sources, scope_required=True):
    """Common checks for list-of-object fields that carry their own source_id."""
    if items is None:
        return
    if items == []:
        err(where, f"'{field}' must be null (not stated) rather than an empty list")
        return
    for j, x in enumerate(items):
        w = f"{where}.{field}[{j}]"
        if not isinstance(x, dict):
            err(w, "must be an object")
            continue
        for k in required_keys:
            if x.get(k) in (None, ""):
                err(w, f"missing '{k}'")
        if x.get("source_id") not in rec_sources:
            err(w, "source_id must be listed in the record's source_ids")
        if scope_required and x.get("scope") not in SCOPES:
            err(w, f"scope must be one of {sorted(SCOPES)}")


def check_source(s, org_ids):
    where = f"sources[{s.get('source_id')}]"
    if s.get("organization_id") not in org_ids:
        err(where, f"unknown organization_id '{s.get('organization_id')}'")
    check_url(where, "url", s.get("url"))
    if s.get("access_result") not in ACCESS_RESULTS:
        err(where, f"access_result must be one of {sorted(ACCESS_RESULTS)}")
    for flag in s.get("reliability_flags", []):
        if flag not in RELIABILITY_FLAGS:
            err(where, f"unknown reliability flag '{flag}'")
    try:
        ts = datetime.fromisoformat(s.get("accessed_at", ""))
        if ts.tzinfo is None:
            err(where, "accessed_at must include a timezone offset")
    except (TypeError, ValueError):
        err(where, f"accessed_at is not an ISO-8601 timestamp: {s.get('accessed_at')!r}")
    if not all(isinstance(c, str) and c for c in s.get("conflicts_or_stale_information", [])):
        err(where, "conflicts_or_stale_information must be a list of non-empty strings")


def check_org(o, source_ids, source_org):
    where = f"organizations[{o.get('organization_id')}]"
    if o.get("geographic_scope") not in GEOGRAPHIC_SCOPES:
        err(where, f"geographic_scope must be one of {sorted(GEOGRAPHIC_SCOPES)}")
    for f in ("official_website", "contact_page_url"):
        check_url(where, f, o.get(f))
    for sid in o.get("source_ids", []):
        if sid not in source_ids:
            err(where, f"unknown source_id '{sid}'")
        elif source_org.get(sid) != o.get("organization_id"):
            err(where, f"source '{sid}' belongs to organization '{source_org.get(sid)}'")
    lat, lon = o.get("latitude"), o.get("longitude")
    if (lat is None) != (lon is None):
        err(where, "latitude and longitude must both be set or both be null")
    if lat is not None and not (-90 <= lat <= 90):
        err(where, f"latitude out of range: {lat}")
    if lon is not None and not (-180 <= lon <= 180):
        err(where, f"longitude out of range: {lon}")
    ev_fields = check_evidence_list(where, o.get("field_evidence", []), source_ids, set(o.get("source_ids", [])))
    if lat is not None and lon is not None and not ev_fields.get("coordinates"):
        err(where, "populated coordinates need a field_evidence entry with field 'coordinates'")
    if o.get("physical_address") and not ev_fields.get("physical_address"):
        err(where, "physical_address is populated but has no field_evidence entry")
    for j, loc in enumerate(o.get("locations", [])):
        w = f"{where}.locations[{j}]"
        if not isinstance(loc, dict) or not loc.get("address") or not loc.get("label"):
            err(w, "each location needs at least 'label' and 'address'")
        elif loc.get("source_id") not in o.get("source_ids", []):
            err(w, f"source_id '{loc.get('source_id')}' not in organization source_ids")


def check_opportunity(r, source_ids, source_org, org_ids, flagged_sources):
    oid = r.get("opportunity_id")
    where = f"opportunities[{oid}]"
    rec_sources = set(r.get("source_ids", []))
    if r.get("organization_id") not in org_ids:
        err(where, f"unknown organization_id '{r.get('organization_id')}'")
    for sid in rec_sources:
        if sid not in source_ids:
            err(where, f"unknown source_id '{sid}'")
        elif source_org.get(sid) != r.get("organization_id"):
            err(where, f"source '{sid}' belongs to organization '{source_org.get(sid)}'")
    check_url(where, "application_or_information_url", r.get("application_or_information_url"), required=False)

    # ---- enums
    status = r.get("application_status")
    if status not in APPLICATION_STATUSES:
        err(where, f"application_status must be one of {sorted(APPLICATION_STATUSES)}")
    if r.get("record_type") not in RECORD_TYPES:
        err(where, f"record_type must be one of {sorted(RECORD_TYPES)}")
    ctype = r.get("commitment_type")
    if ctype not in COMMITMENT_TYPES:
        err(where, f"commitment_type must be one of {sorted(COMMITMENT_TYPES)}")
    if r.get("hours_period") is not None and r.get("hours_period") not in HOURS_PERIODS:
        err(where, f"hours_period must be one of {sorted(HOURS_PERIODS)} or null")
    if (r.get("minimum_hours") is None) != (r.get("hours_period") is None):
        err(where, "minimum_hours and hours_period must both be set or both be null")
    for tag in r.get("activity_tags", []):
        if tag not in ACTIVITY_TAGS:
            err(where, f"unknown activity tag '{tag}'")
    atags = r.get("animal_tags", [])
    for tag in atags:
        if tag not in ANIMAL_TAGS:
            err(where, f"unknown animal tag '{tag}'")
    if len(atags) > 1 and ({"not_applicable", "unspecified"} & set(atags)):
        err(where, "'not_applicable'/'unspecified' cannot be combined with other animal tags")
    for f in ("activity_tags", "animal_tags"):
        if len(set(r.get(f, []))) != len(r.get(f, [])):
            err(where, f"duplicate values in {f}")

    # ---- numbers
    for f in ("minimum_age", "minimum_hours", "minimum_commitment_months"):
        v = r.get(f)
        if is_num(v) and v < 0:
            err(where, f"{f} must be nonnegative (got {v})")
    if r.get("minimum_age") == 0:
        warn(where, "minimum_age is 0 (a published 'all ages' rule); check that the guardian requirement is shown to users")

    # ---- guardian: only published statements; null means not stated
    g = r.get("guardian_requirement")
    if isinstance(g, dict):
        extra = g.keys() - {"required", "applies_under_age", "details", "scope"}
        if extra:
            err(where, f"guardian_requirement has unexpected keys {sorted(extra)} (derived values are not allowed)")
        if not isinstance(g.get("required"), bool):
            err(where, "guardian_requirement.required must be true/false")
        if g.get("applies_under_age") is not None and (not type_ok(g["applies_under_age"], INT) or g["applies_under_age"] < 0):
            err(where, "guardian_requirement.applies_under_age must be a nonnegative integer or null")
        if not g.get("details"):
            err(where, "guardian_requirement.details is required")
        if g.get("scope") not in SCOPES:
            err(where, f"guardian_requirement.scope must be one of {sorted(SCOPES)}")

    # ---- list fields with their own sources
    check_items(where, "training_requirements", r.get("training_requirements"), ("type", "description"), rec_sources)
    for j, t in enumerate(r.get("training_requirements") or []):
        if isinstance(t, dict) and t.get("type") not in TRAINING_TYPES:
            err(f"{where}.training_requirements[{j}]", f"type must be one of {sorted(TRAINING_TYPES)}")
    check_items(where, "fees", r.get("fees"), ("currency", "applies_when"), rec_sources, scope_required=False)
    for j, fee in enumerate(r.get("fees") or []):
        if isinstance(fee, dict) and (not is_num(fee.get("amount")) or fee["amount"] < 0):
            err(f"{where}.fees[{j}]", "amount must be a nonnegative number")
    check_items(where, "other_requirements", r.get("other_requirements"), ("requirement",), rec_sources)
    check_items(where, "notes_for_applicants", r.get("notes_for_applicants"), ("note", "type"), rec_sources)
    for j, n in enumerate(r.get("notes_for_applicants") or []):
        if isinstance(n, dict) and n.get("type") not in NOTE_TYPES:
            err(f"{where}.notes_for_applicants[{j}]", f"type must be one of {sorted(NOTE_TYPES)}")
    for f in ("recurring_schedule", "orientation_info"):
        check_items(where, f, r.get(f), ("original_text", "summary"), rec_sources)
        for j, x in enumerate(r.get(f) or []):
            if isinstance(x, dict) and DATE_PATTERN.search(str(x.get("original_text", "")) + " " + str(x.get("summary", ""))):
                err(f"{where}.{f}[{j}]", "contains a specific calendar date; dated or past notices belong in dated_notices, never in recurring schedules")
    check_items(where, "dated_notices", r.get("dated_notices"), ("original_text", "stated_date_text", "timing_assessment", "assessed_on"), rec_sources)
    for j, n in enumerate(r.get("dated_notices") or []):
        if not isinstance(n, dict):
            continue
        w = f"{where}.dated_notices[{j}]"
        if n.get("timing_assessment") not in TIMING_ASSESSMENTS:
            err(w, f"timing_assessment must be one of {sorted(TIMING_ASSESSMENTS)}")
        if n.get("stated_year") is not None and not type_ok(n.get("stated_year"), INT):
            err(w, "stated_year must be an integer printed by the source, or null")
        if n.get("timing_assessment") in ("upcoming", "past") and n.get("stated_year") is None:
            err(w, f"'{n.get('timing_assessment')}' requires a year stated by the source; use 'appears_past_year_not_stated' or 'unknown'")
        if n.get("timing_assessment") == "upcoming":
            try:
                if date.fromisoformat(str(n.get("assessed_on"))) > date.today():
                    err(w, "assessed_on is in the future")
            except ValueError:
                err(w, "assessed_on must be an ISO date")
    tc = r.get("time_commitment")
    check_items(where, "time_commitment", tc, ("published_text",), rec_sources)
    for j, x in enumerate(tc or []):
        if not isinstance(x, dict):
            continue
        w = f"{where}.time_commitment[{j}]"
        if x.get("hours_per") is not None and x.get("hours_per") not in HOURS_PER:
            err(w, f"hours_per must be one of {sorted(HOURS_PER)} or null")
        for k in ("hours_min", "hours_max", "duration_months_min", "duration_months_max"):
            if x.get(k) is not None and (not is_num(x[k]) or x[k] < 0):
                err(w, f"{k} must be a nonnegative number or null")
        for lo, hi in (("hours_min", "hours_max"), ("duration_months_min", "duration_months_max")):
            if is_num(x.get(lo)) and is_num(x.get(hi)) and x[lo] > x[hi]:
                err(w, f"{lo} is greater than {hi}")
        if (x.get("hours_min") is not None or x.get("hours_max") is not None) and x.get("hours_per") is None:
            err(w, "hours need an hours_per unit")
        if not isinstance(x.get("duration_is_typical_not_minimum"), bool):
            err(w, "duration_is_typical_not_minimum must be true/false")
        if x.get("duration_is_typical_not_minimum") and r.get("minimum_commitment_months") is not None \
                and r.get("minimum_commitment_months") == x.get("duration_months_min"):
            err(w, "a typical duration must not be copied into minimum_commitment_months")

    # ---- commitment type consistency
    if ctype == "one_time":
        if r.get("hours_period") is not None or r.get("minimum_commitment_months") is not None:
            err(where, "a one_time commitment cannot have a recurring hours_period or a minimum_commitment_months")
        if not any(isinstance(x, dict) and x.get("hours_per") == "session" for x in (tc or [])):
            err(where, "a one_time commitment needs a time_commitment entry measured per session")
    if ctype == "recurring" and r.get("minimum_hours") is None:
        err(where, "a recurring commitment needs published minimum_hours and hours_period")
    if ctype == "variable" and not tc:
        err(where, "a variable commitment needs the published wording in time_commitment")
    if ctype == "unknown" and r.get("minimum_hours") is not None:
        err(where, "minimum_hours is published, so commitment_type cannot be 'unknown'")

    # ---- record types
    rtype = r.get("record_type")
    if rtype == "interest_area_only" and status == "explicitly_accepting_applications":
        err(where, "an interest_area_only record cannot be marked as explicitly accepting applications")
    if rtype == "independent_support_activity" and r.get("recurring_schedule"):
        err(where, "an independent_support_activity must not carry a shelter shift schedule")

    for j, q in enumerate(r.get("unresolved_questions", [])):
        if not isinstance(q, dict) or not q.get("question") or "field" not in q:
            err(f"{where}.unresolved_questions[{j}]", "needs 'field' (may be null) and 'question'")

    # ---- evidence
    ev_fields = check_evidence_list(where, r.get("field_evidence", []), source_ids, rec_sources)
    for f in EVIDENCED_FIELDS:
        if r.get(f) is not None and not ev_fields.get(f):
            err(where, f"'{f}' is populated but has no field_evidence entry")
    if ctype in ("recurring", "one_time", "variable") and not (ev_fields.get("commitment_type") or ev_fields.get("time_commitment")):
        err(where, f"commitment_type '{ctype}' needs a field_evidence entry")
    if status in ("explicitly_accepting_applications", "explicitly_closed") and not ev_fields.get("application_status"):
        err(where, f"application_status '{status}' needs a field_evidence entry")

    # ---- requirement applicability
    app = r.get("requirement_applicability") or {}
    questions = {q.get("field") for q in r.get("unresolved_questions", []) if isinstance(q, dict)}
    conflicted = {e.get("field") for e in r.get("field_evidence", []) if isinstance(e, dict) and e.get("conflict")}
    for f in app:
        if f not in REQUIREMENT_FIELDS:
            err(where, f"requirement_applicability has unknown field '{f}'")
    for f in REQUIREMENT_FIELDS:
        v = r.get(f)
        populated = v is not None and v != "unknown"
        a = app.get(f)
        if populated and a is None:
            err(where, f"'{f}' is populated but has no requirement_applicability entry")
        if f in conflicted and (a is None or a.get("status") != "conflicting"):
            err(where, f"'{f}' has conflicting evidence, so its applicability must be 'conflicting'")
        if f in conflicted and v not in (None, [], "unknown"):
            err(where, f"field '{f}' has conflicting evidence but a normalized value ({v!r}); leave it null")
        if a is None:
            continue
        aw = f"{where}.requirement_applicability.{f}"
        if not isinstance(a, dict):
            err(aw, "must be an object")
            continue
        st = a.get("status")
        if st not in APPLICABILITY_STATUSES:
            err(aw, f"status must be one of {sorted(APPLICABILITY_STATUSES)}")
        sids = a.get("source_ids")
        if not isinstance(sids, list) or not sids:
            err(aw, "source_ids must be a non-empty list")
            sids = []
        for sid in sids:
            if sid not in rec_sources:
                err(aw, f"source '{sid}' is not listed in the record's source_ids")
        if not a.get("reason"):
            err(aw, "reason is required")
        if st == "conflicting" and v not in (None, [], "unknown"):
            err(aw, "a conflicting requirement must have a null normalized value")
        if st == "published_applicable":
            if f in conflicted:
                err(aw, "cannot be published_applicable while conflicting evidence is recorded")
            if sids and all(s in flagged_sources for s in sids):
                err(aw, "cannot be published_applicable when every supporting source is flagged possibly_superseded")
            if not populated:
                err(aw, "published_applicable needs a populated value")
        if st in ("needs_confirmation", "conflicting") and f not in questions:
            err(aw, f"a '{st}' requirement needs an unresolved question for field '{f}'")



# ---------------------------------------------------------------- geography (Session 10 files)
LOCATION_STATUSES = {"verified_site", "candidate_site_unconfirmed", "volunteer_home", "not_published"}
CT_LAT, CT_LON = (40.9, 42.1), (-73.8, -71.7)   # generous Connecticut bounding box
TIMESTAMP_TZ = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2}|Z)$")
ZCTA_HEADER = ["zcta", "intpt_lat", "intpt_lon", "aland_sqmi"]


def _in_ct(lat, lon) -> bool:
    return is_num(lat) and is_num(lon) and CT_LAT[0] <= lat <= CT_LAT[1] and CT_LON[0] <= lon <= CT_LON[1]


def check_zcta(data_dir: Path) -> int:
    """data/geo/ct_zcta.csv: 5-digit string IDs (leading zeros kept), unique, Connecticut coordinates."""
    import csv
    path = data_dir / "geo" / "ct_zcta.csv"
    if not path.is_file():
        err("geo/ct_zcta.csv", "file not found")
        return 0
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if not rows or rows[0] != ZCTA_HEADER:
        err("geo/ct_zcta.csv", f"header must be {ZCTA_HEADER}")
        return 0
    seen = set()
    for i, row in enumerate(rows[1:], start=2):
        where = f"geo/ct_zcta.csv line {i}"
        if len(row) != 4:
            err(where, "expected 4 columns")
            continue
        z = row[0]
        if not re.fullmatch(r"06\d{3}", z):
            err(where, f"ZCTA '{z}' must be a 5-digit Connecticut code starting 06 (leading zero kept)")
        if z in seen:
            err(where, f"duplicate ZCTA {z}")
        seen.add(z)
        try:
            lat, lon = float(row[1]), float(row[2])
        except ValueError:
            err(where, "latitude/longitude must be numbers")
            continue
        if not _in_ct(lat, lon):
            err(where, f"coordinates {lat}, {lon} are outside Connecticut")
    meta_path = data_dir / "geo" / "ct_zcta_metadata.json"
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for k in ("dataset", "download_url", "license", "postal_zip_or_zcta", "dataset_date", "rows_kept"):
            if not meta.get(k):
                err("geo/ct_zcta_metadata.json", f"missing '{k}'")
        if meta.get("rows_kept") != len(seen):
            err("geo/ct_zcta_metadata.json", f"rows_kept {meta.get('rows_kept')} != {len(seen)} rows in ct_zcta.csv")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        err("geo/ct_zcta_metadata.json", f"missing or invalid: {type(e).__name__}")
    return len(seen)


def check_towns(data_dir: Path) -> int:
    """data/geo/ct_towns.csv: unique town names with Connecticut reference points."""
    import csv
    path = data_dir / "geo" / "ct_towns.csv"
    if not path.is_file():
        err("geo/ct_towns.csv", "file not found")
        return 0
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    names = set()
    for i, r in enumerate(rows, start=2):
        if r.get("town") in names:
            err(f"geo/ct_towns.csv line {i}", f"duplicate town {r.get('town')}")
        names.add(r.get("town"))
        try:
            if not _in_ct(float(r["intpt_lat"]), float(r["intpt_lon"])):
                err(f"geo/ct_towns.csv line {i}", "reference point outside Connecticut")
        except (KeyError, ValueError, TypeError):
            err(f"geo/ct_towns.csv line {i}", "latitude/longitude must be numbers")
    return len(names)


def check_locations(data_dir: Path, opps: list, source_ids: set, source_org: dict, org_ids: set) -> None:
    """data/volunteer_locations.json: unique IDs, valid references, complete in-range coordinate pairs, and a
    geocoded site behind every verified_site record. Unknown locations must stay unknown (no coordinates)."""
    path = data_dir / "volunteer_locations.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        err("volunteer_locations.json", "file not found")
        return
    except json.JSONDecodeError as e:
        err("volunteer_locations.json", f"invalid JSON: {e}")
        return
    opp_org = {r.get("opportunity_id"): r.get("organization_id") for r in opps}
    sites = {}
    for s in data.get("sites") or []:
        sid = s.get("site_id")
        where = f"volunteer_locations.sites[{sid}]"
        if not isinstance(sid, str) or not sid:
            err(where, "site_id must be a non-empty string")
            continue
        if sid in sites:
            err(where, "duplicate site_id")
        sites[sid] = s
        if s.get("organization_id") not in org_ids:
            err(where, f"unknown organization '{s.get('organization_id')}'")
        if not s.get("address") or re.search(r"p\.?\s*o\.?\s*box", str(s.get("address")), re.I):
            err(where, "needs a physical street address (never a P.O. box)")
        ev = s.get("address_evidence") or []
        if not ev:
            err(where, "address_evidence is required")
        for e in ev:
            if e.get("source_id") not in source_ids:
                err(where, f"unknown source '{e.get('source_id')}'")
            elif source_org.get(e.get("source_id")) != s.get("organization_id"):
                err(where, f"source '{e.get('source_id')}' belongs to another organization")
            if not e.get("quote") or not TIMESTAMP_TZ.match(str(e.get("accessed_at") or "")):
                err(where, "evidence needs a quote and an accessed_at timestamp with timezone")
        g = s.get("geocode")
        if g is not None:
            lat, lon = g.get("latitude"), g.get("longitude")
            if (lat is None) != (lon is None):
                err(where, "latitude and longitude must both be set or both null")
            elif lat is not None and not _in_ct(lat, lon):
                err(where, f"coordinates {lat}, {lon} are out of range (not in Connecticut)")
            if g.get("match_count") != 1:
                err(where, "geocode must come from exactly one geocoder match")
    seen = set()
    for r in data.get("opportunity_locations") or []:
        oid = r.get("opportunity_id")
        where = f"volunteer_locations.opportunity_locations[{oid}]"
        if oid not in opp_org:
            err(where, "unknown opportunity_id")
            continue
        if oid in seen:
            err(where, "duplicate opportunity_id")
        seen.add(oid)
        st = r.get("location_status")
        if st not in LOCATION_STATUSES:
            err(where, f"location_status must be one of {sorted(LOCATION_STATUSES)}")
            continue
        for k in ("site_id", "candidate_site_id", "related_site_id"):
            ref = r.get(k)
            if ref is not None and ref not in sites:
                err(where, f"{k} '{ref}' is not a known site")
            elif ref is not None and sites[ref].get("organization_id") != opp_org[oid]:
                err(where, f"{k} '{ref}' belongs to another organization")
        if st == "verified_site":
            site = sites.get(r.get("site_id"))
            g = (site or {}).get("geocode") or {}
            if site is None or g.get("latitude") is None or g.get("longitude") is None:
                err(where, "verified_site needs a site with geocoded coordinates")
            if not r.get("evidence"):
                err(where, "verified_site needs role-level evidence placing the role at the site")
        elif r.get("site_id") is not None:
            err(where, f"site_id must be null unless location_status is verified_site (got {st})")
        if st == "candidate_site_unconfirmed" and not r.get("candidate_site_id"):
            err(where, "candidate_site_unconfirmed needs candidate_site_id")
        if st == "not_published" and any(r.get(k) for k in ("candidate_site_id", "related_site_id")):
            err(where, "not_published records must not point at a site")
        for e in r.get("evidence") or []:
            if e.get("source_id") not in source_ids:
                err(where, f"unknown source '{e.get('source_id')}'")
            elif source_org.get(e.get("source_id")) != opp_org[oid]:
                err(where, f"source '{e.get('source_id')}' belongs to another organization")
    for oid in set(opp_org) - seen:
        err(f"volunteer_locations.opportunity_locations", f"no entry for opportunity '{oid}' (use not_published if unknown)")
        # (home-based travel evidence is checked below)
    for r in data.get("opportunity_locations") or []:
        where = f"volunteer_locations.opportunity_locations[{r.get('opportunity_id')}]"
        for e in r.get("travel_evidence") or []:
            if e.get("source_id") not in source_ids:
                err(where, f"travel_evidence: unknown source '{e.get('source_id')}'")
            elif source_org.get(e.get("source_id")) != opp_org.get(r.get("opportunity_id")):
                err(where, f"travel_evidence: source '{e.get('source_id')}' belongs to another organization")
        if (r.get("travel_note") or r.get("related_site_purpose")) and r.get("location_status") != "volunteer_home":
            err(where, "travel notes and related-site purposes are only for volunteer_home records")
        if r.get("related_site_purpose") and not r.get("related_site_id"):
            err(where, "related_site_purpose needs related_site_id")
    # organization locations: one verified site per organization, or none (several sites / P.O. box only)
    seen_orgs = set()
    for ol in data.get("organization_locations") or []:
        oid = ol.get("organization_id")
        where = f"volunteer_locations.organization_locations[{oid}]"
        if oid not in org_ids:
            err(where, "unknown organization")
            continue
        if oid in seen_orgs:
            err(where, "duplicate organization")
        seen_orgs.add(oid)
        sid = ol.get("site_id")
        if sid is not None:
            site = sites.get(sid)
            if site is None or site.get("organization_id") != oid:
                err(where, f"site '{sid}' is unknown or belongs to another organization")
            elif not (site.get("geocode") or {}).get("latitude"):
                err(where, f"site '{sid}' has no coordinates")
            if ol.get("other_site_ids"):
                err(where, "an organization with several sites must not name a single site_id")
        for other in ol.get("other_site_ids") or []:
            if other not in sites or sites[other].get("organization_id") != oid:
                err(where, f"other site '{other}' is unknown or belongs to another organization")
        if not ol.get("basis"):
            err(where, "basis is required")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", type=Path, default=ROOT / "data")
    args = ap.parse_args(argv)
    errors.clear()
    warnings.clear()
    data_dir = args.data_dir

    sources = load(data_dir, "sources")
    orgs = load(data_dir, "organizations")
    opps = load(data_dir, "opportunities")

    source_ids = check_shape(sources, SOURCE_FIELDS, "source_id", "sources")
    org_ids = check_shape(orgs, ORG_FIELDS, "organization_id", "organizations")
    check_shape(opps, OPP_FIELDS, "opportunity_id", "opportunities")
    source_org = {s.get("source_id"): s.get("organization_id") for s in sources if isinstance(s.get("source_id"), str)}
    flagged = {s.get("source_id") for s in sources
               if isinstance(s.get("reliability_flags"), list) and "possibly_superseded" in s["reliability_flags"]}

    # Each record is checked independently; malformed values are reported instead of crashing the run.
    for label, rows, idf, fn, extra in (
            ("sources", sources, "source_id", check_source, (org_ids,)),
            ("organizations", orgs, "organization_id", check_org, (source_ids, source_org)),
            ("opportunities", opps, "opportunity_id", check_opportunity, (source_ids, source_org, org_ids, flagged))):
        for r in rows:
            try:
                fn(r, *extra)
            except Exception as e:  # noqa: BLE001
                err(f"{label}[{r.get(idf) if isinstance(r, dict) else '?'}]", f"could not fully check record: {type(e).__name__}: {e}")

    try:
        n_zcta = check_zcta(data_dir)
        check_towns(data_dir)
        check_locations(data_dir, opps, source_ids, source_org, org_ids)
    except Exception as e:  # noqa: BLE001
        n_zcta = 0
        err("geography", f"could not fully check: {type(e).__name__}: {e}")

    print(f"Data folder: {data_dir}")
    print(f"Loaded {len(sources)} sources, {len(orgs)} organizations, {len(opps)} opportunities, "
          f"{n_zcta} Connecticut ZIP areas.")
    if opps:
        org_scope = {str(o.get("organization_id")): str(o.get("geographic_scope")) for o in orgs}
        counts = {
            "application_status": Counter(str(r.get("application_status")) for r in opps),
            "geographic_scope": Counter(org_scope.get(str(r.get("organization_id")), "unknown_organization") for r in opps),
            "record_type": Counter(str(r.get("record_type")) for r in opps),
            "commitment_type": Counter(str(r.get("commitment_type")) for r in opps),
            "requirement applicability": Counter(str(a.get("status")) for r in opps
                                                 for a in (r.get("requirement_applicability") or {}).values()
                                                 if isinstance(a, dict)),
        }
        for name, c in counts.items():
            print(f"Opportunities by {name}: " + ", ".join(f"{k}={v}" for k, v in sorted(c.items(), key=str)))
    for w in warnings:
        print(f"WARNING  {w}")
    for e in errors:
        print(f"ERROR    {e}")
    print(f"\nResult: {len(errors)} error(s), {len(warnings)} warning(s).")
    print("Note: passing validation means the data is structurally consistent, not that it is factually accurate.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
