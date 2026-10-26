"""Session 12: closed roles left out of discovery, status labels, and the five location categories.

Deterministic checks on the REAL dataset with SYNTHETIC profiles; agent tests use a MOCKED model. ZIPs are test values.
"""
import asyncio
import dataclasses
from types import SimpleNamespace

from fastapi.testclient import TestClient
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from backend.agent import build_agent, run_assistant, validate_output
from backend.api import app
from backend.data import get_dataset
from backend.geo import Geo, get_geo
from backend.matching import assess, find_alternatives
from backend.schemas import AgentOutput, AssistantRequest, VolunteerProfile
from backend.tools import AgentDeps, search_opportunities

DS, GEO = get_dataset(), get_geo()
client = TestClient(app)
ZC = GEO.check_zip("06511")
CLOSED = {oid for oid, o in DS.opportunities.items() if o.application_status == "explicitly_closed"}


def deps(**p):
    return AgentDeps(dataset=DS, base_profile=VolunteerProfile(**p), user_texts=["SYNTHETIC"])


# ---------------------------------------------------------------- 1) closed roles left out of discovery
def test_closed_records_are_left_out_of_lists_searches_and_alternatives():
    assert CLOSED  # FNHAS handlers/foster, Branford general, CHS Newington/Waterford fosters
    for params in ({}, {"scope": "all"}, {"scope": "all", "record_type": ["described_volunteer_role",
                                                                          "interest_area_only",
                                                                          "independent_support_activity"]}):
        r = client.get("/api/opportunities", params=params).json()   # Home and Explore both use this route
        assert not CLOSED & {x["opportunity_id"] for x in r["results"]}
    r = client.get("/api/opportunities").json()
    assert r["closed_hidden"] >= 1 and r["count"] == len(r["results"])
    every = client.get("/api/opportunities", params={"scope": "all", "include_closed": True}).json()
    assert CLOSED <= {x["opportunity_id"] for x in every["results"]}  # still in the dataset
    res = asyncio.run(search_opportunities(SimpleNamespace(deps=deps(age=30)), include_wider_connecticut=True))
    assert not CLOSED & {x["opportunity_id"] for x in res["results"] + res["broader_options"]}
    alts = find_alternatives(DS, VolunteerProfile(age=30, include_wider_connecticut=True), limit=64)
    assert not CLOSED & {a["opportunity_id"] for a in alts}


def test_old_application_status_parameter_is_ignored():
    with_param = client.get("/api/opportunities", params={"application_status": "explicitly_closed"}).json()
    assert with_param["count"] == client.get("/api/opportunities").json()["count"]
    assert not CLOSED & {x["opportunity_id"] for x in with_param["results"]}


# ---------------------------------------------------------------- 2) direct question + detail page for a closed role
def test_closed_role_detail_page_still_works():
    d = client.get("/api/opportunities/fnhas_cat_handler").json()
    assert d["application_status"] == "explicitly_closed" and d["application_status_label"] == "Applications closed"
    assert [a["label"] for a in d["next_actions"]] == ["Visit volunteer page", "Contact organization"]   # never "Apply"


def test_named_closed_role_is_explained_not_recommended():
    d = deps(age=30)
    named = asyncio.run(search_opportunities(SimpleNamespace(deps=d), query="cat handler", include_closed=True))
    assert [r["opportunity_id"] for r in named["results"]] == ["fnhas_cat_handler"]
    d.assessed["fnhas_cat_handler"] = assess(DS, DS.opportunities["fnhas_cat_handler"], d.profile)
    d.alternatives_called = True
    rec = [{"opportunity_id": "fnhas_cat_handler", "stated_fit": d.assessed["fnhas_cat_handler"].overall_status,
            "why_relevant": "cats"}]
    assert any("closed applications" in p for p in validate_output(d, AgentOutput(answer="x", recommendations=rec)))


def test_mocked_direct_question_flow_returns_non_match_and_open_alternatives():
    steps = [("tool", "search_opportunities", {"query": "cat handler", "include_closed": True}),
             ("tool", "assess_profile", {"opportunity_ids": ["fnhas_cat_handler"], "profile": {"age": 30},
                                         "supporting_quotes": {"age": "I'm 30"}}),
             ("tool", "find_alternatives", {"activities": ["animal_socialization"]}),
             ("final", None)]
    state = {"i": 0}

    def fn(messages, info: AgentInfo):
        step = steps[min(state["i"], len(steps) - 1)]
        state["i"] += 1
        if step[0] == "tool":
            return ModelResponse(parts=[ToolCallPart(step[1], step[2])])
        alts = [p for m in messages for p in getattr(m, "parts", []) if getattr(p, "tool_name", "") == "find_alternatives"
                and hasattr(p, "content") and isinstance(p.content, dict)]
        alt_id = alts[-1].content["alternatives"][0]["opportunity_id"]
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {
            "answer": "The New Haven cat handler role is closed; here is a cat option to ask about.",
            "non_matches": [{"opportunity_id": "fnhas_cat_handler", "stated_fit": "needs_confirmation",
                             "why_not": "Applications are closed."}],
            "alternative_ids": [alt_id]})])
    resp, _ = asyncio.run(run_assistant(AssistantRequest(message="SYNTHETIC: I'm 30. Is the New Haven cat handler role open?"),
                                        agent=build_agent(FunctionModel(fn))))
    assert resp.ok, resp.answer
    assert resp.explained_non_matches[0].assessment.application_status.label == "Applications closed"
    assert resp.alternatives and all(a.assessment.application_status.status != "explicitly_closed" for a in resp.alternatives)


