# Book Print API 축약본

> 원본: `.claude/docs/bookprint-api-v2.md` (7,400줄)
> 디테일이 필요하면 원본에서 Grep으로 검색할 것

---

## 1. 환경

| 항목 | Sandbox | Live |
|------|---------|------|
| Base URL | `https://api-sandbox.sweetbook.com/v1` | `https://api.sweetbook.com/v1` |
| API Key | Sandbox 전용 (SB 접두사) | Live 전용 |
| 가격 | 테스트 (100원 이하) | 실제 가격 |
| 인쇄/배송 | 안 함 | 한진택배 3~4영업일 |
| 주문 상태 | **PAID에서 멈춤** | 전체 흐름 진행 |
| 충전금 | 포털에서 무료 충전 | PG 결제 |

인증: `Authorization: Bearer {API_KEY}`

---

## 2. 판형 (SQUAREBOOK_HC)

| 항목 | 값 |
|------|-----|
| 이름 | 고화질 스퀘어북 (하드커버) |
| 크기 | 243 × 248mm |
| 페이지 | 24~130p (2단위 증가) |
| 표지 | 하드커버 |
| 코팅 | Silk |
| 내지 용지 | Arte 130g |
| 제본 | PUR |

---

## 3. 전체 워크플로우

```
1. 책 생성      POST /books
2. 사진 업로드   POST /books/{bookUid}/photos (multipart)
3. 표지 생성     POST /books/{bookUid}/cover (multipart)
4. 내지 삽입     POST /books/{bookUid}/contents (multipart, 반복)
5. 최종화       POST /books/{bookUid}/finalization
6. 견적 조회     POST /orders/estimate
7. 주문 생성     POST /orders
```

---

## 4. 템플릿 시스템

### 4.1 템플릿 종류 (template_kind)

| kind | 용도 | breakBefore 허용 | pageSide 허용 |
|------|------|-----------------|--------------|
| `cover` | 표지 (책당 1개) | - | - |
| `content` | 내지 (여러 번 가능) | none, column, page | 불가 |
| `divider` | 간지/구분 페이지 | page만 | left/right |
| `publish` | 발행면/판권 | page만 | left/right |

### 4.2 파라미터 바인딩

| binding | 설명 | 예시 |
|---------|------|------|
| `text` | 텍스트 | `$$title$$`, `$$contents$$` |
| `file` | 이미지 파일명 또는 URL | `$$photo$$`, `$$coverPhoto$$` |
| `collageGallery` | 콜라주 (1~9장) | `$$collagePhotos$$` |
| `rowGallery` | 행 갤러리 (제한없음) | `$$photos$$` |

### 4.3 범용 컬럼 템플릿 (핵심!)

테마 무관, 모든 계정에서 사용 가능.
**파라미터: `date`(텍스트) + `contents`(텍스트) + 이미지 파일 1장**

| 컬럼 수 | UID | 설명 |
|---------|-----|------|
| 1컬럼 | `cnH0Ud1nl1f9` | 페이지 전체 1열 |
| 2컬럼 | `4G5qpFLebGKd` | 좌우 2열 (신문/잡지 스타일) |
| 3컬럼 | `2Ec6Dp8duR3z` | 3열 |

**호출 예시 (1컬럼):**
```bash
curl -X POST '.../books/{bookUid}/contents?breakBefore=page' \
  -H 'Authorization: Bearer API_KEY' \
  -F 'files=@image.jpg;type=image/jpeg' \
  -F 'templateUid=cnH0Ud1nl1f9' \
  -F 'parameters={"date":"1","contents":"이야기 본문 텍스트"}'
```

**컬럼 배치 규칙:**
- 같은 컬럼 수 템플릿만 같은 면에 배치 가능
- 2컬럼: 한 페이지에 2개 콘텐츠 (좌/우)
- 표지 다음 첫 내지는 항상 오른쪽 면(right)
- 이미지 파일 1장 + 텍스트 파라미터 필요

### 4.4 테마별 템플릿 조회

```
GET /templates?bookSpecUid=SQUAREBOOK_HC&templateKind=cover
GET /templates?bookSpecUid=SQUAREBOOK_HC&templateKind=content
GET /templates?bookSpecUid=SQUAREBOOK_HC&templateKind=publish
GET /templates?bookSpecUid=SQUAREBOOK_HC&templateKind=divider
```

테마 종류: 구글포토북A/B/C, 일기장A/B, 알림장A/B/C

**주의: 커스텀 템플릿(포털에서 복사/편집)은 만든 계정에서만 사용 가능 (isPublic: false)**

---

## 5. API 상세

### 5.1 책 생성

```json
POST /books
{
  "title": "책 제목",
  "bookSpecUid": "SQUAREBOOK_HC",
  "creationType": "TEST"
}
```
응답: `bookUid` (이후 모든 API에 사용)

### 5.2 사진 업로드

