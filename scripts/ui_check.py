#!/usr/bin/env python3
"""Browser checks of the RUNNING website (optional; not needed to run the app).

Needs:  pip install playwright   (uses the installed Google Chrome via channel="chrome")
Run:    python scripts/ui_check.py http://127.0.0.1:8000           # includes 2 REAL assistant turns
        python scripts/ui_check.py http://127.0.0.1:8000 --no-ai   # skip model calls

All messages are SYNTHETIC. The "backend unavailable" check is SIMULATED by aborting the
request in the browser. Each run writes to a NEW folder, output/screenshots/runs/ui_check_<date-time>/
(screenshots and ui_test_report.json), so a rerun never overwrites earlier evidence. UI_CHECK_OUT and
UI_CHECK_REPORT override the locations.
To save the real assistant turns as traces, start the backend with AVF_SAVE_TRACES=1.
"""
import json, re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001"
RUN_AI = "--no-ai" not in sys.argv
TAG = time.strftime("%H%M%S")  # makes each real AI message unique so no gateway-cache replay is possible
import os
RUN_DIR = Path(__file__).resolve().parent.parent / "output" / "screenshots" / "runs" / f"ui_check_{time.strftime('%Y%m%d-%H%M%S')}"
OUT = Path(os.environ.get("UI_CHECK_OUT") or RUN_DIR)  # run-specific by default: never overwrites earlier screenshots
OUT.mkdir(parents=True, exist_ok=bool(os.environ.get("UI_CHECK_OUT")))
report = {"base": BASE, "checks": [], "console_errors": [], "overflow": {}}


def check(name, ok, detail=""):
    report["checks"].append({"check": name, "passed": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))


def shot(page, name, full=True):
    if full:
        page.evaluate("() => window.scrollTo(0, 0)"); page.wait_for_timeout(200)  # avoid sticky-header stitching artifacts
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=full)


