# Dreambook 책 조립 완전 가이드

> 이 문서는 두 가지를 결합한 종합 레퍼런스다:
> 1. **SDK/데모 분석** — 기업(스위트북)이 만든 정석 코드 기반
> 2. **우리 프로젝트 분석** — Dreambook 코드의 실제 흐름
>
> 미리보기 구현, Book Print API 디버깅, 새 세션 컨텍스트 복원 시 이 문서를 참고할 것.
> **작성일**: 2026-04-07

---

## 1. 판형 규격 (SQUAREBOOK_HC)

| 항목 | 값 |
|------|-----|
| UID | `SQUAREBOOK_HC` |
| 이름 | 정사각형 양장본 (하드커버) |
| 내지 크기 | 243mm × 248mm |
| 페이지 범위 | 24p ~ 130p (2p 단위 증분) |
| 표지 | Hardcover, Snow 150g |
| 내지 | Arte 130g, Silk 코팅 |
| 제본 | PUR 바인딩 (왼쪽) |
| Sandbox 가격 | 기본 100원 + 10원/2p |

### 페이지 좌표계

- **PW (페이지 너비)**: 978px
- **PH (페이지 높이)**: 1000.8px
- 1px ≈ 0.248mm

---

## 2. 정석 워크플로우 (SDK/데모 기반)

### 2.1 10단계 순서

```
 1. 충전금 확인       GET  /credits
 2. 책 생성 (draft)   POST /books → bookUid
 3. 사진 업로드       POST /books/{bookUid}/photos → fileName
 4. 표지 생성         POST /books/{bookUid}/cover
 5. 내지 삽입 (반복)  POST /books/{bookUid}/contents
 6. 빈내지 패딩       POST /books/{bookUid}/contents (페이지 부족 시)
 7. 발행면 삽입       POST /books/{bookUid}/contents (templateKind=publish)
 8. 책 확정           POST /books/{bookUid}/finalization
 9. 견적 조회         POST /orders/estimate
10. 주문 생성         POST /orders
```

### 2.2 SDK 파이프라인 코드 (server_pipeline.py)

```python
# 1. 충전금
credit = client.credits.get_balance()

# 2. 책 생성
book = client.books.create(book_spec_uid="SQUAREBOOK_HC", title="...", creation_type="TEST")
book_uid = book["data"]["bookUid"]

# 3. 사진 업로드
upload = client.photos.upload(book_uid, "sample_photo.jpg")
photo_name = upload["data"]["fileName"]

# 4. 표지
client.covers.create(book_uid, template_uid=TPL_COVER,
    parameters={"coverPhoto": photo_name, ...})

# 5. 간지 + 내지 (반복, 0.5초 간격)
client.contents.insert(book_uid, template_uid=TPL_GANJI, parameters={...})
for entry in entries:
    client.contents.insert(book_uid, template_uid=TPL_NAEJI, parameters={...})
    time.sleep(0.5)

# 6. 빈내지 패딩
for i in range(padding_needed):
    client.contents.insert(book_uid, template_uid=TPL_BLANK, break_before="page")

# 7. 발행면
client.contents.insert(book_uid, template_uid=TPL_PUBLISH, parameters={...})

# 8. finalize (재시도 루프)
for attempt in range(5):
    try:
        client.books.finalize(book_uid)
        break
    except ApiError as e:
        if "최소 페이지 미달" in str(e.details):
            for _ in range(4):
                client.contents.insert(book_uid, template_uid=TPL_BLANK, break_before="page")
        else:
            raise

# 9. 견적
estimate = client.orders.estimate([{"bookUid": book_uid, "quantity": 1}])

# 10. 주문
order = client.orders.create(items=[...], shipping=SHIPPING)
```

---

## 3. contents.insert 상세

### 3.1 요청

```
POST /books/{bookUid}/contents?breakBefore=page
Content-Type: multipart/form-data

templateUid: "uZICIRIwJzuB"
parameters: '{"monthYearTitle":"제목","author":"저자"}'
```

### 3.2 응답 (cursor 포함)

```json
{
  "success": true,
  "data": { "result": "inserted", "breakBefore": "page" },
  "cursor": { "pageNum": 2, "pageSide": "right", "pageCount": 3 }
}
```

