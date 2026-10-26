"""Location memory, area limits, distance claims and uncertain-rule wording in the agent layer.

Deterministic checks on the REAL dataset with SYNTHETIC profiles, plus MOCKED-model runs (PydanticAI
FunctionModel). They do not prove real gpt-6-luna behavior; real runs are in output/agent_runs/.
"""
import asyncio
from types import SimpleNamespace

from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from backend.agent import build_agent, follow_ups, run_assistant, validate_output
from backend.data import get_dataset
from backend.matching import assess
from backend.schemas import AgentOutput, AssistantRequest, ChatTurn, MessageFact, VolunteerProfile
from backend.tools import AgentDeps, find_alternatives_tool, search_opportunities, update_location_preferences

DS = get_dataset()


def deps(texts=("SYNTHETIC",), **confirmed):
    return AgentDeps(dataset=DS, base_profile=VolunteerProfile(**confirmed), user_texts=list(texts))


def call(fn, d, **kw):
    return asyncio.run(fn(SimpleNamespace(deps=d), **kw))


def assessed(d, *ids):
    for oid in ids:
        d.assessed[oid] = assess(DS, DS.opportunities[oid], d.profile)
        d.returned_ids.add(oid)
    return d


# ---------------------------------------------------------------- memory: what the person wrote, verified
def test_town_zip_and_transport_need_the_persons_own_words():
    d = deps(["I'm 23, love dogs, and don't have a car. I need something close to where I live.",
              "I live in New Haven.", "Right next to Yale SOM."])
    call(update_location_preferences, d, lives_in_town="New Haven", has_car=False, wants_nearby=True,
         supporting_quotes={"town": "I live in New Haven", "has_car": "don't have a car",
                            "wants_nearby": "I need something close"})
    assert (d.profile.town, d.profile.has_car, d.profile.wants_nearby) == ("New Haven", False, True)
    assert d.provenance["town"] == "from_message"
    # a ZIP can never be inferred from a landmark: the quote must contain the digits
    res = call(update_location_preferences, d, zip_code="06511", supporting_quotes={"zip_code": "Right next to Yale SOM"})
    assert d.profile.zip_code is None and res["location_context"]["zip_area"]["status"] == "not_provided"


def test_invalid_zip_is_reported_and_never_stored():
    d = deps(["my zip is 6511"])
    res = call(update_location_preferences, d, zip_code="6511", supporting_quotes={"zip_code": "my zip is 6511"})
    assert res["zip_input_problem"]["status"] == "invalid_format" and d.profile.zip_code is None


def test_zip_typed_by_the_person_is_used_and_can_be_changed():
    d = deps(["06511", "sorry, it's 06513"])
    call(update_location_preferences, d, zip_code="06511", supporting_quotes={"zip_code": "06511"})
    assert d.profile.zip_code == "06511"
    first = call(search_opportunities, d, query="Dog walker")["results"][0]["travel"]["distance_shown_on_page"]
    call(update_location_preferences, d, zip_code="06513", supporting_quotes={"zip_code": "it's 06513"},
         corrected_fields=["zip_code"])
    assert d.profile.zip_code == "06513"
    second = call(search_opportunities, d, query="Dog walker")["results"][0]["travel"]["distance_shown_on_page"]
    assert first != second  # the estimate follows the new ZIP


def test_remembered_facts_survive_beyond_the_history_window():
    """Facts quoted in messages older than the 10-turn history still verify via earlier_user_messages."""
    req = AssistantRequest(
        message="Anything else?", history=[ChatTurn(role="user", content=f"msg {i}") for i in range(10)],
        message_facts=[MessageFact(field="town", value="New Haven", supporting_text="I live in New Haven")],
        earlier_user_messages=["I live in New Haven."])

    state = {"i": 0}

    def fn(messages, info: AgentInfo):  # one broad search, then a plain answer
        state["i"] += 1
        if state["i"] % 2:
            return ModelResponse(parts=[ToolCallPart("search_opportunities", {})])
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {"answer": "SYNTHETIC reply"})])
    resp, _ = asyncio.run(run_assistant(req, agent=build_agent(FunctionModel(fn))))
    assert resp.profile_used.town == "New Haven"
    req2 = req.model_copy(update={"earlier_user_messages": []})
    resp2, _ = asyncio.run(run_assistant(req2, agent=build_agent(FunctionModel(fn))))
    assert resp2.profile_used.town is None  # without the person's words, the fact is not trusted