```
POST /books/{bookUid}/photos
Content-Type: multipart/form-data
-F 'file=@photo.jpg'
```
- 지원: JPEG, PNG, GIF, BMP, TIFF, WebP, HEIC/HEIF
- SVG 미지원
- 요청당 최대 200MB
- 책당 최대 200장
- 응답: `fileName` (이후 파라미터에 사용)
- 300 DPI 이상 권장

### 5.3 표지 생성

```
POST /books/{bookUid}/cover
Content-Type: multipart/form-data
-F 'templateUid=...'
-F 'parameters={"coverPhoto":"photo123.JPG","subtitle":"부제목","dateRange":"2026"}'
```
- 이미지 전달: 파일명(Photos API 업로드), URL, $upload+files 필드

### 5.4 내지 삽입

```
POST /books/{bookUid}/contents?breakBefore=page
Content-Type: multipart/form-data
-F 'files=@image.jpg'
-F 'templateUid=cnH0Ud1nl1f9'
-F 'parameters={"date":"1","contents":"본문 텍스트"}'
```
- `breakBefore`: none(연속) / column(다음 컬럼) / page(새 페이지)
- 페이지마다 다른 templateUid 사용 가능
- 같은 테마가 아닌 다른 테마 템플릿도 사용 가능 (단, 레이아웃 크기 다를 수 있음)

### 5.5 최종화

```
POST /books/{bookUid}/finalization
```
- draft → finalized (이후 수정 불가)
- 페이지 수가 판형의 min~max 범위, increment 배수여야 함

### 5.6 견적/주문

```json
POST /orders/estimate
{ "items": [{"bookUid": "bk_xxx", "quantity": 1}] }

POST /orders
{
  "items": [{"bookUid": "bk_xxx", "quantity": 1}],
  "shipping": {
    "recipientName": "홍길동",
    "recipientPhone": "010-1234-5678",
    "postalCode": "06100",
    "address1": "서울시 강남구...",
    "address2": "101호"
  }
}
```

### 5.7 주문 상태 흐름

```
PAID(20) → PDF_READY(25) → CONFIRMED(30) → IN_PRODUCTION(40)
→ PRODUCTION_COMPLETE(50) → SHIPPED(60) → DELIVERED(70)
```
취소: PAID/PDF_READY에서만 가능. 배송지 변경: PAID~CONFIRMED.

---

## 6. 동적 레이아웃

- `isDynamic: true` → 텍스트 길이에 따라 높이 자동 조정
- `splittable: true` → 긴 텍스트가 다음 페이지로 자동 분할
- 갤러리: 사진 수에 따라 자동 배치 (collageGallery 1~9장, rowGallery 무제한)
- 컬럼: flow.columns로 1~3열 지정, columnGap으로 간격

---

## 7. 특수 페이지 규칙

- `divider`/`publish`는 항상 독립 페이지 (breakBefore=page 강제)
- `pageSide=left|right`로 배치 면 지정 가능
- content에서는 pageSide 사용 불가
- 스퀘어북 첫 내지는 항상 right 면에서 시작

---

## 8. 이미지 규격

- 권장 해상도: 300 DPI 이상
- 배치 모드 (템플릿에 고정):
  - Cover(채우기): 영역 가득 채움, 비율 차이 시 잘림
  - Contain(맞추기): 전체 보이도록 축소, 여백 가능
- HEIC/HEIF → JPEG 자동 변환
- EXIF 회전 자동 보정

---

## 9. 웹훅

```
PUT /webhooks/config
{ "url": "https://...", "events": ["order.paid", "order.confirmed", ...] }
```

이벤트: `order.paid`, `order.confirmed`, `order.status_changed`, `order.shipped`, `order.cancelled`

서명 검증: `X-Webhook-Signature` 헤더 (HMAC-SHA256)

---

## 10. 에러 코드

| 코드 | 의미 |
|------|------|
| 400 | 잘못된 요청 (파라미터 누락, 유효성 실패) |
| 401 | 인증 실패 (API Key 오류) |
| 403 | 접근 거부 (폐기된 키, IP 제한) |
| 404 | 리소스 없음 |
| 409 | 충돌 (이미 finalized 등) |
| 429 | Rate Limit 초과 |

---

## 11. 우리 서비스 (Dreambook) 적용 계획

### 동화책 24페이지 구성

```
표지:     공용 표지 템플릿 (coverPhoto + subtitle/title + dateRange)
1p:       간지(divider) 또는 내지 — 제목 페이지
2~23p:    1컬럼 템플릿(cnH0Ud1nl1f9) — 이미지 + 스토리 텍스트
24p:      발행면(publish) — 제목 + 저자 + 발행일 + 제작사
```

### 핵심 결정 사항
- **컬럼 템플릿 사용**: 범용 1컬럼 `cnH0Ud1nl1f9`로 이미지+텍스트 동시 삽입
- **테마**: 공용 템플릿이므로 테마 제약 없음
- **표지**: 테마별 공용 표지 중 선택 (구글포토북/일기장 등)
- **발행면**: 테마별 공용 publish 템플릿 사용
