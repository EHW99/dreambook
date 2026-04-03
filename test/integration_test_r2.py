"""Integration Test Round 2 - Backend API Tests"""
import httpx
import json
import os
import sys
import io
from PIL import Image

BASE = "http://localhost:8000"
results = []


def log(step, method, url, status, ok, note=""):
    tag = "PASS" if ok else "FAIL"
    results.append((step, method, url, status, tag, note))
    print(f"  [{tag}] {step}: {method} {url} -> {status} {note}")


# 1. Signup
import time
email = f"inttest_r2_{int(time.time())}@test.com"
password = "Test1234!"
r = httpx.post(f"{BASE}/api/auth/signup", json={"email": email, "password": password, "name": "TesterR2"})
if r.status_code == 201:
    log("1", "POST", "/api/auth/signup", r.status_code, True)
elif r.status_code in (400, 409):
    log("1", "POST", "/api/auth/signup", r.status_code, True, "(already exists)")
else:
    log("1", "POST", "/api/auth/signup", r.status_code, False, r.text[:100])

# 2. Login
r = httpx.post(f"{BASE}/api/auth/login", json={"email": email, "password": password})
log("2", "POST", "/api/auth/login", r.status_code, r.status_code == 200)
token = r.json().get("access_token", "") if r.status_code == 200 else ""
headers = {"Authorization": f"Bearer {token}"}

# 3. Me
r = httpx.get(f"{BASE}/api/auth/me", headers=headers)
log("3", "GET", "/api/auth/me", r.status_code, r.status_code == 200)

# 4. Upload photo (create real PNG)
img = Image.new("RGB", (600, 600), (200, 180, 230))
buf = io.BytesIO()
img.save(buf, "PNG")
buf.seek(0)
r = httpx.post(f"{BASE}/api/photos", headers=headers, files={"file": ("test_r2.png", buf, "image/png")})
log("4", "POST", "/api/photos", r.status_code, r.status_code in (200, 201))
photo_id = r.json().get("id") if r.status_code in (200, 201) else None

# 5. Get photos
r = httpx.get(f"{BASE}/api/photos", headers=headers)
log("5", "GET", "/api/photos", r.status_code, r.status_code == 200)

# 6. Buy voucher
r = httpx.post(f"{BASE}/api/vouchers/purchase", headers=headers, json={"voucher_type": "story_and_print"})
log("6", "POST", "/api/vouchers/purchase", r.status_code, r.status_code in (200, 201))
voucher_id = r.json().get("id") if r.status_code in (200, 201) else None
print(f"    Voucher ID: {voucher_id}")

# 7. Create book
r = httpx.post(f"{BASE}/api/books", headers=headers, json={"voucher_id": voucher_id})
log("7", "POST", "/api/books", r.status_code, r.status_code in (200, 201))
book_id = r.json().get("id") if r.status_code in (200, 201) else None

