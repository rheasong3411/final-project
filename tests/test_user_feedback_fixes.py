"""Problems confirmed while developer-retesting the prospective user's feedback (2026-10-26).

Real dataset, SYNTHETIC re-enactment of the participant's situation, MOCKED model. (The participant did not retest.)
"""
import asyncio

from fastapi.testclient import TestClient
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from backend.agent import build_agent, run_assistant, validate_output
from backend.api import app
from backend.data import get_dataset
from backend.geo import get_geo
from backend.matching import assess
from backend.schemas import AgentOutput, AssistantRequest, ChatTurn, MessageFact, VolunteerProfile
from backend.tools import AgentDeps, profile_facts, quote_supports, update_profile

DS = get_dataset()
client = TestClient(app)
M1 = ("i’m 25 and live in New Haven. i like cats, don’t have a car, and can volunteer for 2–3 hours on Saturday or "
      "Sunday mornings. what could fit me?")


def run(req, steps):
    state = {"i": 0}

    def fn(messages, info: AgentInfo):
        step = steps[min(state["i"], len(steps) - 1)]
        state["i"] += 1
        name = step[1] if step[0] == "tool" else info.output_tools[0].name
        return ModelResponse(parts=[ToolCallPart(name, step[-1])])
    return asyncio.run(run_assistant(req, agent=build_agent(FunctionModel(fn))))[0]


# The model reads "2–3 hours on Saturday or Sunday mornings" as 3 hours PER WEEK and a 3-hour session, and marks the
# days and times as "inferred" (what made them unverified suggestions in the reproduction).
GUESSING_MODEL = [
    ("tool", "update_location_preferences", {"lives_in_town": "New Haven", "has_car": False,
                                             "supporting_quotes": {"lives_in_town": "live in New Haven",
                                                                   "has_car": "don’t have a car"}}),
    ("tool", "search_opportunities", {}),
    ("tool", "assess_profile", {"opportunity_ids": ["ah_cat_socializing", "bcc_shy_cat_socializing"],
                                "profile": {"age": 25, "animal_preferences": ["cats"], "available_days": ["sat", "sun"],
                                            "available_times": ["morning"], "available_hours": 3, "hours_period": "week",
                                            "max_session_hours": 3},
                                "supporting_quotes": {"age": "i’m 25", "animal_preferences": "i like cats",
                                                      "available_days": "Saturday or Sunday mornings",
                                                      "available_times": "Saturday or Sunday mornings",
                                                      "available_hours": "2–3 hours", "max_session_hours": "2–3 hours",
                                                      "hours_period": "2–3 hours on Saturday or Sunday mornings"},
                                "inferred_fields": ["available_days", "available_times"]}),
    ("final", {"answer": "Here are some cat-focused options."})]


def first_turn():
    return run(AssistantRequest(message=M1), GUESSING_MODEL)


# ---------------------------------------------------------------- profile capture and retention
def test_stated_answers_are_captured_and_the_range_is_kept():
    r = first_turn()
    p = r.profile_used
    assert r.ok and (p.age, p.town, p.has_car) == (25, "New Haven", False)
    assert p.animal_preferences == ["cats"] and p.available_days == ["sat", "sun"] and p.available_times == ["morning"]
    assert (p.available_hours, p.available_hours_max) == (2, 3)               # "2–3 hours" kept as a range
    assert p.hours_period is None and p.max_session_hours is None             # nothing silently chosen
    assert p.zip_code is None                                                 # no ZIP invented
    statuses = {f.field: f.status for f in r.profile_facts}
    assert statuses["available_days"] == statuses["available_times"] == "from_message"   # used, not "suggestions"
    assert statuses["has_car"] == "from_message"                              # "no car" is shown, so it is kept
    assert not [f for f in r.profile_facts if f.status == "suggested"]        # misreadings not offered back
    assert r.follow_up_questions[0] == "When you say 2–3 hours, is that each week, each month, or for a single visit?"