# ---------------------------------------------------------------- follow-up questions
def test_location_follow_ups_and_no_repeated_town_question():
    d = deps(has_car=False)
    assert follow_ups(d, [])[0] == "Which town do you live in?"
    d = deps(has_car=False, town="New Haven")
    qs = follow_ups(d, ["Which town do you live in?", "How many hours a week could you give?"])
    assert qs[0] == "Do you need to stay within New Haven, or can you travel to nearby towns?"
    assert not any("Which town" in q for q in qs) and any("ZIP" in q for q in qs)
    d = deps(has_car=False, town="New Haven", volunteer_only_in="New Haven", prefers_not_to_share_zip=True)
    assert follow_ups(d, []) == []  # answered and declined: nothing asked again


def test_dead_end_under_an_area_limit_offers_activity_or_wider_area():
    d = assessed(deps(age=23, town="New Haven", volunteer_only_in="New Haven"), "fnhas_dog_handler")
    out = AgentOutput(answer="The New Haven dog handler role is closed.",
                      non_matches=[{"opportunity_id": "fnhas_dog_handler", "stated_fit": "needs_confirmation",
                                    "why_not": "closed"}])
    q = follow_ups(d, [], out)
    assert q and "different kind of activity, or widen the area beyond New Haven" in q[0]
    assert follow_ups(d, ["Would you consider widening the area?"], out) == ["Would you consider widening the area?"]


def test_answer_may_not_ask_for_a_known_town():
    d = assessed(deps(town="New Haven"), "gnhcp_grant_writing")
    out = AgentOutput(answer="Which town do you live in?")
    assert any("do not ask for their town again" in p for p in validate_output(d, out))


# ---------------------------------------------------------------- explicit area limit
def test_search_always_applies_the_persons_area_limit():
    d = deps(volunteer_only_in="New Haven")
    res = call(search_opportunities, d, animals=["dogs"], only_in_town="North Haven", include_closed=True)
    assert res["results"] and all(r["towns"] == ["New Haven"] for r in res["results"])
    assert "limit" in (res["note"] or "")
    # by default the closed New Haven dog roles are left out; broader options keep the limit too
    default = call(search_opportunities, d, animals=["dogs"])
    assert default["results"] == [] and default["closed_matches_left_out"] >= 1
    assert all(DS.confirmed_in_town(DS.opportunities[r["opportunity_id"]], "New Haven") for r in default["broader_options"])


def test_recommendations_outside_the_limit_are_rejected_unless_labelled():
    d = assessed(deps(age=23, volunteer_only_in="New Haven"), "ah_cat_socializing", "fnhas_dog_handler")
    d.alternatives_called = True
    rec = [{"opportunity_id": "ah_cat_socializing", "stated_fit": "needs_confirmation", "why_relevant": "cats"}]
    assert any("not confirmed to be in New Haven" in p
               for p in validate_output(d, AgentOutput(answer="Try The Animal Haven.", recommendations=rec)))
    ok = AgentOutput(answer="Nothing open is confirmed in New Haven. If you'd widen the area, The Animal Haven "
                            "may fit; its 12-month rule is listed on an older form and needs confirmation.",
                     outside_area_ids=["ah_cat_socializing"])
    assert validate_output(d, ok) == []
    closed = AgentOutput(answer="x", outside_area_ids=["fnhas_dog_handler"])
    assert any("is in New Haven" in p or "not a suitable" in p for p in validate_output(d, closed))


