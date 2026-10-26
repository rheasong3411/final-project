"""Regression tests for the Session 4 backend corrections.

Deterministic tests use the REAL dataset with SYNTHETIC profiles. Tests that drive the agent use a
MOCKED model (PydanticAI FunctionModel) and do not prove real gpt-6-luna behavior.
"""
import asyncio
import json
from types import SimpleNamespace

from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from backend.agent import build_agent, run_assistant, validate_output
from backend.data import get_dataset
from backend.matching import assess
from backend.schemas import AgentOutput, AssistantRequest, VolunteerProfile
from backend.tools import AgentDeps, search_opportunities, update_profile

from conftest import item

DS = get_dataset()


def deps(**app_profile):
    return AgentDeps(dataset=DS, base_profile=VolunteerProfile(**app_profile))


def scripted(steps):
    """Mock model that returns the given steps in order: ('tool', name, args) or ('final', args)."""
    state = {"i": 0}

    def fn(messages, info: AgentInfo):
        step = steps[min(state["i"], len(steps) - 1)]
        state["i"] += 1
        if step[0] == "tool":
            return ModelResponse(parts=[ToolCallPart(step[1], step[2])])
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, step[1])])
    return FunctionModel(fn)


def run(steps, message="SYNTHETIC test message", profile=None):
    return asyncio.run(run_assistant(AssistantRequest(message=message, profile=profile), agent=build_agent(scripted(steps))))


# ---------------------------------------------------------------- 1) profile consistency
def test_two_tool_calls_with_different_profile_fields_stay_consistent():
    """Call 1 gives age; call 2 adds hours. The earlier assessment must be recomputed under the final profile."""
    stale_output = {"answer": "New Haven fundraising may fit.",
                    "recommendations": [{"opportunity_id": "fnhas_fundraising_education",
                                         "stated_fit": "needs_confirmation", "why_relevant": "fundraising"}]}
    fixed_output = {"answer": "GNHCP grant writing meets the published requirements we checked. New Haven "
                              "fundraising needs at least 8 hours a month, more than the 1 hour a week you gave.",
                    "recommendations": [{"opportunity_id": "gnhcp_grant_writing",
                                         "stated_fit": "meets_published_requirements_checked",
                                         "why_relevant": "desk-based help"}],
                    "non_matches": [{"opportunity_id": "fnhas_fundraising_education", "stated_fit": "not_met",
                                     "why_not": "hours below the published minimum"}],
                    "cited_source_ids": ["gnhcp_volunteer", "fnhas_volunteer"]}
    resp, trace = run([
        ("tool", "assess_profile", {"opportunity_ids": ["fnhas_fundraising_education"], "profile": {"age": 30},
                                    "supporting_quotes": {"age": "I'm 30"}}),
        ("tool", "assess_profile", {"opportunity_ids": ["gnhcp_grant_writing"],
                                    "profile": {"available_hours": 1, "hours_period": "week"},
                                    "supporting_quotes": {"available_hours": "1 hour a week",
                                                          "hours_period": "1 hour a week"}}),
        ("final", stale_output),   # stale: written from call 1's result -> must be rejected
        ("final", fixed_output),
    ], message="SYNTHETIC: I'm 30 and have about 1 hour a week.")
    assert resp.ok, resp.error
    retries = [p for s in trace["steps"] for p in s["parts"] if p["type"] == "retry_prompt"]
    assert retries and "not_met" in json.dumps(retries[0]["content"])
    final = resp.profile_used
    assert final.age == 30 and final.available_hours == 1 and final.hours_period == "week"
    fp = final.fingerprint()
    shown = resp.recommendations + resp.explained_non_matches
    assert all(r.assessment.profile_fingerprint == fp for r in shown)
    nm = resp.explained_non_matches[0].assessment
    assert nm.overall_status == "not_met" and item(nm, "minimum_hours").profile_fields_used["available_hours"] == 1
    assert resp.recommendations[0].assessment.overall_status == "meets_published_requirements_checked"
    assert "not_met" not in resp.answer and "8 hours a month" in resp.answer  # explanation matches the result
    assert resp.profile_provenance == {"age": "from_message", "available_hours": "from_message",
                                       "hours_period": "from_message"}
    assert {f.field: f.supporting_text for f in resp.profile_facts if f.used_in_assessment} == {
        "age": "I'm 30", "available_hours": "1 hour a week", "hours_period": "1 hour a week"}


def test_confirmed_form_answers_win_over_chat():
    d = deps(age=30, town="New Haven")  # form-confirmed
    d.user_texts = ["SYNTHETIC: actually I'm 16"]
    ev = update_profile(d, VolunteerProfile(age=16), {"age": "I'm 16"}, corrected_fields=["age"])
    assert d.profile.age == 30 and ev[0]["status"] == "conflicts_with_confirmed"
    assert d.provenance["age"] == "confirmed"


