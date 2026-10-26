"""Session 15: Explore and the assistant share one filter; hard constraints are never relaxed silently.

Deterministic checks on the REAL dataset with SYNTHETIC profiles; agent runs use a MOCKED model.
"""
import asyncio
import itertools
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from backend.agent import build_agent, run_assistant, validate_output
from backend.api import app
from backend.config import MAX_SEARCH_RESULTS
from backend.data import get_dataset
from backend.matching import assess
from backend.schemas import AgentOutput, AssistantRequest, VolunteerProfile
from backend.tools import AgentDeps, search_opportunities, update_profile

DS = get_dataset()
client = TestClient(app)
ALL_TYPES = ["described_volunteer_role", "interest_area_only", "independent_support_activity"]


def deps(texts=("SYNTHETIC",), **p):
    return AgentDeps(dataset=DS, base_profile=VolunteerProfile(**p), user_texts=list(texts))


def tool(d, **kw):
    return asyncio.run(search_opportunities(SimpleNamespace(deps=d), **kw))


# ---------------------------------------------------------------- 1) the same explicit filters, the same candidates
CASES = list(itertools.product(
    [False, True],                                     # Greater New Haven vs wider Connecticut
    [None, "one_time", "recurring", "variable"],       # published commitment
    [None, ["dogs"], ["cats"], ["not_applicable"]],    # animals (not_applicable = no animal contact)
    [False, True],                                     # described roles only vs + interest/independent records
))


@pytest.mark.parametrize("wider,commitment,animals,others", CASES)
def test_explore_and_assistant_return_the_same_candidates(wider, commitment, animals, others):
    params = {"scope": "all" if wider else "greater_new_haven",
              "record_type": ALL_TYPES if others else ["described_volunteer_role"]}
    if commitment:
        params["commitment_type"] = commitment
    if animals:
        params["animal"] = animals
    explore = client.get("/api/opportunities", params=params).json()
    agent = tool(deps(), include_wider_connecticut=wider, commitment=commitment, animals=animals,
                 include_other_ways_to_help=others)
    assert agent["count"] == explore["count"]
    assert [r["opportunity_id"] for r in agent["results"]] == [r["opportunity_id"] for r in explore["results"]][:MAX_SEARCH_RESULTS]
    assert explore["closed_hidden"] == agent["closed_matches_left_out"]


@pytest.mark.parametrize("town", ["North Haven", "North Branford", "Newington", "Norwalk", "New Haven"])
def test_town_filter_means_the_roles_own_town_on_both_pages(town):
    explore = client.get("/api/opportunities", params={"scope": "all", "town": town}).json()
    agent = tool(deps(), only_in_town=town, include_wider_connecticut=True)
    assert agent["count"] == explore["count"]
    assert all(DS.opportunities[r["opportunity_id"]].location_town == town for r in explore["results"])
    # a home town is never a filter
    home = tool(deps(town=town), include_wider_connecticut=True)
    assert home["count"] == client.get("/api/opportunities", params={"scope": "all"}).json()["count"]


def test_town_options_are_published_role_towns_of_non_closed_roles():
    towns = client.get("/api/filters").json()["towns"]
    assert "New Haven" not in towns   # its only role-level New Haven records are closed
    assert set(towns) == {o.location_town for o in DS.opportunities.values()
                          if o.location_town and o.application_status != "explicitly_closed"}


def test_unknown_commitment_never_matches_a_commitment_filter():
    for c in ("one_time", "recurring", "variable"):
        r = client.get("/api/opportunities", params={"scope": "all", "commitment_type": c}).json()
        assert all(x["commitment_type"] == c for x in r["results"])


# ---------------------------------------------------------------- 2) strict one-time requests
def test_one_time_in_greater_new_haven_finds_nothing_and_reports_what_exists_elsewhere():
    r = tool(deps(), commitment="one_time")
    assert r["count"] == 0 and r["results"] == []
    assert [m["opportunity_id"] for m in r["matches_outside_scope"]] == ["chs_newington_group_trails"]
    assert r["commitment_unknown_leads"] and all(
        DS.opportunities[x["opportunity_id"]].commitment_type in ("unknown", "variable") for x in r["commitment_unknown_leads"])


