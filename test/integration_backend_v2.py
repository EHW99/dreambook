"""2단계-A: 백엔드 내부 API 테스트 (올바른 순서)"""
import httpx
import json
import sys
import random
import struct
import zlib

BASE = "http://localhost:8000"
results = []

def test(name, method, path, token=None, **kwargs):
    url = f"{BASE}{path}"
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = httpx.request(method, url, headers=headers, timeout=30, **kwargs)
        status = r.status_code
        try:
            body = r.json()
        except:
            body = r.text[:500]
        success = status < 400
        results.append({"name": name, "status": status, "success": success, "body": body})
        tag = "PASS" if success else "FAIL"
        print(f"[{tag}] {name}: HTTP {status}")
        if not success:
            detail = body.get("detail", "") if isinstance(body, dict) else str(body)[:200]
            print(f"  Detail: {detail}")
        return body, status
    except Exception as e:
        results.append({"name": name, "status": 0, "success": False, "body": str(e)})
        print(f"[FAIL] {name}: {e}")
        return None, 0

def create_test_png():
    width, height = 600, 600
    raw_data = b""
    for y in range(height):
        raw_data += b"\x00"
        for x in range(width):
            raw_data += b"\xff\x80\x80\xff"
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xffffffff)
        return struct.pack(">I", len(data)) + c + crc
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(raw_data)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")

print("\n=== Backend API Integration Tests (v2) ===\n")

suffix = random.randint(10000, 99999)
email = f"inttest_{suffix}@example.com"
password = "testpass12345"

# 1. Signup
body, _ = test("1. POST /api/auth/signup", "POST", "/api/auth/signup",
    json={"email": email, "password": password})

# 2. Login
body, _ = test("2. POST /api/auth/login", "POST", "/api/auth/login",
    json={"email": email, "password": password})
token = body.get("access_token") if body else None
if not token:
    sys.exit(1)

# 3. Me
test("3. GET /api/auth/me", "GET", "/api/auth/me", token=token)

# 4. Photo upload
png_data = create_test_png()
body, _ = test("4. POST /api/photos", "POST", "/api/photos", token=token,
    files={"file": ("test.png", png_data, "image/png")})
photo_id = body.get("id") if body else None
print(f"  photo_id: {photo_id}")

# 5. Photo list
body, _ = test("5. GET /api/photos", "GET", "/api/photos", token=token)

# 6. Voucher purchase
body, _ = test("6. POST /api/vouchers/purchase", "POST", "/api/vouchers/purchase", token=token,
    json={"voucher_type": "story_and_print"})
voucher_id = body.get("id") if body else None

# 7. Create book
body, _ = test("7. POST /api/books", "POST", "/api/books", token=token,
    json={"voucher_id": voucher_id})
book_id = body.get("id") if body else None

# 8. Step-by-step PATCH (info, step 1-3)
body, _ = test("8a. PATCH books (child info, step 1)", "PATCH", f"/api/books/{book_id}", token=token,
    json={"child_name": "테스트아이", "child_birth_date": "2020-05-15", "photo_id": photo_id, "current_step": 1})

body, _ = test("8b. PATCH books (job, step 2)", "PATCH", f"/api/books/{book_id}", token=token,
    json={"job_category": "의료", "job_name": "의사", "current_step": 2})

body, _ = test("8c. PATCH books (style, step 3)", "PATCH", f"/api/books/{book_id}", token=token,
    json={"story_style": "dreaming_today", "current_step": 3})

body, _ = test("8d. PATCH books (art style, step 4)", "PATCH", f"/api/books/{book_id}", token=token,
    json={"art_style": "watercolor", "current_step": 4})

# 9. Create character
body, _ = test("9. POST /api/books/:id/character", "POST", f"/api/books/{book_id}/character", token=token)
char_id = body.get("id") if body else None
print(f"  char_id: {char_id}")