def test_chat_facts_need_a_verbatim_quote_and_corrections_recompute():
    d = deps()
    d.user_texts = ["SYNTHETIC: I'm 26 and live in New Haven", "SYNTHETIC: actually I'm 16, sorry"]
    d.assessed["gnhcp_grant_writing"] = assess(DS, DS.opportunities["gnhcp_grant_writing"], d.profile)
    update_profile(d, VolunteerProfile(age=26), {"age": "I'm 26"})
    assert d.profile.age == 26 and d.provenance["age"] == "from_message"
    assert d.assessed["gnhcp_grant_writing"].overall_status == "meets_published_requirements_checked"
    update_profile(d, VolunteerProfile(age=16), {"age": "I'm 16"})                       # not marked as correction
    assert d.profile.age == 26 and d.suggestions["age"]["value"] == 16
    update_profile(d, VolunteerProfile(age=16), {"age": "I'm 16"}, corrected_fields=["age"])
    assert d.profile.age == 16
    a = d.assessed["gnhcp_grant_writing"]  # invalidated by the change and recomputed
    assert a.profile_fingerprint == d.profile.fingerprint() and a.overall_status == "not_met"


def test_stale_assessment_is_rejected_by_validator():
    d = deps(age=30)
    d.assessed["gnhcp_grant_writing"] = assess(DS, DS.opportunities["gnhcp_grant_writing"], d.profile)
    d.profile = VolunteerProfile(age=16)  # simulate a profile change without recomputation
    out = AgentOutput(answer="x", recommendations=[{"opportunity_id": "gnhcp_grant_writing",
                                                    "stated_fit": "meets_published_requirements_checked",
                                                    "why_relevant": "x"}])
    assert any("no current assessment" in p for p in validate_output(d, out))


# ---------------------------------------------------------------- 2) one-time session requirements
def test_one_time_session_unknown_needs_confirmation_even_with_weekly_hours(run):
    a = run("chs_newington_group_trails", age=30, available_hours=10, hours_period="week")
    s = item(a, "session_length")
    assert s.status == "needs_confirmation" and "3–4 hours" in s.published_requirement
    assert item(a, "minimum_hours") is None and item(a, "minimum_commitment_months") is None


def test_one_time_session_clearly_insufficient_and_ranges(run):
    assert item(run("chs_newington_group_trails", age=30, max_session_hours=2), "session_length").status == "not_met"
    assert item(run("chs_newington_group_trails", age=30, max_session_hours=3.5), "session_length").status == "needs_confirmation"
    assert item(run("chs_newington_group_trails", age=30, max_session_hours=4), "session_length").status == "met"


def test_session_rule_respects_applicability():
    o = DS.opportunities["chs_newington_group_trails"]
    app = dict(o.requirement_applicability)
    app["time_commitment"] = app["time_commitment"].model_copy(update={"status": "needs_confirmation"})
    shaky = o.model_copy(update={"requirement_applicability": app})
    a = assess(DS, shaky, VolunteerProfile(age=30, max_session_hours=1))
    s = item(a, "session_length")
    assert s.status == "needs_confirmation" and a.overall_status != "not_met"


# ---------------------------------------------------------------- 3) alternatives and evidence
def test_unassessed_alternative_is_rejected():
    d = deps(age=30)
    d.returned_ids.add("bcc_fundraising")  # appeared in a search, never assessed
    out = AgentOutput(answer="x", alternative_ids=["bcc_fundraising"])
    assert any("no current assessment" in p for p in validate_output(d, out))


def test_not_met_or_closed_alternative_is_rejected_but_can_be_a_non_match():
    d = deps(age=19)
    d.assessed["ah_dog_walking"] = assess(DS, DS.opportunities["ah_dog_walking"], d.profile)     # not_met (21+)
    d.assessed["fnhas_cat_handler"] = assess(DS, DS.opportunities["fnhas_cat_handler"], d.profile)  # closed
    bad = AgentOutput(answer="x", alternative_ids=["ah_dog_walking", "fnhas_cat_handler"])
    assert sum("not a suitable alternative" in p for p in validate_output(d, bad)) == 2
    ok = AgentOutput(answer="Dog walking at The Animal Haven needs age 21.",
                     non_matches=[{"opportunity_id": "ah_dog_walking", "stated_fit": "not_met", "why_not": "age"}])
    d.alternatives_called = True
    assert validate_output(d, ok) == []


