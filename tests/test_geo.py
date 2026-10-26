"""ZIP areas, verified volunteering locations, distances and location privacy. No model calls.

All ZIPs and profiles are SYNTHETIC test inputs. 06511 is the public ZIP of Yale SOM's area, used as a
test value only.
"""
import json
import math

from fastapi.testclient import TestClient

from backend.api import app
from backend.config import DATA_DIR
from backend.data import get_dataset
from backend.geo import get_geo, haversine_miles, round_miles, town_matches
from backend.run_log import redact_locations, save_trace
from backend.schemas import VolunteerProfile

GEO = get_geo()
DS = get_dataset()
client = TestClient(app)


# ---------------------------------------------------------------- ZIP validation
def test_connecticut_zip_keeps_its_leading_zero():
    zc = GEO.check_zip("06511")
    assert zc.status == "supported" and "06511" not in zc.message and zc.lat and zc.lon
    assert VolunteerProfile(zip_code="06511").zip_code == "06511"  # stays a string
    assert all(z.startswith("06") and len(z) == 5 for z in GEO.zcta)  # the file kept leading zeros


def test_invalid_formats_are_distinguished_from_missing_zips():
    for bad in ["6511", "065111", "06 511", "o6511", "06511a", ""]:
        assert GEO.check_zip(bad).status in ("invalid_format", "not_provided"), bad
    assert GEO.check_zip("6511").status == "invalid_format"
    for absent in ["06520", "06501"]:  # Yale's unique ZIP and a New Haven P.O. Box ZIP: real, but no ZCTA
        zc = GEO.check_zip(absent)
        assert zc.status == "not_in_dataset" and "P.O. Box" in zc.message


def test_outside_connecticut_explains_coverage_and_never_widens():
    zc = GEO.check_zip("10001")
    assert zc.status == "outside_coverage" and "Connecticut" in zc.message and "Greater New Haven" in zc.message


def test_public_zip_check_never_returns_coordinates():
    assert set(GEO.check_zip("06511").public()) == {"status", "message"}


# ---------------------------------------------------------------- distance math
def test_haversine_matches_an_independent_formula():
    # spherical law of cosines, written separately, on the same sphere
    def cosines(lat1, lon1, lat2, lon2):
        p1, p2, dl = map(math.radians, (lat1, lat2, lon2 - lon1))
        return 3958.8 * math.acos(math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl))
    a = (41.31727, -72.926373)          # ZCTA 06511 internal point (Census 2026 Gazetteer)
    b = (41.371339530426, -72.840054131161)  # 89 Mill Rd, North Haven (Census Geocoder)
    assert abs(haversine_miles(*a, *b) - cosines(*a, *b)) < 1e-6
    # 1 degree of latitude on this sphere = 2*pi*3958.8/360 miles
    assert abs(haversine_miles(41, -72, 42, -72) - 2 * math.pi * 3958.8 / 360) < 1e-9


def test_rounding_never_implies_false_precision():
    assert round_miles(0.4) == (0.5, "Less than 1 mile")
    assert round_miles(1.2)[1] == "About 1 mile" and round_miles(1.3)[1] == "About 1.5 miles"
    assert round_miles(9.7)[1] == "About 9.5 miles" and round_miles(9.8)[1] == "About 10 miles"
    assert round_miles(14.4)[1] == "About 14 miles" and round_miles(28.6)[1] == "About 29 miles"


def test_representative_distances_from_zip_06511():
    zc = GEO.check_zip("06511")
    got = {oid: GEO.distance(oid, zc)["label"] for oid in
           ["fnhas_dog_handler", "ah_dog_walking", "bcc_shelter_care", "branford_general_volunteer"]}
    assert got == {"fnhas_dog_handler": "New Haven · About 1 mile away",
                   "ah_dog_walking": "North Haven · About 6 miles away",
                   "bcc_shelter_care": "North Branford · About 9 miles away",
                   "branford_general_volunteer": "Branford · About 9 miles away"}
    d = GEO.distance("ah_dog_walking", zc)
    assert d["type"] == "volunteering_site" and d["explanation"] == (
        "Distances are straight-line estimates from your ZIP area. For some activities, the distance is to the "
        "organization; the activity location may differ.")
    assert 5.5 < d["sort_miles"] < 6.25 and d["miles"] == 6.0   # sorted on the unrounded value


def test_unverified_locations_never_get_a_volunteering_site_distance():
    zc = GEO.check_zip("06511")
    for oid in ("gnhcp_direct_care", "ah_administrative", "paws_dog_walker", "fnhas_foster", "chs_collection_drive"):
        d = GEO.distance(oid, zc)
        assert d["type"] != "volunteering_site" and "volunteering site" not in (d["display"] or "")
        assert GEO.location_of(oid)["maps_url"] is None and not GEO.location_of(oid)["coordinates_verified"]