# ---------------------------------------------------------------- 3) status labels
def test_status_labels_and_next_steps():
    acc = client.get("/api/opportunities/paws_cat_volunteer").json()
    unc = client.get("/api/opportunities/ah_dog_walking").json()
    assert acc["application_status_label"] == "Accepting applications"
    assert [a["label"] for a in acc["next_actions"]] == ["Visit volunteer page", "Contact organization"]
    assert unc["application_status_label"] == "Availability not confirmed"
    assert [(a["label"], a["url"]) for a in unc["next_actions"]] == [
        ("Visit volunteer page", "https://theanimalhavenct.org/volunteer/"),
        ("Contact organization", "https://theanimalhavenct.org/contact/")]


def test_apply_label_only_for_an_application_page_that_is_not_closed():
    """No current destination is an application form, so nobody gets 'Apply'. A SYNTHETIC check of the rule:"""
    assert not any(a["kind"] == "application" for o in DS.opportunities.values() for a in DS.next_actions(o))
    o = DS.opportunities["ah_dog_walking"].model_copy(update={"application_or_information_url": DS.sources["ah_application"].url})
    assert DS.next_actions(o)[0]["label"] == "Apply on organization's website"   # 'Volunteer Application' page
    closed = DS.opportunities["fnhas_cat_handler"].model_copy(update={"application_or_information_url": DS.sources["ah_application"].url})
    assert DS.next_actions(closed)[0]["label"] == "Visit volunteer page"          # closed: never 'Apply'
    lst = client.get("/api/opportunities").json()["results"]
    assert all(x["next_actions"] and x["next_actions"][0]["kind"] == "volunteer_page" for x in lst)


# ---------------------------------------------------------------- 5-9) location categories (Session 16 labels)
def test_verified_site():
    d, loc = GEO.distance("ah_dog_walking", ZC), GEO.location_of("ah_dog_walking")
    assert loc["kind"] == "verified_site" and loc["maps_url"] and loc["evidence"]
    assert d["label"] == "North Haven · About 6 miles away" and d["type"] == "volunteering_site" and d["secondary"] is None


def test_organization_address_fallback():
    loc, d = GEO.location_of("gnhcp_direct_care"), GEO.distance("gnhcp_direct_care", ZC)
    assert loc["kind"] == "organization_location" and loc["organization_site"]["label"] == "GNHCP Center"
    assert loc["location_status"] == "candidate_site_unconfirmed"   # the original classification is preserved
    assert d["label"] == "Organization: Northford · About 11 miles away" and d["secondary"] == "Activity location may differ"
    assert d["type"] == "organization_location" and not loc["coordinates_verified"]


def test_multi_site_organization_with_a_role_site():
    d = GEO.distance("chs_newington_laundry", ZC)   # the role page places it at CHS Newington
    assert d["type"] == "volunteering_site" and d["label"] == "Newington · About 29 miles away"


def test_multi_site_organization_without_a_role_site_uses_the_nearest_named_site():
    loc, d = GEO.location_of("chs_collection_drive"), GEO.distance("chs_collection_drive", ZC)
    assert loc["kind"] == "organization_location" and loc["organization_site"] is None
    assert [s["label"] for s in loc["other_sites"]] == ["CHS Newington adoption center", "CHS Waterford (Quaker Hill)", "CHS Wilton"]
    assert d["type"] == "organization_nearest_site" and d["label"] == "Nearest organization site: CHS Wilton · About 27 miles away"
    assert d["secondary"] == "Activity location may differ"
    # the nearest site depends on the ZIP area (06375 is Quaker Hill)
    assert GEO.distance("chs_collection_drive", GEO.check_zip("06375"))["label"].startswith("Nearest organization site: CHS Waterford")


