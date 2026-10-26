from playwright.sync_api import sync_playwright
OUT="/Users/rhea/Desktop/MGT409 AI/Final Project/animal-volunteer/output/screenshots/final_build_20261026-040843"
with sync_playwright() as pw:
    b=pw.chromium.launch(channel="chrome")
    p=b.new_page(viewport={"width":1280,"height":900}, device_scale_factor=2)
    p.goto("http://127.0.0.1:8001/explore?wider=1"); p.wait_for_selector(".opp-card")
    p.fill("#ex-zip","06511"); p.click("form:has(#ex-zip) button[type=submit]"); p.wait_for_timeout(900)
    p.click("#t-fnhas_adoption_events a"); p.wait_for_selector("text=Where it takes place"); p.wait_for_timeout(800)
    p.add_style_tag(content=".site-header{position:static !important}")
    aside=p.locator("aside[aria-label='Location, apply and compare']")
    aside.screenshot(path=OUT+"/detail_location_next_step.png")
    p.click("button:has-text('Compare requirements')"); p.wait_for_timeout(300)
    p.go_back(); p.wait_for_selector(".opp-card"); p.wait_for_timeout(400)
    for oid in ("ah_dog_walking","bcc_foster"):
        p.click(f"article:has(#t-{oid}) button:has-text('Compare requirements')"); p.wait_for_timeout(300)
    p.locator("a:has-text('View comparison'), button:has-text('View comparison')").first.click()
    p.wait_for_selector("text=Compare opportunities"); p.wait_for_timeout(1200)
    p.add_style_tag(content=".site-header{position:static !important}")
    p.locator(".compare-table").screenshot(path=OUT+"/compare_three_roles.png")
    p.screenshot(path=OUT+"/compare_viewport.png")
    b.close()
print("ok")
