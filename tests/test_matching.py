"""Deterministic matching on the REAL dataset with SYNTHETIC profiles. No model calls."""
import itertools

from backend.matching import checklist, find_alternatives
from backend.schemas import VolunteerProfile

from conftest import item


# 1) a minor with unknown guardian availability
def test_minor_unknown_guardian_needs_confirmation(run):
    a = run("branford_general_volunteer", age=14)  # published: all ages; under 16 with parent/guardian
    g = item(a, "guardian_requirement")
    assert g.status == "needs_confirmation" and g.profile_fields_used["guardian_available"] is None
    assert a.overall_status == "needs_confirmation"


def test_minor_guardian_answers(run):
    assert item(run("paws_families_for_felines", age=15, guardian_available=True, include_wider_connecticut=True),
                "guardian_requirement").status == "met"
    no = run("paws_families_for_felines", age=15, guardian_available=False)
    assert item(no, "guardian_requirement").status == "not_met" and no.overall_status == "not_met"


def test_minor_where_guardian_rule_not_published(run):
    g = item(run("bcc_fundraising", age=15), "guardian_requirement")
    assert g.status == "needs_confirmation" and g.applicability == "not_published"
    assert "does not mean a guardian is not required" in g.explanation


# 2) an adult for whom guardian requirements are unspecified
def test_adult_unspecified_guardian_not_called_not_required(run, ds):
    assert ds.opportunities["gnhcp_grant_writing"].guardian_requirement is None
    a = run("gnhcp_grant_writing", age=30)
    assert item(a, "guardian_requirement") is None  # not relevant for adults, and never invented
    text = " ".join([r.explanation for r in a.requirements] + a.notes).lower()
    assert "no guardian" not in text and "guardian not required" not in text
    assert a.overall_status == "meets_published_requirements_checked"
    assert "subject to the organization's confirmation" in a.overall_summary


# 3) Animal Haven's uncertain or conflicting requirements
def test_animal_haven_conflicting_age_between_versions_never_excludes(run):
    # Ages between the conflicting versions (18 and 21) stay uncertain. (Below EVERY version: see
    # test_conflicting_age_exclusions.py, changed 2026-10-26.)
    for age in (18, 19, 20):
        a = run("ah_cat_socializing", age=age)
        assert item(a, "minimum_age").status == "needs_confirmation"
        assert item(a, "minimum_age").applicability == "conflicting"
        assert a.overall_status != "not_met"
        quotes = [e.quote for e in item(a, "minimum_age").evidence]
        assert any("21" in q for q in quotes) and any("18" in q for q in quotes)  # both claims preserved


def test_animal_haven_meeting_every_version_still_needs_confirmation(run):
    # Owner-testing fix: matching every conflicting/older version is not a green "met". The status stays amber and
    # the numerical comparison is kept separately (listed_value_matched + a note).
    a = run("ah_cat_socializing", age=30, commitment_months=12)
    assert item(a, "minimum_age").status == "needs_confirmation" and item(a, "minimum_age").listed_value_matched
    assert a.overall_status != "meets_published_requirements_checked"
    assert item(a, "minimum_age").explanation == ("Your age meets both published minimums; confirm the organization's "
                                                  "current rule.")


def test_animal_haven_legacy_form_rules_raise_questions(run):
    a = run("ah_dog_walking", age=30, available_hours=1, hours_period="week", commitment_months=3)
    assert item(a, "minimum_hours").status == "needs_confirmation"            # 2 hrs/week from legacy form
    assert item(a, "minimum_commitment_months").status == "needs_confirmation"  # 12 months from legacy form
    assert a.overall_status == "needs_confirmation"
    sched = item(run("ah_shelter_cleaning", age=30), "recurring_schedule")
    assert sched.applicability == "needs_confirmation" and sched.status == "needs_confirmation"


def test_animal_haven_agreed_dog_walking_age_is_enforceable(run):
    a = run("ah_dog_walking", age=19)
    assert item(a, "minimum_age").status == "not_met" and a.overall_status == "not_met"


# 4) a one-time activity must not inherit a recurring commitment
def test_one_time_activity_has_no_recurring_rules(run):
    a = run("chs_newington_group_trails", age=30, commitment_months=0.5, available_hours=1, hours_period="month",
            include_wider_connecticut=True)
    reqs = {r.requirement for r in a.requirements}
    assert "minimum_hours" not in reqs and "minimum_commitment_months" not in reqs
    assert a.overall_status != "not_met"
    assert any("One-time activity" in n and "3-4 hours, one time" in n for n in a.notes)
    assert not any("6 month" in r.explanation for r in a.requirements)


# 5) missing hours or commitment information
def test_missing_answers_are_not_failures(run):
    a = run("fnhas_adoption_events", age=30)
    assert item(a, "minimum_hours").status == "needs_confirmation"
    assert item(a, "minimum_commitment_months").status == "needs_confirmation"
    assert a.overall_status == "needs_confirmation"


