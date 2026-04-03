"""Direct Book Print API Test - Round 2"""
import httpx
import json
import os
import sys
import io
from PIL import Image
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

API_KEY = os.getenv("BOOKPRINT_API_KEY", "")
BASE_URL = os.getenv("BOOKPRINT_BASE_URL", "https://api-sandbox.sweetbook.com/v1").rstrip("/")

if not API_KEY:
    print("ERROR: BOOKPRINT_API_KEY not set")
    sys.exit(1)

headers = {"Authorization": f"Bearer {API_KEY}"}
client = httpx.Client(timeout=60.0)
results = []


def log(step, method, url, status, ok, note=""):
    tag = "PASS" if ok else "FAIL"
    results.append((step, method, url, status, tag, note))
    print(f"  [{tag}] {step}: {method} {url} -> {status} {note}")


# 1. GET /credits
r = client.get(f"{BASE_URL}/credits", headers=headers)
log("1", "GET", "/credits", r.status_code, r.status_code == 200)
if r.status_code == 200:
    print(f"    Balance: {r.json().get('data', {}).get('balance', 0)}")

# 2. POST /credits/sandbox/charge
r = client.post(f"{BASE_URL}/credits/sandbox/charge", headers=headers,
                json={"amount": 1000000, "memo": "integration test r2"})
log("2", "POST", "/credits/sandbox/charge", r.status_code, r.status_code in (200, 201))

# 3. POST /books
r = client.post(f"{BASE_URL}/books", headers=headers,
                json={"title": "Integration Test R2", "bookSpecUid": "SQUAREBOOK_HC", "creationType": "TEST"})
log("3", "POST", "/books", r.status_code, r.status_code in (200, 201))
book_uid = r.json().get("data", {}).get("bookUid") if r.status_code in (200, 201) else None
print(f"    bookUid: {book_uid}")

if not book_uid:
    print("Cannot continue without bookUid")
    sys.exit(1)

# 4. POST /books/{bookUid}/photos (upload real PNG)
img = Image.new("RGB", (800, 800), (200, 180, 230))
buf = io.BytesIO()
img.save(buf, "PNG")
buf.seek(0)
r = client.post(f"{BASE_URL}/books/{book_uid}/photos", headers=headers,
                files={"file": ("test_image.png", buf, "image/png")})
log("4", "POST", f"/books/{book_uid}/photos", r.status_code, r.status_code in (200, 201))
photo_file_name = r.json().get("data", {}).get("fileName") if r.status_code in (200, 201) else None
print(f"    fileName: {photo_file_name}")

# Also upload a JPEG to test MIME type detection
img_jpeg = Image.new("RGB", (800, 800), (180, 200, 230))
buf2 = io.BytesIO()
img_jpeg.save(buf2, "JPEG")
buf2.seek(0)
r = client.post(f"{BASE_URL}/books/{book_uid}/photos", headers=headers,
                files={"file": ("test_jpeg.jpg", buf2, "image/jpeg")})
log("4b", "POST", f"/books/{book_uid}/photos (JPEG)", r.status_code, r.status_code in (200, 201))
jpeg_file_name = r.json().get("data", {}).get("fileName") if r.status_code in (200, 201) else None
print(f"    JPEG fileName: {jpeg_file_name}")

# 5. GET /templates?bookSpecUid=SQUAREBOOK_HC&templateKind=cover
r = client.get(f"{BASE_URL}/templates", headers=headers,
               params={"bookSpecUid": "SQUAREBOOK_HC", "templateKind": "cover", "limit": 100})
log("5", "GET", "/templates (cover)", r.status_code, r.status_code == 200)
cover_templates = []
if r.status_code == 200:
    data = r.json().get("data", {})
    cover_templates = data.get("templates", data.get("items", []))
    print(f"    Cover templates: {len(cover_templates)}")

# 6. GET /templates?bookSpecUid=SQUAREBOOK_HC&templateKind=content
r = client.get(f"{BASE_URL}/templates", headers=headers,
               params={"bookSpecUid": "SQUAREBOOK_HC", "templateKind": "content", "limit": 100})
log("6", "GET", "/templates (content)", r.status_code, r.status_code == 200)
content_templates = []
if r.status_code == 200:
    data = r.json().get("data", {})
    content_templates = data.get("templates", data.get("items", []))
    print(f"    Content templates: {len(content_templates)}")

# 7. GET /templates/{templateUid} — check detail and params for first cover template
cover_template_uid = None
cover_params_def = {}
if cover_templates:
    # Check first 3 cover templates for params
    for ct in cover_templates[:3]:
        uid = ct["templateUid"]
        r = client.get(f"{BASE_URL}/templates/{uid}", headers=headers)
        if r.status_code == 200:
            detail = r.json().get("data", {})
            params = detail.get("parameters", {})
            print(f"    Cover template {uid}: params={list(params.keys())}")
            if not cover_template_uid or len(params) < len(cover_params_def):
                cover_template_uid = uid
                cover_params_def = params
    log("7a", "GET", f"/templates/{cover_template_uid}", 200, True, f"params={list(cover_params_def.keys())}")

content_template_uid = None
content_params_def = {}
if content_templates:
    # Find the simplest content template
    for ct in content_templates[:10]:
        uid = ct["templateUid"]
        r = client.get(f"{BASE_URL}/templates/{uid}", headers=headers)
        if r.status_code == 200:
            detail = r.json().get("data", {})
            params = detail.get("parameters", {})
            print(f"    Content template {uid}: params={list(params.keys())} bindings={[(k,v.get('binding')) for k,v in params.items()]}")
            if not content_template_uid or len(params) < len(content_params_def):
                content_template_uid = uid
                content_params_def = params
                if len(params) == 0:
                    break
    log("7b", "GET", f"/templates/{content_template_uid}", 200, True, f"params={list(content_params_def.keys())}")

