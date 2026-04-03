# BookPrint API 완전 레퍼런스

> **버전**: v1.0 (2026-03-24) | **작성일**: 2026-04-02  
> **소스**: [공식 문서](https://api.sweetbook.com/docs/) + [Python SDK](https://github.com/sweet-book/bookprintapi-python-sdk) 코드 교차 검증

---

## 목차

1. [기본 정보](#1-기본-정보)
   - [서비스 개요](#11-서비스-개요)
   - [환경 (Sandbox / Live)](#12-환경-sandbox--live)
   - [인증](#13-인증)
   - [공통 요청/응답 구조](#14-공통-요청응답-구조)
   - [Rate Limit](#15-rate-limit)
   - [페이지네이션](#16-페이지네이션)
   - [멱등성 (Idempotency)](#17-멱등성-idempotency)
   - [날짜 형식](#18-날짜-형식)
2. [전체 워크플로우](#2-전체-워크플로우)
3. [API 레퍼런스](#3-api-레퍼런스)
   - [BookSpecs (판형)](#31-bookspecs-판형)
   - [Templates (템플릿)](#32-templates-템플릿)
   - [Books (책)](#33-books-책)
   - [Photos (사진)](#34-photos-사진)
   - [Covers (표지)](#35-covers-표지)
   - [Contents (내지)](#36-contents-내지)
   - [Orders (주문)](#37-orders-주문)
   - [Credits (충전금)](#38-credits-충전금)
   - [Webhooks (웹훅)](#39-webhooks-웹훅)
4. [개념 설명 (Concepts)](#4-개념-설명-concepts)
   - [Template Engine](#41-template-engine)
   - [Dynamic Layout](#42-dynamic-layout)
   - [Element Grouping](#43-element-grouping)
   - [Gallery Templates](#44-gallery-templates)
   - [Column Templates](#45-column-templates)
   - [Base Layer](#46-base-layer)
   - [Text Processing](#47-text-processing)
   - [Special Page Rules](#48-special-page-rules)
5. [에러 코드](#5-에러-코드)
6. [SDK 사용법](#6-sdk-사용법)
7. [트러블슈팅](#7-트러블슈팅)
8. [실제 테스트 결과](#8-실제-테스트-결과)
9. [부록](#9-부록)

---

## 1. 기본 정보

### 1.1 서비스 개요

BookPrint API (Book Print API)는 **스위트북(SweetBook Inc.)** 에서 운영하는 B2B 포토북 인쇄 서비스이다. REST API를 통해 포토북 생성, 주문, 인쇄, 배송까지 전 과정을 자동화할 수 있다.

| 항목 | 값 |
|------|-----|
| API 버전 | v1 |
| 응답 형식 | JSON |
| 인증 방식 | API Key (Bearer Token) |
| 제공사 | SWEETBOOK Inc. |
| 연락처 | sweet@sweetbook.com / 02-886-0156 |
| 사업자등록번호 | 131-86-00220 |

### 1.2 환경 (Sandbox / Live)

| 항목 | Sandbox | Live |
|------|---------|------|
| Base URL | `https://api-sandbox.sweetbook.com/v1` | `https://api.sweetbook.com/v1` |
| API Key | Sandbox 전용 | Live 전용 |
| 충전금 | 테스트 충전금 (포털에서 무료 충전) | 실제 충전금 (PG 결제) |
| 가격 | 테스트 가격 (100원 이하) | 협의된 실제 가격 |
| 인쇄 | 실행 안 됨 | 실제 제작 |
| 배송 | 없음 | 한진택배 (3-4 영업일) |
| 웹훅 | 발생함 | 발생함 |
| 주문 상태 | PAID에서 멈춤 | 전체 워크플로우 진행 |
| 데이터 | Sandbox 전용 (Live와 완전 격리) | Live 전용 |

**환경 전환 시 변경 사항**: Base URL과 API Key만 변경하면 된다. API 인터페이스는 동일하다.

```bash
# Sandbox
curl -X GET 'https://api-sandbox.sweetbook.com/v1/books' \
  -H "Authorization: Bearer {SANDBOX_API_KEY}"

# Live
curl -X GET 'https://api.sweetbook.com/v1/books' \
  -H "Authorization: Bearer {LIVE_API_KEY}"
```

**계정 유형별 접근**:
- **개인 계정**: 가입 즉시 Sandbox 사용 가능. Live 접근 불가.
- **사업자 계정**: Sandbox + Live 모두 사용 가능. 사업 협의 완료 필요.

### 1.3 인증

모든 API 요청에 `Authorization` 헤더가 필요하다.

```
Authorization: Bearer {YOUR_API_KEY}
```

**API Key 특성**:

| 항목 | 설명 |
|------|------|
| 형식 | `SB{10자}.{32자}` (예: `SB9A1X36H2YZ.a1b2c3d4e5f6g7h8...`) |
| 접두사 | 모든 키는 `SB`로 시작 |
| 만료 | 없음 (폐기 전까지 유효) |
| 발급 | 파트너 포털 > API Key 관리 |
| 환경 감지 | 도메인에 "sandbox" 포함 시 Sandbox, 그 외 Live |
| IP 제한 | `allow_ips` 설정으로 화이트리스트 가능 |

> **주의**: API Key 전체 값은 **발급 시에만** 확인 가능하다. 즉시 안전한 곳에 저장해야 한다. 서버는 SHA-256 해시로만 보관한다.

**보안 모범 사례**:
- 환경변수로 관리 (하드코딩 금지)
- 서버 사이드에서만 사용 (클라이언트 노출 금지)
- 유출 시 즉시 포털에서 폐기 후 재발급

### 1.4 공통 요청/응답 구조

**요청 Content-Type**:
- `application/json`: 일반 API 요청
- `multipart/form-data`: 파일 업로드

**성공 응답**:
```json
{
  "success": true,
  "message": "Success",
  "data": { ... }
}
```

**에러 응답**:
```json
{
  "success": false,
  "message": "Error message",
  "data": null,
  "errors": ["상세 에러 메시지"],
  "fieldErrors": [
    {"field": "recipientName", "message": "recipientName is required"}
  ]
}
```

**HTTP 상태 코드**:

| 코드 | 의미 |
|------|------|
| 200 | 성공 (조회/수정) |
| 201 | 성공 (생성) |
| 204 | 성공 (삭제, 응답 body 없음) |
| 400 | 요청 데이터 오류 |
| 401 | 인증 실패 (API Key 무효) |
| 402 | 충전금 부족 |
| 403 | 접근 거부 (폐기된 키 또는 IP 차단) |
| 404 | 리소스 없음 |
| 409 | 충돌 (중복 요청, Idempotency Key 충돌) |
| 429 | Rate Limit 초과 |
| 500 | 서버 오류 |

### 1.5 Rate Limit

| 대상 | 제한 | 기준 |
|------|------|------|
| 인증 엔드포인트 | 10 req/min | IP 기반 |
| 일반 API | 300 req/min | API Key 기반 |
| 파일 업로드 | 200 req/min | API Key 기반 |

초과 시 `429 Too Many Requests` 반환. `Retry-After` 헤더에 대기 시간(60초) 포함.

### 1.6 페이지네이션

limit/offset 기반 페이지네이션을 사용한다.

**요청 파라미터**:

| 파라미터 | 기본값 | 최대 | 설명 |
|----------|--------|------|------|
| `limit` | 20 | 100 | 한 페이지 결과 수 |
| `offset` | 0 | - | 건너뛸 항목 수 |

**응답 구조**:
```json
{
  "data": {
    "items": [...],
    "pagination": {
      "total": 150,
      "limit": 20,
      "offset": 0,
      "hasNext": true
    }
  }
}
```

### 1.7 멱등성 (Idempotency)

동일한 요청을 여러 번 보내더라도 서버 상태가 한 번 요청한 것과 동일하게 유지되는 성질.

**HTTP 메서드별 멱등성**:

| 메서드 | 멱등성 | 설명 |
|--------|--------|------|
| GET | O | 안전한 조회, 상태 변경 없음 |
| PUT | O | 리소스 교체, 결과 동일 |
| DELETE | O | 반복 삭제, 결과 동일 |
| POST | X | 리소스 생성 -- 중복 방지 필요 |

**SweetBook의 중복 방지 메커니즘**:
- Redis 분산 잠금 (30초 TTL) 사용
- 처리 완료 시 즉시 잠금 해제
- 중복 요청 시 `409 Conflict` 반환

```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_REQUEST",
    "message": "이미 동일한 요청이 처리 중입니다",
    "retryAfter": 30
  }
}
```

**SDK에서의 처리**: Python SDK의 `Client._headers()`는 매 요청마다 `Idempotency-Key: {UUID}` 헤더를 자동 생성한다. 주문 생성 등 POST 요청의 중복 실행 방지에 활용된다.

> **차이점 (SDK vs 문서)**: 공식 문서는 `Idempotency-Key` 헤더 사용을 권장하고, SDK는 이를 매 요청마다 자동으로 새 UUID를 생성하여 첨부한다. AsyncClient는 `X-Transaction-ID` 헤더명을 사용한다.

### 1.8 날짜 형식

모든 타임스탬프는 **ISO 8601 UTC** 형식을 사용한다.

```
2026-03-17T09:30:00Z
```

---

## 2. 전체 워크플로우

### 2.1 10단계 워크플로우

```
1. 판형 선택          GET /book-specs
2. 템플릿 선택        GET /templates
3. 책 생성 (draft)    POST /books
4. 사진 업로드        POST /books/{bookUid}/photos
5. 표지 생성          POST /books/{bookUid}/cover
6. 내지 삽입 (반복)   POST /books/{bookUid}/contents
7. 책 확정            POST /books/{bookUid}/finalization
8. 가격 견적          POST /orders/estimate
9. 주문 생성          POST /orders
10. 웹훅 수신         Webhook
```

### 2.2 시나리오별 구현

**시나리오 A: 사용자 선택형 (앨범 앱)**  
사용자가 직접 템플릿을 선택하고 사진을 업로드하여 포토북을 만드는 방식. 판형/템플릿 목록을 캐시하여 반복 API 호출을 줄이는 것이 핵심.

**시나리오 B: 서버 자동 생성형 (일기장/알림장 앱)**  
서버가 데이터(일기, 알림장 등)를 기반으로 자동으로 포토북을 생성하는 방식. 템플릿 UID와 파라미터 매핑을 서버에 사전 설정해야 한다.

### 2.3 SDK로 보는 전체 흐름

```python
from bookprintapi import Client

client = Client()  # .env에서 API Key 자동 로드

# 1. 책 생성
book = client.books.create(
    book_spec_uid="SQUAREBOOK_HC",
    title="우리 가족 앨범",
    creation_type="TEST"
)
book_uid = book["data"]["bookUid"]

# 2. 사진 업로드
client.photos.upload(book_uid, "photo1.jpg")
client.photos.upload(book_uid, "photo2.jpg")

# 3. 표지 생성
client.covers.create(book_uid,
    template_uid="COVER_TEMPLATE_UID",
    parameters={"title": "우리 가족 앨범", "frontPhoto": "photo1.jpg"}
)

# 4. 내지 삽입 (반복)
client.contents.insert(book_uid,
    template_uid="CONTENT_TEMPLATE_UID",
    parameters={"photo": "photo2.jpg", "text": "즐거운 하루"}
)

# 5. 책 확정
client.books.finalize(book_uid)

# 6. 견적 조회
estimate = client.orders.estimate([{"bookUid": book_uid, "quantity": 1}])
paid = estimate["data"]["paidCreditAmount"]
print(f"결제 금액: {paid:,.0f}원 (VAT 포함)")

# 7. 주문
order = client.orders.create(
    items=[{"bookUid": book_uid, "quantity": 1}],
    shipping={
        "recipientName": "홍길동",
        "recipientPhone": "010-1234-5678",
        "postalCode": "06100",
        "address1": "서울특별시 강남구 테헤란로 123",
        "address2": "4층",
        "memo": "부재 시 경비실"
    },
    external_ref="MY-ORDER-001"
)
order_uid = order["data"]["orderUid"]
```

---

## 3. API 레퍼런스

### 3.1 BookSpecs (판형)

BookSpec은 책의 물리적 제조 규격(크기, 제본, 표지 유형, 페이지 범위)을 정의한다.

#### GET /book-specs -- 판형 목록 조회

```
GET https://api.sweetbook.com/v1/book-specs
Authorization: Bearer {API_KEY}
```

**응답 필드**:

| 필드 | 타입 | 설명 |
|------|------|------|
| `bookSpecUid` | string | 고유 식별자 (책 생성 시 사용) |
| `name` | string | 표시 이름 |
| `innerTrimWidthMm` | number | 내지 가로 (mm) |
| `innerTrimHeightMm` | number | 내지 세로 (mm) |
| `pageMin` | int | 최소 페이지 |
| `pageMax` | int | 최대 페이지 |
| `pageIncrement` | int | 페이지 증가 단위 |
| `coverType` | string | Softcover / Hardcover |
| `bindingType` | string | PUR |
| `priceBase` | number | 기본 가격 (최소 페이지 기준) |
| `pricePerIncrement` | number | 추가 페이지당 비용 |
| `layoutSize` | object | 작업 영역 크기 |

**사용 가능한 판형**:

| 판형 UID | 이름 | 크기 (mm) | 페이지 | 표지 | 용도 |
|----------|------|-----------|--------|------|------|
| `PHOTOBOOK_A4_SC` | A4 소프트커버 | 210x297 | 24-130 (2단위) | Softcover | 일지, 포트폴리오 |
| `PHOTOBOOK_A5_SC` | A5 소프트커버 | 148x210 | 50-200 (2단위) | Softcover | 대용량 앨범 |
| `SQUAREBOOK_HC` | 정방형 하드커버 | 243x248 | 24-130 (2단위) | Hardcover | 프리미엄 선물, 졸업앨범 |

**가격 계산 공식**:

```
총 가격 = priceBase + ((pageCount - pageMin) / pageIncrement) * pricePerIncrement
```

예시 (SQUAREBOOK_HC, 40페이지):
- 기본가: 19,800원 (24p 포함)
- 추가: (40 - 24) / 2 * 500 = 4,000원
- **합계: 23,800원**

> Sandbox에서는 테스트 가격(100원 이하)이 적용된다. Live 가격은 스위트북과 별도 협의.

#### GET /book-specs/{bookSpecUid} -- 판형 상세 조회

```
GET https://api.sweetbook.com/v1/book-specs/SQUAREBOOK_HC
Authorization: Bearer {API_KEY}
```

**curl 예시**:
```bash
curl 'https://api-sandbox.sweetbook.com/v1/book-specs/SQUAREBOOK_HC' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

> **실제 테스트 결과**: `GET /book-specs`는 `accountUid` 관련 403 Forbidden 에러가 발생한다. [8장 참고](#8-실제-테스트-결과)

---

### 3.2 Templates (템플릿)

템플릿은 텍스트, 이미지, 그래픽 요소의 배치를 정의하는 사전 구성 디자인 프레임워크이다.

**템플릿 종류**:

| 종류 | templateKind | 적용 API | 설명 |
|------|-------------|----------|------|
| 표지 | `cover` | `POST /books/{bookUid}/cover` | 1권당 1개 |
| 내지 | `content` | `POST /books/{bookUid}/contents` | 반복 적용 가능 |

**카테고리**: diary, notice, album, yearbook, wedding, baby, travel, etc

#### GET /templates -- 템플릿 목록 조회

```
GET https://api.sweetbook.com/v1/templates
Authorization: Bearer {API_KEY}
```

**쿼리 파라미터**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `bookSpecUid` | string | 권장 | 판형 필터 (예: `SQUAREBOOK_HC`) |
| `templateKind` | string | - | `cover` 또는 `content` |
| `category` | string | - | 카테고리 필터 |
| `limit` | int | - | 결과 수 (기본 50) |
| `offset` | int | - | 페이지네이션 오프셋 |

**응답 필드**: `templateUid`, `templateName`, `templateKind`, `category`, `bookSpecUid`, `isPublic`, `status`, `thumbnails`, `createdAt`, `updatedAt`

```bash
curl 'https://api-sandbox.sweetbook.com/v1/templates?bookSpecUid=SQUAREBOOK_HC&templateKind=content' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

#### GET /templates/{templateUid} -- 템플릿 상세 조회

상세 정보: `parameters` (파라미터 정의), `layout` (레이아웃 사양), `layoutRules`, `baseLayer`, `thumbnails`

#### GET /template-categories -- 카테고리 목록 조회

```
GET https://api.sweetbook.com/v1/template-categories
Authorization: Bearer {API_KEY}
```

**파라미터 바인딩 유형**:

| 타입 | binding 값 | 설명 | 예시 |
|------|-----------|------|------|
| 텍스트 | `text` | 문자열 값 | `"bookTitle": "앨범"` |
| 파일 | `file` | 이미지 URL 또는 업로드 파일명 | `"lineBg": "https://..."` |
| 갤러리 | `rowGallery` | 사진 파일명 배열 | `"photos": ["photo1.jpg"]` |

---

### 3.3 Books (책)

#### POST /books -- 책 생성

```
POST https://api.sweetbook.com/v1/books
Content-Type: application/json
Authorization: Bearer {API_KEY}
```

**요청 파라미터**:

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `title` | string | O | 책 제목 |
| `bookSpecUid` | string | O | 판형 UID |
| `specProfileUid` | string | - | 규격 프로필 UID |
| `creationType` | string | - | `NORMAL` (기본) 또는 `TEST` |
| `externalRef` | string | - | 외부 참조 ID (최대 100자) |

> **차이점 (SDK vs 문서)**: 공식 문서에서는 `title`이 필수이지만, SDK의 `books.create()`에서는 `title`이 선택이고 `book_spec_uid`만 필수이다. `bookAuthor`, `specProfileUid` 등은 SDK에서 직접 지원하지 않으나 `client.post()`로 직접 전송 가능.

**요청 JSON 예시**:
```json
{
  "title": "나의 포토북",
  "bookSpecUid": "SQUAREBOOK_HC",
  "creationType": "TEST",
  "externalRef": "PARTNER-ORDER-001"
}
```

**응답** (201 Created):
```json
{
  "success": true,
  "message": "책 생성 완료",
  "data": {
    "bookUid": "bk_3dJTg8WOpR2e"
  }
}
```

**curl 예시**:
```bash
curl -X POST 'https://api-sandbox.sweetbook.com/v1/books' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "나의 포토북",
    "bookSpecUid": "SQUAREBOOK_HC",
    "creationType": "TEST"
  }'
```

**SDK 예시**:
```python
result = client.books.create(
    book_spec_uid="SQUAREBOOK_HC",
    title="나의 포토북",
    creation_type="TEST",
    external_ref="PARTNER-001"
)
book_uid = result["data"]["bookUid"]
```

#### GET /books -- 책 목록 조회

```
GET https://api.sweetbook.com/v1/books
Authorization: Bearer {API_KEY}
```

**쿼리 파라미터**:

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `limit` | int | 20 | 결과 수 (최대 100) |
| `offset` | int | 0 | 오프셋 |
| `pdfStatusIn` | string | - | PDF 상태 필터 (콤마 구분) |
| `createdFrom` | string | - | 시작일 (ISO 8601) |
| `createdTo` | string | - | 종료일 (ISO 8601) |

> **차이점 (SDK vs 문서)**: SDK의 `books.list()`는 `status` 파라미터("draft"/"finalized")를 지원하지만, 공식 문서에서는 `pdfStatusIn` 필터를 사용한다.

**응답 필드**: `bookUid`, `title`, `bookSpecUid`, `status` (0: draft, 2: finalized, 9: deleted), `pdfStatus`, `pageCount`, `createdAt`, `externalRef`

**SDK 예시**:
```python
# 전체 목록
result = client.books.list(limit=50)

# finalized만
result = client.books.list(status="finalized", limit=20, offset=0)
```

#### GET /books/{bookUid} -- 책 상세 조회

```bash
curl 'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

**SDK 예시**:
```python
detail = client.books.get("bk_3dJTg8WOpR2e")
```

#### POST /books/{bookUid}/finalization -- 책 확정

draft 상태의 책을 finalized로 변환. 확정 후에는 내용 수정 불가.

**제약 조건**:
- draft 상태만 가능
- 페이지 수가 bookSpec의 pageMin~pageMax 범위 내
- 페이지 수가 pageIncrement의 배수

**자동 처리**:
- 표지 등뼈(spine) 너비 자동 조정 (최종 페이지 수 기반)
- 좌측 요소 유지, 우측 요소 이동, 등뼈 내 세로 텍스트 반절 이동

**응답** (201 Created / 200 OK -- 이미 확정됨, 멱등):
```json
{
  "success": true,
  "message": "책 최종화 완료",
  "data": {
    "result": "페이지를 추가하지 않고 완료",
    "pageCount": 24,
    "finalizedAt": "2025-10-01T02:28:45.505Z"
  }
}
```

**에러 응답** (페이지 부족):
```json
{
  "success": false,
  "message": "Validation Error",
  "data": null,
  "errors": ["페이지 수는 최소 20페이지 이상이어야 합니다"]
}
```

**SDK 예시**:
```python
result = client.books.finalize("bk_3dJTg8WOpR2e")
```

#### DELETE /books/{bookUid} -- 책 삭제

draft 상태만 삭제 가능.

```bash
curl -X DELETE 'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

**SDK 예시**:
```python
client.books.delete("bk_3dJTg8WOpR2e")
```

> **SDK 참고**: SDK의 Books 엔드포인트 경로는 `/Books` (대문자 B)를 사용한다. 공식 문서는 `/books` (소문자). 서버에서 대소문자 구분 없이 처리되는 것으로 보인다.

---

### 3.4 Photos (사진)

#### POST /books/{bookUid}/photos -- 사진 업로드

```
POST https://api.sweetbook.com/v1/books/{bookUid}/photos
Content-Type: multipart/form-data
Authorization: Bearer {API_KEY}
```

**폼 필드**: `file` (필수)

**지원 형식**: JPEG, PNG, GIF (첫 프레임), BMP, TIFF, WebP, HEIC/HEIF

**업로드 제한**:

| 항목 | 제한 |
|------|------|
| 요청당 최대 | 200MB (SDK: 1장씩 전송) |
| 개별 파일 | 50MB |
| 책당 최대 사진 수 | 200장 |
| Rate Limit | 200 req/min |

**자동 처리**:
- HEIC/HEIF -> JPEG 변환
- EXIF 회전 자동 적용
- 썸네일 생성 (최대 800px)
- 원본 보존 (4000px로 리사이즈)
- Magic Byte로 실제 파일 형식 검증
- MD5 해시 중복 감지

> SVG는 지원하지 않는다. PNG 또는 JPEG로 변환 후 업로드해야 한다.

**응답**:
```json
{
  "success": true,
  "data": {
    "fileName": "photo250105143052123.JPG",
    "originalName": "IMG_1234.jpg",
    "size": 1234567,
    "mimeType": "image/jpeg",
    "uploadedAt": "2026-01-05T14:30:52Z",
    "isDuplicate": false,
    "hash": "d41d8cd98f00b204e9800998ecf8427e"
  }
}
```

**curl 예시**:
```bash
curl -X POST 'https://api-sandbox.sweetbook.com/v1/books/bk_xxx/photos' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -F 'file=@photo1.jpg'
```

**SDK 예시**:
```python
# 1장 업로드
result = client.photos.upload("bk_xxx", "photo1.jpg")
file_name = result["data"]["fileName"]

# 여러 장 업로드 (순차)
results = client.photos.upload_multiple("bk_xxx", ["img1.jpg", "img2.jpg", "img3.jpg"])
```

#### GET /books/{bookUid}/photos -- 사진 목록 조회

```python
result = client.photos.list("bk_xxx")
```

#### DELETE /books/{bookUid}/photos/{fileName} -- 사진 삭제

draft 상태 책만 삭제 가능. 응답: `204 No Content`.

```python
client.photos.delete("bk_xxx", "photo250105143052123.JPG")
```

**해상도 권장**: 인쇄 품질을 위해 300 DPI 이상 권장. 스마트폰 사진은 대체로 충분. SNS/메신저에서 가져온 이미지는 압축되어 해상도가 낮을 수 있다.

---

### 3.5 Covers (표지)

#### POST /books/{bookUid}/cover -- 표지 생성/수정

```
POST https://api.sweetbook.com/v1/books/{bookUid}/cover
Content-Type: multipart/form-data
Authorization: Bearer {API_KEY}
```

**폼 필드**:

| 필드 | 필수 | 설명 |
|------|------|------|
| `templateUid` | O | 표지 템플릿 UID |
| `parameters` | - | JSON 문자열 (템플릿 파라미터) |
| 동적 이미지 필드 | - | 템플릿 변수명과 매칭되는 이미지 |

**이미지 제공 방법** (4가지):
1. **파일 업로드**: multipart/form-data로 직접 전송
2. **URL**: http/https/www로 시작하는 URL 문자열
3. **서버 파일명**: Photos API로 업로드한 파일명
4. **$upload 플레이스홀더**: `"frontPhoto": "$upload"` + files 필드에 파일 매칭

**응답**: `201 Created` (신규) / `200 OK` (수정)

```json
{
  "success": true,
  "message": "Cover created successfully",
  "data": {
    "result": "inserted"
  }
}
```

**curl 예시**:
```bash
curl -X POST 'https://api-sandbox.sweetbook.com/v1/books/bk_xxx/cover' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -F 'templateUid=tpl_F8d15af9fd' \
  -F 'parameters={"title":"나의 앨범","frontPhoto":"$upload"}' \
  -F 'files=@front.jpg'
```

**SDK 예시**:
```python
# 업로드된 파일명 사용
client.covers.create("bk_xxx",
    template_uid="tpl_cover001",
    parameters={"title": "My Book", "frontPhoto": "photo1.jpg"}
)

# $upload 플레이스홀더 + 파일 직접 업로드
client.covers.create("bk_xxx",
    template_uid="tpl_cover001",
    parameters={"title": "My Book", "frontPhoto": "$upload"},
    files=["cover.jpg"]
)
```

#### GET /books/{bookUid}/cover -- 표지 조회

```python
result = client.covers.get("bk_xxx")
```

#### DELETE /books/{bookUid}/cover -- 표지 삭제

```python
client.covers.delete("bk_xxx")
```

---

### 3.6 Contents (내지)

#### POST /books/{bookUid}/contents -- 내지 삽입

```
POST https://api.sweetbook.com/v1/books/{bookUid}/contents?breakBefore={value}
Content-Type: multipart/form-data
Authorization: Bearer {API_KEY}
```

**쿼리 파라미터**:

| 파라미터 | 값 | 설명 |
|----------|-----|------|
| `breakBefore` | `none` | 이전 컨텐츠 바로 다음에 배치 (기본값) |
| | `column` | 다음 컬럼 또는 새 페이지 |
| | `page` | 새 페이지/사이드부터 시작 |

**폼 필드**: `templateUid` (필수), `parameters` (JSON 문자열), 동적 이미지 필드

**template_kind별 breakBefore 허용**:

| template_kind | none | column | page | pageSide |
|---------------|------|--------|------|----------|
| content | O | O | O | X (에러) |
| divider | X (에러) | X (에러) | O (기본) | O (left/right) |
| publish | X (에러) | X (에러) | O (기본) | O (left/right) |

**응답** (201 Created):
```json
{
  "success": true,
  "message": "Content created successfully",
  "data": {
    "result": "inserted",
    "breakBefore": "page"
  }
}
```

**curl 예시**:
```bash
curl -X POST 'https://api-sandbox.sweetbook.com/v1/books/bk_xxx/contents?breakBefore=page' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -F 'templateUid=tpl_content001' \
  -F 'parameters={"date":"2026-01-01","diaryText":"오늘의 일기"}'
```

**SDK 예시**:
```python
# 텍스트 전용 내지
client.contents.insert("bk_xxx",
    template_uid="tpl_content001",
    parameters={"date": "2026-01-01", "diary_text": "오늘의 일기"},
    break_before="page"
)

# 이미지 포함 내지
client.contents.insert("bk_xxx",
    template_uid="tpl_content002",
    parameters={"photo": "$upload", "text": "설명"},
    files=["image.jpg"]
)
```

#### DELETE /books/{bookUid}/contents -- 전체 내지 삭제

표지는 유지하고 모든 내지 페이지를 삭제한다.

**응답**:
```json
{
  "success": true,
  "message": "책 내지 초기화 완료",
  "data": {
    "deletedPages": 15,
    "message": "15개의 내지 페이지가 삭제되었습니다"
  }
}
```

**SDK 예시**:
```python
client.contents.clear("bk_xxx")
```

---

### 3.7 Orders (주문)

#### 주문 상태 코드

| 코드 | 상태 | 설명 | 파트너 취소 | 배송지 변경 |
|------|------|------|:-----------:|:-----------:|
| 20 | PAID | 결제 완료 (충전금 차감) | O | O |
| 25 | PDF_READY | PDF 생성 완료 | O | O |
| 30 | CONFIRMED | 제작 확정 (인쇄일 배정) | X | O |
| 40 | IN_PRODUCTION | 인쇄 중 | X | X |
| 45 | COMPLETED | 개별 항목 제작 완료 | X | X |
| 50 | PRODUCTION_COMPLETE | 전체 제작 완료 | X | X |
| 60 | SHIPPED | 발송 완료 | X | X |
| 70 | DELIVERED | 배송 완료 | X | X |
| 80 | CANCELLED | 취소 | - | - |
| 81 | CANCELLED_REFUND | 취소 및 환불 완료 | - | - |
| 90 | ERROR | 오류 | - | - |

**상태 흐름**:
```
PAID(20) -> PDF_READY(25) -> CONFIRMED(30) -> IN_PRODUCTION(40) -> PRODUCTION_COMPLETE(50) -> SHIPPED(60) -> DELIVERED(70)
                                                                                               \-> CANCELLED(80/81)
```

#### POST /orders/estimate -- 견적 조회

충전금 차감 없이 가격만 확인한다.

```
POST https://api.sweetbook.com/v1/orders/estimate
Content-Type: application/json
Authorization: Bearer {API_KEY}
```

**요청**:
```json
{
  "items": [
    {"bookUid": "bk_xxx", "quantity": 1}
  ]
}
```

**응답 필드**:

| 필드 | 설명 |
|------|------|
| `items[]` | 항목별 상세 (bookUid, pageCount, quantity, unitPrice, itemAmount) |
| `productAmount` | 제작비 합계 |
| `shippingFee` | 배송비 |
| `packagingFee` | 포장비 |
| `totalAmount` | 합계 (세전) |
| `paidCreditAmount` | **실제 차감 금액 (VAT 10% 포함)** |
| `creditBalance` | 현재 충전금 잔액 |
| `creditSufficient` | 잔액 충분 여부 (boolean) |

**가격 계산 공식**:
```
상품금액 = 단가 x 수량
합계     = 상품금액 + 배송비(3,500원) + 포장비(500원/건)
결제금액 = Floor(합계 x 1.1 / 10) x 10   (VAT 10% 포함, 10원 미만 절삭)
```

> **차이점 (SDK README vs 문서)**: SDK README에서는 배송비 3,000원으로 기재되어 있으나, 공식 문서 Orders API에서는 배송비 3,500원 + 포장비 500원/건으로 설명한다.

**SDK 예시**:
```python
estimate = client.orders.estimate([{"bookUid": "bk_xxx", "quantity": 1}])
data = estimate["data"]
print(f"결제금액: {data['paidCreditAmount']:,.0f}원")
print(f"잔액 충분: {data['creditSufficient']}")
```

#### POST /orders -- 주문 생성

finalized 상태의 책으로 주문을 생성한다. **충전금이 즉시 차감**된다.

```
POST https://api.sweetbook.com/v1/orders
Content-Type: application/json
Authorization: Bearer {API_KEY}
```

**요청 파라미터**:

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `items` | array | O | 주문 항목 (최소 1개) |
| `items[].bookUid` | string | O | FINALIZED 상태 책 UID |
| `items[].quantity` | int | O | 수량 (1-100) |
| `shipping` | object | O | 배송 정보 |
| `shipping.recipientName` | string | O | 수령인 (최대 100자) |
| `shipping.recipientPhone` | string | O | 전화번호 (최대 20자) |
| `shipping.postalCode` | string | O | 우편번호 (최대 10자) |
| `shipping.address1` | string | O | 주소 (최대 200자) |
| `shipping.address2` | string | - | 상세주소 (최대 200자) |
| `shipping.memo` | string | - | 배송 메모 (최대 200자) |
| `externalRef` | string | - | 외부 참조 ID (최대 100자) |

**요청 JSON 예시**:
```json
{
  "items": [
    {"bookUid": "bk_abc123", "quantity": 1}
  ],
  "shipping": {
    "recipientName": "홍길동",
    "recipientPhone": "010-1234-5678",
    "postalCode": "06100",
    "address1": "서울특별시 강남구 테헤란로 123",
    "address2": "4층",
    "memo": "부재 시 경비실"
  },
  "externalRef": "MY-ORDER-001"
}
```

**응답** (201 Created):
```json
{
  "success": true,
  "message": "Order created",
  "data": {
    "orderUid": "or_3eAx1IQiGByu",
    "orderType": "NORMAL",
    "orderStatus": 20,
    "orderStatusDisplay": "Payment completed",
    "totalProductAmount": 60400.00,
    "totalShippingFee": 3500.00,
    "totalPackagingFee": 500.00,
    "totalAmount": 64400.00,
    "creditBalanceAfter": 935600.00,
    "recipientName": "홍길동",
    "items": [
      {
        "itemUid": "oi_aB3cD4eF5gH6",
        "bookUid": "bk_abc123",
        "quantity": 1,
        "unitPrice": 60400.00
      }
    ]
  }
}
```

**에러 상태**:

| 코드 | 의미 |
|------|------|
| 201 | 성공 |
| 400 | 검증 실패 |
| 401 | 인증 실패 |
| 402 | 충전금 부족 |
| 500 | 서버 오류 |

**curl 예시**:
```bash
curl -X POST 'https://api-sandbox.sweetbook.com/v1/orders' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "items": [{"bookUid": "bk_abc123", "quantity": 1}],
    "shipping": {
      "recipientName": "홍길동",
      "recipientPhone": "010-1234-5678",
      "postalCode": "06100",
      "address1": "서울특별시 강남구 테헤란로 123"
    }
  }'
```

**SDK 예시**:
```python
order = client.orders.create(
    items=[{"bookUid": "bk_abc123", "quantity": 1}],
    shipping={
        "recipientName": "홍길동",
        "recipientPhone": "010-1234-5678",
        "postalCode": "06100",
        "address1": "서울특별시 강남구 테헤란로 123",
    },
    external_ref="MY-ORDER-001"
)
order_uid = order["data"]["orderUid"]
```

#### GET /orders -- 주문 목록 조회

```
GET https://api.sweetbook.com/v1/orders?limit=20&offset=0
Authorization: Bearer {API_KEY}
```

**쿼리 파라미터**:

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `limit` | int | 결과 수 (기본 20) |
| `offset` | int | 오프셋 |
| `status` | int | 상태 코드 필터 |
| `from` | string | 시작 일시 (ISO) |
| `to` | string | 종료 일시 (ISO) |

**SDK 예시**:
```python
result = client.orders.list(limit=30, status=20)
```

#### GET /orders/{orderUid} -- 주문 상세 조회

```python
detail = client.orders.get("or_3eAx1IQiGByu")
```

#### POST /orders/{orderUid}/cancel -- 주문 취소

**PAID(20)** 또는 **PDF_READY(25)** 상태만 가능. 충전금 자동 환불.

**요청**:
```json
{
  "cancelReason": "고객 요청으로 취소"
}
```

**SDK 예시**:
```python
result = client.orders.cancel("or_xxx", "고객 요청으로 취소")
refund = result["data"]["refundAmount"]
```

#### PATCH /orders/{orderUid}/shipping -- 배송지 변경

**PAID ~ CONFIRMED** 상태에서 가능. 변경할 필드만 전송한다.

**요청 JSON**:
```json
{
  "recipientName": "김영희",
  "address1": "서울 서초구 반포대로 100"
}
```

**SDK 예시**:
```python
client.orders.update_shipping("or_xxx",
    recipient_name="김영희",
    recipient_phone="010-9999-8888",
    postal_code="06500",
    address1="서울 서초구 반포대로 100",
    address2="3층",
    shipping_memo="오후 배송 희망"
)
```

> **SDK 필드 매핑**: Python SDK는 snake_case -> camelCase 자동 변환 (예: `recipient_name` -> `recipientName`)

---

### 3.8 Credits (충전금)

#### GET /credits -- 잔액 조회

```
GET https://api.sweetbook.com/v1/credits
Authorization: Bearer {API_KEY}
```

**응답**:
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "balance": 100000,
    "currency": "KRW",
    "env": "test"
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `balance` | number | 현재 잔액 (원) |
| `currency` | string | 항상 "KRW" |
| `env` | string | "test" 또는 "live" |

**SDK 예시**:
```python
result = client.credits.get_balance()
balance = result["data"]["balance"]
```

#### GET /credits/transactions -- 거래 내역 조회

```
GET https://api.sweetbook.com/v1/credits/transactions?limit=20&offset=0
Authorization: Bearer {API_KEY}
```

**쿼리 파라미터**: `limit`, `offset`, `from`, `to`

**응답 필드**: `createdAt`, `reason`/`reasonDisplay`, `amount`, `balanceAfter`, `memo`

**SDK 예시**:
```python
result = client.credits.get_transactions(limit=50, from_date="2026-01-01", to_date="2026-03-31")
```

#### POST /credits/sandbox/charge -- Sandbox 테스트 충전

Sandbox 환경 전용. 계정 자동 생성.

**요청**:
```json
{
  "amount": 100000,
  "memo": "테스트 충전"
}
```

**SDK 예시**:
```python
result = client.credits.sandbox_charge(100000, memo="테스트 충전")
balance = result["data"]["balance"]
```

**충전금 시스템 요약**:

| 항목 | Sandbox | Live |
|------|---------|------|
| 충전 방법 | 포털에서 무료 충전 / API (sandbox_charge) | PG 결제로 충전 |
| 차감 시점 | 주문 생성 시 자동 | 주문 생성 시 자동 |
| 환불 | 취소 시 즉시 | 취소 시 즉시 |
| 분리 | Live와 완전 격리 | Sandbox와 완전 격리 |

**402 에러 응답** (충전금 부족):
```json
{
  "success": false,
  "message": "Insufficient Credit",
  "data": {
    "required": 64400.00,
    "balance": 10000.00,
    "currency": "KRW"
  }
}
```

---

### 3.9 Webhooks (웹훅)

웹훅을 통해 주문 상태 변경을 실시간으로 수신한다. 폴링 불필요.

#### PUT /webhooks/config -- 웹훅 등록/수정

```
PUT https://api.sweetbook.com/v1/webhooks/config
Content-Type: application/json
Authorization: Bearer {API_KEY}
```

**요청 파라미터**:

| 필드 | 필수 | 설명 |
|------|------|------|
| `webhookUrl` | O | HTTPS URL (최대 500자) |
| `events` | - | 구독할 이벤트 목록. null이면 전체 구독 |
| `description` | - | 설명 (최대 200자) |

**요청 예시**:
```json
{
  "webhookUrl": "https://example.com/webhooks/sweetbook",
  "events": ["order.paid", "order.shipped"],
  "description": "주문 알림"
}
```

> **중요**: `secretKey`는 최초 등록 시에만 전체 값이 반환된다. 이후 조회 시에는 앞 8자만 보인다 (예: `whsk_a1b...`).

#### GET /webhooks/config -- 웹훅 설정 조회

```bash
curl 'https://api.sweetbook.com/v1/webhooks/config' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

#### DELETE /webhooks/config -- 웹훅 비활성화

소프트 삭제. 전송 이력은 유지된다.

#### POST /webhooks/test -- 테스트 이벤트 전송

```json
{"eventType": "order.paid"}
```

**응답**:
```json
{
  "success": true,
  "data": {
    "deliveryUid": "wh_abc123xyz",
    "eventType": "order.paid",
    "status": "SUCCESS",
    "responseStatus": 200,
    "responseBody": "{\"received\": true}"
  }
}
```

#### GET /webhooks/deliveries -- 전송 이력 조회

`eventType`, `status` 파라미터로 필터링 가능.

```bash
curl 'https://api.sweetbook.com/v1/webhooks/deliveries?status=FAILED&limit=10' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

#### 웹훅 이벤트 목록

| 이벤트 | 트리거 | 주요 데이터 |
|--------|--------|-------------|
| `order.paid` | 주문 생성 (충전금 차감) | bookUid, quantity, totalCredits, shippingAddress |
| `order.confirmed` | 제작 확정 | confirmedAt, estimatedShipDate |
| `order.status_changed` | 상태 변경 시마다 | previousStatus, newStatus |
| `order.shipped` | 발송 완료 | trackingNumber, trackingCarrier, shippedAt |
| `order.cancelled` | 주문 취소 | cancelledAt, cancelReason, refundedCredits |

**택배사 코드**: `CJ`, `HANJIN`, `LOTTE`

#### 웹훅 요청 헤더

| 헤더 | 설명 | 예시 |
|------|------|------|
| `X-Webhook-Signature` | HMAC-SHA256 서명 (hex) | `a1b2c3d4...` |
| `X-Webhook-Timestamp` | 서명 생성 시각 (Unix초) | `1709280000` |
| `X-Webhook-Event` | 이벤트 타입 | `order.paid` |
| `X-Webhook-Delivery` | 고유 전송 ID (중복 감지용) | `wh_abc123xyz` |

**Sandbox 구분**: 웹훅 페이로드의 `isTest` 필드로 Sandbox/Live 구분 가능.

#### 서명 검증 (HMAC-SHA256)

**수식**: `HMAC-SHA256(secretKey, "{timestamp}.{JSON body}")`

**SDK 예시** (Python):
```python
from bookprintapi.webhook import verify_signature

# Flask
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    sig = request.headers.get('X-Webhook-Signature', '')
    ts = request.headers.get('X-Webhook-Timestamp', '')
    body = request.get_data()
    
    if not verify_signature(body, sig, ts, WEBHOOK_SECRET):
        abort(401)
    
    event = request.json
    event_type = request.headers.get('X-Webhook-Event', '')
    
    if event_type == 'order.paid':
        print(f"주문 생성: {event['data']['order_uid']}")
    elif event_type == 'order.shipped':
        print(f"발송: {event['data']['tracking_number']}")
    
    return jsonify({"received": True}), 200
```

> **차이점 (SDK vs 문서)**: SDK의 `verify_signature()`는 `signature` 파라미터에서 `sha256=` 접두사를 자동 제거한다. 공식 문서의 `X-Webhook-Signature` 헤더에는 접두사 없이 hex 값만 담긴다고 설명하지만, SDK는 양쪽 모두 처리한다. 또한 SDK는 `tolerance` 파라미터(기본 300초)로 타임스탬프 만료 검증을 추가로 수행한다.

#### 재시도 정책

실패(비 2xx 응답 또는 타임아웃) 시 최대 3회 자동 재시도:

| 재시도 | 대기 시간 |
|--------|-----------|
| 1회 | 1분 |
| 2회 | 5분 |
| 3회 | 30분 |

3회 실패 후 `EXHAUSTED` 상태. `webhook.exhausted` 이벤트 발생 (동일 알림 1시간 쿨다운).

**전송 상태**:

| 상태 | 설명 |
|------|------|
| PENDING | 전송 대기/진행 중 |
| SUCCESS | 전송 성공 (2xx 응답) |
| FAILED | 실패, 재시도 대기 |
| EXHAUSTED | 최대 재시도(3회) 초과 |

**HTTP 타임아웃**: 30초. 오래 걸리는 처리는 비동기로 수행하고 200을 즉시 반환해야 한다.

#### 구현 모범 사례

- 200-299 상태 코드로 응답 (그 외는 실패 처리)
- 30초 내 응답 완료
- 항상 `X-Webhook-Signature` 검증
- `X-Webhook-Delivery`로 중복 이벤트 처리 (같은 이벤트가 중복 전송될 수 있음)
- HTTPS만 사용

---

## 4. 개념 설명 (Concepts)

### 4.1 Template Engine

Template Engine v1.0 (2026-03-24)은 API 플랫폼의 템플릿 처리 사양이다.

**핵심 변경 사항**:
- 필수 프로퍼티 선언 제거 (parameters에 정의된 모든 파라미터는 기본 required=true)
- visible 바인딩으로 레이아웃 요소 가시성 제어
- shiftUpOnHide 레이아웃 규칙 추가

**파라미터 정의 구조**:
```json
{
  "parameters": {
    "bookTitle": { "binding": "text", "type": "string", "description": "책 제목" },
    "fontSize": { "binding": "text", "type": "int", "description": "폰트 크기" },
    "photo1": { "binding": "file", "type": "string", "description": "메인 사진" }
  }
}
```

**binding 유형**: `text` (문자열 기반), `file` (이미지/파일 ID/URL)  
**type**: `string`, `int`, `double`, `boolean`

**visible 바인딩**: 요소의 `visible` 속성에 `"$$paramName$$"` 형태로 바인딩하면 해당 파라미터 값에 따라 가시성이 제어된다.

**layoutRules 구조**:

| 속성 | 설명 |
|------|------|
| `space` | 레이아웃 컨테이너 ("page") |
| `margin.pageMargin` | spine, fore, head, tail 여백 |
| `margin.mirrorEvenPages` | 짝수 페이지에서 spine/fore 반전 |
| `flow.columns` | 컬럼 수 (1-3) |
| `flow.columnGap` | 컬럼 간 간격 |
| `shiftUpOnHide` | 숨겨진 요소 아래 재배치 |
| `lanes` | X-lane 경계 정의 |

**요소 타입**: `text`, `graphic` (정적 이미지), `photo` (파일 참조), `group` (groupName으로 구성)

**타입 변환**: API 입력은 문자열로 전달되지만 지정된 타입으로 변환된다 (예: "14" -> int 14).

### 4.2 Dynamic Layout

Dynamic Layout은 Contents API의 핵심 기능으로, 템플릿 요소를 페이지 전체에 걸쳐 자동 배치한다.

**주요 기능**:

| 기능 | 설명 |
|------|------|
| Auto Placement | 컬럼, 사이드, 페이지 자동 선택 |
| Column System | 1-3 컬럼 레이아웃 (슬롯 기반) |
| Text Splitting | `splittable` 속성으로 긴 텍스트 자동 분할 |
| Dynamic Height | `isDynamic` 속성으로 실시간 텍스트 높이 계산 |
| breakBefore Control | 배치 위치 세밀 제어 |
| Lanes | X 범위 기반 독립 Y 흐름 |
| shiftUpOnHide | 조건부 요소 숨김 시 자동 레이아웃 리플로우 |
| DynamicDelta | isDynamic 요소 높이 변화에 대한 Y 좌표 보정 |

**페이지 구조 (양면 인쇄)**:

PUR 제본 기본:

| pageNum | pageSide | 설명 |
|---------|----------|------|
| 0 | right | 표지 |
| 1 | right | 첫 번째 내지 (오른쪽 시작) |
| 2 | left/right | 두 번째 내지 |

**JSON 파일명 규칙**: 표지 `cover.json`, 1페이지 `000.json`, N페이지 `{N-1:D3}.json` (3자리 zero-padding)

**컬럼 시스템**:

`layoutRules.flow.columns`로 정의. 슬롯은 0부터 시작.

```
X좌표 = (슬롯인덱스 * slotWidth) + (pageSide == "right" ? pageWidth : 0)
```

**pageMargin + columnGap이 있는 경우** (신규 레이아웃):
```
contentWidth = pageWidth - (spine + fore)
slotWidth = (contentWidth - columnGap * (columns - 1)) / columns
좌측 X = fore + slotIndex * (slotWidth + columnGap) + templateX
우측 X = pageWidth + spine + slotIndex * (slotWidth + columnGap) + templateX
높이 = fullPageHeight - (head + tail)
첫 요소 Y = head + originalY
```

| 항목 | 레거시 | 신규 (pageMargin + columnGap) |
|------|--------|-------------------------------|
| 컬럼 너비 | `pageWidth / columns` | `(contentWidth - columnGap*(columns-1)) / columns` |
| 좌측 X | `slotIndex * slotWidth` | `fore + slotIndex * (slotWidth + columnGap) + templateX` |
| 우측 X | `pageWidth + slotIndex * slotWidth` | `pageWidth + spine + slotIndex * (slotWidth + columnGap) + templateX` |

> pageMargin이 존재하면 (0이라도) 신규 레이아웃이 적용된다. 1컬럼 템플릿에서는 columnGap이 무시된다.

**breakBefore 상세**:

| 값 | 동작 | 용도 |
|----|------|------|
| `none` | 이전 컨텐츠 직후 배치 | 연속 콘텐츠, 텍스트 흐름 |
| `column` | 다음 컬럼/슬롯으로 이동 | 컬럼 분리, 섹션 시작 |
| `page` | 다음 사이드 또는 페이지로 이동 | 챕터 시작, 중요 콘텐츠 |

**isDynamic + splittable 조합**:

| isDynamic | splittable | 동작 |
|-----------|-----------|------|
| false | false | 템플릿 높이 사용, 단일 배치 (기본) |
| true | false | 동적 높이 계산, 단일 배치 |
| false | true | 템플릿 높이 사용, 분할 배치 (비권장) |
| **true** | **true** | **동적 높이 + 분할 배치 (권장)** |

요소 정의 예시:
```json
{
  "type": "text",
  "text": "$$userContent$$",
  "isDynamic": true,
  "splittable": true,
  "fontSize": 14,
  "width": 400,
  "height": 100
}
```

**Lanes (X 기반 독립 Y 흐름)**:

일부 템플릿에서 서로 다른 X 영역이 독립적인 Y 흐름을 가져야 할 때 사용한다.

```json
{
  "layoutRules": {
    "lanes": [
      { "id": "left",  "xMin": 0,   "xMax": 155  },
      { "id": "right", "xMin": 155, "xMax": 1000 }
    ]
  }
}
```

각 lane은 독립적인 maxY를 추적한다.

**shiftUpOnHide (조건부 요소 숨김)**:

`layoutRules.shiftUpOnHide: true`와 요소의 `visible: "$$param$$"`를 조합하면, 파라미터가 `false`일 때 요소를 숨기고 아래 요소를 위로 올린다. lanes가 있으면 같은 X-lane의 요소만 이동한다.

**DynamicDelta (isDynamic 앵커 보정)**:
```
최종 Y = max(anchoredY, sequentialY)
anchoredY = TemplateBaseY + OriginalY + DynamicDelta
DynamicDelta = Sum(실제높이 - 템플릿높이)
```
새 템플릿 시작 시 DynamicDelta는 0으로 초기화.

**itemSpacing (템플릿 간격)**:
```json
{
  "layoutRules": {
    "flow": {
      "itemSpacing": { "size": 15 }
    }
  }
}
```
새 템플릿의 첫 요소 배치 시 이전 콘텐츠의 하단 Y에 `itemSpacing.size`를 추가한다. 미설정 시 요소의 `OriginalY`가 간격으로 사용된다.

### 4.3 Element Grouping

같은 그룹의 요소들은 항상 같은 컬럼/페이지에 배치된다.

**특성**:
- `groupName` 속성으로 그룹 지정
- 그룹 내 요소 하나라도 공간 부족 시 전체 그룹이 다음 컬럼/페이지로 이동
- splittable 텍스트는 그룹과 독립적으로 분할 가능
- 그룹 높이가 페이지 높이를 초과하면 에러 반환

```json
{
  "element_id": "text-1",
  "type": "text",
  "groupName": "group1"
}
```

**그룹 규칙**: 같은 `groupName`의 요소는 Y좌표 순서대로 연속해야 한다. 다른 그룹이 사이에 끼면 별도 그룹으로 분리된다.

**배치 동작**:
1. 전체 그룹이 현재 컬럼에 들어감 -> 함께 배치
2. 공간 초과 -> 전체 그룹 다음 컬럼/페이지로 이동
3. splittable 텍스트 + 공간 있음 -> 텍스트만 분할, 나머지 유지
4. splittable 텍스트 + 공간 없음 -> 전체 그룹 이동

**에러 (splittable 없이 페이지 초과)**:
```json
{
  "success": false,
  "message": "Template error: Group height exceeds page height"
}
```
해결: 요소 수 줄이기, 높이 줄이기, 또는 텍스트에 `splittable: true` 추가.

**최종 PAGE JSON**: `groupName`, `splittable`, `isDynamic`, `originalHeight`는 제거된다.

**X-lane 분리**: lanes가 정의되면 다른 lane의 요소는 별도 그룹으로 처리된다.

### 4.4 Gallery Templates

> 공식 문서 `/docs/concepts/gallery-templates/` 페이지는 현재 404로 접근 불가. 아래는 다른 문서 페이지에서 수집한 정보.

Gallery 템플릿은 사진 파일명 배열을 받아 동적으로 여러 페이지에 사진을 분배하는 레이아웃이다.

**파라미터 바인딩**: `rowGallery` 타입으로, 사진 파일명 배열을 전달한다.
```json
{
  "photos": ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
}
```

갤러리 이미지는 `POST /books/{bookUid}/photos`로 사전 업로드가 필요하다. 사진 수에 따라 자동으로 페이지 수가 조절된다.

### 4.5 Column Templates

> 공식 문서 `/docs/concepts/column-templates/` 페이지는 현재 404로 접근 불가. 아래는 다른 문서 페이지에서 수집한 정보.

Column 템플릿은 텍스트와 이미지를 세로로 쌓는 레이아웃으로, 일기장/리뷰 등 가변 길이 콘텐츠에 적합하다. 유연한 레이아웃 조정을 지원하며, `layoutRules.flow.columns`로 1-3 컬럼을 설정할 수 있다.

### 4.6 Base Layer

Base Layer는 모든 페이지에 자동으로 적용되는 헤더/푸터/장식 배경 레이어이다.

**주요 기능**:

| 기능 | 설명 |
|------|------|
| 페이지별 자동 적용 | 내용이 여러 페이지로 분할되면 각 페이지에 자동 적용 |
| 홀수/짝수 분리 | 좌/우 페이지에 다른 레이아웃 |
| 시스템 변수 | 페이지 번호, 날짜 등 자동 치환 |
| 사용자 파라미터 | `$$variableName$$` 형태로 바인딩 |

**구조**:
```json
{
  "baseLayer": {
    "odd": { "elements": [/* 오른쪽(홀수) 페이지 요소 */] },
    "even": { "elements": [/* 왼쪽(짝수) 페이지 요소 */] }
  }
}
```

**페이지 규칙**: page 1(right/odd) -> odd baseLayer, page 2(left/even) -> even baseLayer, 이후 교대.

**시스템 변수** (`@@변수명@@`):
- `@@pageNum@@` -- 현재 페이지 번호
- `@@datetime.year@@`, `@@datetime.month@@`, `@@datetime.date@@` -- 현재 날짜
- `@@bookTitle@@` -- 책 제목

**사용자 파라미터**: `$$variableName$$` 형태로 API 호출 시 전달한 템플릿 파라미터 값으로 치환.

**element_id 접두사 규칙**:
- 홀수 페이지: `bl-odd-*`
- 짝수 페이지: `bl-even-*`

**좌표 시스템** (스프레드 기준, ~1956px 전체 폭):
- 왼쪽 페이지(짝수): X: 50-928 (978px 폭)
- 오른쪽 페이지(홀수): X: 1028-1906 (978px 폭)

**지원 요소 타입**: `text` (헤더, 푸터, 페이지 번호), `graphic` (이미지, 장식선, 로고)

**주의사항**:
- 모든 baseLayer 요소에 고유 ID 필요
- odd 요소는 x >= 1028, even 요소는 x ~ 50 부근
- 헤더/푸터 영역이 콘텐츠와 겹치지 않도록 `layoutRules.margin` 설정

### 4.7 Text Processing

WPF FormattedText 기반 텍스트 높이 계산 시스템. .NET 4.5 레거시 에디터와 완벽한 일관성 유지.

**측정 규칙**:

| 항목 | 값 |
|------|-----|
| 너비 인셋 | 8px (텍스트 프레임 너비에서 제외) |
| 줄 높이 | `fontSize * 1.6984` (고정 배수) |
| 텍스트 정렬 | 양쪽 맞춤 (Justified) |
| 최종 높이 | `max(한 줄 높이, 전체 높이 + 10px 패딩)` |
| 내부 폰트 크기 | `fontSize * 1.1` |

**TextUtil API 메서드**:

| 메서드 | 설명 |
|--------|------|
| `GetHeight()` | 콘텐츠, 크기, 스타일 기반 텍스트 높이 계산 |
| `GetLineCount()` | 지정 너비 내 줄 수 반환 |
| `GetOneLineHeight()` | 콘텐츠 무관 한 줄 높이 |
| `GetDispartText()` | 높이 제한 내 텍스트 분할 (여러 세그먼트 반환) |
| `BadTextRemover()` | HTML 엔티티/특수문자 제거 |

**테스트 API**: `POST /books/{bookUid}/text-height` -- 높이 계산 결과를 페이지에 추가 (개발 용도).

**텍스트 분할 구현**: 이진 탐색(O(log n))으로 분할 지점 결정. 단어 경계 우선 조정 (공백 > 구두점 > 95% 최소 유지 > 원본 분할점).

**폰트 처리**: `textBold`, `textItalic` 속성으로 스타일링. 시스템에 설치된 폰트 필요 (Windows `C:\Windows\Fonts\`).

**성능**:

| 항목 | 값 |
|------|-----|
| 단일 측정 | 5-8ms |
| 배치 (10건) | ~45ms |
| STA 스레드 풀 | 기본 4개 (2-16 설정 가능) |
| 큐 타임아웃 | 추가 2초, 측정 10초 |
| 큐 용량 | 1,000건 |

**제한 사항**:
- **Windows 전용** (WPF 의존) -- Docker에서는 Windows 컨테이너 필요
- DPI 고정: 96
- 시스템 설치 폰트만 사용 가능 (디렉토리 배치 불가)
- WPF와 브라우저 간 렌더링 차이 존재

### 4.8 Special Page Rules

`template_kind`에 따른 특수 페이지 배치 규칙과 `pageSide` 동작을 정의한다.

**template_kind 종류**:

| 종류 | 설명 | breakBefore | pageSide |
|------|------|-------------|----------|
| `content` | 일반 내지 (Flow 엔진 연속 배치) | none/column/page | 사용 불가 (에러) |
| `divider` | 구분 페이지 (독립 특수 페이지) | page만 (기본) | left/right 선택 가능 |
| `publish` | 발행면/판권 페이지 (독립 특수 페이지) | page만 (기본) | left/right 선택 가능 |

**특수 페이지 배치 규칙**: 항상 기존 콘텐츠 이후에만 배치 (역방향 이동 불가).

**pageSide 배치 알고리즘** (divider/publish):

| 현재 Side | 요청 Side | 결과 페이지 | 결과 Side | 설명 |
|-----------|-----------|-------------|-----------|------|
| left | left | +1 | left | 다음 페이지 왼쪽 |
| left | right | same | right | 같은 페이지 오른쪽 |
| right | left | +1 | left | 다음 페이지 왼쪽 |
| right | right | +1 | right | 다음 페이지 오른쪽 |

**정방형 책 예외**: 첫 내지(pagenum=1)는 right에서 시작. `pageSide=left` 요청 시 pagenum=2, left에 배치.

---

## 5. 에러 코드

### HTTP 상태별 에러

| 상태 | 의미 | 원인 | 해결 |
|------|------|------|------|
| 400 | Bad Request | 필수 필드 누락, 잘못된 값 | `fieldErrors` 확인 후 수정 |
| 401 | Unauthorized | API Key 누락/무효 | 키 확인, 환경 URL 일치 확인 |
| 402 | Payment Required | 충전금 부족 | 포털에서 충전 후 재시도 |
| 403 | Forbidden | 폐기된 키, IP 차단, 권한 부족 | 포털에서 키 상태 확인 |
| 404 | Not Found | bookUid/orderUid 오류 | 생성 응답의 ID 재확인 |
| 409 | Conflict | 중복 요청, Idempotency Key 충돌 | 기존 요청 결과 조회 |
| 429 | Too Many Requests | Rate Limit 초과 | `Retry-After` 헤더 확인, 빈도 줄이기 |
| 500 | Internal Server Error | 서버 오류 | 잠시 후 재시도, 지속 시 지원 연락 |

### 에러 응답 형식

**일반 에러**:
```json
{
  "success": false,
  "message": "Unauthorized. Invalid API key.",
  "data": null
}
```

**필드 검증 에러** (400):
```json
{
  "success": false,
  "message": "Validation failed",
  "fieldErrors": [
    {"field": "email", "message": "Invalid email format"},
    {"field": "recipientName", "message": "recipientName is required"}
  ]
}
```

**충전금 부족** (402):
```json
{
  "success": false,
  "message": "Insufficient Credit",
  "data": {
    "required": 12500,
    "balance": 5000,
    "currency": "KRW"
  }
}
```

**중복 요청** (409):
```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_REQUEST",
    "message": "이미 동일한 요청이 처리 중입니다",
    "retryAfter": 30
  }
}
```

### 에러 처리 권장 패턴

```python
from bookprintapi import Client, ApiError

client = Client()

try:
    order = client.orders.create(
        items=[{"bookUid": "bk_invalid", "quantity": 1}],
        shipping={...}
    )
except ApiError as e:
    print(f"오류: {e}")                 # [400] Bad Request
    print(f"상태코드: {e.status_code}")  # 400
    print(f"에러코드: {e.error_code}")   # 에러 코드 (있는 경우)
    print(f"상세: {e.details}")          # ["Book을 찾을 수 없습니다: bk_invalid"]
    
    if e.status_code == 402:
        print("충전금이 부족합니다. 충전 후 다시 시도하세요.")
    elif e.status_code == 429:
        print("요청이 너무 많습니다. 잠시 후 재시도하세요.")
```

---

## 6. SDK 사용법

### 6.1 설치

```bash
# 소스에서 설치
pip install -e .

# 또는 설치 없이 사용
import sys; sys.path.insert(0, "/path/to/bookprintapi-python-sdk")
from bookprintapi import Client
```

**요구사항**: Python 3.10+, `requests>=2.31`, `python-dotenv>=1.0.0`

**비동기 사용 시**: `pip install httpx` 추가

### 6.2 환경 설정

**환경변수**:

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `BOOKPRINT_API_KEY` | API Key (필수) | - |
| `BOOKPRINT_ENV` | `sandbox` 또는 `live` | `live` |
| `BOOKPRINT_BASE_URL` | API URL 직접 지정 (위 두 변수보다 우선) | - |

> **차이점 (SDK vs 문서)**: SDK 환경변수명은 `BOOKPRINT_*` 접두사를 사용한다. 공식 문서의 코드 예시에서는 `SWEETBOOK_API_KEY`를 사용하는 경우도 있다.

**URL 매핑**:

| environment 값 | URL |
|----------------|-----|
| `live` (기본) | `https://api.sweetbook.com/v1` |
| `sandbox` | `https://api-sandbox.sweetbook.com/v1` |

**초기화 방법**:

```python
# 방법 1: 환경변수 (.env 파일)
from bookprintapi import Client
client = Client()  # BOOKPRINT_API_KEY에서 자동 로드

# 방법 2: 직접 지정
client = Client(
    api_key="SBxxxxx.xxxx",
    environment="sandbox"
)

# 방법 3: Base URL 직접 지정
client = Client(
    api_key="SBxxxxx.xxxx",
    base_url="https://api-sandbox.sweetbook.com/v1"
)

# 방법 4: 타임아웃/재시도 설정
client = Client(
    api_key="SBxxxxx.xxxx",
    timeout=120,        # 초 (기본 60)
    max_retries=5       # 재시도 횟수 (기본 3)
)
```

### 6.3 SDK 구조

```python
client = Client(api_key="SBxxxxx.xxxx")

client.books       # BooksClient -- 책 생성/조회/확정/삭제
client.photos      # PhotosClient -- 사진 업로드/조회/삭제
client.covers      # CoversClient -- 표지 생성/조회/삭제
client.contents    # ContentsClient -- 내지 삽입/삭제
client.orders      # OrdersClient -- 주문 생성/조회/취소/배송지변경
client.credits     # CreditsClient -- 충전금 잔액/거래내역/Sandbox충전
```

**내부 동작**:
- 모든 요청에 `Authorization: Bearer {api_key}` 헤더 자동 추가
- 매 요청마다 `Idempotency-Key: {UUID}` 자동 생성
- `User-Agent: BookPrintAPI-Python/0.1.0`
- 실패 시 자동 재시도: 최대 3회 (429, 500, 502, 503, 504)
- Exponential backoff (factor=1)

### 6.4 비동기 클라이언트 (AsyncClient)

```python
from bookprintapi.async_client import AsyncClient

# async with 사용 (권장)
async with AsyncClient(api_key="SBxxxxx.xxxx", environment="sandbox") as client:
    balance = await client.credits.get_balance()
    books = await client.books.list(status="finalized")
    
# 또는 수동 관리
client = AsyncClient(api_key="SBxxxxx.xxxx")
balance = await client.credits.get_balance()
await client.close()
```

**AsyncClient 지원 모듈**:

| 모듈 | 메서드 |
|------|--------|
| `client.books` | list, create, get, finalize, delete |
| `client.orders` | estimate, create, list, get, cancel, update_shipping |
| `client.credits` | get_balance, get_transactions, sandbox_charge |

> **주의**: AsyncClient는 `photos`, `covers`, `contents`를 지원하지 않는다. 파일 업로드가 필요한 작업은 동기 Client를 사용해야 한다.

**AsyncClient 차이점**:
- httpx 기반 (requests 대신)
- `X-Transaction-ID` 헤더 사용 (동기 Client의 `Idempotency-Key` 대신)
- `User-Agent: BookPrintAPI-Python-Async/0.1.0`

### 6.5 웹훅 서명 검증

```python
from bookprintapi.webhook import verify_signature

valid = verify_signature(
    payload=request_body,           # 요청 body (str 또는 bytes)
    signature="sha256=abc123...",    # X-Webhook-Signature 헤더
    timestamp="1710000000",         # X-Webhook-Timestamp 헤더
    secret="whsk_your_secret",      # 웹훅 시크릿 키
    tolerance=300                   # 타임스탬프 허용 오차 (초, 기본 300)
)
```

**서명 계산 방식**: `HMAC-SHA256(secret, "{timestamp}.{payload}")`

**특이사항**:
- `sha256=` 접두사 자동 제거
- tolerance=0이면 타임스탬프 검증 생략
- 서명 불일치 시 False 반환
- 타임스탬프 만료/형식 오류 시 ValueError 발생

### 6.6 ResponseParser 유틸리티

```python
from bookprintapi import ResponseParser

result = client.books.list()
parser = ResponseParser(result)

data = parser.get_data()          # result["data"] 또는 result 전체
items = parser.get_list()         # data가 리스트이면 반환
details = parser.get_dict()       # data가 딕셔너리이면 반환
pagination = parser.get_pagination()  # data["pagination"]
message = parser.get_message()    # result["message"]
raw = parser.raw                  # 원본 응답
```

### 6.7 예외 클래스

```python
from bookprintapi import ApiError, ValidationError

# ApiError -- API 요청 실패 시 발생
try:
    client.orders.create(...)
except ApiError as e:
    e.message       # 에러 메시지
    e.status_code   # HTTP 상태 코드 (None 가능 -- 네트워크 에러)
    e.error_code    # 에러 코드 (있는 경우)
    e.details       # 상세 에러 목록 (list)

# ValidationError -- 파라미터 검증 실패 (AsyncClient에서 사용)
try:
    await client.books.get("")  # 빈 문자열
except ValidationError as e:
    e.message       # 검증 실패 메시지
    e.field         # 실패한 필드명
```

**ApiError.from_response()**: HTTP 응답에서 자동으로 에러 객체 생성. 응답 body에서 `message`, `error_code`, `errors` 추출.

---

## 7. 트러블슈팅

### 자주 발생하는 문제

| 문제 | 원인 | 해결 |
|------|------|------|
| 401 Unauthorized | API Key 오류 또는 환경 URL 불일치 | Key 확인, Sandbox URL에 Sandbox Key 사용 |
| 402 Payment Required | 충전금 부족 | `GET /credits`로 잔액 확인, 포털에서 충전 |
| 400 Validation Error | 필수 필드 누락/잘못된 값 | `fieldErrors` 배열에서 구체적 필드 확인 |
| 404 Not Found | bookUid/orderUid 오류 | 생성 응답에서 받은 ID 재확인 |
| 429 Too Many Requests | Rate Limit 초과 | `Retry-After` 헤더 확인, 요청 빈도 줄이기 |
| 이미지 업로드 실패 | SVG 또는 손상된 파일 | JPG/PNG/WebP/HEIC만 지원 |
| 확정(finalize) 실패 | 최소 페이지 수 미충족 | 내지 페이지 추가 후 재시도 |
| 웹훅 수신 안 됨 | URL 접근 불가, HTTPS 미사용, 방화벽 | `POST /webhooks/test`로 테스트 |
| 주문 취소 실패 | CONFIRMED 이후 상태 | PAID/PDF_READY에서만 취소 가능 |
| Sandbox Key로 Live URL 호출 | 환경 불일치 | 환경별 전용 Key와 URL 사용 |
| GET /book-specs 403 에러 | accountUid 권한 문제 | 사업자 계정 전환 필요 가능 |

### FAQ

**Q: Sandbox에서 만든 데이터를 Live로 옮길 수 있나?**  
A: 불가. Sandbox와 Live는 완전히 격리된 환경이다. 데이터 자동 마이그레이션 없음.

**Q: Sandbox 충전금이 부족할 때?**  
A: 파트너 포털에서 무제한 무료 충전 가능. 또는 SDK: `client.credits.sandbox_charge(100000)`

**Q: API Key가 유출되었을 때?**  
A: 즉시 파트너 포털에서 폐기 후 새 키 발급. 키는 무제한 생성 가능.

**Q: 배송 추적은?**  
A: `order.shipped` 웹훅에 `tracking_carrier`와 `tracking_number`가 포함된다. 택배사 추적 시스템에서 조회.

**Q: 인쇄 품질 문제 발생 시?**  
A: 파트너 포털에서 불량 부분 사진 첨부하여 접수. 인쇄 결함 확인 시 3-4 영업일 내 무상 재제작.

**Q: 이미지 해상도가 낮으면?**  
A: 해상도 부족은 인쇄 불량으로 분류되지 않는다. 300 DPI 이상 원본 이미지 사용 권장.

**Q: Postman으로 테스트하려면?**  
A: Authorization 탭에서 Bearer Token 선택, API Key 입력.

**Q: 웹훅 구현이 어려울 때 대안은?**  
A: `GET /orders/{orderUid}`로 폴링. 5-10분 간격 권장 (Rate Limit 주의).

### 운영 전환 (Go-Live) 체크리스트

1. 스위트북과 사업 협의 완료 (가격, 물량, 납기)
2. 사업자 계정 전환 완료
3. Live API Key 발급
4. Base URL 변경 (`api-sandbox` -> `api`)
5. 실제 충전금 결제/충전
6. 운영 환경 웹훅 URL 업데이트
7. IP 화이트리스트 설정 (권장)
8. 에러 처리 및 재시도 로직 검증
9. 충전금 잔액 모니터링 설정
10. 첫 Live 주문 테스트 (**실제 인쇄/배송됨!**)

**운영 SLA**:

| 단계 | 소요 시간 | 비고 |
|------|-----------|------|
| 제작 | 3-4 영업일 | CONFIRMED 이후, 공휴일 제외 |
| 배송 | 1-2일 | 한진택배 |

---

## 8. 실제 테스트 결과

SDK와 Sandbox 환경에서의 실제 테스트 결과 기록.

### 정상 동작 확인된 엔드포인트

| 엔드포인트 | 결과 | 비고 |
|-----------|------|------|
| `GET /credits` | 정상 | 잔액, 통화, 환경 정보 반환 |
| `GET /credits/transactions` | 정상 | 거래 내역 조회 |
| `POST /credits/sandbox/charge` | 정상 | 테스트 충전 성공 |
| `GET /books` (`/Books`) | 정상 | 책 목록 조회 |
| `POST /books` | 정상 | 책 생성 |
| `GET /books/{bookUid}` | 정상 | 책 상세 조회 |
| `POST /books/{bookUid}/finalization` | 정상 | 책 확정 |
| `POST /orders/estimate` | 정상 | 견적 조회 |
| `POST /orders` | 정상 | 주문 생성, 충전금 즉시 차감 |
| `GET /orders` | 정상 | 주문 목록 조회 |
| `POST /orders/{orderUid}/cancel` | 정상 | 주문 취소, 충전금 즉시 환불 |

### 에러 발생 엔드포인트

| 엔드포인트 | 에러 | 상세 |
|-----------|------|------|
| `GET /book-specs` | **403 Forbidden** | `accountUid` 관련 에러 발생. API Key 인증은 통과하지만 계정 권한 문제로 판형 목록을 가져올 수 없다. 개인 계정의 Sandbox 환경에서 발생할 수 있으며, 사업자 계정 전환 또는 스위트북 담당자 문의가 필요할 수 있다. |

### SDK 환경변수 설정 (테스트 시 사용)

```
BOOKPRINT_API_KEY=SBxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BOOKPRINT_BASE_URL=https://api-sandbox.sweetbook.com/v1
```

`BOOKPRINT_ENV=sandbox`를 설정하거나, `BOOKPRINT_BASE_URL`을 직접 지정하면 된다. `BOOKPRINT_BASE_URL`이 `BOOKPRINT_ENV`보다 우선한다.

### SDK vs 문서 차이점 종합

| 항목 | SDK (코드 기준) | 공식 문서 | 비고 |
|------|----------------|----------|------|
| Books 경로 | `/Books` (대문자 B) | `/books` (소문자) | 서버에서 대소문자 무관 처리 추정 |
| books.create title | 선택 파라미터 | 필수 파라미터 | SDK는 title 없이도 호출 가능 |
| books.list 필터 | `status` (draft/finalized) | `pdfStatusIn` | 서로 다른 필터 파라미터 |
| Idempotency 헤더 | 매 요청 자동 UUID (`Idempotency-Key`) | 권장 사항으로만 언급 | SDK가 자동 처리 |
| AsyncClient 헤더 | `X-Transaction-ID` | 문서에 없음 | AsyncClient 전용 |
| 배송비 | README: 3,000원 | API 문서: 3,500원 + 포장비 500원/건 | 실제 금액은 estimate API로 확인 |
| 환경변수명 | `BOOKPRINT_*` | `SWEETBOOK_*` (일부 예시) | SDK 기준 사용 권장 |
| 웹훅 서명 | `sha256=` 접두사 자동 제거 + tolerance 검증 | hex 값만 전달 | SDK가 더 유연하게 처리 |
| webhook_receiver.py | `X-Webhook-Signature`에 `sha256=` 포함 가정 | hex 값만 설명 | SDK verify_signature가 양쪽 모두 처리 |

---

## 9. 부록

### 9.1 파트너 등록 과정

1. **회원가입**: 이메일 인증 -> 비밀번호 설정 -> 개인 계정 생성
2. **포털 로그인**: 파트너 대시보드 접근
3. **Sandbox API Key 발급**: API Key 관리 > 새 API Key 발급 > Sandbox 선택
4. **첫 API 호출 테스트**: `GET /book-specs` (또는 `GET /credits`)
5. **Sandbox 충전금 충전**: 포털 > 충전금 관리

### 9.2 Demo Applications

| 앱 | 설명 | GitHub |
|----|------|--------|
| diaryBook | 일기장 A/B 포토북 (JSON 업로드/직접 입력) | sweet-book/diaryBook-demo |
| kidsDailyBook | 어린이집 알림장 A/B/C (월별 디자인 자동 적용) | sweet-book/kidsDailyBook-demo |
| socialBook | Google Photos 연동 포토북 (OAuth 로그인) | sweet-book/socialBook-demo |
| partner-order | 파트너 주문 시스템 (전체 주문 플로우) | sweet-book/partner-order-demo |

### 9.3 회사 정보

| 항목 | 값 |
|------|-----|
| 회사명 | 주식회사 스위트북 (SWEETBOOK Inc.) |
| 대표 | 박지민 |
| 주소 | 서울특별시 금천구 서부샛길 648 대륭테크노타운6차 901호 |
| 사업자등록번호 | 131-86-00220 |
| 통신판매업신고 | 제2012-서울금천-0376호 |
| 전화 | 02-886-0156 |
| 팩스 | 02-6008-0146 |
| 이메일 | sweet@sweetbook.com |

### 9.4 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| v1.0 | 2026-03-24 | 최초 공개 릴리스 |

### 9.5 CLI 예제 (examples/ 폴더)

SDK에 포함된 CLI 예제로 전체 플로우를 체험할 수 있다.

```bash
cd examples

# === 충전금 (simple_credits.py) ===
python simple_credits.py balance              # 잔액 조회
python simple_credits.py charge 100000        # Sandbox 충전
python simple_credits.py charge 50000 "테스트 충전"  # 메모 포함
python simple_credits.py transactions         # 거래 내역

# === 책 (simple_books.py) ===
python simple_books.py list                   # 전체 목록
python simple_books.py list --status finalized # finalized만
python simple_books.py create "제목"          # 새 책 생성
python simple_books.py create "제목" --spec SQUAREBOOK_HC --type TEST
python simple_books.py get <bookUid>          # 상세
python simple_books.py finalize <bookUid>     # 확정
python simple_books.py delete <bookUid>       # 삭제

# === 주문 (simple_orders.py) ===
python simple_orders.py estimate <bookUid>    # 견적
python simple_orders.py estimate <bookUid> 2  # 2권 견적
python simple_orders.py create <bookUid> --name 홍길동 --phone 010-1234-5678 --postal 06100 --addr1 "서울..."
python simple_orders.py list                  # 주문 목록
python simple_orders.py list --status 20      # PAID만
python simple_orders.py get <orderUid>        # 상세
python simple_orders.py cancel <orderUid> "취소 사유"
python simple_orders.py shipping <orderUid> --name 김영희 --phone 010-9999-8888

# === 서버 파이프라인 (server_pipeline.py) ===
# 전체 자동화: 충전금 확인 -> 책 생성 -> 표지 -> 내지 -> 확정 -> 견적 -> 주문 -> 취소
python server_pipeline.py

# === 웹훅 수신 서버 (webhook_receiver.py) ===
# Flask 기반, WEBHOOK_SECRET 환경변수 필요
python webhook_receiver.py
```

### 9.6 공식 문서 접근 불가 페이지

2026-04-02 기준 404 반환되는 페이지:
- `https://api.sweetbook.com/docs/concepts/gallery-templates/` (Gallery Templates)
- `https://api.sweetbook.com/docs/concepts/column-templates/` (Column Templates)

해당 내용은 다른 문서 페이지(templates, dynamic-layout 등)에서 수집한 정보로 대체하였다.