JS SDK에서 cursor를 data에 병합하는 코드:
```javascript
// sweetbook-sdk-user.js
const data = new ResponseParser(body).getData();
if (body?.cursor && data) {
    data.pageNum = body.cursor.pageNum;
    data.pageSide = body.cursor.pageSide;
}
return data;
```

### 3.3 breakBefore 규칙

| templateKind | `none` | `column` | `page` | `pageSide` |
|-------------|--------|----------|--------|------------|
| content | O | O | O | X (에러) |
| divider | X | X | O (기본) | O (left/right) |
| publish | X | X | O (기본) | O (left/right) |

`'none'`은 JS에서 빈 문자열로 변환: `breakBefore === 'none' ? '' : breakBefore`

---

## 4. pageSide 메커니즘

### 4.1 기본 규칙

정방형 책(SQUAREBOOK_HC): **p1은 항상 right에서 시작**. 이후 left/right 교대.

### 4.2 pageSide 배치 알고리즘 (divider/publish)

| 현재 Side | 요청 Side | 결과 | 설명 |
|-----------|-----------|------|------|
| left | left | +1 페이지, left | 다음 스프레드 왼쪽 |
| left | right | 같은 페이지, right | 같은 스프레드 오른쪽 |
| right | left | +1 페이지, left | 다음 스프레드 왼쪽 |
| right | right | +1 페이지, right | 다음 스프레드 오른쪽 |

### 4.3 발행면 위치 보장 (데모 앱 공통 패턴)

```javascript
// 3개 데모 앱 전부 동일한 패턴
const lastSide = lastResult?.pageSide || 'right';
if (lastSide === 'left' && tplUids.tplBlank) {
    await sdkPostContent(client, bookUid, tplUids.tplBlank, {}, 'page');
}
await sdkPostContent(client, bookUid, tplUids.tplPublish, publishParams, 'page');
```

### 4.4 실제 테스트 결과 (우리 동화책)

```
간지:     pageNum= 1, pageSide=right
그림1:    pageNum= 2, pageSide=left
스토리1:  pageNum= 2, pageSide=right   ← 같은 pageNum (같은 스프레드)
그림2:    pageNum= 3, pageSide=left
스토리2:  pageNum= 3, pageSide=right
...
```

break_before="page"로 모든 내지를 삽입해도 그림(left)+스토리(right)가 같은 스프레드에 정상 배치됨.

---

## 5. 에러 처리 패턴 (SDK/데모 기반)

### 5.1 일시중지/이어서하기 (Pause/Resume)

데모 앱 3개 공통:
```javascript
let _paused = false;
let _saved = null;  // {bookUid, entries, startIndex, successCount, failCount, lastResult, ...}

for (let i = startIndex; i < entries.length; i++) {
    if (_paused) {
        _saved = { ...ctx, startIndex: i, successCount, failCount, lastResult };
        return;
    }
    try {
        lastResult = await sdkPostContent(...);
        successCount++;
    } catch (err) {
        _saved = { ...ctx, startIndex: i, successCount, failCount, lastResult };
        return;  // "이어서하기"로 재시도 가능
    }
}
```

### 5.2 빈 이미지 파라미터 제거 (stripEmptyImages)

```javascript
const IMAGE_KEYS = new Set(['coverPhoto','photo','photo1','photo2','frontPhoto','backPhoto']);
function stripEmptyImages(obj) {
    const result = {};
    for (const [k, v] of Object.entries(obj)) {
        if (IMAGE_KEYS.has(k) && (!v || v === '')) continue;
        result[k] = v;
    }
    return result;
}
```

### 5.3 finalize 재시도 (SDK)

```python
for attempt in range(5):
    try:
        fin = client.books.finalize(book_uid)
        break
    except ApiError as e:
        if "최소 페이지 미달" in str(e.details):
            for _ in range(4):
                client.contents.insert(book_uid, template_uid=TPL_BLANK, break_before="page")
        else:
            raise
```

### 5.4 Rate Limit

- 일반 API: 300 req/min
- 파일 업로드: 200 req/min
- SDK(Python): 0.5초 간격 (`time.sleep(0.5)`)
- SDK 내장: 자동 재시도 (최대 3회, exponential backoff, 429/500/502/503/504)

---

## 6. 우리 템플릿 6개 상세

### 6.1 표지 (Cover) — `4SezofiW67xk`

| 항목 | 값 |
|------|-----|
| templateKind | `cover` |
| isPublic | false |

**파라미터**: `coverPhoto`(file, 필수), `subtitle`(text, 필수), `author`(text, 필수)