# 8. POST /books/{bookUid}/cover — test cover creation with proper params
if cover_template_uid and photo_file_name:
    # Build cover parameters dynamically based on params_def
    cover_params = {}
    for name, defn in cover_params_def.items():
        binding = defn.get("binding", "text")
        if binding == "file":
            cover_params[name] = photo_file_name
        elif binding == "text":
            lower = name.lower()
            if "title" in lower or "booktitle" in lower:
                cover_params[name] = "Integration Test R2"
            elif "spine" in lower:
                cover_params[name] = "Test Book"
            elif "date" in lower or "range" in lower:
                cover_params[name] = "2026-04-04"
            else:
                cover_params[name] = ""

    print(f"    Cover params: {cover_params}")
    form_data = {
        "templateUid": (None, cover_template_uid),
        "parameters": (None, json.dumps(cover_params)),
    }
    r = client.post(f"{BASE_URL}/books/{book_uid}/cover", headers=headers, files=form_data)
    log("8", "POST", f"/books/{book_uid}/cover", r.status_code, r.status_code in (200, 201))
    if r.status_code >= 400:
        print(f"    Cover error: {r.text[:300]}")
else:
    log("8", "POST", "/cover", 0, False, "No template/photo")

# 9. POST /books/{bookUid}/contents — test content insertion with proper params
inserted_count = 0
if content_template_uid and photo_file_name:
    for page_num in range(1, 25):  # 24 pages for SQUAREBOOK_HC minimum
        content_params = {}
        for name, defn in content_params_def.items():
            binding = defn.get("binding", "text")
            if binding == "file":
                content_params[name] = photo_file_name
            elif binding == "rowGallery":
                content_params[name] = [photo_file_name]
            elif binding == "text":
                lower = name.lower()
                if "text" in lower or "diary" in lower:
                    content_params[name] = f"Page {page_num} content"
                elif "year" in lower:
                    content_params[name] = "2026"
                elif "month" in lower:
                    content_params[name] = "4"
                elif "date" in lower or lower == "day":
                    content_params[name] = "4"
                elif "label" in lower:
                    content_params[name] = f"Page {page_num}"
                elif "title" in lower:
                    content_params[name] = f"Page {page_num}"
                else:
                    content_params[name] = ""

        form_data = {
            "templateUid": (None, content_template_uid),
            "parameters": (None, json.dumps(content_params)),
        }
        r = client.post(f"{BASE_URL}/books/{book_uid}/contents", headers=headers,
                       files=form_data, params={"breakBefore": "page"})
        if r.status_code in (200, 201):
            inserted_count += 1
        else:
            print(f"    Content page {page_num} error: {r.status_code} {r.text[:200]}")
            break

    log("9", "POST", f"/books/{book_uid}/contents", 201 if inserted_count == 24 else 400,
        inserted_count == 24, f"inserted={inserted_count}/24")
else:
    log("9", "POST", "/contents", 0, False, "No template")

# 10. POST /books/{bookUid}/finalization
if inserted_count >= 24:
    r = client.post(f"{BASE_URL}/books/{book_uid}/finalization", headers=headers)
    log("10", "POST", f"/books/{book_uid}/finalization", r.status_code, r.status_code in (200, 201))
    if r.status_code >= 400:
        print(f"    Finalization error: {r.text[:300]}")

    # 11. POST /orders/estimate
    if r.status_code in (200, 201):
        r = client.post(f"{BASE_URL}/orders/estimate", headers=headers,
                       json={"items": [{"bookUid": book_uid, "quantity": 1}]})
        log("11", "POST", "/orders/estimate", r.status_code, r.status_code == 200)
        if r.status_code == 200:
            est = r.json().get("data", {})
            print(f"    Estimate: totalAmount={est.get('totalAmount')}, paidCredit={est.get('paidCreditAmount')}")

        # 12. POST /orders
        r = client.post(f"{BASE_URL}/orders", headers=headers, json={
            "items": [{"bookUid": book_uid, "quantity": 1}],
            "shipping": {
                "recipientName": "Integration Test",
                "recipientPhone": "010-1234-5678",
                "postalCode": "06101",
                "address1": "Seoul Gangnam",
                "address2": "4F"
            }
        })
        log("12", "POST", "/orders", r.status_code, r.status_code in (200, 201))
        if r.status_code in (200, 201):
            order_data = r.json().get("data", {})
            print(f"    orderUid: {order_data.get('orderUid')}, status: {order_data.get('orderStatus')}")
        else:
            print(f"    Order error: {r.text[:300]}")
else:
    log("10", "POST", "/finalization", 0, False, f"Only {inserted_count} pages")
    log("11", "POST", "/orders/estimate", 0, False, "Skipped")
    log("12", "POST", "/orders", 0, False, "Skipped")

# Summary
print()
print("=== Book Print API Direct Test Summary ===")
passed = sum(1 for r in results if r[4] == "PASS")
failed = sum(1 for r in results if r[4] == "FAIL")
print(f"PASS: {passed}, FAIL: {failed}, Total: {len(results)}")
for r in results:
    if r[4] == "FAIL":
        print(f"  FAIL: {r[0]} {r[1]} {r[2]} -> {r[3]} {r[5]}")

client.close()
