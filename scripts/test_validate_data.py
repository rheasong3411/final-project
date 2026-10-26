#!/usr/bin/env python3
"""Self-tests for scripts/validate_data.py.

Run from the animal-volunteer/ folder:

    python scripts/test_validate_data.py -v

Each test copies data/ into a temporary folder, breaks one thing on purpose, and
checks that the validator reports the expected error (exit code 1) without crashing.
The first test checks that the real data passes. Standard library only.
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import validate_data  # noqa: E402

DATA = HERE.parent / "data"
BASE = {n: json.loads((DATA / f"{n}.json").read_text())
        for n in ("sources", "organizations", "opportunities", "volunteer_locations")}
GEO_FILES = {n: (DATA / "geo" / n).read_text() for n in ("ct_zcta.csv", "ct_zcta_metadata.json", "ct_towns.csv")}


def run(mutate=None, raw_opportunities=None):
    d = copy.deepcopy(BASE)
    d["geo"] = dict(GEO_FILES)
    if mutate:
        mutate(d)
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "geo").mkdir()
        for name, text in d.pop("geo").items():
            (Path(tmp) / "geo" / name).write_text(text)
        for name, rows in d.items():
            (Path(tmp) / f"{name}.json").write_text(json.dumps(rows))
        if raw_opportunities is not None:
            (Path(tmp) / "opportunities.json").write_text(raw_opportunities)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = validate_data.main(["--data-dir", tmp])
    return code, out.getvalue()


def opp(d, oid):
    return next(r for r in d["opportunities"] if r["opportunity_id"] == oid)


class RealData(unittest.TestCase):
    def test_real_data_passes(self):
        code, out = run()
        self.assertEqual(code, 0, out)
        self.assertIn("0 error(s)", out)


class BrokenData(unittest.TestCase):
    def expect(self, needle, mutate=None, raw=None):
        code, out = run(mutate, raw)
        self.assertEqual(code, 1, out)
        self.assertIn(needle, out)
        self.assertNotIn("Traceback", out)

    # ---- structure, IDs, references, types (the original 21 self-tests, updated for schema v2)
    def test_duplicate_id(self):
        self.expect("duplicate opportunity_id", lambda d: d["opportunities"].append(copy.deepcopy(d["opportunities"][0])))

    def test_unknown_organization(self):
        self.expect("unknown organization_id", lambda d: opp(d, "ah_dog_walking").update(organization_id="nope"))

    def test_invalid_status(self):
        self.expect("application_status must be", lambda d: opp(d, "ah_dog_walking").update(application_status="open"))

    def test_negative_hours(self):
        self.expect("must be nonnegative", lambda d: opp(d, "ah_dog_walking").update(minimum_hours=-2))

    def test_age_without_evidence(self):
        self.expect("'minimum_age' is populated but has no field_evidence",
                    lambda d: opp(d, "bcc_fundraising").update(minimum_age=18))

    def test_value_despite_conflict(self):
        self.expect("has conflicting evidence but a normalized value",
                    lambda d: opp(d, "ah_cat_socializing").update(minimum_age=21))

    def test_one_coordinate(self):
        self.expect("both be set or both be null", lambda d: d["organizations"][0].update(latitude=41.3))

    def test_coordinates_without_evidence(self):
        self.expect("with field 'coordinates'", lambda d: d["organizations"][0].update(latitude=41.3, longitude=-72.9))

    def test_latitude_range(self):
        self.expect("latitude out of range", lambda d: d["organizations"][0].update(latitude=141.3, longitude=-72.9))

    def test_bad_url(self):
        self.expect("not a valid http(s) URL",
                    lambda d: opp(d, "ah_dog_walking").update(application_or_information_url="ftp:/x"))

    def test_timestamp_without_timezone(self):
        self.expect("timezone", lambda d: d["sources"][0].update(accessed_at="2026-10-25T15:50:44"))

    def test_wrong_type(self):
        self.expect("has type str", lambda d: opp(d, "ah_dog_walking").update(minimum_age="21"))

    def test_hours_without_period(self):
        self.expect("both be set or both be null", lambda d: opp(d, "ah_dog_walking").update(hours_period=None))

    def test_evidence_source_not_on_record(self):
        self.expect("not listed in the record's source_ids", lambda d: opp(d, "bcc_fundraising")["field_evidence"].append(
            {"field": "x", "source_id": "paws_volunteer", "evidence": "x", "scope": "role"}))

    def test_missing_field(self):
        self.expect("missing field 'fees'", lambda d: opp(d, "bcc_fundraising").pop("fees"))

    def test_list_valued_status(self):
        self.expect("ERROR", lambda d: opp(d, "ah_dog_walking").update(application_status=["x"]))

    def test_list_valued_id(self):
        self.expect("ERROR", lambda d: opp(d, "ah_dog_walking").update(opportunity_id=["x"]))

    def test_list_valued_tag(self):
        self.expect("ERROR", lambda d: opp(d, "ah_dog_walking").update(activity_tags=[["x"]]))

    def test_empty_evidence_source(self):
        self.expect("missing or empty", lambda d: opp(d, "ah_dog_walking")["field_evidence"].append(
            {"field": "minimum_age", "source_id": "", "evidence": "", "scope": "role"}))

    def test_empty_requirement_list(self):
        self.expect("must be null (not stated) rather than an empty list", lambda d: opp(d, "bcc_fundraising").update(fees=[]))

    def test_malformed_json(self):
        self.expect("invalid JSON", raw="[{oops")

    # ---- correction-pass rules
    def test_guardian_derived_from_age_rejected(self):
        def m(d):
            r = opp(d, "gnhcp_grant_writing")
            r["guardian_requirement"] = {"required": False, "applies_under_age": None, "basis": "derived_from_minimum_age",
                                         "details": "x", "scope": "organization"}
            r["field_evidence"].append({"field": "guardian_requirement", "source_id": "gnhcp_volunteer",
                                        "evidence": "Derived: organization minimum age is 21", "scope": "organization"})
        self.expect("not a derivation from minimum age", m)

    def test_legacy_only_rule_cannot_be_applicable(self):
        self.expect("every supporting source is flagged possibly_superseded",
                    lambda d: opp(d, "ah_dog_walking")["requirement_applicability"]["minimum_hours"].update(status="published_applicable"))

    def test_conflict_cannot_be_applicable(self):
        self.expect("must be 'conflicting'",
                    lambda d: opp(d, "ah_cat_socializing")["requirement_applicability"]["minimum_age"].update(status="published_applicable"))

    def test_uncertain_requirement_needs_question(self):
        def m(d):
            r = opp(d, "bcc_foster")
            r["unresolved_questions"] = [q for q in r["unresolved_questions"] if q["field"] != "minimum_age"]
        self.expect("needs an unresolved question for field 'minimum_age'", m)

    def test_populated_requirement_needs_applicability(self):
        self.expect("has no requirement_applicability entry",
                    lambda d: opp(d, "gnhcp_grant_writing")["requirement_applicability"].pop("minimum_age"))

    def test_past_date_in_recurring_schedule(self):
        self.expect("dated or past notices belong in dated_notices", lambda d: opp(d, "branford_general_volunteer").update(
            recurring_schedule=[{"original_text": "The Next general volunteer orientation will be Sunday, October 11 at 2 pm.",
                                 "summary": "x", "source_id": "branford_volunteering", "scope": "program"}]))

    def test_upcoming_requires_stated_year(self):
        self.expect("requires a year stated by the source",
                    lambda d: opp(d, "branford_general_volunteer")["dated_notices"][0].update(timing_assessment="upcoming"))

    def test_one_time_cannot_have_six_months(self):
        self.expect("one_time commitment cannot have",
                    lambda d: opp(d, "chs_newington_group_trails").update(minimum_commitment_months=6))

    def test_recurring_needs_hours(self):
        self.expect("recurring commitment needs published minimum_hours",
                    lambda d: opp(d, "gnhcp_grant_writing").update(commitment_type="recurring"))

    def test_unknown_record_type(self):
        self.expect("record_type must be one of", lambda d: opp(d, "ah_grant_writing").update(record_type="placement"))

    def test_unknown_commitment_type(self):
        self.expect("commitment_type must be one of", lambda d: opp(d, "ah_grant_writing").update(commitment_type="ongoing"))

    def test_interest_area_cannot_be_open(self):
        def m(d):
            r = opp(d, "ah_grant_writing")
            r["application_status"] = "explicitly_accepting_applications"
            r["field_evidence"].append({"field": "application_status", "source_id": "ah_volunteer", "evidence": "x", "scope": "role"})
        self.expect("interest_area_only record cannot be marked", m)

    def test_typical_duration_not_minimum(self):
        def m(d):
            r = opp(d, "bcc_foster")
            r["minimum_commitment_months"] = 2
            r["field_evidence"].append({"field": "minimum_commitment_months", "source_id": "bcc_foster", "evidence": "x", "scope": "role"})
            r["requirement_applicability"]["minimum_commitment_months"] = {"status": "published_applicable", "source_ids": ["bcc_foster"], "reason": "x"}
        self.expect("typical duration must not be copied", m)

    def test_independent_activity_has_no_shift(self):
        self.expect("must not carry a shelter shift schedule", lambda d: opp(d, "chs_collection_drive").update(
            recurring_schedule=[{"original_text": "x", "summary": "x", "source_id": "chs_volunteer", "scope": "program"}]))



class BrokenGeography(unittest.TestCase):
    """Session 10: ZIP areas and volunteer_locations.json."""
    expect = BrokenData.expect

    def _site(self, d, sid):
        return next(x for x in d["volunteer_locations"]["sites"] if x["site_id"] == sid)

    def _role(self, d, oid):
        return next(x for x in d["volunteer_locations"]["opportunity_locations"] if x["opportunity_id"] == oid)

    def test_zcta_leading_zero_lost(self):
        self.expect("leading zero kept", lambda d: d["geo"].__setitem__("ct_zcta.csv", d["geo"]["ct_zcta.csv"].replace("\n06511,", "\n6511,")))

    def test_zcta_duplicate(self):
        self.expect("duplicate ZCTA", lambda d: d["geo"].__setitem__("ct_zcta.csv", d["geo"]["ct_zcta.csv"] + "06511,41.3,-72.9,1\n"))

    def test_zcta_out_of_range(self):
        self.expect("outside Connecticut", lambda d: d["geo"].__setitem__("ct_zcta.csv", d["geo"]["ct_zcta.csv"].replace("\n06511,41.31727", "\n06511,45.31727")))

    def test_duplicate_site_id(self):
        self.expect("duplicate site_id", lambda d: d["volunteer_locations"]["sites"].append(dict(self._site(d, "ah_shelter"))))

    def test_half_coordinate_pair(self):
        self.expect("both be set or both null", lambda d: self._site(d, "ah_shelter")["geocode"].__setitem__("longitude", None))

    def test_site_coordinates_out_of_range(self):
        self.expect("out of range", lambda d: self._site(d, "ah_shelter")["geocode"].__setitem__("latitude", 91.0))

    def test_verified_site_without_coordinates(self):
        self.expect("verified_site needs a site with geocoded coordinates",
                    lambda d: self._site(d, "fnhas_shelter").__setitem__("geocode", None))

    def test_unknown_opportunity_reference(self):
        self.expect("unknown opportunity_id",
                    lambda d: self._role(d, "ah_dog_walking").__setitem__("opportunity_id", "no_such_role"))

    def test_unknown_source_reference(self):
        self.expect("unknown source", lambda d: self._site(d, "ah_shelter")["address_evidence"][0].__setitem__("source_id", "nope"))

    def test_site_for_another_organization(self):
        self.expect("belongs to another organization",
                    lambda d: self._role(d, "ah_dog_walking").__setitem__("site_id", "bcc_center"))

    def test_unknown_location_cannot_get_a_site(self):
        self.expect("site_id must be null unless", lambda d: self._role(d, "ah_administrative").__setitem__("site_id", "ah_shelter"))

    def _org(self, d, oid):
        return next(x for x in d["volunteer_locations"]["organization_locations"] if x["organization_id"] == oid)

    def test_org_location_site_of_another_organization(self):
        self.expect("unknown or belongs to another organization", lambda d: self._org(d, "fnhas").__setitem__("site_id", "bcc_center"))

    def test_multi_site_org_cannot_name_one_site(self):
        self.expect("must not name a single site_id", lambda d: self._org(d, "chs").__setitem__("site_id", "chs_wilton"))

    def test_travel_note_only_for_home_based(self):
        self.expect("only for volunteer_home", lambda d: self._role(d, "ah_dog_walking").__setitem__("travel_note", "x"))

    def test_town_reference_outside_ct(self):
        self.expect("reference point outside Connecticut", lambda d: d["geo"].__setitem__("ct_towns.csv", d["geo"]["ct_towns.csv"].replace("Branford,0917007310,41.280027", "Branford,0917007310,45.280027")))

    def test_missing_entry_for_a_record(self):
        self.expect("no entry for opportunity", lambda d: d["volunteer_locations"]["opportunity_locations"].pop())


if __name__ == "__main__":
    unittest.main()
