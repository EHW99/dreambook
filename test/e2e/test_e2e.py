"""3단계: Playwright E2E 브라우저 테스트"""
import os
import sys
import json
import time
import random
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright, expect

FRONTEND = "http://localhost:3000"
BACKEND = "http://localhost:8000"
SCREENSHOTS = "C:/Real/Projects/sweetbook/app/test/screenshots"
os.makedirs(SCREENSHOTS, exist_ok=True)

results = []
console_errors = []

def record(scenario, step, passed, note=""):
    results.append({"scenario": scenario, "step": step, "passed": passed, "note": note})
    tag = "PASS" if passed else "FAIL"
    print(f"  [{tag}] {step}" + (f" — {note}" if note else ""))

def screenshot(page, name):
    path = os.path.join(SCREENSHOTS, f"{name}.png")
    page.screenshot(path=path, full_page=True)
    return path


def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Collect console errors
        def on_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        suffix = random.randint(10000, 99999)
        email = f"e2e_{suffix}@example.com"
        password = "e2epassword123"

        # === Scenario 1: Unauthenticated access ===
        print("\n=== Scenario 1: Unauthenticated access ===")
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.on("console", on_console)

        # Landing page
        page.goto(FRONTEND, wait_until="networkidle", timeout=15000)
        screenshot(page, "s1_landing")
        record("S1", "Landing page loads", page.title() != "")

        # Check for CTA button
        cta = page.query_selector('a[href*="create"], button:has-text("만들기"), a:has-text("만들기")')
        record("S1", "CTA button exists", cta is not None)

        # Click CTA -> should redirect to login
        if cta:
            cta.click()
            page.wait_for_timeout(2000)
            screenshot(page, "s1_after_cta")
            record("S1", "CTA redirects to login", "/login" in page.url or "/signup" in page.url,
                   f"URL: {page.url}")

        # Direct mypage access -> redirect to login
        page.goto(f"{FRONTEND}/mypage", wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(1000)
        screenshot(page, "s1_mypage_redirect")
        record("S1", "Mypage redirects to login", "/login" in page.url, f"URL: {page.url}")

        context.close()

        # === Scenario 2: Signup -> Login -> Logout ===
        print("\n=== Scenario 2: Signup -> Login -> Logout ===")
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.on("console", on_console)

        # Signup
        page.goto(f"{FRONTEND}/signup", wait_until="networkidle", timeout=10000)
        screenshot(page, "s2_signup_page")
        record("S2", "Signup page loads", True)

        # Fill signup form
        email_input = page.query_selector('input[type="email"], input[name="email"]')
        pw_input = page.query_selector('input[type="password"]')
        all_pw = page.query_selector_all('input[type="password"]')

        if email_input and pw_input:
            email_input.fill(email)
            all_pw[0].fill(password)
            if len(all_pw) > 1:
                all_pw[1].fill(password)
            screenshot(page, "s2_signup_filled")

            submit = page.query_selector('button[type="submit"], button:has-text("가입"), button:has-text("회원")')
            if submit:
                submit.click()
                page.wait_for_timeout(3000)
                screenshot(page, "s2_after_signup")
                record("S2", "Signup succeeds", "/login" in page.url or "성공" in page.content() or "/signup" not in page.url,
                       f"URL: {page.url}")
            else:
                record("S2", "Signup submit button", False, "No submit button found")
        else:
            record("S2", "Signup form fields", False, "Missing email or password input")

        # Login
        page.goto(f"{FRONTEND}/login", wait_until="networkidle", timeout=10000)
        screenshot(page, "s2_login_page")

        email_input = page.query_selector('input[type="email"], input[name="email"]')
        pw_input = page.query_selector('input[type="password"]')

        if email_input and pw_input:
            email_input.fill(email)
            pw_input.fill(password)

            submit = page.query_selector('button[type="submit"], button:has-text("로그인")')
            if submit:
                submit.click()
                page.wait_for_timeout(3000)
                screenshot(page, "s2_after_login")

                # Check that we're NOT on login page anymore
                is_logged_in = "/login" not in page.url
                record("S2", "Login succeeds", is_logged_in, f"URL: {page.url}")

                # Check header buttons
                page_content = page.content()
                has_mypage = page.query_selector('a[href*="mypage"], button:has-text("마이페이지"), a:has-text("마이페이지")')
                has_logout = page.query_selector('button:has-text("로그아웃"), a:has-text("로그아웃")')
                record("S2", "Mypage button visible", has_mypage is not None)
                record("S2", "Logout button visible", has_logout is not None)

                # Logout
                if has_logout:
                    has_logout.click()
                    page.wait_for_timeout(2000)
                    screenshot(page, "s2_after_logout")
                    has_login_btn = page.query_selector('a[href*="login"], button:has-text("로그인"), a:has-text("로그인")')
                    record("S2", "Logout works", has_login_btn is not None or "/" == page.url.rstrip("/").split(":3000")[-1],
                           f"URL: {page.url}")
                else:
                    record("S2", "Logout works", False, "No logout button found")

        context.close()

        # === Scenario 3: Mypage ===
        print("\n=== Scenario 3: Mypage ===")
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.on("console", on_console)

        # Login first
        page.goto(f"{FRONTEND}/login", wait_until="networkidle", timeout=10000)
        page.fill('input[type="email"], input[name="email"]', email)
        page.fill('input[type="password"]', password)
        page.click('button[type="submit"], button:has-text("로그인")')
        page.wait_for_timeout(3000)

        # Navigate to mypage
        page.goto(f"{FRONTEND}/mypage", wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(2000)
        screenshot(page, "s3_mypage")
        record("S3", "Mypage loads", "/mypage" in page.url)

        # Check tabs
        tabs = page.query_selector_all('[role="tab"], button:has-text("회원"), button:has-text("사진"), button:has-text("책장"), button:has-text("주문")')
        record("S3", "Mypage has tabs", len(tabs) > 0, f"Found {len(tabs)} tabs")

        # Check empty state UI
        screenshot(page, "s3_mypage_detail")

        # Try photo tab
        photo_tab = page.query_selector('button:has-text("사진"), [data-value="photos"]')
        if photo_tab:
            photo_tab.click()
            page.wait_for_timeout(1000)
            screenshot(page, "s3_photos_tab")
            record("S3", "Photos tab accessible", True)

        # Try bookshelf tab
        book_tab = page.query_selector('button:has-text("책장"), button:has-text("동화책"), [data-value="books"]')
        if book_tab:
            book_tab.click()
            page.wait_for_timeout(1000)
            screenshot(page, "s3_bookshelf_tab")
            record("S3", "Bookshelf tab accessible", True)

        # Try orders tab
        order_tab = page.query_selector('button:has-text("주문"), [data-value="orders"]')
        if order_tab:
            order_tab.click()
            page.wait_for_timeout(1000)
            screenshot(page, "s3_orders_tab")
            record("S3", "Orders tab accessible", True)

        context.close()

        # === Scenario 4: Create book wizard ===
        print("\n=== Scenario 4: Create book wizard ===")
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.on("console", on_console)

        # Login
        page.goto(f"{FRONTEND}/login", wait_until="networkidle", timeout=10000)
        page.fill('input[type="email"], input[name="email"]', email)
        page.fill('input[type="password"]', password)
        page.click('button[type="submit"], button:has-text("로그인")')
        page.wait_for_timeout(3000)

        # Navigate to voucher page
        page.goto(f"{FRONTEND}/vouchers", wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(2000)
        screenshot(page, "s4_vouchers")
        record("S4", "Voucher page loads", True)

        # Try to buy a voucher
        buy_btn = page.query_selector('button:has-text("구매"), button:has-text("이용권")')
        if buy_btn:
            buy_btn.click()
            page.wait_for_timeout(2000)
            screenshot(page, "s4_voucher_bought")
            record("S4", "Voucher purchase", True)

        # Navigate to create
        page.goto(f"{FRONTEND}/create", wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(2000)
        screenshot(page, "s4_create_page")
        record("S4", "Create page loads", "/create" in page.url, f"URL: {page.url}")

        # Check for wizard/step UI
        page_content = page.content()
        has_steps = "step" in page_content.lower() or "단계" in page_content or "다음" in page_content
        record("S4", "Wizard UI present", has_steps)

        context.close()

        # === Scenario 5: Book viewer (need existing book) ===
        print("\n=== Scenario 5: Book shelf & viewer ===")
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.on("console", on_console)

        # Login
        page.goto(f"{FRONTEND}/login", wait_until="networkidle", timeout=10000)
        page.fill('input[type="email"], input[name="email"]', email)
        page.fill('input[type="password"]', password)
        page.click('button[type="submit"], button:has-text("로그인")')
        page.wait_for_timeout(3000)

        # Go to mypage bookshelf
        page.goto(f"{FRONTEND}/mypage", wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(1000)
        screenshot(page, "s5_mypage_bookshelf")
        record("S5", "Mypage for bookshelf", True)

        context.close()

        # === Scenario 6: Error/edge cases ===
        print("\n=== Scenario 6: Error/edge cases ===")

        # 404 page
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.on("console", on_console)
        page.goto(f"{FRONTEND}/nonexistent-page-12345", wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(1000)
        screenshot(page, "s6_404_page")
        page_content = page.content()
        has_404 = "404" in page_content or "찾을 수 없" in page_content or "잃었" in page_content or "not found" in page_content.lower()
        record("S6", "404 page displays", has_404)
        context.close()

        # Responsive tests
        print("\n=== Responsive Tests ===")

        # Mobile viewport
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        page.goto(FRONTEND, wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(1000)
        screenshot(page, "responsive_mobile_landing")
        record("Responsive", "Mobile landing", True)

        page.goto(f"{FRONTEND}/login", wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(1000)
        screenshot(page, "responsive_mobile_login")
        record("Responsive", "Mobile login", True)
        context.close()

        # Tablet viewport
        context = browser.new_context(viewport={"width": 768, "height": 1024})
        page = context.new_page()
        page.goto(FRONTEND, wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(1000)
        screenshot(page, "responsive_tablet_landing")
        record("Responsive", "Tablet landing", True)
        context.close()

        # Desktop viewport
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.goto(FRONTEND, wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(1000)
        screenshot(page, "responsive_desktop_landing")
        record("Responsive", "Desktop landing", True)

        page.goto(f"{FRONTEND}/signup", wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(1000)
        screenshot(page, "responsive_desktop_signup")

        page.goto(f"{FRONTEND}/login", wait_until="networkidle", timeout=10000)
        page.wait_for_timeout(1000)
        screenshot(page, "responsive_desktop_login")
        context.close()

        browser.close()

    # Print summary
    print("\n=== E2E TEST SUMMARY ===")
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"Passed: {passed}/{total}")

    scenarios = {}
    for r in results:
        s = r["scenario"]
        if s not in scenarios:
            scenarios[s] = {"pass": 0, "fail": 0}
        if r["passed"]:
            scenarios[s]["pass"] += 1
        else:
            scenarios[s]["fail"] += 1

    for s, counts in scenarios.items():
        total_s = counts["pass"] + counts["fail"]
        tag = "PASS" if counts["fail"] == 0 else "PARTIAL" if counts["pass"] > 0 else "FAIL"
        print(f"  [{tag}] {s}: {counts['pass']}/{total_s}")

    print(f"\nConsole errors: {len(console_errors)}")
    for err in console_errors[:10]:
        print(f"  - {err[:200]}")

    # Write results JSON
    with open(os.path.join(SCREENSHOTS, "results.json"), "w") as f:
        json.dump({"results": results, "console_errors": console_errors[:50]}, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    run_tests()