def test_an_organizations_town_alone_does_not_satisfy_a_town_limit():
    """FNHAS adoption events happen 'throughout the Greater New Haven area': not confirmed in New Haven."""
    o = DS.opportunities["fnhas_adoption_events"]
    assert DS.towns_of(o) == ["New Haven"] and not DS.confirmed_in_town(o, "New Haven")
    assert DS.confirmed_in_town(DS.opportunities["fnhas_dog_handler"], "New Haven")
    d = assessed(deps(age=23, volunteer_only_in="New Haven"), "fnhas_adoption_events")
    d.alternatives_called = True
    rec = _rec("fnhas_adoption_events", d.assessed["fnhas_adoption_events"].overall_status)
    assert any("not confirmed to be in New Haven" in p
               for p in validate_output(d, AgentOutput(answer="Adoption events may fit.", recommendations=rec)))
    assert validate_output(d, AgentOutput(answer="Event venues aren't published; if you'd widen the area, adoption "
                                                 "events may fit.", outside_area_ids=["fnhas_adoption_events"])) == []


def test_find_alternatives_separates_outside_area_candidates():
    d = deps(age=23, volunteer_only_in="New Haven")
    res = call(find_alternatives_tool, d)
    assert all(DS.confirmed_in_town(DS.opportunities[a["opportunity_id"]], "New Haven") for a in res["alternatives"])
    assert res["outside_area_candidates"] and "widen" in res["note"]


def test_outside_area_ids_need_a_limit():
    d = assessed(deps(age=23), "ah_cat_socializing")
    assert any("only for when the person limited" in p
               for p in validate_output(d, AgentOutput(answer="x", outside_area_ids=["ah_cat_socializing"])))


# ---------------------------------------------------------------- distances and travel claims
def _rec(oid, fit):
    return [{"opportunity_id": oid, "stated_fit": fit, "why_relevant": "x"}]


def test_prose_may_not_state_distances_even_correct_ones():
    d = assessed(deps(age=23, zip_code="06511"), "ah_cat_socializing")
    d.alternatives_called = True
    rec = _rec("ah_cat_socializing", "needs_confirmation")
    ok = AgentOutput(answer="See the estimated distance on each option; it's a straight-line estimate.", recommendations=rec)
    assert validate_output(d, ok) == []
    for claim in ["The Animal Haven is approx. 6 miles from your ZIP area.", "It's about 4.2 miles away.",
                  "It's six miles away.", "It's under a mile away.", "About 10 km."]:
        assert any("do not write distances" in p for p in
                   validate_output(d, AgentOutput(answer=claim, recommendations=rec))), claim


def test_swapped_distance_claim_is_rejected_and_cards_keep_their_own_distance():
    """Regression: two options at different distances (Animal Haven ~6 mi, Branford Compassion Club ~9 mi from the
    test ZIP). A claim that swaps them used to pass because '6' matched *some* returned distance."""
    d = assessed(deps(age=23, zip_code="06511"), "ah_cat_socializing", "bcc_shelter_care")
    d.alternatives_called = True
    recs = _rec("ah_cat_socializing", d.assessed["ah_cat_socializing"].overall_status) + \
        _rec("bcc_shelter_care", d.assessed["bcc_shelter_care"].overall_status)
    swapped = AgentOutput(answer="Branford Compassion Club is approx. 6 miles from your ZIP area; The Animal Haven "
                                 "is approx. 9 miles.", recommendations=recs)
    assert any("do not write distances" in p for p in validate_output(d, swapped))
    from backend.agent import assemble_response
    good = AgentOutput(answer="Two cat options; see each estimate.", recommendations=recs)
    resp = assemble_response(DS, d, good, "t")
    shown = {r.opportunity_id: r.location.distance.label for r in resp.recommendations}
    assert shown == {"ah_cat_socializing": "North Haven · About 6 miles away",
                     "bcc_shelter_care": "North Branford · About 9 miles away"}


