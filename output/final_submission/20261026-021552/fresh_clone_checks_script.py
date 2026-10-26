"""Checks on the FRESH GitHub clone (port 8011): main pages, filters, comparison, ZIP reset, and one real Find my fit
conversation (gpt-6-luna via Portkey). Synthetic input. Writes only to the new folder given."""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

B = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8011"
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=False)
MSG = "I'm 25, live in New Haven, like cats, and don't have a car. I can volunteer 2–3 hours on Saturday mornings. What could fit me?"
res, run = [], {}


def check(n, ok, d=""):
    res.append({"check": n, "passed": bool(ok), "detail": str(d)[:500]})
    print(("PASS " if ok else "FAIL ") + n + (f" — {str(d)[:300]}" if d else ""), flush=True)


with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome")
    for label, vp in [("desktop", {"width": 1440, "height": 900}), ("mobile", {"width": 390, "height": 844})]:
        ctx = b.new_context(viewport=vp); p = ctx.new_page(); errs, bad = [], []
        p.on("pageerror", lambda e: errs.append(str(e)))
        p.on("response", lambda r: bad.append(f"{r.status} {r.url}") if r.url.startswith(B) and r.status >= 400 else None)
        for path, sel in [("/", ".opp-card"), ("/explore", ".opp-card"), ("/about", "h1"), ("/find-my-fit", "#msg")]:
            p.goto(B + path); p.wait_for_selector(sel)
            check(f"{label}: {path} loads", True)
        p.goto(B + "/"); p.wait_for_selector(".opp-card"); p.screenshot(path=str(OUT / f"home_{label}.png"))
        # filters
        p.goto(B + "/explore"); p.wait_for_selector(".opp-card"); n0 = int(p.inner_text("#results-heading").split()[0])
        p.locator(".checks label:has-text('Cats')").first.click(); p.wait_for_timeout(900)
        n1 = int(p.inner_text("#results-heading").split()[0])
        towns = p.eval_on_selector_all("#town option", "os => os.map(o => o.value).filter(Boolean)")
        check(f"{label}: animal filter narrows results; towns match scope", 0 < n1 < n0 and "Norwalk" not in towns, (n0, n1, towns))
        # ZIP + distance sort, then Clear all
        p.fill("#ex-zip", "06511"); p.click("form:has(#ex-zip) button[type=submit]"); p.wait_for_timeout(900)
        p.select_option("#sort", "closest"); p.wait_for_timeout(500)
        has_dist = any(" · About " in t or "Less than" in t for t in p.locator(".opp-card .place-line").all_inner_texts())
        p.click("button:has-text('Clear all filters')"); p.wait_for_timeout(700)
        check(f"{label}: ZIP gives distances; Clear all resets ZIP, sort and filters",
              has_dist and p.input_value("#ex-zip") == "" and p.input_value("#sort") == "" and int(p.inner_text("#results-heading").split()[0]) == n0)
        # comparison
        for i in (0, 1):
            p.locator(".opp-card").nth(i).locator("button:has-text('Compare requirements')").click(); p.wait_for_timeout(250)
        p.locator("a:has-text('View comparison'), button:has-text('View comparison')").first.click()
        p.wait_for_selector("text=Compare opportunities"); p.wait_for_timeout(900)
        cols = p.locator(".compare-table thead th").count() if label == "desktop" else p.locator(".compare-cards article").count()
        check(f"{label}: comparison of two roles", cols == (3 if label == "desktop" else 2), cols)
        p.screenshot(path=str(OUT / f"compare_{label}.png"))
        # detail page
        p.goto(B + "/opportunities/ah_cat_socializing"); p.wait_for_selector("text=Where it takes place")
        check(f"{label}: detail page with sources and next step", p.locator("text=Next step").count() >= 1 and p.locator(".next-actions a").count() >= 1)
        if label == "desktop":
            p.goto(B + "/find-my-fit"); p.wait_for_selector("#msg"); p.fill("#msg", MSG)
            with p.expect_response(lambda r: r.url.endswith("/api/assistant"), timeout=280000) as w:
                p.click("form.composer button[type=submit]")
            r = w.value.json(); p.wait_for_timeout(1800)
            u = r.get("profile_used") or {}
            run = {"run_id": r.get("run_id"), "ok": r.get("ok"), "requested_model": r.get("requested_model"),
                   "returned_models": r.get("returned_models"), "usage_api_reported": r.get("usage"), "answer": r.get("answer"),
                   "follow_up_questions": r.get("follow_up_questions"),
                   "profile_used": {k: v for k, v in u.items() if v not in (None, [], False) or k == "has_car"},
                   "tool_evidence": {"profile_changes_from_tools": len(r.get("profile_changes") or []),
                                     "requirement_assessments": len(r.get("requirement_assessments") or []),
                                     "recommendations": [x["opportunity_id"] for x in r.get("recommendations", [])],
                                     "alternatives": [x["opportunity_id"] for x in r.get("alternatives", [])],
                                     "sources_cited": len(r.get("sources") or [])}}
            print("ANSWER:", r.get("answer"), "\nFOLLOW-UPS:", r.get("follow_up_questions"), flush=True)
            check("real Find my fit: answered by gpt-6-luna via Portkey", r["ok"] and r["requested_model"] == "gpt-6-luna"
                  and any("gpt-6-luna" in m for m in r["returned_models"]), (r.get("error"), r["returned_models"]))
            check("real Find my fit: profile captured (age, town, cats, no car, Saturday morning, 2–3 h range)",
                  u.get("age") == 25 and u.get("town") == "New Haven" and "cats" in (u.get("animal_preferences") or [])
                  and u.get("has_car") is False and u.get("available_days") == ["sat"] and u.get("available_times") == ["morning"]
                  and (u.get("available_hours"), u.get("available_hours_max")) == (2, 3), run["profile_used"])
            check("real Find my fit: tools ran (profile updates, assessments, option cards)",
                  run["tool_evidence"]["profile_changes_from_tools"] > 0 and (run["tool_evidence"]["recommendations"] or run["tool_evidence"]["alternatives"])
                  and p.locator(".current-turn .option-card").count() >= 1, run["tool_evidence"])
            us = r.get("usage") or {}
            check("real Find my fit: API-reported usage present", (us.get("requests") or 0) >= 2 and (us.get("input_tokens") or 0) > 0
                  and us.get("output_tokens"), us)
            p.locator(".current-turn summary:has-text('Run details')").click(); p.wait_for_timeout(200)
            check("real Find my fit: Run details shows model and usage", "gpt-6-luna" in p.locator(".current-turn").inner_text()
                  and "API-reported usage" in p.locator(".current-turn").inner_text())
            p.locator(".current-turn").scroll_into_view_if_needed(); p.screenshot(path=str(OUT / "find_my_fit_real_desktop.png"))
            p.screenshot(path=str(OUT / "find_my_fit_real_full_desktop.png"), full_page=True)
        check(f"{label}: no horizontal overflow", not p.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"))
        check(f"{label}: no page errors or failed app requests", not errs and not bad, (errs[:2], bad[:2]))
        ctx.close()
    b.close()
(OUT / "fresh_clone_checks.json").write_text(json.dumps({"base": B, "checks": res, "real_run": run,
    "passed": sum(r["passed"] for r in res), "total": len(res)}, indent=1, ensure_ascii=False))
print(sum(r["passed"] for r in res), "/", len(res))
