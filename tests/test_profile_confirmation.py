"""Profile confirmation (Session 5): model-assigned labels alone never make a fact trusted.

Deterministic tests on the REAL dataset with SYNTHETIC profiles; the run_assistant tests use a
MOCKED model (FunctionModel), not gpt-6-luna.
"""
import asyncio

from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from backend.agent import build_agent, run_assistant
from backend.data import get_dataset
from backend.matching import assess
from backend.schemas import AssistantRequest, VolunteerProfile
from backend.tools import AgentDeps, profile_facts, update_profile

DS = get_dataset()


def deps(texts, **confirmed):
    d = AgentDeps(dataset=DS, base_profile=VolunteerProfile(**confirmed))
    d.user_texts = list(texts)
    return d


def test_unquoted_eligibility_fact_is_a_suggestion_and_not_used():
    d = deps(["SYNTHETIC: I want to help cats"])
    update_profile(d, VolunteerProfile(age=26, commitment_months=12))  # model claims facts, no quotes
    assert d.profile.age is None and d.profile.commitment_months is None
    assert {f["field"]: f["status"] for f in profile_facts(d)} == {"age": "suggested", "commitment_months": "suggested"}
    a = assess(DS, DS.opportunities["gnhcp_grant_writing"], d.profile)
    assert [r.status for r in a.requirements if r.requirement == "minimum_age"] == ["needs_confirmation"]


def test_fabricated_or_mismatched_quotes_are_rejected():
    d = deps(["SYNTHETIC: I'm twenty-six and can help for about a year"])
    update_profile(d, VolunteerProfile(age=26), {"age": "I'm 26"})                         # not in the text
    update_profile(d, VolunteerProfile(commitment_months=12), {"commitment_months": "about a year"})  # no number
    update_profile(d, VolunteerProfile(guardian_available=True), {"guardian_available": "help for about a year"})
    assert d.profile.age is None and d.profile.commitment_months is None and d.profile.guardian_available is None
    notes = {f["field"]: f["note"] for f in profile_facts(d)}
    assert "not found" in notes["age"] and "number" in notes["commitment_months"] and "guardian" in notes["guardian_available"]


def test_verified_quote_is_used_but_marked_for_confirmation():
    d = deps(["SYNTHETIC: I'm 26, about 3 hours a week"])
    update_profile(d, VolunteerProfile(age=26, available_hours=3, hours_period="week"),
                   {"age": "I'm 26", "available_hours": "about 3 hours a week", "hours_period": "3 hours a week"})
    facts = {f["field"]: f for f in profile_facts(d)}
    assert facts["age"]["status"] == "from_message" and facts["age"]["used_in_assessment"]
    assert facts["age"]["supporting_text"] == "I'm 26" and "confirm" in facts["age"]["note"].lower()


def test_inferred_non_eligibility_fact_guides_search_but_is_labelled():
    d = deps(["SYNTHETIC: weekday afternoons work for me"])
    update_profile(d, VolunteerProfile(available_days=["mon", "tue", "wed", "thu", "fri"]),
                   {"available_days": "weekday afternoons"}, inferred_fields=["available_days"])
    assert d.profile.available_days == ["mon", "tue", "wed", "thu", "fri"]
    assert d.provenance["available_days"] == "suggested"


def _mock_agent():
    state = {"calls": 0}

    def fn(messages, info: AgentInfo):
        state["calls"] += 1
        if state["calls"] == 1:
            return ModelResponse(parts=[ToolCallPart("assess_profile", {
                "opportunity_ids": ["gnhcp_grant_writing"], "profile": {}})])
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {
            "answer": "Grant writing at GNHCP may fit.",
            "recommendations": [{"opportunity_id": "gnhcp_grant_writing",
                                 "stated_fit": "meets_published_requirements_checked", "why_relevant": "x"}]})])
    return build_agent(FunctionModel(fn))


def test_message_facts_persist_across_turns_only_when_reverified():
    hist = [{"role": "user", "content": "SYNTHETIC: I'm 26 and love cats"}, {"role": "assistant", "content": "ok"}]
    good = AssistantRequest(message="SYNTHETIC: what about writing grants?", history=hist,
                            message_facts=[{"field": "age", "value": 26, "supporting_text": "I'm 26"}])
    resp, _ = asyncio.run(run_assistant(good, agent=_mock_agent()))
    assert resp.ok and resp.profile_used.age == 26
    assert [f.status for f in resp.profile_facts if f.field == "age"] == ["from_message"]
    forged = AssistantRequest(message="SYNTHETIC: what about writing grants?", history=hist,
                              message_facts=[{"field": "age", "value": 26, "supporting_text": "I'm 62"}])
    resp2, trace2 = asyncio.run(run_assistant(forged, agent=_mock_agent()))
    # The unverifiable carried fact is not used: the age check needs confirmation, so the mock's
    # "meets" claim is rejected and no recommendation is shown.
    assert trace2["profile_used"].get("age") is None
    assert resp2.ok is False and resp2.recommendations == []


def test_form_confirmed_profile_is_trusted():
    req = AssistantRequest(message="SYNTHETIC: anything with cats?", profile={"age": 26})
    resp, _ = asyncio.run(run_assistant(req, agent=_mock_agent()))
    assert resp.ok and resp.profile_provenance == {"age": "confirmed"}


def test_declined_fields_are_never_applied_from_chat():
    d = deps(["SYNTHETIC: I'm 26"])
    d.declined = {"age"}
    update_profile(d, VolunteerProfile(age=26), {"age": "I'm 26"})
    assert d.profile.age is None and d.profile_changes[-1]["status"] == "declined_by_person"
