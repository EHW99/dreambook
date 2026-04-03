"""2단계-B: Book Print API 직접 호출 테스트"""
import httpx
import json
import sys
import os
import time

# Load .env
from pathlib import Path
env_path = Path("C:/Real/Projects/sweetbook/app/backend/.env")
env_vars = {}
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip()

API_KEY = env_vars.get("BOOKPRINT_API_KEY", "")
BASE_URL = env_vars.get("BOOKPRINT_BASE_URL", "https://api-sandbox.sweetbook.com/v1")

if not API_KEY:
    print("ERROR: BOOKPRINT_API_KEY not found in .env")
    sys.exit(1)

headers = {"Authorization": f"Bearer {API_KEY}"}
results = []

def test(name, method, path, **kwargs):
    url = f"{BASE_URL}{path}"
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

# 1. GET /credits
print("\n=== Book Print API Direct Tests ===\n")
body, status = test("GET /credits", "GET", "/credits")

# 2. POST /credits/sandbox/charge
body, status = test("POST /credits/sandbox/charge", "POST", "/credits/sandbox/charge",
    json={"amount": 1000000, "memo": "integration test"})

# 3. POST /books
body, status = test("POST /books", "POST", "/books",
    json={"title": "Integration Test Book", "bookSpecUid": "SQUAREBOOK_HC", "creationType": "TEST"})

book_uid = None
if body and isinstance(body, dict):
    book_uid = body.get("data", {}).get("bookUid")
    print(f"  bookUid: {book_uid}")

if not book_uid:
    print("Cannot continue without bookUid")
    # Print summary
    print("\n=== SUMMARY ===")
    for r in results:
        print(f"{'PASS' if r['success'] else 'FAIL'} | {r['name']} | HTTP {r['status']}")
    sys.exit(1)

# 4. POST /books/{bookUid}/photos — upload a test image
# Create a minimal PNG (1x1 red pixel)
import struct
import zlib

def create_test_png():
    """Create a minimal valid 100x100 PNG."""
    width, height = 100, 100
    raw_data = b""
    for y in range(height):
        raw_data += b"\x00"  # filter byte
        for x in range(width):
            raw_data += b"\xff\x00\x00\xff"  # RGBA red

    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xffffffff)
        return struct.pack(">I", len(data)) + c + crc

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(raw_data)

    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")

png_data = create_test_png()
test_img_path = "C:/Real/Projects/sweetbook/app/test/test_image.png"
with open(test_img_path, "wb") as f:
    f.write(png_data)

body, status = test("POST /books/{bookUid}/photos", "POST", f"/books/{book_uid}/photos",
    files={"file": ("test_image.png", png_data, "image/png")})

file_name = None
if body and isinstance(body, dict):
    file_name = body.get("data", {}).get("fileName")
    print(f"  fileName: {file_name}")

# Upload a second photo for cover
body2, status2 = test("POST /books/{bookUid}/photos (cover)", "POST", f"/books/{book_uid}/photos",
    files={"file": ("cover_image.png", png_data, "image/png")})

cover_file_name = None
if body2 and isinstance(body2, dict):
    cover_file_name = body2.get("data", {}).get("fileName")
    print(f"  cover fileName: {cover_file_name}")

# 5. GET /templates?bookSpecUid=SQUAREBOOK_HC
body, status = test("GET /templates (cover)", "GET", "/templates",
    params={"bookSpecUid": "SQUAREBOOK_HC", "templateKind": "cover", "limit": 10})

cover_template_uid = None
if body and isinstance(body, dict):
    data = body.get("data", {})
    items = []
    if isinstance(data, dict):
        items = data.get("templates", data.get("items", []))
    elif isinstance(data, list):
        items = data
    print(f"  Response data keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
    print(f"  Found {len(items)} cover templates")
    if items:
        cover_template_uid = items[0].get("templateUid")
        print(f"  Using template: {cover_template_uid}")

body, status = test("GET /templates (content)", "GET", "/templates",
    params={"bookSpecUid": "SQUAREBOOK_HC", "templateKind": "content", "limit": 10})

content_template_uid = None
if body and isinstance(body, dict):
    data = body.get("data", {})
    items = []
    if isinstance(data, dict):
        items = data.get("templates", data.get("items", []))
    elif isinstance(data, list):
        items = data
    print(f"  Response data keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
    print(f"  Found {len(items)} content templates")
    if items:
        content_template_uid = items[0].get("templateUid")
        print(f"  Using template: {content_template_uid}")

# 6. GET /templates/{templateUid} — template detail
if cover_template_uid:
    body, status = test("GET /templates/{templateUid}", "GET", f"/templates/{cover_template_uid}")
    if body and isinstance(body, dict):
        tpl_data = body.get("data", {})
        params_def = tpl_data.get("parameters", [])
        print(f"  Template parameters: {json.dumps(params_def, ensure_ascii=False)[:500]}")

# 7. POST /books/{bookUid}/cover
if cover_template_uid:
    cover_params = {}
    if cover_file_name:
        cover_params["frontPhoto"] = cover_file_name
    cover_params["title"] = "Integration Test"

    body, status = test("POST /books/{bookUid}/cover", "POST", f"/books/{book_uid}/cover",
        data={"templateUid": cover_template_uid, "parameters": json.dumps(cover_params)})

# 8. POST /books/{bookUid}/contents — insert multiple pages (need 24 minimum for SQUAREBOOK_HC)
if content_template_uid and file_name:
    for i in range(12):  # 12 insertions × 2 pages each = 24 pages
        content_params = {"text": f"Page {i+1} text", "photo": file_name}
        label = f"POST /books/{{bookUid}}/contents (page {i+1})"
        body, status = test(label, "POST", f"/books/{book_uid}/contents",
            params={"breakBefore": "page"},
            data={"templateUid": content_template_uid, "parameters": json.dumps(content_params)})
        if status >= 400:
            break

# 9. POST /books/{bookUid}/finalization
body, status = test("POST /books/{bookUid}/finalization", "POST", f"/books/{book_uid}/finalization")
if body and isinstance(body, dict):
    print(f"  Finalization data: {json.dumps(body.get('data', {}), ensure_ascii=False)[:300]}")

# 10. POST /orders/estimate
if book_uid:
    body, status = test("POST /orders/estimate", "POST", "/orders/estimate",
        json={"items": [{"bookUid": book_uid, "quantity": 1}]})

# 11. POST /orders
if book_uid:
    body, status = test("POST /orders", "POST", "/orders",
        json={
            "items": [{"bookUid": book_uid, "quantity": 1}],
            "shipping": {
                "recipientName": "테스터",
                "recipientPhone": "010-1234-5678",
                "postalCode": "06101",
                "address1": "서울시 강남구 테헤란로 123",
                "address2": "4층",
                "memo": "테스트 주문"
            }
        })
    if body and isinstance(body, dict):
        order_uid = body.get("data", {}).get("orderUid")
        print(f"  orderUid: {order_uid}")

# Summary
print("\n=== SUMMARY ===")
passed = sum(1 for r in results if r["success"])
total = len(results)
print(f"Passed: {passed}/{total}")
for r in results:
    tag = "PASS" if r["success"] else "FAIL"
    print(f"  [{tag}] {r['name']}: HTTP {r['status']}")