def test_only_one_time_is_a_hard_constraint_but_a_preference_is_not():
    msg = "I can only do a one-time project of a few hours with my coworkers."
    d = deps([msg])
    update_profile(d, VolunteerProfile(commitment_required="one_time", max_session_hours=3),
                   {"commitment_required": "I can only do a one-time project", "max_session_hours": "a few hours"})
    assert d.profile.commitment_required == "one_time"           # quoted, with "only" and "one-time"
    assert d.profile.max_session_hours is None                    # "a few hours" is not a number
    pref = deps(["I'd prefer something one-time if possible."])
    update_profile(pref, VolunteerProfile(commitment_required="one_time"),
                   {"commitment_required": "I'd prefer something one-time"})
    assert pref.profile.commitment_required is None               # a preference, not "only": not applied
    # the profile's hard constraint is applied to every search, even if the model omits it
    assert tool(d)["commitment_filter"] == "one_time"


def test_unknown_commitment_records_cannot_be_offered_as_one_time_matches():
    d = deps(["I can only do a one-time project"], commitment_required="one_time")
    for oid in ("fnhas_adoption_events", "ah_fundraising_events"):
        d.assessed[oid] = assess(DS, DS.opportunities[oid], d.profile)
    d.alternatives_called = True
    rec = [{"opportunity_id": "fnhas_adoption_events", "stated_fit": d.assessed["fnhas_adoption_events"].overall_status,
            "why_relevant": "events"}]
    assert any("does not publish a 'one_time' commitment" in p
               for p in validate_output(d, AgentOutput(answer="x", recommendations=rec)))
    ok = AgentOutput(answer="I couldn't find a confirmed one-time opportunity matching your requirements.",
                     ask_about_ids=["fnhas_adoption_events"])
    assert validate_output(d, ok) == []
    assert any("only for when the person has a hard" in p for p in validate_output(
        deps(), AgentOutput(answer="x", ask_about_ids=["fnhas_adoption_events"])))


def test_mocked_one_time_conversation_separates_uncertain_activities():
    msg = "I can only do a one-time project of a few hours with my coworkers."
    steps = [("tool", "assess_profile", {"opportunity_ids": ["fnhas_adoption_events"], "profile": {"commitment_required": "one_time"},
                                         "supporting_quotes": {"commitment_required": "I can only do a one-time project"}}),
             ("tool", "search_opportunities", {}),
             ("final", {"answer": "Here is what I found.", "ask_about_ids": ["fnhas_adoption_events"]})]
    state = {"i": 0}

    def fn(messages, info: AgentInfo):
        step = steps[min(state["i"], len(steps) - 1)]
        state["i"] += 1
        name = step[1] if step[0] == "tool" else info.output_tools[0].name
        return ModelResponse(parts=[ToolCallPart(name, step[-1])])
    resp, _ = asyncio.run(run_assistant(AssistantRequest(message=msg), agent=build_agent(FunctionModel(fn))))
    assert resp.ok, resp.answer
    assert resp.answer.startswith("I couldn't find a confirmed one-time opportunity matching your requirements.")
    assert resp.recommendations == [] and resp.alternatives == []
    assert resp.ask_about[0].why_relevant == "One-time participation and group availability need confirmation"
    assert any("Connecticut locations" in q for q in resp.follow_up_questions)   # offered, not done


def test_explicit_one_time_limit_is_detected_conservatively():
    from backend.agent import _HARD_COMMITMENT as H
    assert H.search("I can only do a one-time project of a few hours with my coworkers.")
    assert H.search("we can only manage a single event") and H.search("Just a one-off please")
    for text in ("I'd prefer a one-time thing", "I can only come once a week",
                 "I can only volunteer in North Haven, weekly is fine", "a fundraiser event sounds fun"):
        assert not H.search(text), text


def test_server_records_the_constraint_and_never_duplicates_the_gap_sentence():
    msg = "I can only do a one-time project of a few hours with my coworkers."
    model_answer = ("I couldn't find a confirmed one-time opportunity matching your requirements in Greater New Haven. "
                    "Want me to include other Connecticut locations?")
    steps = [("tool", "search_opportunities", {}), ("final", {"answer": model_answer})]
    state = {"i": 0}

    def fn(messages, info: AgentInfo):   # the model never mentions the constraint itself
        step = steps[min(state["i"], len(steps) - 1)]
        state["i"] += 1
        name = step[1] if step[0] == "tool" else info.output_tools[0].name
        return ModelResponse(parts=[ToolCallPart(name, step[-1])])
    resp, _ = asyncio.run(run_assistant(AssistantRequest(message=msg), agent=build_agent(FunctionModel(fn))))
    assert resp.ok and resp.profile_used.commitment_required == "one_time"
    assert resp.profile_used.max_session_hours is None
    gap = "I couldn't find a confirmed one-time opportunity matching your requirements."
    assert resp.answer == gap + " Want me to include other Connecticut locations?"   # exact wording, once
    assert resp.answer.lower().count("couldn't find a confirmed one-time") == 1