def test_walkability_transit_and_travel_time_claims_are_rejected():
    d = assessed(deps(age=23), "ah_cat_socializing")
    d.alternatives_called = True
    rec = _rec("ah_cat_socializing", "needs_confirmation")
    for claim in ["It's walkable from downtown.", "It's convenient for you.", "You can get there by bus.",
                  "It's a 15-minute drive."]:
        assert validate_output(d, AgentOutput(answer=claim, recommendations=rec)), claim
    assert validate_output(d, AgentOutput(answer="I can't confirm whether it's reachable by bus; check a map.",
                                          recommendations=rec)) == []


# ---------------------------------------------------------------- uncertain rules stay uncertain
def test_uncertain_animal_haven_rules_must_be_described_as_uncertain():
    d = assessed(deps(age=23), "ah_dog_walking")
    d.alternatives_called = True
    rec = _rec("ah_dog_walking", d.assessed["ah_dog_walking"].overall_status)
    flat = AgentOutput(answer="Animal Haven requires a 12-month commitment and 2 hours per week.", recommendations=rec)
    assert any("needs confirmation" in p for p in validate_output(d, flat))
    leading = AgentOutput(answer="Animal Haven dog walking may fit.", recommendations=rec,
                          follow_up_questions=["Can you meet the required 12 months?"])
    assert any("leading question" in p for p in validate_output(d, leading))
    hedged = AgentOutput(answer="An older Animal Haven form lists a 12-month commitment and 2 hours per week; "
                                "confirm whether these still apply.", recommendations=rec,
                         follow_up_questions=["How many months could you commit?"])
    assert validate_output(d, hedged) == []
    # another organization's PUBLISHED 12-month rule in its own sentence is not treated as uncertain
    assessed(d, "fnhas_dog_bathing")
    both = AgentOutput(answer="An older Animal Haven form lists a 12-month commitment; confirm it. Friends of the New "
                              "Haven Animal Shelter publishes 8 hours per month and a 12-month commitment.",
                       recommendations=rec + _rec("fnhas_dog_bathing", d.assessed["fnhas_dog_bathing"].overall_status))
    assert validate_output(d, both) == []


# ---------------------------------------------------------------- end to end (mocked model)
def test_response_carries_locations_outside_area_and_context():
    steps = [("tool", "update_location_preferences", {
                 "lives_in_town": "New Haven", "zip_code": "06511", "volunteer_only_in": "New Haven",
                 "supporting_quotes": {"town": "I live in New Haven", "zip_code": "06511",
                                       "volunteer_only_in": "I need to stay in New Haven"}}),
             ("tool", "assess_profile", {"opportunity_ids": ["ah_cat_socializing", "fnhas_dog_handler"],
                                         "profile": {"age": 23}, "supporting_quotes": {"age": "I'm 23"}}),
             ("tool", "find_alternatives", {}),
             ("final", {"answer": "No open role is confirmed in New Haven. The New Haven dog handler role is closed. "
                                  "If you'd widen the area, The Animal Haven may fit.",
                        "non_matches": [{"opportunity_id": "fnhas_dog_handler", "stated_fit": "needs_confirmation",
                                         "why_not": "Applications are closed."}],
                        "outside_area_ids": ["ah_cat_socializing"]})]
    state = {"i": 0}

    def fn(messages, info: AgentInfo):
        step = steps[min(state["i"], len(steps) - 1)]
        state["i"] += 1
        name = step[1] if step[0] == "tool" else info.output_tools[0].name
        return ModelResponse(parts=[ToolCallPart(name, step[-1])])
    msg = "SYNTHETIC: I'm 23. I live in New Haven, ZIP 06511. I need to stay in New Haven."
    resp, trace = asyncio.run(run_assistant(AssistantRequest(message=msg), agent=build_agent(FunctionModel(fn))))
    assert resp.ok, resp.answer
    out = resp.outside_area_suggestions[0]
    assert out.location.in_chosen_area is False and out.location.distance.label == "North Haven · About 6 miles away"
    nm = resp.explained_non_matches[0]
    assert nm.location.in_chosen_area is True and nm.assessment.application_status.status == "explicitly_closed"
    assert resp.location_context["volunteer_only_in"] == "New Haven"
    assert "06511" not in str(resp.location_context)