**레이아웃** (전체 표지 = 뒷표지 + 책등 + 앞표지):

| element | type | 크기 | 위치 | 폰트 | 내용 |
|---------|------|------|------|------|------|
| book-back | rectangle | 47×1041 | (1013, 0) | - | 책등 배경 |
| spine-subtitle | text | 48×946 | (1011, 95) | tvN 즐거운이야기 Bold 28px | `$$subtitle$$` |
| front-photo | photo | **636×636** | (1249, 156) | - | 앞표지 사진 |
| front-subtitle | text | 479×52 | (1327, 820) | tvN 즐거운이야기 Bold 40px | `$$subtitle$$` |
| text-ik0ldz93 | text | 179×40 | (1478, 876) | NotoSansKR 16px | `$$author$$` |
| text-w2mbi50b | text | 269×40 | (372, 453) | tvN 즐거운이야기 Bold 16px | 뒷표지 `$$subtitle$$` |
| graphic-eto7jdcw | graphic | 269×50 | (372, 950) | - | **Dreambook 로고** (고정 이미지) |

**앞표지 상대 좌표** (앞표지 시작 x≈1060 기준):
- 사진: (189, 156) 636×636
- 제목: (267, 820) 479×52
- 저자: (418, 876) 179×40

### 6.2 간지 (Title Page / Divider) — `uZICIRIwJzuB`

| templateKind | `divider` | isPublic | false |

**파라미터**: `monthYearTitle`(text, 필수), `author`(text, 필수)

| element | 크기 | 위치 | 폰트 |
|---------|------|------|------|
| month-year-title | 807×97 | (85, 407) | tvN 즐거운이야기 Bold 50px, 중앙 |
| author | 264×34 | (357, 559) | 나눔바른펜 주아 20px, 중앙 |

### 6.3 그림 페이지 (Illustration) — `5TLmcVySw3Ca`

| templateKind | `content` | isPublic | false |

**파라미터**: `photo`(file, **필수**)

| element | 크기 | 위치 | 비고 |
|---------|------|------|------|
| photo | **900×900** | (14, 12.4) | pageMargin: spine=25, head=30 |

**baseLayer** (페이지 번호):
- even(left): (51.45, 955.75) 나눔고딕 12px, 좌측 정렬
- odd(right): (855.17, 955.75) 나눔고딕 12px, 우측 정렬

### 6.4 스토리 페이지 (Story) — `7AtlblwFXwPE`

| templateKind | `content` | isPublic | false |

**파라미터**: `storyText`(text, 필수)

| element | 크기 | 위치 | 폰트 |
|---------|------|------|------|
| storyText | **700×800** | (114, 62.4) | NanumMyeongjo 24px Bold, 중앙 |

pageMargin/baseLayer: 그림 페이지와 동일

### 6.5 발행면 (Publish) — `5gBcekhFJVNT`

| templateKind | `publish` | isPublic | false |

**파라미터**: `photo`(file, 선택), `title`(text, 필수), `publishDate`(text, 필수), `author`(text, 필수), `hashtags`(text, 선택), `publisher`(text, 선택)

| element | type | 크기 | 위치 | 폰트 |
|---------|------|------|------|------|
| publish-photo | photo | 293×293 | (50, 277) | - |
| publish-title | text | 652×50 | (50, 600) | 나눔고딕 20px |
| publish-info | text | 350×100 | (50, 650) | 나눔고딕 12px |
| graphic | graphic | 268×47 | (53, 833) | **Dreambook 로고** (고정) |

### 6.6 빈내지 (Blank) — `2mi1ao0Z4Vxl`

| templateKind | `content` | isPublic | **true** (공용) |

파라미터 없음. `layoutRules.pageSide: "left"`

---

## 7. 템플릿 접근 권한

| | 상세조회 (GET /templates/{uid}) | 사용 (POST cover/contents) |
|--|-------------------------------|---------------------------|
| 개인 (isPublic=false) | 소유 계정만 (다른 계정 404) | **모든 계정 가능** |
| 공용 (isPublic=true) | 모든 계정 | 모든 계정 |

→ 우리 개인 템플릿 5개는 상세조회 불가하지만 **UID만 알면 사용은 가능**
→ 코드에서 `get_template_detail()`은 실제 워크플로우에서 사용하지 않음

---

## 8. 동화책 24페이지 구조