def test_answers_are_retained_on_follow_up_messages():
    r1 = first_turn()
    facts = [MessageFact(field=f.field, value=f.value, supporting_text=f.supporting_text)
             for f in r1.profile_facts if f.status == "from_message"]
    hist = [ChatTurn(role="user", content=M1), ChatTurn(role="assistant", content=r1.answer)]
    r2 = run(AssistantRequest(message="what are the requirements for the Animal Haven cat role?", message_facts=facts,
                              history=hist, asked_follow_ups=r1.follow_up_questions),
             [("tool", "search_opportunities", {}),
              ("tool", "assess_profile", {"opportunity_ids": ["ah_cat_socializing"], "profile": {}}),
              ("final", {"answer": "Here are its requirements."})])
    p = r2.profile_used
    assert (p.age, p.town, p.has_car, p.animal_preferences) == (25, "New Haven", False, ["cats"])
    assert (p.available_days, p.available_times, p.available_hours, p.available_hours_max) == (["sat", "sun"], ["morning"], 2, 3)
    # the optional questions already asked are not repeated
    assert len(r1.follow_up_questions) == 2       # turn 1: the hours question and the area question
    assert not set(r2.follow_up_questions) & set(r1.follow_up_questions)
    assert not any("stay within" in q or "each week, each month" in q for q in r2.follow_up_questions)


def test_a_period_is_only_taken_from_explicit_words():
    d = AgentDeps(dataset=DS, base_profile=VolunteerProfile(), user_texts=["2 hours on weekends", "2 hours a week"])
    assert not quote_supports(d, "hours_period", "week", "2 hours on weekends")[0]   # "weekend" is not "per week"
    assert quote_supports(d, "hours_period", "week", "2 hours a week")[0]


def test_period_and_visit_length_are_used_when_stated():
    steps = [("tool", "search_opportunities", {}), ("final", {"answer": "ok"})]
    r = run(AssistantRequest(message="I can do 2–3 hours a week, mornings."), steps)
    assert (r.profile_used.available_hours, r.profile_used.available_hours_max, r.profile_used.hours_period) == (2, 3, "week")
    r = run(AssistantRequest(message="I can do 2–3 hours per visit."), steps)
    assert r.profile_used.max_session_hours == 3 and r.profile_used.available_hours is None


def test_existing_correction_behaviour_is_preserved_for_ranges():
    d = AgentDeps(dataset=DS, base_profile=VolunteerProfile(), user_texts=["actually 4 hours a week"],
                  current_message="actually 4 hours a week")
    update_profile(d, VolunteerProfile(available_hours=2, available_hours_max=3), {"available_hours": "2–3 hours",
                                                                                  "available_hours_max": "2–3 hours"})
    assert d.profile.available_hours is None   # quote not in the person's messages here: not applied


# ---------------------------------------------------------------- matching with ranges and schedules
def test_hours_range_is_decided_only_when_both_ends_agree():
    def hrs(lo, hi, per):
        a = assess(DS, DS.opportunities["fnhas_cat_handler"],
                   VolunteerProfile(age=25, available_hours=lo, available_hours_max=hi, hours_period=per))
        return next(r for r in a.requirements if r.requirement == "minimum_hours")
    assert hrs(2, 3, "week").status == "met"                     # 8 h/month: even 2 h/week covers it
    assert hrs(1, 3, "week").status == "needs_confirmation"      # part of the range meets it
    assert hrs(2, 3, "month").status == "not_met"                # even the upper end is below 8 h/month
    assert "2–3 hours per month" in hrs(2, 3, "month").explanation


def test_stated_days_appear_on_every_relevant_card_without_inventing_a_schedule():
    p = VolunteerProfile(age=25, available_days=["sat", "sun"], available_times=["morning"])
    a = assess(DS, DS.opportunities["ah_cat_socializing"], p)
    s = next(r for r in a.requirements if r.requirement == "recurring_schedule")
    assert s.status == "needs_confirmation" and s.applicability == "not_published"
    assert "Saturday or Sunday mornings" in s.explanation
    assert not any(r.requirement == "recurring_schedule" for r in
                   assess(DS, DS.opportunities["ah_cat_socializing"], VolunteerProfile(age=25)).requirements)