# ---------------------------------------------------------------- location data integrity
def test_every_record_has_a_location_status_and_only_verified_sites_have_coordinates():
    loc = json.loads((DATA_DIR / "volunteer_locations.json").read_text())
    roles = {r["opportunity_id"]: r for r in loc["opportunity_locations"]}
    assert set(roles) == set(DS.opportunities)
    sites = {s["site_id"]: s for s in loc["sites"]}
    for r in roles.values():
        if r["location_status"] == "verified_site":
            s = sites[r["site_id"]]
            assert s["geocode"]["match_count"] == 1 and r["evidence"], r["opportunity_id"]
            assert s["organization_id"] == DS.opportunities[r["opportunity_id"]].organization_id
            assert DS.towns_of(DS.opportunities[r["opportunity_id"]]) == [s["town"]]
        else:
            assert r["site_id"] is None
    for s in sites.values():
        assert "P.O. Box" not in s["address"] and "PO Box" not in s["address"]
        assert s["address_evidence"] and all(e["accessed_at"].startswith("2026-10-25") for e in s["address_evidence"])


def test_maps_link_sends_only_the_destination():
    url = GEO.location_of("ah_dog_walking")["maps_url"]
    assert url.startswith("https://www.google.com/maps/search/?api=1&query=89+Mill+Road")
    assert "origin" not in url and "06511" not in url


def test_town_matching_is_exact():
    assert town_matches("New Haven", "New Haven") and not town_matches("Haven", "North Haven")
    assert not town_matches("Branford", "North Branford")
    assert town_matches("North Branford", "Northford (village of North Branford)")
    assert {o.opportunity_id for o in DS.search(town="Branford", include_closed=True)} >= {"branford_general_volunteer"}
    assert "bcc_shelter_care" not in {o.opportunity_id for o in DS.search(town="Branford", include_closed=True)}


def test_location_fields_do_not_change_the_assessment_fingerprint():
    base = VolunteerProfile(age=23, town="New Haven")
    moved = VolunteerProfile(age=23, town="New Haven", zip_code="06511", has_car=False, wants_nearby=True,
                             volunteer_only_in="New Haven")
    assert base.fingerprint() == moved.fingerprint()
    assert base.fingerprint() != VolunteerProfile(age=23, town="Branford").fingerprint()  # town affects fees


# ---------------------------------------------------------------- API
def test_estimates_endpoint_statuses_and_order_of_unknowns():
    ids = ["ah_dog_walking", "fnhas_dog_handler", "gnhcp_direct_care", "not_a_real_id"]
    r = client.post("/api/location/estimates", json={"zip_code": "06511", "opportunity_ids": ids}).json()
    assert r["zip_area"]["status"] == "supported" and set(r["estimates"]) == set(ids[:3])
    assert r["estimates"]["gnhcp_direct_care"]["distance"]["label"] == "Organization: Northford · About 11 miles away"
    assert r["estimates"]["gnhcp_direct_care"]["distance"]["secondary"] == "Activity location may differ"
    assert r["estimates"]["fnhas_dog_handler"]["maps_url"]
    for z, st in [("6511", "invalid_format"), ("06520", "not_in_dataset"), ("10001", "outside_coverage")]:
        body = client.post("/api/location/estimates", json={"zip_code": z, "opportunity_ids": ids[:1]}).json()
        assert body["zip_area"]["status"] == st and body["estimates"]["ah_dog_walking"]["distance"]["status"] == "no_zip_area"


def test_list_and_detail_include_location_without_any_zip():
    r = client.get("/api/opportunities").json()
    assert all("location" in x for x in r["results"])
    d = client.get("/api/opportunities/fnhas_dog_handler").json()
    assert d["location"]["site"]["address"].startswith("81 Fournier Street") and d["location"]["maps_url"]


def test_closeness_never_changes_fit_or_status():
    a1 = client.post("/api/opportunities/fnhas_dog_handler/assess", json={"profile": {"age": 23}}).json()
    a2 = client.post("/api/opportunities/fnhas_dog_handler/assess",
                     json={"profile": {"age": 23, "zip_code": "06511"}}).json()
    assert a1["overall_status"] == a2["overall_status"] and a1["application_status"] == a2["application_status"]
    assert a2["application_status"]["status"] == "explicitly_closed"  # 1 mile away, still closed


# ---------------------------------------------------------------- privacy
def test_saved_traces_redact_zip_codes(tmp_path):
    trace = {"run_id": "t1", "input": {"message": "My ZIP is 06511.", "profile": {"zip_code": "06511"}},
             "steps": [{"args": {"zip_code": "06511", "supporting_quotes": {"zip_code": "06511"}}}]}
    text = save_trace(trace, tmp_path).read_text()
    assert "06511" not in text and "[ZIP redacted]" in text
    assert redact_locations({"latency_s": 12345.6, "id": "ab12345cd"}) == {"latency_s": 12345.6, "id": "ab12345cd"}
