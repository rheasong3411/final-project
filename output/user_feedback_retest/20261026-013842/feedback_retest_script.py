"""Developer retesting of the prospective user's feedback (NOT the participant). Real gpt-6-luna calls through the app
(test server 8002, traces saved), synthetic re-enactment of the participant's situation. Usage: feedback_retest.py OUT LABEL"""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

B = "http://127.0.0.1:8002"
OUT = Path(sys.argv[1]); LABEL = sys.argv[2]; SHOTS = OUT / "screenshots"
SHOTS.mkdir(parents=True, exist_ok=False)
MSGS = ["i’m 25 and live in New Haven. i like cats, don’t have a car, and can volunteer for 2–3 hours on Saturday or Sunday mornings. what could fit me?",
        "what are the requirements for the Animal Haven cat role? how long would i need to commit, and does my age work?",
        "how would i get to these places without a car? which ones are closest?"]
WANT = {"age": 25, "town": "New Haven", "has_car": False}
res, turns = [], []


def check(n, ok, d=""):
    res.append({"check": n, "passed": bool(ok), "detail": str(d)[:700]})
    print(("PASS " if ok else "FAIL ") + n + (f" — {str(d)[:400]}" if d else ""), flush=True)


def cards(p):
    return p.evaluate("""() => [...document.querySelectorAll('.current-turn .option-card')].map(c => {
        let h = c.closest('.grid'); while (h && h.tagName !== 'H3') h = h.previousElementSibling;
        const rows = Object.fromEntries([...c.querySelectorAll('.fact-line')].map(l => [l.querySelector('dt').textContent.trim(),
                                                                                       l.querySelector('dd').textContent.trim()]));
        return {section: h ? h.textContent.trim() : '', id: c.querySelector('h3').id.replace(/^rc-[a-z]+-/, ''), rows,
                why: (c.querySelector(':scope > p') || {}).textContent || ''};
    })""")


def profile_checks(i, r):
    u = r.get("profile_used") or {}
    facts = {f["field"]: f["status"] for f in r.get("profile_facts", [])}
    got = {k: u.get(k) for k in ("age", "town", "has_car", "animal_preferences", "available_days", "available_times",
                                  "available_hours", "available_hours_max", "hours_period", "max_session_hours", "zip_code")}
    check(f"turn {i}: age, town and no car used", all(u.get(k) == v for k, v in WANT.items()), got)
    check(f"turn {i}: interest in cats used", "cats" in (u.get("animal_preferences") or []), got)
    check(f"turn {i}: weekend days used", set(u.get("available_days") or []) == {"sat", "sun"}, got)
    check(f"turn {i}: morning availability used", u.get("available_times") == ["morning"], got)
    check(f"turn {i}: 2–3 hours kept as a range", u.get("available_hours") == 2 and u.get("available_hours_max") == 3, got)
    check(f"turn {i}: no period or session length silently chosen", u.get("hours_period") is None and u.get("max_session_hours") is None, got)
    check(f"turn {i}: no ZIP invented", not u.get("zip_code"), got)
    return got, facts