def test_town_only_location_uses_a_town_reference_point():
    """No current record is town-only, so a SYNTHETIC variant: a role with its own published town whose organization
    has no single verified site (Cat Tales has only a P.O. box)."""
    g = Geo(GEO.zcta, GEO.towns, GEO.meta, GEO.sites, GEO.roles, GEO.org_locs,
            {**GEO.role_towns, "cattales_shelter_care": "Middletown"}, GEO.role_orgs)
    loc, d = g.location_of("cattales_shelter_care"), g.distance("cattales_shelter_care", ZC)
    assert loc["kind"] == "town_only" and d["type"] == "town_reference"
    assert d["label"].startswith("Middletown town center · About ") and d["secondary"] == "Activity location may differ"
    assert sum(GEO.location_of(o)["kind"] == "town_only" for o in GEO.roles) == 0   # real data: none


def test_home_based_never_ranked_as_zero():
    loc, d = GEO.location_of("chs_foster_wilton"), GEO.distance("chs_foster_wilton", ZC)
    assert loc["kind"] == "home_based" and loc["headline"] == "Help from your home" and "pick up supplies" in loc["travel_note"]
    assert d["type"] == "related_site" and d["label"] == "Supply pickup: CHS Wilton · About 27 miles away"
    assert d["sort_miles"] > 0                                          # travel to this site is sourced
    ref = GEO.distance("paws_foster", ZC)                                 # no travel stated
    assert ref["type"] == "organization_reference" and ref["sort_miles"] is None and ref["label"].startswith("Organization: Norwalk")


def test_no_verified_physical_address_gives_no_distance():
    loc, d = GEO.location_of("cattales_shelter_care"), GEO.distance("cattales_shelter_care", ZC)
    assert loc["kind"] == "unknown" and d["label"] is None and d["sort_miles"] is None


def test_every_record_has_one_kind_and_no_org_estimate_promotes_a_record():
    kinds = {o: GEO.location_of(o)["kind"] for o in DS.opportunities}
    assert set(kinds.values()) <= {"verified_site", "organization_location", "town_only", "home_based", "unknown"}
    assert {o for o, k in kinds.items() if k == "verified_site"} == {
        o for o, r in GEO.roles.items() if r["location_status"] == "verified_site"}


# ---------------------------------------------------------------- 10) one combined distance sort
def test_distance_sort_is_one_list_with_records_without_distance_last():
    d = deps(age=30, zip_code="06511")
    res = asyncio.run(search_opportunities(SimpleNamespace(deps=d), sort_by_closest=True, include_wider_connecticut=True,
                                           include_other_ways_to_help=True))
    keys = [GEO.distance(r["opportunity_id"], ZC)["sort_miles"] for r in res["results"]]
    known = [k for k in keys if k is not None]
    assert known == sorted(known) and keys[:len(known)] == known       # unrounded order; unknowns after
    kinds = {GEO.distance(r["opportunity_id"], ZC)["type"] for r in res["results"]}
    assert "organization_location" in kinds and "volunteering_site" in kinds   # one list, both labelled


# ---------------------------------------------------------------- 11) explicit town limits
def test_organization_address_does_not_satisfy_a_town_limit():
    o = DS.opportunities["fnhas_adoption_events"]   # FNHAS is located in New Haven; events are "throughout" the area
    assert GEO.location_of("fnhas_adoption_events")["kind"] == "organization_location"
    assert not DS.confirmed_in_town(o, "New Haven")


# ---------------------------------------------------------------- 12) changing or clearing the ZIP
def test_changing_or_clearing_the_zip():
    a = client.post("/api/location/estimates", json={"zip_code": "06511", "opportunity_ids": ["fnhas_dog_handler"]}).json()
    b = client.post("/api/location/estimates", json={"zip_code": "06513", "opportunity_ids": ["fnhas_dog_handler"]}).json()
    assert a["estimates"]["fnhas_dog_handler"]["distance"]["display"] != b["estimates"]["fnhas_dog_handler"]["distance"]["display"]
    c = client.post("/api/location/estimates", json={"zip_code": "", "opportunity_ids": ["fnhas_dog_handler"]}).json()
    assert c["zip_area"]["status"] == "not_provided" and c["estimates"]["fnhas_dog_handler"]["distance"]["display"] is None


# ---------------------------------------------------------------- 13) wording
def test_about_wording_everywhere_and_no_approx():
    est = client.post("/api/location/estimates", json={"zip_code": "06511", "opportunity_ids": list(DS.opportunities)}).json()
    shown = [e["distance"]["label"] for e in est["estimates"].values() if e["distance"]["label"]]
    assert shown and not any("Approx" in s for s in shown) and all(" · About " in s or " · Less than" in s for s in shown)
    near = client.post("/api/location/estimates", json={"zip_code": "06511", "opportunity_ids": ["fnhas_dog_handler"]}).json()
    assert near["estimates"]["fnhas_dog_handler"]["distance"]["label"] == "New Haven · About 1 mile away"
    g = dataclasses.replace(ZC, lat=41.3312, lon=-72.9402)   # a point next to 81 Fournier Street
    assert GEO.distance("fnhas_dog_handler", g)["label"] == "New Haven · Less than 1 mile away"