# 10. Select character
body, _ = test("10. PATCH select character", "PATCH", f"/api/books/{book_id}/character/{char_id}/select", token=token)

# 11. PATCH to step 5 (character confirmed)
body, _ = test("11. PATCH books (step 5, post-character)", "PATCH", f"/api/books/{book_id}", token=token,
    json={"current_step": 5})

# 12. PATCH options + plot (step 6-8)
body, _ = test("12a. PATCH books (options, step 6)", "PATCH", f"/api/books/{book_id}", token=token,
    json={"page_count": 24, "book_spec_uid": "SQUAREBOOK_HC", "current_step": 6})

body, _ = test("12b. PATCH books (plot, step 7)", "PATCH", f"/api/books/{book_id}", token=token,
    json={"plot_input": "의사가 되어 동물을 치료하는 이야기", "current_step": 7})

# 13. Generate story
body, _ = test("13. POST /api/books/:id/generate", "POST", f"/api/books/{book_id}/generate", token=token)
pages = body.get("pages", []) if body else []
print(f"  Generated {len(pages)} pages, status: {body.get('status') if body else 'N/A'}")

# 14. Get pages
body, _ = test("14. GET /api/books/:id/pages", "GET", f"/api/books/{book_id}/pages", token=token)
page_id = None
if body and isinstance(body, list) and len(body) > 0:
    page_id = body[0].get("id")
    print(f"  {len(body)} pages, first page_id: {page_id}")

# 15. Edit page text
if page_id:
    body, _ = test("15. PATCH /api/books/:id/pages/:pageId", "PATCH",
        f"/api/books/{book_id}/pages/{page_id}", token=token,
        json={"text_content": "수정된 텍스트"})

# 16. Estimate
body, _ = test("16. POST /api/books/:id/estimate", "POST", f"/api/books/{book_id}/estimate", token=token)
if body and isinstance(body, dict):
    print(f"  total_amount={body.get('total_amount')}, sufficient={body.get('credit_sufficient')}")

# 17. Order
body, status = test("17. POST /api/books/:id/order", "POST", f"/api/books/{book_id}/order", token=token,
    json={"shipping": {
        "recipient_name": "테스터",
        "recipient_phone": "010-1234-5678",
        "postal_code": "06101",
        "address1": "서울시 강남구 테헤란로 123",
        "address2": "4층",
        "shipping_memo": "테스트 주문"
    }})
order_id_val = None
if body and isinstance(body, dict):
    order_id_val = body.get("id")
    print(f"  order_id: {order_id_val}, status: {body.get('status')}")

# 18. Orders list
body, _ = test("18. GET /api/orders", "GET", "/api/orders", token=token)

# 19. Order detail
if order_id_val:
    body, _ = test("19. GET /api/orders/:id", "GET", f"/api/orders/{order_id_val}", token=token)

# 20. Audio data
body, _ = test("20. GET /api/books/:id/audio-data", "GET", f"/api/books/{book_id}/audio-data", token=token)

# 21. Voucher list
body, _ = test("21. GET /api/vouchers", "GET", "/api/vouchers", token=token)

# 22. Books list
body, _ = test("22. GET /api/books", "GET", "/api/books", token=token)

# 23. Book detail
body, _ = test("23. GET /api/books/:id", "GET", f"/api/books/{book_id}", token=token)

# 24. Characters list
body, _ = test("24. GET /api/books/:id/characters", "GET", f"/api/books/{book_id}/characters", token=token)

# 25. Password change
body, _ = test("25. PATCH /api/users/password", "PATCH", "/api/users/password", token=token,
    json={"current_password": password, "new_password": "newpassword123"})

# Summary
print("\n=== SUMMARY ===")
passed = sum(1 for r in results if r["success"])
total = len(results)
print(f"Passed: {passed}/{total}")
for r in results:
    tag = "PASS" if r["success"] else "FAIL"
    print(f"  [{tag}] {r['name']}: HTTP {r['status']}")
