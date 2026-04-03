"""2단계-A: 백엔드 내부 API 테스트"""
import httpx
import json
import sys
import time
import os

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
            print(f"  Response: {json.dumps(body, ensure_ascii=False)[:300]}")
        return body, status
    except Exception as e:
        results.append({"name": name, "status": 0, "success": False, "body": str(e)})
        print(f"[FAIL] {name}: {e}")
        return None, 0

print("\n=== Backend API Integration Tests ===\n")

# Use unique email to avoid conflicts
import random
suffix = random.randint(10000, 99999)
email = f"test_{suffix}@example.com"
password = "testpassword123"

# 1. POST /api/auth/signup
body, status = test("1. POST /api/auth/signup", "POST", "/api/auth/signup",
    json={"email": email, "password": password})

# 2. POST /api/auth/login
body, status = test("2. POST /api/auth/login", "POST", "/api/auth/login",
    json={"email": email, "password": password})

token = None
if body and isinstance(body, dict):
    token = body.get("access_token")
    print(f"  Token obtained: {'yes' if token else 'no'}")

if not token:
    print("Cannot continue without token")
    print("\n=== SUMMARY ===")
    for r in results:
        print(f"{'PASS' if r['success'] else 'FAIL'} | {r['name']} | HTTP {r['status']}")
    sys.exit(1)

# 3. GET /api/auth/me
body, status = test("3. GET /api/auth/me", "GET", "/api/auth/me", token=token)

# 4. POST /api/photos — upload photo
import struct, zlib

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

png_data = create_test_png()

body, status = test("4. POST /api/photos", "POST", "/api/photos", token=token,
    files={"file": ("test_photo.png", png_data, "image/png")})

photo_id = None
if body and isinstance(body, dict):
    photo_id = body.get("id")
    print(f"  photo_id: {photo_id}")

# 5. GET /api/photos
body, status = test("5. GET /api/photos", "GET", "/api/photos", token=token)
if body and isinstance(body, list):
    print(f"  Photos count: {len(body)}")

# 6. POST /api/vouchers/purchase
body, status = test("6. POST /api/vouchers/purchase", "POST", "/api/vouchers/purchase", token=token,
    json={"voucher_type": "story_and_print"})

voucher_id = None
if body and isinstance(body, dict):
    voucher_id = body.get("id")
    print(f"  voucher_id: {voucher_id}")

# 7. POST /api/books — create book
body, status = test("7. POST /api/books", "POST", "/api/books", token=token,
    json={"voucher_id": voucher_id})

book_id = None
if body and isinstance(body, dict):
    book_id = body.get("id")
    print(f"  book_id: {book_id}")

if not book_id:
    print("Cannot continue without book_id")
    print("\n=== SUMMARY ===")
    for r in results:
        print(f"{'PASS' if r['success'] else 'FAIL'} | {r['name']} | HTTP {r['status']}")
    sys.exit(1)

# 8. PATCH /api/books/:id — fill in info
update_data = {
    "child_name": "테스트아이",
    "child_birth_date": "2020-01-01",
    "photo_id": photo_id,
    "job_category": "의료",
    "job_name": "의사",
    "story_style": "dreaming_today",
    "art_style": "watercolor",
    "page_count": 24,
    "book_spec_uid": "SQUAREBOOK_HC",
    "plot_input": "아이가 의사가 되어 동물들을 치료하는 이야기",
    "current_step": 8,
}
body, status = test("8. PATCH /api/books/:id", "PATCH", f"/api/books/{book_id}", token=token,
    json=update_data)

# 9. POST /api/books/:id/character — create character
body, status = test("9. POST /api/books/:id/character", "POST", f"/api/books/{book_id}/character", token=token)

char_id = None
if body and isinstance(body, dict):
    char_id = body.get("id")
    print(f"  character_id: {char_id}")

# 10. PATCH /api/books/:id/character/:charId/select
if char_id:
    body, status = test("10. PATCH /api/books/:id/character/:charId/select", "PATCH",
        f"/api/books/{book_id}/character/{char_id}/select", token=token)

# 11. POST /api/books/:id/generate — generate story
body, status = test("11. POST /api/books/:id/generate", "POST", f"/api/books/{book_id}/generate", token=token)
if body and isinstance(body, dict):
    pages = body.get("pages", [])
    print(f"  Generated pages: {len(pages)}")

# 12. GET /api/books/:id/pages
body, status = test("12. GET /api/books/:id/pages", "GET", f"/api/books/{book_id}/pages", token=token)
page_id = None
if body and isinstance(body, list) and len(body) > 0:
    page_id = body[0].get("id")
    print(f"  Pages count: {len(body)}, first page_id: {page_id}")

# 13. PATCH /api/books/:id/pages/:pageId — edit text
if page_id:
    body, status = test("13. PATCH /api/books/:id/pages/:pageId", "PATCH",
        f"/api/books/{book_id}/pages/{page_id}", token=token,
        json={"text_content": "수정된 텍스트입니다."})

# 14. POST /api/books/:id/estimate
body, status = test("14. POST /api/books/:id/estimate", "POST", f"/api/books/{book_id}/estimate", token=token)
if body and isinstance(body, dict):
    print(f"  Estimate: total_amount={body.get('total_amount')}, credit_sufficient={body.get('credit_sufficient')}")

# 15. POST /api/books/:id/order
body, status = test("15. POST /api/books/:id/order", "POST", f"/api/books/{book_id}/order", token=token,
    json={
        "shipping": {
            "recipient_name": "테스터",
            "recipient_phone": "010-1234-5678",
            "postal_code": "06101",
            "address1": "서울시 강남구 테헤란로 123",
            "address2": "4층",
            "shipping_memo": "테스트 주문"
        }
    })
if body and isinstance(body, dict):
    order_id = body.get("id")
    print(f"  order_id: {order_id}")

# 16. GET /api/orders
body, status = test("16. GET /api/orders", "GET", "/api/orders", token=token)
if body and isinstance(body, list):
    print(f"  Orders count: {len(body)}")

# Additional tests

# Test password change
body, status = test("17. PATCH /api/users/password", "PATCH", "/api/users/password", token=token,
    json={"current_password": password, "new_password": "newpassword123"})

# Test GET /api/books
body, status = test("18. GET /api/books", "GET", "/api/books", token=token)

# Test GET /api/vouchers
body, status = test("19. GET /api/vouchers", "GET", "/api/vouchers", token=token)

# Test book detail
body, status = test("20. GET /api/books/:id", "GET", f"/api/books/{book_id}", token=token)

# Test audio data
body, status = test("21. GET /api/books/:id/audio-data", "GET", f"/api/books/{book_id}/audio-data", token=token)

# Summary
print("\n=== SUMMARY ===")
passed = sum(1 for r in results if r["success"])
total = len(results)
print(f"Passed: {passed}/{total}")
for r in results:
    tag = "PASS" if r["success"] else "FAIL"
    print(f"  [{tag}] {r['name']}: HTTP {r['status']}")