if book_id:
    # 8a. Patch child info
    r = httpx.patch(f"{BASE}/api/books/{book_id}", headers=headers, json={
        "child_name": "테스터R2", "child_birth": "2020-01-01", "child_gender": "male", "current_step": 2
    })
    log("8a", "PATCH", f"/api/books/{book_id}", r.status_code, r.status_code == 200, "child info")

    # 8b. Patch job
    r = httpx.patch(f"{BASE}/api/books/{book_id}", headers=headers, json={
        "job_name": "소방관", "job_category": "공공", "current_step": 3
    })
    log("8b", "PATCH", f"/api/books/{book_id}", r.status_code, r.status_code == 200, "job")

    # 8c. Patch style
    r = httpx.patch(f"{BASE}/api/books/{book_id}", headers=headers, json={
        "style": "adventure", "current_step": 4
    })
    log("8c", "PATCH", f"/api/books/{book_id}", r.status_code, r.status_code == 200, "style")

    # 8d. Patch art style
    r = httpx.patch(f"{BASE}/api/books/{book_id}", headers=headers, json={
        "art_style": "watercolor", "current_step": 5
    })
    log("8d", "PATCH", f"/api/books/{book_id}", r.status_code, r.status_code == 200, "art_style")

    # 9. Character
    r = httpx.post(f"{BASE}/api/books/{book_id}/character", headers=headers, json={})
    log("9", "POST", f"/api/books/{book_id}/character", r.status_code, r.status_code in (200, 201))
    char_id = None
    if r.status_code in (200, 201):
        chars = r.json()
        if isinstance(chars, list) and chars:
            char_id = chars[0].get("id")
        elif isinstance(chars, dict):
            char_id = chars.get("id")

    # 10. Select character
    if char_id:
        r = httpx.patch(f"{BASE}/api/books/{book_id}/character/{char_id}/select", headers=headers)
        log("10", "PATCH", f"/api/books/{book_id}/character/{char_id}/select", r.status_code, r.status_code == 200)

        # Step 6
        r = httpx.patch(f"{BASE}/api/books/{book_id}", headers=headers, json={"current_step": 6})
        log("10b", "PATCH", f"/api/books/{book_id}", r.status_code, r.status_code == 200, "step 6")

    # 11. Options step 6 + summary step 7
    r = httpx.patch(f"{BASE}/api/books/{book_id}", headers=headers, json={
        "page_count": 24, "book_spec_uid": "SQUAREBOOK_HC", "current_step": 7
    })
    log("11a", "PATCH", f"/api/books/{book_id}", r.status_code, r.status_code == 200, "options")

    r = httpx.patch(f"{BASE}/api/books/{book_id}", headers=headers, json={
        "plot_summary": "테스터가 소방관이 되는 이야기", "current_step": 8
    })
    log("11b", "PATCH", f"/api/books/{book_id}", r.status_code, r.status_code == 200, "plot")

    # 12. Generate
    r = httpx.post(f"{BASE}/api/books/{book_id}/generate", headers=headers, json={}, timeout=30)
    log("12", "POST", f"/api/books/{book_id}/generate", r.status_code, r.status_code in (200, 201))

    # 13. Get pages
    r = httpx.get(f"{BASE}/api/books/{book_id}/pages", headers=headers)
    log("13", "GET", f"/api/books/{book_id}/pages", r.status_code, r.status_code == 200)
    pages = r.json() if r.status_code == 200 else []
    print(f"    Pages count: {len(pages)}")

    # Check if placeholder images exist
    if pages:
        first_page = pages[0]
        imgs = first_page.get("images", [])
        if imgs:
            img_path = imgs[0].get("image_path", "")
            exists = os.path.exists(img_path) if img_path else False
            print(f"    First page image path: {img_path}")
            print(f"    Image file exists: {exists}")

    # 14. Edit page
    if pages:
        page_id = pages[0].get("id")
        r = httpx.patch(f"{BASE}/api/books/{book_id}/pages/{page_id}", headers=headers, json={"text_content": "수정된 텍스트"})
        log("14", "PATCH", f"/api/books/{book_id}/pages/{page_id}", r.status_code, r.status_code == 200)

    # 15. Estimate
    r = httpx.post(f"{BASE}/api/books/{book_id}/estimate", headers=headers, json={})
    log("15", "POST", f"/api/books/{book_id}/estimate", r.status_code, r.status_code == 200)
    if r.status_code == 200:
        print(f"    Estimate: {r.json()}")

    # 16. Order
    r = httpx.post(f"{BASE}/api/books/{book_id}/order", headers=headers, json={
        "shipping": {
            "recipient_name": "홍길동",
            "recipient_phone": "010-1234-5678",
            "postal_code": "06101",
            "address1": "서울시 강남구 테헤란로 123",
            "address2": "4층"
        }
    }, timeout=120)
    log("16", "POST", f"/api/books/{book_id}/order", r.status_code, r.status_code in (200, 201))
    if r.status_code not in (200, 201):
        print(f"    Order error: {r.text[:500]}")

# 17. Orders list
r = httpx.get(f"{BASE}/api/orders", headers=headers)
log("17", "GET", "/api/orders", r.status_code, r.status_code == 200)

# 18. Audio data
if book_id:
    r = httpx.get(f"{BASE}/api/books/{book_id}/audio-data", headers=headers)
    log("18", "GET", f"/api/books/{book_id}/audio-data", r.status_code, r.status_code == 200)

# 19. Vouchers
r = httpx.get(f"{BASE}/api/vouchers", headers=headers)
log("19", "GET", "/api/vouchers", r.status_code, r.status_code == 200)

# 20. Books list
r = httpx.get(f"{BASE}/api/books", headers=headers)
log("20", "GET", "/api/books", r.status_code, r.status_code == 200)

# 21. Password change
r = httpx.patch(f"{BASE}/api/users/password", headers=headers, json={
    "current_password": password, "new_password": "NewPass1234!"
})
log("21", "PATCH", "/api/users/password", r.status_code, r.status_code == 200)

# Summary
print()
print("=== Summary ===")
passed = sum(1 for r in results if r[4] == "PASS")
failed = sum(1 for r in results if r[4] == "FAIL")
print(f"PASS: {passed}, FAIL: {failed}, Total: {len(results)}")
for r in results:
    if r[4] == "FAIL":
        print(f"  FAIL: {r[0]} {r[1]} {r[2]} -> {r[3]} {r[5]}")
