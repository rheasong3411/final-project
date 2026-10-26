"""Developer retesting, final build: affected screens on desktop and mobile. One real gpt-6-luna message per viewport
(test server 8002, traces saved). Synthetic re-enactment; not the participant."""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

B = "http://127.0.0.1:8002"
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=False)
M1 = ("i’m 25 and live in New Haven. i like cats, don’t have a car, and can volunteer for 2–3 hours on Saturday or "
      "Sunday mornings. what could fit me?")
res, runs = [], []


def check(n, ok, d=""):
    res.append({"check": n, "passed": bool(ok), "detail": str(d)[:500]})
    print(("PASS " if ok else "FAIL ") + n + (f" — {str(d)[:300]}" if d else ""), flush=True)


def rows(p):
    return dict(p.eval_on_selector_all(".pref-row", "rs => rs.map(r => [r.querySelector('dt').textContent.trim(), r.querySelector('.pref-value').textContent.trim()])"))


with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome")
    for label, vp in [("desktop", {"width": 1440, "height": 900}), ("mobile", {"width": 390, "height": 844})]:
        ctx = b.new_context(viewport=vp); p = ctx.new_page(); errs = []
        p.on("pageerror", lambda e: errs.append(str(e)))
        p.goto(B + "/find-my-fit"); p.wait_for_selector("#msg"); p.fill("#msg", M1)
        with p.expect_response(lambda r: r.url.endswith("/api/assistant"), timeout=280000) as w:
            p.click("form.composer button[type=submit]")
        r = w.value.json(); p.wait_for_timeout(1800)
        runs.append({"viewport": label, "run_id": r.get("run_id"), "returned_models": r.get("returned_models"),
                     "usage_api_reported": r.get("usage"), "answer": r.get("answer"), "follow_up_questions": r.get("follow_up_questions")})
        rw = rows(p)
        check(f"{label}: Your answers lists every stated fact, including no car",
              rw.get("Has a car") == "No" and rw.get("Age") == "25" and rw.get("Days") == "Sat, Sun" and rw.get("Times of day") == "Morning"
              and rw.get("Hours you can give", "").startswith("2–3") and rw.get("Animals") == "Cats", rw)
        card = p.locator(".current-turn .option-card").first
        txt = card.inner_text()
        check(f"{label}: card shows the person's weekend mornings on the Schedule line", "Sat, Sun · morning" in txt, txt[:300])
        check(f"{label}: card has a directions link", card.locator("a:has-text('Directions')").count() >= 1)
        check(f"{label}: a warning shared by several lines appears once per card",
              all(txt.count(n) <= 1 for n in ("Listed on an older application form", "Sources disagree")), txt[:200])
        p.locator(".current-turn .option-card").first.scroll_into_view_if_needed(); p.screenshot(path=str(OUT / f"fmf_card_{label}.png"))
        p.locator("#prefs-h").scroll_into_view_if_needed(); p.screenshot(path=str(OUT / f"your_answers_{label}.png"))
        # Explore: town options follow the scope; narrowing clears an out-of-scope town; Clear all unchanged
        p.goto(B + "/explore"); p.wait_for_selector(".opp-card")
        gnh = p.eval_on_selector_all("#town option", "os => os.map(o => o.value).filter(Boolean)")
        p.goto(B + "/explore?wider=1&town=Norwalk"); p.wait_for_selector(".opp-card")
        wide = p.eval_on_selector_all("#town option", "os => os.map(o => o.value).filter(Boolean)")
        check(f"{label}: town options follow the scope", not {"Norwalk", "Newington"} & set(gnh) and {"Norwalk", "Newington"} <= set(wide), (gnh, wide))
        p.locator("label.toggle:has-text('Include other Connecticut locations') input").click(); p.wait_for_timeout(700)
        check(f"{label}: turning wider Connecticut off clears an out-of-scope town", "town=" not in p.url and p.input_value("#town") == "", p.url)
        p.screenshot(path=str(OUT / f"explore_towns_{label}.png"))
        p.fill("#ex-zip", "06511"); p.click("form:has(#ex-zip) button[type=submit]"); p.wait_for_timeout(800)
        p.select_option("#sort", "closest"); p.wait_for_timeout(400); p.click("button:has-text('Clear all filters')"); p.wait_for_timeout(500)
        check(f"{label}: Explore Clear all still clears ZIP and distance sort", p.input_value("#ex-zip") == "" and p.input_value("#sort") == "")
        # Detail pages: directions to verified site / organization address, simple age wording
        p.goto(B + "/opportunities/ah_cat_socializing"); p.wait_for_selector("text=Where it takes place")
        block = p.locator(".location-block").inner_text()
        check(f"{label}: detail has directions to the verified site", p.locator(".location-block a:has-text('Directions')").count() == 1
              and "only the destination filled in" in block, block[:200])
        p.fill("#fit-age", "25"); p.click("button:has-text('Check my fit')"); p.wait_for_selector("text=Requirement by requirement"); p.wait_for_timeout(300)
        age = p.locator("#check-fit .req-item", has=p.locator("h4", has_text="age")).first.inner_text()
        check(f"{label}: detail age explanation is simple, values kept", "Your age meets both published minimums; confirm the organization's current rule." in age
              and "18+ or 21+" in age, age[:300])
        p.locator(".location-block").scroll_into_view_if_needed(); p.screenshot(path=str(OUT / f"detail_directions_{label}.png"))
        p.goto(B + "/opportunities/fnhas_adoption_events"); p.wait_for_selector("text=Where it takes place")
        block = p.locator(".location-block").inner_text()
        check(f"{label}: organization-address directions are labelled as such",
              "Organization location (the activity location may differ)" in block and p.locator(".location-block a:has-text('Directions')").count() == 1, block[:200])
        check(f"{label}: no page errors", not errs, errs[:2])
        ctx.close()
    # form: a range entered by the person
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); p = ctx.new_page()
    p.goto(B + "/find-my-fit"); p.wait_for_selector("#msg"); p.click("summary:has-text('Add or edit your answers')")
    p.fill("#mf-hours", "2"); p.fill("#mf-hoursMax", "3"); p.select_option("#mf-period", "week"); p.click("button:has-text('Save my changes')"); p.wait_for_timeout(400)
    check("form: a range is saved as a range", rows(p).get("Hours you can give") == "2–3 per week", rows(p))
    ctx.close(); b.close()

usage = {k: sum((x["usage_api_reported"] or {}).get(k) or 0 for x in runs) for k in
         ("requests", "input_tokens", "cached_input_tokens", "cache_write_input_tokens", "uncached_input_tokens", "output_tokens")}
(OUT / "screens_report.json").write_text(json.dumps({"checks": res, "real_model_runs": runs, "usage_total_api_reported": usage,
                                                    "passed": sum(r["passed"] for r in res), "total": len(res)}, indent=1, ensure_ascii=False))
print("USAGE", usage); print(sum(r["passed"] for r in res), "/", len(res))