def no_overflow(page, label):
    w = page.evaluate("() => [document.documentElement.scrollWidth, window.innerWidth]")
    report["overflow"][label] = w
    check(f"no horizontal overflow: {label}", w[0] <= w[1], f"scrollWidth={w[0]} innerWidth={w[1]}")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    desk = browser.new_context(viewport={"width": 1440, "height": 900})
    page = desk.new_page()
    page.on("console", lambda m: report["console_errors"].append(f"[{m.type}] {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: report["console_errors"].append(f"[pageerror] {e}"))

    # 1) navigation + direct loads
    for path, heading in [("/", "Find animal-volunteering"), ("/explore", "Animal-volunteering opportunities"),
                          ("/about", "How Animal Volunteer Finder works"), ("/find-my-fit", "Tell us a little"),
                          ("/compare", "Compare opportunities"), ("/opportunities/chs_newington_group_trails", "One-time group project"),
                          ("/no-such-page", "This page doesn't exist")]:
        page.goto(BASE + path)
        h = page.locator("h1, h3").filter(has_text=heading).first
        try:
            h.wait_for(timeout=8000); check(f"direct load {path}", True)
        except Exception as e:
            check(f"direct load {path}", False, str(e)[:120])
    page.goto(BASE + "/")
    page.get_by_role("navigation", name="Primary").get_by_role("link", name="Explore").click()
    page.wait_for_url("**/explore"); check("nav link Explore", True)
    page.get_by_role("navigation", name="Primary").get_by_role("link", name="Find my fit").click()
    page.wait_for_url("**/find-my-fit"); check("nav Find my fit button", True)

    # Home screenshots
    page.goto(BASE + "/"); page.wait_for_selector(".opp-card")
    check("home shows 3 real opportunities", page.locator(".opp-card").count() == 3, str(page.locator(".opp-card").count()))
    shot(page, "desktop_home"); no_overflow(page, "desktop /")

    # 2) filters, reset, empty results
    page.goto(BASE + "/explore"); page.wait_for_selector(".opp-card")
    default_count = page.locator("#results-heading").inner_text()
    # Session 15: the town filter matches a role's own published town; "Branford" is no longer offered because its
    # only role-level record is closed. North Haven has several roles of its own.
    page.select_option("#town", "North Haven"); page.wait_for_timeout(600)
    branford = page.locator("#results-heading").inner_text()
    check("town filter changes results", branford != default_count, f"{default_count} -> {branford}")
    check("active filter chip shown", page.get_by_role("button", name=re.compile("Remove filter: Volunteering in: North Haven")).count() == 1)
    page.get_by_role("button", name="Clear all filters").click(); page.wait_for_timeout(600)
    check("clear all restores default", page.locator("#results-heading").inner_text() == default_count)
    page.fill("#q", "zzzz-no-match"); page.get_by_role("button", name="Search", exact=True).click()
    page.get_by_text("No matching opportunities to show").wait_for(timeout=8000)
    check("empty state shown", True); shot(page, "desktop_explore_empty_state", full=False)
    page.get_by_role("button", name="Clear all filters").first.click(); page.wait_for_timeout(600)
    page.locator("label.toggle").filter(has_text="Include other Connecticut locations").click(); page.wait_for_timeout(800)
    check("other-Connecticut opt-in labelled on cards", page.get_by_text("Other Connecticut location").count() > 1)
    page.get_by_role("button", name="Clear all filters").click(); page.wait_for_timeout(600)
    shot(page, "desktop_explore")
    no_overflow(page, "desktop /explore")

    # 3) select, compare, remove
    buttons = page.get_by_role("button", name=re.compile(r"^Compare requirements"))
    for i in range(3):
        buttons.nth(i).click()
    fourth = page.get_by_role("button", name=re.compile(r"^Compare requirements")).first
    check("fourth compare disabled", fourth.is_disabled())
    check("compare tray shows 3", page.get_by_text("3 opportunities selected").count() == 1)
    page.get_by_role("link", name="View comparison").click(); page.wait_for_url("**/compare")
    page.wait_for_selector(".compare-table")
    check("compare table has 3 columns", page.locator(".compare-table thead th").count() == 4)
    shot(page, "desktop_compare")
    page.locator(".compare-table thead").get_by_role("button", name=re.compile("^Remove")).first.click()
    page.wait_for_timeout(800)
    check("remove from compare", page.locator(".compare-table thead th").count() == 3)

    # 4) details + source links
    page.goto(BASE + "/opportunities/branford_general_volunteer"); page.wait_for_selector(".fact")
    ev = page.locator("details.disclosure summary", has_text="Evidence").first
    ev.click()
    link = page.locator("details.disclosure[open] a[target=_blank]").first
    rel = link.get_attribute("rel") or ""
    check("evidence source link opens safely", "noopener" in rel and "noreferrer" in rel, rel)
    check("access-date explanation shown", page.get_by_text("does not mean the organization confirmed").count() >= 1)
    check("past notice labelled not upcoming", page.get_by_text("Not an upcoming date.").count() >= 1)
    # Session 13: "Visit volunteer page ↗" / "Contact organization ↗", with the destination in the accessible name
    official = page.get_by_role("link", name=re.compile(r"Visit volunteer page \(opens branford-ct\.gov"))
    check("official page button labelled with destination",
          official.count() >= 1 and "branford-ct.gov" in (official.first.get_attribute("href") or ""))
    shot(page, "desktop_opportunity_detail")
    no_overflow(page, "desktop /opportunities/branford_general_volunteer")

    # 5) deterministic fit check with missing information (age only, synthetic)
    page.fill("#fit-age", "14")
    page.get_by_role("button", name="Check my fit").click()
    page.get_by_text("Requirement by requirement").wait_for(timeout=10000)
    guardian_q = page.locator(".req-item", has_text="Parent or guardian").get_by_text("Needs confirmation").count()
    hours_q = page.locator(".req-item", has_text="Hours").get_by_text("Needs confirmation").count()
    check("fit check: unknown guardian -> needs confirmation", guardian_q >= 1)
    check("fit check: missing hours -> needs confirmation", hours_q >= 1)
    check("fit check: application status shown separately", page.get_by_text("Application status (separate from fit):").count() == 1)
    page.locator("#check-fit").screenshot(path=str(OUT / "desktop_check_my_fit_missing_info.png"))

    # 8) unavailable-backend state (SIMULATED network failure via request interception)
    page.goto(BASE + "/find-my-fit")
    page.route("**/api/assistant", lambda route: route.abort())
    page.fill("#msg", "SYNTHETIC: I'm 30 and like cats.")
    page.get_by_role("button", name="Send").click()
    page.get_by_text("The app's server couldn't be reached.").wait_for(timeout=10000)
    check("backend-unavailable message shown (simulated)", True)
    check("draft preserved after failure", page.input_value("#msg") == "SYNTHETIC: I'm 30 and like cats.")
    check("no fake recommendations after failure", page.get_by_text("Options to consider").count() == 0)
    shot(page, "desktop_find_my_fit_error_state_simulated", full=False)
    page.unroute("**/api/assistant")

    # 9) keyboard navigation + visible focus
    page.goto(BASE + "/")
    page.keyboard.press("Tab")
    first = page.evaluate("() => document.activeElement.textContent")
    check("first Tab reaches skip link", "Skip to main content" in (first or ""), first)
    focus_ok = []
    for _ in range(4):
        page.keyboard.press("Tab")
        focus_ok.append(page.evaluate("() => getComputedStyle(document.activeElement).boxShadow !== 'none'"))
    check("focus ring visible on tabbed controls", all(focus_ok), str(focus_ok))
    page.keyboard.press("Tab")
    page.screenshot(path=str(OUT / "desktop_keyboard_focus_visible.png"), clip={"x": 0, "y": 0, "width": 1440, "height": 140})

    # 6 + 7) REAL AI conversation through the UI, then a preference change and confirmation
    if RUN_AI:
        page.goto(BASE + "/find-my-fit")
        msg1 = (f"SYNTHETIC TEST {TAG}: I'm 26 and live in New Haven. I'd like to help with cats, about 3 hours a week, "
                "for at least a year, on weekday afternoons.")
        page.fill("#msg", msg1); t0 = time.time()
        page.get_by_role("button", name="Send").click()
        page.locator(".bubble-assistant").first.wait_for(timeout=200000)
        check("real AI reply rendered", True, f"{time.time() - t0:.1f}s")
        check("recommendation cards rendered", page.locator(".bubble-assistant article.card").count() >= 1,
              str(page.locator(".bubble-assistant article.card").count()))
        fit_labels = page.locator(".bubble-assistant .badge").all_inner_texts()
        check("fit and application status both shown", any("Availability not confirmed" in x or "closed" in x.lower() or "Accepting" in x for x in fit_labels)
              and any(x.startswith(("Meets", "Needs", "Does not")) or "Fit:" in x for x in fit_labels), "; ".join(fit_labels[:6]))
        pending = page.locator(".pref-item", has_text="From your message").count() + page.locator(".pref-item", has_text="Assistant's suggestion").count()
        check("chat-derived facts shown as unconfirmed", pending >= 1, str(pending))
        shot(page, "desktop_find_my_fit_real_reply")
        # confirm one fact
        before_confirmed = page.locator(".pref-item", has_text="Confirmed").count()
        page.locator(".pref-item").filter(has=page.get_by_role("button", name=re.compile("^Confirm"))).first.get_by_role("button", name=re.compile("^Confirm")).click()
        page.wait_for_timeout(500)
        check("confirming moves fact to 'Confirmed by you'", page.locator(".pref-item", has_text="Confirmed").count() == before_confirmed + 1)
        page.get_by_text("re-checked with your updated preferences").wait_for(timeout=20000)
        check("results refreshed after preference change", True)
        page.locator("aside .card").first.screenshot(path=str(OUT / "desktop_find_my_fit_preferences_confirmation.png"))
        # follow-up preference change through chat
        page.fill("#msg", f"SYNTHETIC TEST {TAG}: Actually, I can only give 2 hours a month now.")
        page.get_by_role("button", name="Send").click(); t1 = time.time()
        page.locator(".bubble-assistant").nth(1).wait_for(timeout=200000)
        check("second real reply rendered", True, f"{time.time() - t1:.1f}s")
        check("earlier reply marked as earlier", page.get_by_text("Earlier reply").count() >= 1)
        shot(page, "desktop_find_my_fit_followup")
        page.locator("details.disclosure summary", has_text="Run details").last.click()
        rd = page.locator("details.disclosure[open]", has_text="Run ID").last.inner_text()
        check("run details show returned model", "gpt-6-luna" in rd, rd.replace("\n", " ")[:160])

    # 10) mobile layouts
    mob = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    m = mob.new_page()
    m.on("console", lambda msg: report["console_errors"].append(f"[mobile {msg.type}] {msg.text}") if msg.type == "error" else None)
    for path, name in [("/", "mobile_home"), ("/explore", "mobile_explore"), ("/opportunities/chs_newington_group_trails", "mobile_opportunity_detail"),
                       ("/find-my-fit", "mobile_find_my_fit"), ("/about", "mobile_about")]:
        m.goto(BASE + path); m.wait_for_timeout(1200)
        no_overflow(m, f"mobile {path}"); shot(m, name)
    m.get_by_role("button", name="Menu").click()
    check("mobile menu opens", m.locator("#primary-nav.open").count() == 1)
    m.screenshot(path=str(OUT / "mobile_menu_open.png"))
    m.get_by_role("button", name="Menu").click()
    # mobile compare: stacked cards (in-app navigation keeps the in-memory selection)
    m.goto(BASE + "/explore"); m.wait_for_selector(".opp-card")
    for _ in range(2):
        m.get_by_role("button", name=re.compile(r"^Compare requirements")).first.click()
    m.locator(".compare-tray a").click(); m.wait_for_url("**/compare"); m.wait_for_selector(".compare-cards article")
    check("mobile compare uses stacked cards", m.locator(".compare-cards").is_visible() and not m.locator(".compare-table").is_visible())
    no_overflow(m, "mobile /compare"); shot(m, "mobile_compare_stacked_cards")
    browser.close()

report["console_errors"] = sorted(set(report["console_errors"]))
print("console errors:", report["console_errors"] or "none")
Path(os.environ.get("UI_CHECK_REPORT") or str(OUT / "ui_test_report.json")).write_text(json.dumps(report, indent=2))
print("PASSED", sum(c["passed"] for c in report["checks"]), "of", len(report["checks"]))
