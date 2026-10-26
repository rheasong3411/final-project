"""Readiness check for the prospective-user test: the four guide tasks walked through as a first-time visitor on the
server the participant will use (port 8001, no trace saving). Synthetic input; ONE real assistant message (desktop)."""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

B = "http://127.0.0.1:8001"
OUT = Path(sys.argv[1]); SHOTS = OUT / "screenshots"
assert SHOTS.is_dir() and not any(SHOTS.iterdir())
res, usage = [], None


def check(n, ok, d=""):
    res.append({"check": n, "passed": bool(ok), "detail": str(d)[:500]})
    print(("PASS " if ok else "FAIL ") + n + (f" — {str(d)[:300]}" if d else ""), flush=True)


with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome")
    for label, vp in [("desktop", {"width": 1440, "height": 900}), ("mobile", {"width": 390, "height": 844})]:
        ctx = b.new_context(viewport=vp); p = ctx.new_page(); errs, bad = [], []
        p.on("pageerror", lambda e: errs.append(str(e)))
        p.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        p.on("response", lambda r: bad.append(f"{r.status} {r.url}") if r.url.startswith(B) and r.status >= 400 else None)
        # Home
        p.goto(B + "/"); p.wait_for_selector(".opp-card"); p.wait_for_timeout(500)
        check(f"{label}: home loads with featured cards", p.locator(".opp-card").count() >= 3)
        p.screenshot(path=str(SHOTS / f"home_{label}.png"))
        # T1: find one opportunity -> detail page
        p.locator("a:has-text('Explore')").first.evaluate("e => e.click()"); p.wait_for_selector(".opp-card")
        n = int(p.inner_text("#results-heading").split()[0])
        check(f"{label} T1: Explore lists opportunities", n >= 20, n)
        p.locator(".opp-card h3 a").first.click(); p.wait_for_selector("text=Where it takes place"); p.wait_for_timeout(400)
        hrefs = p.eval_on_selector_all(".next-actions a", "as => as.map(a => a.href)")
        check(f"{label} T1: detail page has the organization's own links", hrefs and all(h.startswith("https://") for h in hrefs), hrefs)
        check(f"{label} T1: detail page has a next step and Check my fit", p.locator("text=Next step").count() >= 1 and p.locator("#check-fit").count() == 1)
        # T2: compare two
        p.click("button:has-text('Compare requirements')"); p.go_back(); p.wait_for_selector(".opp-card"); p.wait_for_timeout(300)
        p.locator(".opp-card").nth(3).locator("button:has-text('Compare requirements')").click(); p.wait_for_timeout(300)
        p.locator("a:has-text('View comparison'), button:has-text('View comparison')").first.click()
        p.wait_for_selector("text=Compare opportunities"); p.wait_for_timeout(900)
        sel = ".compare-table thead th" if label == "desktop" else ".compare-cards article"
        check(f"{label} T2: Compare shows two opportunities", p.locator(sel).count() == (3 if label == "desktop" else 2))
        p.screenshot(path=str(SHOTS / f"compare_{label}.png"))
        # T3: Find my fit
        p.locator("a:has-text('Find my fit')").first.evaluate("e => e.click()"); p.wait_for_selector("#msg")
        check(f"{label} T3: example prompts offered", p.locator(".card-quiet button").count() == 3)
        p.screenshot(path=str(SHOTS / f"find_my_fit_start_{label}.png"))
        if label == "desktop":
            p.locator(".card-quiet button").first.click()
            with p.expect_response(lambda r: r.url.endswith("/api/assistant"), timeout=280000) as i:
                p.click("form.composer button[type=submit]")
            r = i.value.json(); p.wait_for_timeout(1800)
            usage = r.get("usage")
            check("desktop T3: real reply from gpt-6-luna", r["ok"] and any("gpt-6-luna" in m for m in r["returned_models"]),
                  (r.get("error"), r.get("returned_models")))
            check("desktop T3: reply has option cards and a short answer", p.locator(".current-turn .option-card").count() >= 1
                  and len(r["answer"]) < 700, r["answer"])
            check("desktop T3: Your answers filled from the message", p.locator(".pref-row").count() >= 3)
            p.locator(".current-turn").scroll_into_view_if_needed(); p.screenshot(path=str(SHOTS / "find_my_fit_reply_desktop.png"))
            p.click("button:has-text('Confirm these details')"); p.wait_for_timeout(400)
            check("desktop T3: confirming details works", p.locator(".pref-tag-confirmed").count() >= 3 and p.locator(".pref-tag-chat").count() == 0)
            p.locator("#prefs-h").scroll_into_view_if_needed(); p.screenshot(path=str(SHOTS / "your_answers_confirmed_desktop.png"))
            # T4: next step from a card
            check("desktop T4: cards show the organization's page link", p.locator(".current-turn .option-card .next-actions a").count() >= 1)
            p.click("button:has-text('Clear my session')"); p.click("button:has-text('Yes, clear')"); p.wait_for_timeout(400)
            check("desktop: Clear my session leaves a fresh start", p.locator(".pref-row").count() == 0 and p.locator(".bubble").count() == 0
                  and p.locator("a:has-text('Compare (')").count() == 0)
        # About and an unknown address
        p.goto(B + "/about"); p.wait_for_selector("h1"); check(f"{label}: About page loads", "Locations and distances" in p.inner_text("main"))
        p.goto(B + "/no-such-page"); p.wait_for_timeout(500)
        check(f"{label}: unknown address shows a friendly page", p.locator("main").count() == 1 and len(p.inner_text("main")) > 20, p.inner_text("main")[:120])
        check(f"{label}: no horizontal overflow", not p.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"))
        check(f"{label}: no page or console errors", not errs, errs[:3])
        check(f"{label}: no failed requests to the app", not bad, bad[:3])
        ctx.close()
    b.close()
(OUT / "readiness_report.json").write_text(json.dumps({"checks": res, "real_assistant_usage_api_reported": usage,
    "passed": sum(r["passed"] for r in res), "total": len(res)}, indent=1))
print("USAGE", usage); print(sum(r["passed"] for r in res), "/", len(res))