```
[표지] — cover 템플릿

p1  (right) : 간지 (divider)
━━━━━━━━━━━━━━━━━━━━━━━━
p2  (left)  : 그림 1
p3  (right) : 스토리 1
━━━━━━━━━━━━━━━━━━━━━━━━
p4  (left)  : 그림 2
p5  (right) : 스토리 2
...
p22 (left)  : 그림 11
p23 (right) : 스토리 11
━━━━━━━━━━━━━━━━━━━━━━━━
p24 (left)  : 발행면 (publish)
```

---

## 9. 미리보기 구현 정보

### 9.1 스프레드 구성

| 인덱스 | 좌 | 우 | 비율 |
|--------|-----|-----|------|
| 0 | 표지 (단독) | - | 1:1 |
| 1 | 빈 페이지 | 간지 (p1) | 2:1 |
| 2~12 | 그림 N | 스토리 N | 2:1 |
| 13 | 발행면 (p24) | 빈 페이지 | 2:1 |
| 14 | 뒷표지 (단독) | - | 1:1 |

총 15개 스프레드.

### 9.2 렌더링 좌표 (PW=978, PH=1000.8)

**표지 (CoverPage)** — 앞표지 영역만:
- 배경: `#FFF8F0`
- 사진: (171, 156) 636×636, borderRadius=12
- 제목: (249, 820) 479×52, Jua 28px bold, 중앙
- 저자: (400, 876) 179×40, Nanum Gothic 16px, 중앙
- 로고: (372-1060≈하단) `/logo.png` — 뒷표지에만

**간지 (TitlePage)**:
- 제목: (85, 407) 807×97, Jua 50px bold, 중앙
- 저자: (357, 559) 264×34, Jua 20px, 중앙

**그림 (IllustPage)** — pageMargin 적용 (MX=25, MY=30):
- 이미지: (14+MX, 12.4+MY) = **(39, 42.4)** 900×900, borderRadius=20
- 페이지번호: even→(51.45, 955.75) left, odd→(855.17, 955.75) right

**스토리 (StoryPage)** — pageMargin 적용:
- 텍스트: (114+MX, 62.4+MY) = **(139, 92.4)** 700×800
- 폰트: NanumMyeongjo 24px Bold, 중앙, lineHeight=60px
- 페이지번호: 그림과 동일

**발행면 (ColophonPage)**:
- 사진: (50, 277) 293×293
- 제목: (50, 600) 652×50, 나눔고딕 20px
- 정보: (50, 650) 350×100, 나눔고딕 12px, lineHeight=21px
- 로고: (53, 833) 268×47 — `/logo.png`

**뒷표지 (BackCoverPage)**:
- 배경: `#FFF8F0`, 중앙에 "(주)스위트북" 14px #ccc

### 9.3 고정 이미지 (Dreambook 로고)

- 파일: `/logo.png` (frontend/public/)
- 표지 뒷면: (372, 950) 269×50 — `imageSource: /api_platform_image/.../image260405154626959.PNG`
- 발행면 하단: (53, 833) 268×47 — 동일 이미지
- **미리보기에서만 표시** (Book Print API에는 템플릿에 고정되어 있어 별도 전달 불필요)

---

## 10. 우리 코드 현재 상태

### 10.1 execute_order_workflow (bookprint.py)

```
1. ensure_sufficient_credits()
2. create_book(title, "SQUAREBOOK_HC")
3. upload_photo() × N (표지 + 일러스트)
4. create_cover(TPL_COVER, {coverPhoto, subtitle, author})
   — coverPhoto 없으면 파라미터 생략 (빈 문자열 방지)
5. insert_content() × 23 (colophon 제외)
   — title → TPL_TITLE_PAGE
   — illustration → TPL_ILLUSTRATION (이미지 없으면 TPL_BLANK 대체)
   — story → TPL_STORY
   — 발행면 전 pageSide 체크 → 빈내지 삽입
   — colophon → TPL_PUBLISH
6. 삽입 검증 (예상 vs 실제)
7. finalize_book()
8. get_estimate() → 부족 시 추가 충전
9. create_order() → 402 시 재충전 후 재시도
```

### 10.2 AI 생성 파이프라인