def test_unrelated_but_valid_source_is_rejected():
    d = deps(age=30)
    d.assessed["gnhcp_grant_writing"] = assess(DS, DS.opportunities["gnhcp_grant_writing"], d.profile)
    out = AgentOutput(answer="x", recommendations=[{"opportunity_id": "gnhcp_grant_writing",
                                                    "stated_fit": "meets_published_requirements_checked",
                                                    "why_relevant": "x"}],
                      cited_source_ids=["paws_volunteer"])  # exists, but unrelated to GNHCP
    assert any("does not belong" in p for p in validate_output(d, out))


def test_response_includes_sources_for_alternatives_and_checklists():
    resp, _ = run([
        ("tool", "find_alternatives", {"profile": {"age": 12}, "activities": ["dog_walking"]}),
        ("final", {"answer": "Here are labelled alternatives.", "alternative_ids": ["branford_tails_to_trails"],
                   "checklist_for_ids": ["branford_tails_to_trails"]}),
    ])
    assert resp.ok, resp.error
    have = {s.source_id for s in resp.sources}
    alt = resp.alternatives[0].assessment
    assert {s for r in alt.requirements for s in r.source_ids} <= have
    assert {s for c in resp.application_checklists for st in c.steps for s in st.source_ids} <= have


# ---------------------------------------------------------------- 4) search coverage
def _search(d, **kw):
    return asyncio.run(search_opportunities(SimpleNamespace(deps=d), **kw))


def test_residence_town_is_not_a_location_restriction():
    d = deps(age=26, town="New Haven")
    broad = _search(d, animals=["cats"])
    towns = {t for r in broad["results"] for t in r["towns"]}
    assert len(towns - {"New Haven"}) >= 1 and broad["location_filter"].startswith("none")
    narrow = _search(d, animals=["cats"], only_in_town="New Haven", include_closed=True)
    assert narrow["results"] and all(r["towns"] == ["New Haven"] for r in narrow["results"])
    assert all(r["geographic_scope"] == "greater_new_haven" for r in broad["results"])  # never widened silently


def test_non_closed_first_and_broader_options_when_all_closed():
    d = deps(age=26)
    # Session 10: a town limit keeps only roles whose OWN location is published there. The New Haven cat roles
    # with their own location are explicitly closed, so broader options (same limit) are offered instead.
    # Session 12: closed roles are left out of searches unless asked for by name (include_closed=True).
    res = _search(d, animals=["cats"], only_in_town="New Haven")
    assert res["results"] == [] and res["closed_matches_left_out"] == 1  # fnhas_cat_handler
    named = _search(d, animals=["cats"], only_in_town="New Haven", include_closed=True)
    assert {r["application_status"] for r in named["results"]} == {"explicitly_closed"}
    mixed = _search(d)  # mixed statuses: non-closed listed first
    statuses = [r["application_status"] for r in mixed["results"]]
    assert statuses == sorted(statuses, key=lambda st: st == "explicitly_closed")
    wide = _search(d, animals=["cats"])  # >8 matches: closed roles are pushed past the shown results
    assert all(r["application_status"] != "explicitly_closed" for r in wide["results"])
    closed_only = _search(d, query="cat handler")  # New Haven cat handler role: explicitly closed, left out
    assert closed_only["count"] == 0 and closed_only["closed_matches_left_out"] == 1
    assert closed_only["broader_options"] and all(r["application_status"] != "explicitly_closed"
                                                  for r in closed_only["broader_options"])
    assert all(r["geographic_scope"] == "greater_new_haven" for r in closed_only["broader_options"])


def test_cannot_conclude_with_only_closed_options_without_broadening():
    d = deps(age=26, available_hours=3, hours_period="week", commitment_months=12)
    _search(d, query="cat handler")  # narrow search only
    d.assessed["fnhas_cat_handler"] = assess(DS, DS.opportunities["fnhas_cat_handler"], d.profile)
    out = AgentOutput(answer="The cat handler role is closed; nothing else fits.",
                      recommendations=[{"opportunity_id": "fnhas_cat_handler", "stated_fit": "needs_confirmation",
                                        "why_relevant": "cats"}])
    assert any("broaden the search" in p for p in validate_output(d, out))


def test_schedule_fit_and_eligibility_claims_rejected():
    d = deps(age=30)
    d.assessed["gnhcp_grant_writing"] = assess(DS, DS.opportunities["gnhcp_grant_writing"], d.profile)
    rec = [{"opportunity_id": "gnhcp_grant_writing", "stated_fit": "meets_published_requirements_checked",
            "why_relevant": "x"}]
    assert any("schedules are unresolved" in p for p in
               validate_output(d, AgentOutput(answer="Weekday afternoons fit your schedule.", recommendations=rec)))
    assert any("eligible" in p for p in
               validate_output(d, AgentOutput(answer="You are eligible for this role.", recommendations=rec)))
    assert validate_output(d, AgentOutput(answer="Check whether the schedule fits your availability.",
                                          recommendations=rec)) == []
