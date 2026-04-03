"""E2E Playwright Test - Round 4"""
import os, sys, time, json
from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:3000"
BACKEND = "http://localhost:8000"
SCREENSHOTS = "C:/Real/Projects/sweetbook/app/test/screenshots"
os.makedirs(SCREENSHOTS, exist_ok=True)

RESULTS = []

def log(scenario, test, ok, note=""):
    mark = "PASS" if ok else "FAIL"
    RESULTS.append({"scenario": scenario, "test": test, "result": mark, "note": note})
    print(f"[{mark}] {scenario}: {test} {note}")

def run_tests():
    ts = str(int(time.time()))
    email = f"e2e_r4_{ts}@test.com"
    pw = "TestPass123!"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # SCENARIO 1: Landing page
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        page.goto(FRONTEND + "/", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        page.screenshot(path=os.path.join(SCREENSHOTS, "s1_landing_desktop.png"), full_page=True)

        title_el = page.query_selector("text=길을 잃었나봐요")
        is_404 = title_el is not None
        log("S1-Landing", "Root page renders", not is_404, "Shows 404 page" if is_404 else "OK")

        cta = page.query_selector("text=동화책 만들기") or page.query_selector("text=시작하기")
        log("S1-Landing", "CTA button exists", cta is not None)

        # Mobile
        page.set_viewport_size({"width": 375, "height": 812})
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(SCREENSHOTS, "s1_landing_mobile.png"), full_page=True)

        # Tablet
        page.set_viewport_size({"width": 768, "height": 1024})
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(SCREENSHOTS, "s1_landing_tablet.png"), full_page=True)

        page.set_viewport_size({"width": 1280, "height": 800})

        # CTA click -> login redirect
        if cta:
            cta.click()
            page.wait_for_timeout(2000)
            log("S1-Landing", "CTA->login redirect", "/login" in page.url or "/signup" in page.url, f"URL: {page.url}")

        # Mypage redirect
        page.goto(FRONTEND + "/mypage", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        log("S1-Landing", "Mypage->login redirect", "/login" in page.url, f"URL: {page.url}")

        page.close()

        # SCENARIO 2: Signup -> Login -> Logout
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        page.goto(FRONTEND + "/signup", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS, "s2_signup.png"))

        email_input = page.query_selector("input[type='email'], input[name='email']")
        pw_input = page.query_selector("input[type='password']")

        if email_input and pw_input:
            email_input.fill(email)
            pw_inputs = page.query_selector_all("input[type='password']")
            if len(pw_inputs) >= 2:
                pw_inputs[0].fill(pw)
                pw_inputs[1].fill(pw)
            else:
                pw_input.fill(pw)

            submit = page.query_selector("button[type='submit']") or page.query_selector("button >> text=가입")
            if submit:
                submit.click()
                page.wait_for_timeout(3000)

            log("S2-Signup", "Signup form submit", "/login" in page.url, f"URL: {page.url}")
        else:
            log("S2-Signup", "Signup form exists", False)

        # Login
        page.goto(FRONTEND + "/login", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS, "s2_login.png"))

        email_input = page.query_selector("input[type='email'], input[name='email']")
        pw_input = page.query_selector("input[type='password']")

        if email_input and pw_input:
            email_input.fill(email)
            pw_input.fill(pw)
            submit = page.query_selector("button[type='submit']") or page.query_selector("button >> text=로그인")
            if submit:
                submit.click()
                page.wait_for_timeout(3000)

            page.screenshot(path=os.path.join(SCREENSHOTS, "s2_after_login.png"))
            is_logged_in = page.query_selector("text=마이페이지") or page.query_selector("text=로그아웃") or page.query_selector("a[href*='mypage']")
            log("S2-Login", "Login success", is_logged_in is not None or page.url != FRONTEND + "/login", f"URL: {page.url}")

            has_mypage = page.query_selector("text=마이페이지") or page.query_selector("a[href*='mypage']")
            has_logout = page.query_selector("text=로그아웃") or page.query_selector("button >> text=로그아웃")
            log("S2-Login", "Header mypage btn", has_mypage is not None)
            log("S2-Login", "Header logout btn", has_logout is not None)

            if has_logout:
                has_logout.click()
                page.wait_for_timeout(2000)
                page.screenshot(path=os.path.join(SCREENSHOTS, "s2_after_logout.png"))
                has_login = page.query_selector("text=로그인") or page.query_selector("a[href*='login']")
                log("S2-Logout", "After logout shows login", has_login is not None)
        else:
            log("S2-Login", "Login form exists", False)

        page.close()

        # SCENARIO 3: Mypage
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        page.goto(FRONTEND + "/login", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)
        ei = page.query_selector("input[type='email'], input[name='email']")
        pi = page.query_selector("input[type='password']")
        if ei and pi:
            ei.fill(email)
            pi.fill(pw)
            sub = page.query_selector("button[type='submit']") or page.query_selector("button >> text=로그인")
            if sub:
                sub.click()
                page.wait_for_timeout(3000)

        page.goto(FRONTEND + "/mypage", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        page.screenshot(path=os.path.join(SCREENSHOTS, "s3_mypage.png"))

        is_mypage = "/mypage" in page.url
        log("S3-Mypage", "Mypage access", is_mypage, f"URL: {page.url}")

        bookshelf_tab = page.query_selector("text=내 책장") or page.query_selector("text=책장")
        photos_tab = page.query_selector("text=사진") or page.query_selector("text=내 사진")
        log("S3-Mypage", "Tab UI exists", bookshelf_tab is not None or photos_tab is not None)

        page.close()

        # SCENARIO 4: Create flow
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        page.goto(FRONTEND + "/login", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)
        ei = page.query_selector("input[type='email'], input[name='email']")
        pi = page.query_selector("input[type='password']")
        if ei and pi:
            ei.fill(email)
            pi.fill(pw)
            sub = page.query_selector("button[type='submit']") or page.query_selector("button >> text=로그인")
            if sub:
                sub.click()
                page.wait_for_timeout(3000)

        page.goto(FRONTEND + "/create", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        page.screenshot(path=os.path.join(SCREENSHOTS, "s4_create.png"))

        is_create = "/create" in page.url
        log("S4-Create", "Create page access", is_create, f"URL: {page.url}")

        page.close()

        # SCENARIO 6: Error/Edge cases
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        page.goto(FRONTEND + "/nonexistent-page", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS, "s6_404_desktop.png"))
        has_404 = page.query_selector("text=404") or page.query_selector("text=길을 잃")
        log("S6-Error", "404 page", has_404 is not None)

        page.set_viewport_size({"width": 375, "height": 812})
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(SCREENSHOTS, "s6_404_mobile.png"))

        page.goto(FRONTEND + "/login", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS, "s6_login_mobile.png"))

        page.goto(FRONTEND + "/signup", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS, "s6_signup_mobile.png"))

        page.close()

        if console_errors:
            print(f"\nConsole errors ({len(console_errors)}):")
            for err in console_errors[:5]:
                print(f"  {err[:200]}")

        browser.close()

    p_count = sum(1 for r in RESULTS if r["result"] == "PASS")
    f_count = sum(1 for r in RESULTS if r["result"] == "FAIL")
    print(f"\n=== E2E SUMMARY: {p_count} PASS, {f_count} FAIL out of {len(RESULTS)} ===")
    for r in RESULTS:
        if r["result"] == "FAIL":
            print(f"  FAILED: {r['scenario']}/{r['test']} -- {r['note']}")

    return RESULTS

run_tests()