| # | 단계 | 서비스 | 모델 | 입력 → 출력 |
|---|------|--------|------|------------|
| 1 | 직업 번역 | ai_job.py | gpt-4o-mini | 한글 직업명 → {job_name_en, job_outfit} |
| 2 | 캐릭터 시트 | ai_character.py | gpt-image-1-mini | 아이 사진 + 직업(EN) + 그림체 → 캐릭터 1장 |
| 3 | 줄거리 후보 | ai_plot.py | gpt-4o-mini | 이름+직업+나이+성별 → 줄거리 4개 |
| 4 | 스토리 | ai_story.py | gpt-4o-mini | 이름+직업+줄거리+그림체 → 제목 + (텍스트+scene) × 11 |
| 5 | 일러스트 | ai_illustration.py | gpt-image-1-mini | 캐릭터시트 + scene + 직업(EN) → 일러스트 11장 |
| 6 | 표지 | ai_illustration.py | gpt-image-1-mini | 캐릭터시트 + 직업(EN) → 표지 1장 (전용 프롬프트) |

### 10.3 설정값

```python
# 템플릿 UID
TPL_COVER        = "4SezofiW67xk"
TPL_TITLE_PAGE   = "uZICIRIwJzuB"
TPL_ILLUSTRATION = "5TLmcVySw3Ca"
TPL_STORY        = "7AtlblwFXwPE"
TPL_PUBLISH      = "5gBcekhFJVNT"
TPL_BLANK        = "2mi1ao0Z4Vxl"

# AI 플래그
SKIP_AI_CHARACTER    = False
SKIP_AI_ILLUSTRATION = False

# 상수
STORY_PAGE_COUNT = 11
TOTAL_BOOK_PAGES = 24
SANDBOX_CHARGE_AMOUNT = 1_000_000
MAX_CHARACTER_GENERATIONS = 5
```

### 10.4 Book.status 상태 전이

```
draft → character_confirmed → story_generated → editing → completed
```

| status | 진입 시점 |
|--------|----------|
| draft | Book 최초 생성 |
| character_confirmed | 캐릭터 선택 완료 |
| story_generated | 스토리 텍스트 생성 완료 |
| editing | 일러스트 생성 완료 |
| completed | 주문 완료 |

---

## 11. 데모 앱 비교표

| 항목 | SDK (Python) | diaryBook | kidsDailyBook | socialBook |
|------|-------------|-----------|---------------|------------|
| 사진 | photos.upload() | URL 직접 | URL 직접 | URL/upload |
| 빈내지 | 사전 계산 | pageSide 동적 | pageSide 동적 | pageSide+pageCount |
| finalize | 5회 재시도 | UI 버튼 | UI 버튼 | UI+빈내지 추가 |
| 발행면 보류 | 없음 | 없음 | 없음 | MIN_PAGES_FOR_PUBLISH(22) |
| 에러 복구 | 예외 종료 | 이어서하기 | 이어서하기 | 이어서하기 |
| Rate Limit | sleep(0.5) | SDK 내장 | SDK 내장 | SDK 내장 |

---

## 12. 페이지 썸네일 렌더링 API (미공개)

> **중요**: 공식 API 문서에 없고, 데모 앱에도 TODO로 남아있는 **미공개 API**.
> 2026-04-07 직접 테스트하여 동작 확인함.
> 이 API를 사용하면 Book Print API에 보낸 책의 **실제 인쇄될 모습 그대로** 썸네일 이미지를 받을 수 있다.

### 12.1 엔드포인트

#### 렌더 요청

```
POST /render/page-thumbnail
Content-Type: application/json
Authorization: Bearer {API_KEY}

{
  "bookUid": "bk_xxxxx",
  "pageNum": 1
}
```

- `pageNum`: 정수. 0 = 첫 번째 내지(간지), 1~23 = 나머지 내지
- 응답: `{ "success": true, "data": null }` — 비동기 렌더링 요청만 수행
- 렌더링 완료까지 **약 3~5초** 소요

#### 썸네일 조회

```
GET /render/thumbnail/{bookUid}/{fileName}
Authorization: Bearer {API_KEY}
```

- `fileName` 패턴:
  - **표지**: `cover.jpg` — 뒷표지 + 책등 + 앞표지 전체 (가로형)
  - **내지**: `{pageNum}.jpg` — `0.jpg`, `1.jpg`, ... `23.jpg`
- 응답: `image/jpeg` 바이너리
- 렌더링이 아직 안 끝났으면 **404**

### 12.2 페이지 번호 매핑

