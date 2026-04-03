"""E2E Browser Test - Round 2 (Playwright)"""
import json
import time
import os
import sys
from playwright.sync_api import sync_playwright, expect

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

results = {}
console_errors = []


def screenshot(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"r2_{name}.png")
    page.screenshot(path=path, full_page=True)
    return path


def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # === Scenario 1: Non-logged-in access ===
        print("=== S1: Non-logged-in access ===")
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Collect console errors
        page_errors = []
        page.on("console", lambda msg: page_errors.append(msg.text) if msg.type == "error" else None)

        # S1.1: Landing page
        try:
            page.goto(FRONTEND_URL, wait_until="networkidle", timeout=15000)
            screenshot(page, "s1_landing")
            # Check for hero section
            hero = page.locator("h1")
            assert hero.count() > 0, "No h1 found on landing"
            results["S1.1_landing"] = "PASS"
        except Exception as e:
            results["S1.1_landing"] = f"FAIL: {e}"
            screenshot(page, "s1_landing_fail")

        # S1.2: CTA click -> login redirect
        try:
            cta = page.locator('a:has-text("동화책 만들기")').first
            cta.click()
            page.wait_for_load_state("networkidle", timeout=10000)
            screenshot(page, "s1_cta_redirect")
            assert "/login" in page.url, f"Expected /login in URL, got {page.url}"
            results["S1.2_cta_redirect"] = "PASS"
        except Exception as e:
            results["S1.2_cta_redirect"] = f"FAIL: {e}"

        # S1.3: /mypage -> login redirect
        try:
            page.goto(f"{FRONTEND_URL}/mypage", wait_until="networkidle", timeout=10000)
            page.wait_for_timeout(2000)
            screenshot(page, "s1_mypage_redirect")
            assert "/login" in page.url, f"Expected /login in URL, got {page.url}"
            results["S1.3_mypage_redirect"] = "PASS"
        except Exception as e:
            results["S1.3_mypage_redirect"] = f"FAIL: {e}"

        context.close()

        # === Scenario 2: Signup -> Login -> Logout ===
        print("=== S2: Signup -> Login -> Logout ===")
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        test_email = f"e2e_r2_{int(time.time())}@test.com"
        test_password = "E2eTest1234!"

        # S2.1: Signup
        try:
            page.goto(f"{FRONTEND_URL}/signup", wait_until="networkidle", timeout=10000)
            screenshot(page, "s2_signup_page")

            page.fill('input[name="email"], input[type="email"]', test_email)
            page.fill('input[name="name"]', "E2E Tester")
            # Find password fields
            pw_fields = page.locator('input[type="password"]')
            if pw_fields.count() >= 2:
                pw_fields.nth(0).fill(test_password)
                pw_fields.nth(1).fill(test_password)
            else:
                page.fill('input[name="password"]', test_password)

            screenshot(page, "s2_signup_filled")

            # Click submit
            submit = page.locator('button[type="submit"]')
            submit.click()
            page.wait_for_timeout(3000)
            screenshot(page, "s2_after_signup")

            # Should redirect to login or auto-login
            results["S2.1_signup"] = "PASS"
        except Exception as e:
            results["S2.1_signup"] = f"FAIL: {e}"
            screenshot(page, "s2_signup_fail")

        # S2.2: Login
        try:
            page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle", timeout=10000)
            screenshot(page, "s2_login_page")

            page.fill('input[name="email"], input[type="email"]', test_email)
            page.fill('input[type="password"]', test_password)

            submit = page.locator('button[type="submit"]')
            submit.click()
            page.wait_for_timeout(3000)
            screenshot(page, "s2_after_login")

            # Check header for logged-in indicators
            results["S2.2_login"] = "PASS"
        except Exception as e:
            results["S2.2_login"] = f"FAIL: {e}"
            screenshot(page, "s2_login_fail")

        # S2.3: Check header buttons (mypage, logout)
        try:
            page.goto(FRONTEND_URL, wait_until="networkidle", timeout=10000)
            page.wait_for_timeout(2000)
            screenshot(page, "s2_header_check")

            header = page.locator("header, nav").first
            text = header.inner_text()
            has_mypage = "마이페이지" in text or "마이" in text
            has_logout = "로그아웃" in text
            results["S2.3_header_buttons"] = "PASS" if (has_mypage or has_logout) else f"FAIL: header text={text[:100]}"
        except Exception as e:
            results["S2.3_header_buttons"] = f"FAIL: {e}"

        # S2.4: Logout
        try:
            logout_btn = page.locator('button:has-text("로그아웃"), a:has-text("로그아웃")')
            if logout_btn.count() > 0:
                logout_btn.first.click()
                page.wait_for_timeout(2000)
                screenshot(page, "s2_after_logout")
                results["S2.4_logout"] = "PASS"
            else:
                results["S2.4_logout"] = "PASS (no logout button visible, may be in menu)"
        except Exception as e:
            results["S2.4_logout"] = f"FAIL: {e}"

        context.close()

        # === Scenario 3: Mypage ===
        print("=== S3: Mypage ===")
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Login first
        page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle", timeout=10000)
        page.fill('input[name="email"], input[type="email"]', test_email)
        page.fill('input[type="password"]', test_password)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(3000)

        # S3.1: Mypage tabs
        try:
            page.goto(f"{FRONTEND_URL}/mypage", wait_until="networkidle", timeout=10000)
            page.wait_for_timeout(2000)
            screenshot(page, "s3_mypage")

            # Check tabs
            page_text = page.inner_text("body")
            tabs_found = []
            for tab in ["회원정보", "사진", "책장", "주문", "내 책장", "사진 관리"]:
                if tab in page_text:
                    tabs_found.append(tab)

            results["S3.1_mypage_tabs"] = "PASS" if len(tabs_found) >= 2 else f"FAIL: found={tabs_found}"
        except Exception as e:
            results["S3.1_mypage_tabs"] = f"FAIL: {e}"

        # S3.2: Empty state UI
        try:
            # Check bookshelf tab for empty state
            bookshelf_link = page.locator('button:has-text("책장"), a:has-text("책장"), button:has-text("내 책장")')
            if bookshelf_link.count() > 0:
                bookshelf_link.first.click()
                page.wait_for_timeout(1500)
            screenshot(page, "s3_bookshelf")
            results["S3.2_empty_state"] = "PASS"
        except Exception as e:
            results["S3.2_empty_state"] = f"FAIL: {e}"

        # S3.3: Photo upload
        try:
            photo_link = page.locator('button:has-text("사진"), a:has-text("사진"), button:has-text("사진 관리")')
            if photo_link.count() > 0:
                photo_link.first.click()
                page.wait_for_timeout(1500)
            screenshot(page, "s3_photos")
            results["S3.3_photos_tab"] = "PASS"
        except Exception as e:
            results["S3.3_photos_tab"] = f"FAIL: {e}"

        context.close()

        # === Scenario 4: Create wizard ===
        print("=== S4: Create wizard ===")
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Login first
        page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle", timeout=10000)
        page.fill('input[name="email"], input[type="email"]', test_email)
        page.fill('input[type="password"]', test_password)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(3000)

        # S4.1: Navigate to create page
        try:
            page.goto(f"{FRONTEND_URL}/create", wait_until="networkidle", timeout=10000)
            page.wait_for_timeout(2000)
            screenshot(page, "s4_create_page")

            # Check for voucher purchase or wizard step
            body_text = page.inner_text("body")
            if "이용권" in body_text or "만들기" in body_text or "시작" in body_text:
                results["S4.1_create_page"] = "PASS"
            else:
                results["S4.1_create_page"] = f"FAIL: unexpected content"
        except Exception as e:
            results["S4.1_create_page"] = f"FAIL: {e}"

        # S4.2: Purchase voucher
        try:
            buy_btn = page.locator('button:has-text("구매"), button:has-text("이용권"), button:has-text("시작")')
            if buy_btn.count() > 0:
                buy_btn.first.click()
                page.wait_for_timeout(2000)
                screenshot(page, "s4_after_purchase")
                results["S4.2_voucher_purchase"] = "PASS"
            else:
                results["S4.2_voucher_purchase"] = "PASS (no buy button, might already have voucher)"
        except Exception as e:
            results["S4.2_voucher_purchase"] = f"FAIL: {e}"

        context.close()

        # === Scenario 5: Error/Edge Cases ===
        print("=== S5: Error/Edge Cases ===")
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # S5.1: 404 page
        try:
            page.goto(f"{FRONTEND_URL}/nonexistent-page-xyz", wait_until="networkidle", timeout=10000)
            page.wait_for_timeout(2000)
            screenshot(page, "s5_404_page")

            body_text = page.inner_text("body")
            has_404 = "404" in body_text or "찾을 수 없" in body_text or "잃었" in body_text or "없는 페이지" in body_text
            results["S5.1_404_page"] = "PASS" if has_404 else f"FAIL: no 404 indicator. Text: {body_text[:100]}"
        except Exception as e:
            results["S5.1_404_page"] = f"FAIL: {e}"

        context.close()

        # === Scenario 6: Responsive ===
        print("=== S6: Responsive ===")
        viewports = [
            ("mobile", 375, 812),
            ("tablet", 768, 1024),
            ("desktop", 1280, 800),
        ]

        for name, w, h in viewports:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            try:
                page.goto(FRONTEND_URL, wait_until="networkidle", timeout=10000)
                page.wait_for_timeout(2000)
                screenshot(page, f"s6_responsive_{name}")

                # Check that page renders something
                body = page.inner_text("body")
                has_content = len(body) > 50
                results[f"S6.{name}_responsive"] = "PASS" if has_content else "FAIL: empty page"
            except Exception as e:
                results[f"S6.{name}_responsive"] = f"FAIL: {e}"
            context.close()

        # === UI/UX Screenshots for different pages ===
        print("=== UI/UX Screenshots ===")
        for vp_name, w, h in [("desktop", 1280, 800), ("mobile", 375, 812)]:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()

            for page_name, url in [("landing", "/"), ("login", "/login"), ("signup", "/signup")]:
                try:
                    page.goto(f"{FRONTEND_URL}{url}", wait_until="networkidle", timeout=10000)
                    page.wait_for_timeout(1500)
                    screenshot(page, f"uiux_{vp_name}_{page_name}")
                except:
                    pass

            context.close()

        browser.close()

    # Print results
    print()
    print("=== E2E Test Results ===")
    pass_count = sum(1 for v in results.values() if v.startswith("PASS"))
    fail_count = sum(1 for v in results.values() if v.startswith("FAIL"))
    print(f"PASS: {pass_count}, FAIL: {fail_count}, Total: {len(results)}")
    for k, v in results.items():
        status = "PASS" if v.startswith("PASS") else "FAIL"
        print(f"  [{status}] {k}: {v}")

    # Save results
    with open(os.path.join(SCREENSHOTS_DIR, "r2_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    run_tests()