with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome")
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); p = ctx.new_page(); errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(B + "/find-my-fit"); p.wait_for_selector("#msg")
    for i, msg in enumerate(MSGS, 1):
        p.fill("#msg", msg)
        with p.expect_response(lambda r: r.url.endswith("/api/assistant"), timeout=280000) as w:
            p.click("form.composer button[type=submit]")
        r = w.value.json(); p.wait_for_timeout(1800)
        print(f"TURN {i}:", r.get("ok"), r.get("returned_models"), "\n  ANSWER:", r.get("answer"), "\n  FOLLOW-UPS:", r.get("follow_up_questions"), flush=True)
        got, facts = profile_checks(i, r)
        cs = cards(p)
        turns.append({"turn": i, "message": msg, "run_id": r.get("run_id"), "ok": r.get("ok"), "returned_models": r.get("returned_models"),
                      "usage_api_reported": r.get("usage"), "answer": r.get("answer"), "follow_up_questions": r.get("follow_up_questions"),
                      "profile": got, "fact_statuses": facts, "cards": cs, "panel": p.eval_on_selector_all(
                          ".pref-row", "rs => rs.map(r => r.textContent.replace(/\\s+/g, ' ').trim())")})
        check(f"turn {i}: answered by gpt-6-luna", r["ok"] and any("gpt-6-luna" in m for m in r["returned_models"]), r.get("error"))
        if i == 1:
            fu = " ".join(r["follow_up_questions"])
            check("turn 1: asks what the 2–3 hours means (period or per visit) instead of choosing",
                  re.search(r"(each|per|a) (week|month|visit|session)|how often|weekly|every week", fu, re.I) is not None, r["follow_up_questions"])
            check("turn 1: ZIP asked optionally (no car)", re.search(r"\bzip\b", fu + r["answer"], re.I) is not None, fu)
        if i == 2:
            ah = [c for c in cs if c["id"].startswith("ah_")]
            txt = r["answer"] + " " + " ".join(c["why"] for c in cs)
            one_year = re.search(r"(one[- ]year|12[- ]month|twelve[- ]month|a year)", txt, re.I)
            hedged = one_year and re.search(r"older|may|confirm|unclear|outdated|listed", txt[max(0, one_year.start() - 160): one_year.end() + 160], re.I)
            check("turn 2: chat's one-year explanation carries the same uncertainty as the card", (not one_year) or bool(hedged), txt[:500])
            for c in ah:
                com = c["rows"].get("Commitment", "")
                check(f"turn 2: {c['id']} card shows the one-year rule as needing confirmation",
                      ("12 months" not in com) or ("Needs confirmation" in com), com)
                age = c["rows"].get("Minimum age", "")
                check(f"turn 2: {c['id']} age line is simple", "meets both published minimums" in age.lower() or "Meets" in age or age == "", age)
        if i == 3:
            check("turn 3: still knows there's no car", (r.get("profile_used") or {}).get("has_car") is False)
            check("turn 3: no invented bus routes or travel times", not re.search(r"\b(bus (route|line) \d|\d+\s*min(ute)?s? (by|on|walk|ride))\b", r["answer"], re.I), r["answer"])
        p.locator(".current-turn").scroll_into_view_if_needed(); p.screenshot(path=str(SHOTS / f"turn{i}_{LABEL}.png"))
        p.locator("#prefs-h").scroll_into_view_if_needed(); p.screenshot(path=str(SHOTS / f"turn{i}_your_answers_{LABEL}.png"))
    check("no page errors", not errs, errs[:2])
    ctx.close()
    # Explore town options vs scope (no AI)
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); p = ctx.new_page()
    p.goto(B + "/explore"); p.wait_for_selector(".opp-card")
    gnh = p.eval_on_selector_all("#town option", "os => os.map(o => o.value).filter(Boolean)")
    p.goto(B + "/explore?wider=1"); p.wait_for_selector(".opp-card")
    wide = p.eval_on_selector_all("#town option", "os => os.map(o => o.value).filter(Boolean)")
    check("Explore: Greater New Haven scope offers only Greater New Haven towns", not ({"Norwalk", "Newington", "Wilton"} & set(gnh)), gnh)
    check("Explore: wider scope adds other Connecticut towns", set(gnh) < set(wide), wide)
    ctx.close(); b.close()

usage = {k: sum((t["usage_api_reported"] or {}).get(k) or 0 for t in turns) for k in
         ("requests", "input_tokens", "cached_input_tokens", "cache_write_input_tokens", "uncached_input_tokens", "output_tokens")}
(OUT / f"report_{LABEL}.json").write_text(json.dumps({"label": LABEL, "checks": res, "turns": turns, "usage_total_api_reported": usage,
                                                     "passed": sum(r["passed"] for r in res), "total": len(res)}, indent=1, ensure_ascii=False))
print("USAGE", usage); print(sum(r["passed"] for r in res), "/", len(res))