# ---------------------------------------------------------------- consistent, simpler explanations
def test_conflicting_age_wording_is_simple_and_values_stay_available():
    def age(a):
        return next(r for r in assess(DS, DS.opportunities["ah_cat_socializing"], VolunteerProfile(age=a)).requirements
                    if r.requirement == "minimum_age")
    assert age(25).explanation == "Your age meets both published minimums; confirm the organization's current rule."
    assert age(25).status == "needs_confirmation" and age(25).listed_value_matched
    assert age(19).explanation == ("Your age meets one published minimum (18+) but not the other (21+); confirm the "
                                   "organization's current rule.")
    assert age(15).status == "not_met"                                      # still not recommended
    r = age(25)
    assert r.published_requirement == "18+ or 21+ (published minimums differ)" and len({e.source_id for e in r.evidence}) == 2


def test_guardian_still_does_not_override_age():
    a = assess(DS, DS.opportunities["ah_cat_socializing"], VolunteerProfile(age=15, guardian_available=True))
    assert a.overall_status == "not_met"


def test_card_text_must_describe_the_one_year_rule_as_the_card_does():
    d = AgentDeps(dataset=DS, base_profile=VolunteerProfile(age=25), user_texts=["x"])
    d.assessed["ah_cat_socializing"] = assess(DS, DS.opportunities["ah_cat_socializing"], d.profile)
    d.alternatives_called = True
    bad = AgentOutput(answer="Here is a cat role.", recommendations=[{
        "opportunity_id": "ah_cat_socializing", "stated_fit": d.assessed["ah_cat_socializing"].overall_status,
        "why_relevant": "Cat socializing; requires a one-year commitment."}])
    assert any("card text" in p for p in validate_output(d, bad))
    ok = AgentOutput(answer="Here is a cat role.", recommendations=[{
        "opportunity_id": "ah_cat_socializing", "stated_fit": d.assessed["ah_cat_socializing"].overall_status,
        "why_relevant": "Cat socializing; its one-year commitment is listed on an older form, so confirm it."}])
    assert not any("card text" in p for p in validate_output(d, ok))


# ---------------------------------------------------------------- locations and directions
def test_town_options_follow_the_selected_scope():
    f = client.get("/api/filters").json()["towns_by_scope"]
    assert not {"Norwalk", "Newington"} & set(f["greater_new_haven"]) and {"Norwalk", "Newington"} <= set(f["all"])
    assert set(f["greater_new_haven"]) < set(f["all"])


def test_directions_link_to_verified_destinations_only():
    g = get_geo()
    site = g.location_of("ah_cat_socializing")["site"]
    assert site["directions_url"].startswith("https://www.google.com/maps/dir/?api=1&destination=")
    assert "origin" not in site["directions_url"] and "travelmode" not in site["directions_url"]  # person chooses
    org = g.location_of("fnhas_adoption_events")
    assert org["kind"] == "organization_location" and org["organization_site"]["directions_url"]
    unknown = g.location_of("cattales_shelter_care")
    assert unknown["kind"] == "unknown" and unknown["site"] is None and unknown["organization_site"] is None


def test_unknowns_stay_unknown_and_availability_stays_separate():
    a = assess(DS, DS.opportunities["bcc_shy_cat_socializing"],
               VolunteerProfile(age=25, available_days=["sat"], available_times=["morning"]))
    assert a.application_status.status == "needs_confirmation"            # not "accepting applications"
    assert any("not the same as free" in c for c in a.costs) or a.costs   # unknown fees never become free
    assert a.overall_status != "meets_published_requirements_checked"     # weekend availability is a question