def test_unpublished_hours_are_not_unrestricted(run):
    a = run("gnhcp_grant_writing", age=30, available_hours=0.5, hours_period="month")
    assert any("No minimum hours are published (not the same as 'no minimum')" in n for n in a.notes)


def test_documented_hours_conversion(run):
    # requirement 8 h/month (New Haven, applicable)
    assert item(run("fnhas_fundraising_education", age=30, available_hours=2, hours_period="week"), "minimum_hours").status == "met"
    assert item(run("fnhas_fundraising_education", age=30, available_hours=1, hours_period="week"), "minimum_hours").status == "not_met"
    assert item(run("fnhas_fundraising_education", age=30, available_hours=1.9, hours_period="week"), "minimum_hours").status == "needs_confirmation"
    # requirement 3 h/week (Cat Tales shelter, applicable)
    assert item(run("cattales_shelter_care", age=30, available_hours=10, hours_period="month"), "minimum_hours").status == "not_met"
    assert item(run("cattales_shelter_care", age=30, available_hours=14, hours_period="month"), "minimum_hours").status == "needs_confirmation"


# 6) an explicitly closed application category
def test_closed_category_kept_separate_from_fit(run, ds):
    a = run("fnhas_dog_handler", age=30, available_hours=3, hours_period="week", commitment_months=12)
    assert a.application_status.status == "explicitly_closed" and a.application_status.label == "Applications closed"
    assert a.overall_status != "not_met"  # closed is not a requirement failure
    assert "Not published" in a.placement_or_shift_availability
    steps = checklist(ds, ds.opportunities["fnhas_dog_handler"])
    assert "closed" in steps[0]["step"].lower()


def test_application_link_is_not_an_opening(run):
    a = run("gnhcp_grant_writing", age=30)
    assert a.application_status.status == "needs_confirmation"
    assert "does not prove there is an opening" in a.application_status.explanation


# 7) an interest-only record must not appear as a confirmed placement
def test_interest_area_only_hidden_by_default_and_labelled(ds, run):
    assert "ah_grant_writing" not in {o.opportunity_id for o in ds.search()}
    assert "ah_grant_writing" in {o.opportunity_id for o in ds.search(record_types=["interest_area_only"])}
    a = run("ah_grant_writing", age=30)
    assert a.record_type == "interest_area_only" and "Not a confirmed placement" in a.notes[0]
    assert a.application_status.status != "explicitly_accepting_applications"


# 8) Greater New Haven search excludes wider Connecticut by default
def test_default_scope_is_greater_new_haven(ds):
    default = ds.search()
    assert default and all(ds.scope_of(o) == "greater_new_haven" for o in default)
    wider = ds.search(include_wider_connecticut=True)
    assert any(ds.scope_of(o) == "wider_connecticut" for o in wider)


def test_town_filter_does_not_spread_multi_site_towns(ds):
    hits = {o.opportunity_id for o in ds.search(scope="wider_connecticut", town="Newington")}
    assert "chs_foster_wilton" not in hits and "chs_newington_laundry" in hits


# 9) an impossible request gets honest uncertainty or a sourced alternative
def test_ten_year_old_dog_walker_gets_honest_result_and_alternatives(ds):
    p = VolunteerProfile(age=10, interests=["dog_walking"])
    from backend.matching import assess
    for o in ds.search(activities=["dog_walking"]):
        a = assess(ds, o, p)
        assert a.overall_status in ("not_met", "needs_confirmation")
    alts = find_alternatives(ds, p)
    assert alts and all(x["overall_status"] != "not_met" for x in alts)
    assert all(ds.opportunities[x["opportunity_id"]].source_ids for x in alts)


def test_empty_search_is_reported(ds):
    assert ds.search(town="Hartford") == []


# global safety property
def test_not_met_only_from_published_applicable(ds):
    from backend.matching import assess
    profiles = [VolunteerProfile(age=a, available_hours=h, hours_period=per, commitment_months=m, guardian_available=g,
                                 include_wider_connecticut=True)
                for a, h, per, m, g in itertools.product([8, 15, 19, 40, None], [0.5, None], ["week", "month"],
                                                          [1, None], [False, None])]
    for o in ds.opportunities.values():
        for p in profiles:
            for r in assess(ds, o, p).requirements:
                if r.status == "not_met" and r.applicability != "published_applicable":
                    # The only exception: a conflicting minimum age whose every version is above the person's age.
                    from backend.matching import _claimed_age_thresholds
                    assert r.requirement == "minimum_age" and r.applicability == "conflicting", (o.opportunity_id, r.requirement)
                    assert p.age is not None and p.age < min(_claimed_age_thresholds(o, strict=False)), (o.opportunity_id, p.age)