| fileName | 우리 Page | 내용 | 이미지 크기 (참고) |
|----------|----------|------|-----------------|
| `cover.jpg` | - | 표지 전체 (뒷표지+책등+앞표지) | ~113KB |
| `0.jpg` | p1 (title) | 간지 (제목+저자) | ~24KB |
| `1.jpg` | p2 (illustration) | 그림 1 | ~182KB |
| `2.jpg` | p3 (story) | 스토리 1 | ~63KB |
| `3.jpg` | p4 (illustration) | 그림 2 | ~187KB |
| `4.jpg` | p5 (story) | 스토리 2 | ~56KB |
| ... | ... | ... | ... |
| `21.jpg` | p22 (illustration) | 그림 11 | ~33KB |
| `22.jpg` | p23 (story) | 스토리 11 | ~55KB |
| `23.jpg` | p24 (colophon) | 발행면 | ~34KB |

**주의**: 
- `pageNum` ≠ 우리 DB의 `Page.page_number`
- API의 pageNum 0 = 우리의 p1(간지), API의 pageNum 1 = 우리의 p2(그림1)
- 표지는 `cover.jpg`로 별도 조회 (pageNum이 아님)
- 총 내지 24개 (0~23) + 표지 1개 = **25개 이미지**

### 12.3 사용 절차

```python
import asyncio, httpx

async def download_all_thumbnails(book_uid: str, api_key: str, out_dir: str):
    base = "https://api-sandbox.sweetbook.com/v1"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    async with httpx.AsyncClient(timeout=30.0) as c:
        # 1. 전 페이지 렌더 요청 (표지 포함)
        # 표지는 별도 렌더 요청 불필요 — cover.jpg는 항상 존재
        for pn in range(24):
            await c.post(f"{base}/render/page-thumbnail",
                headers={**headers, "Content-Type": "application/json"},
                json={"bookUid": book_uid, "pageNum": pn})
        
        # 2. 렌더링 완료 대기
        await asyncio.sleep(5)
        
        # 3. 다운로드
        # 표지
        r = await c.get(f"{base}/render/thumbnail/{book_uid}/cover.jpg", headers=headers)
        if r.status_code == 200:
            with open(f"{out_dir}/cover.jpg", "wb") as f:
                f.write(r.content)
        
        # 내지 (0~23)
        for pn in range(24):
            r = await c.get(f"{base}/render/thumbnail/{book_uid}/{pn}.jpg", headers=headers)
            if r.status_code == 200:
                with open(f"{out_dir}/{pn}.jpg", "wb") as f:
                    f.write(r.content)
```

### 12.4 제약 사항

- **책이 Book Print API에 존재해야 함** — 우리 DB에만 있는 책은 불가
- **finalize 여부 무관** — draft 상태에서도 렌더링 가능 (테스트 확인)
- **비동기** — POST 요청 후 실제 이미지 생성까지 3~5초 소요
- **캐시** — 한 번 렌더링된 페이지는 재요청 없이 GET으로 바로 조회 가능
- **이미지 형식** — JPEG 고정 (PNG/WebP 미지원)
- **해상도** — 약 1000×1000px 수준 (정확한 해상도는 페이지마다 다름)

### 12.5 활용 방안

| 용도 | 설명 |
|------|------|
| **주문 후 미리보기** | 주문 완료된 책의 실제 인쇄 모습을 정확히 보여줌 |
| **미리보기 검증** | 우리 프론트엔드 렌더링이 실제 결과와 일치하는지 비교 |
| **주문 전 프리뷰** | draft 상태에서도 가능하므로, 주문 전에 Book Print API에 책을 보내고 렌더 결과를 보여줄 수 있음 (단, API 호출 비용 발생) |

### 12.6 데모 앱의 미구현 TODO (참고)

```javascript
// diaryBook-demo/app.js:4-7
* TODO: 썸네일 미리보기 기능 (RenderClient + loadThumbnails)
*   - SDK에 RenderClient 추가 (POST /render/page-thumbnail, GET /render/thumbnail/{bookUid}/{fileName})
*   - 책 생성 완료/일시중지/에러 시 pageNum별 썸네일 자동 로딩
*   - CSS는 style.css에 준비됨 (.thumbnail-section, .spread-slot 등)
```

데모 앱에서도 이 API를 인지하고 있지만 아직 구현하지 않은 상태.
우리가 먼저 활용할 수 있는 기회.
