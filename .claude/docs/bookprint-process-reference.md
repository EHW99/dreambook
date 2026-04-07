# Book Print API -- 정석 프로세스 레퍼런스

> SDK 예제(`server_pipeline.py`)와 데모 앱 4개(일기장, 알림장, 구글포토북, 파트너 주문)를 분석하여 정리한 책 생성 정석 프로세스.

---

## 목차

1. [전체 워크플로우 (정석 순서)](#1-전체-워크플로우)
2. [contents.insert 상세](#2-contentsinsert-상세)
3. [pageSide 메커니즘](#3-pageside-메커니즘)
4. [빈내지 패딩](#4-빈내지-패딩)
5. [에러 처리 패턴](#5-에러-처리-패턴)
6. [표지 생성 상세](#6-표지-생성-상세)
7. [finalize 상세](#7-finalize-상세)
8. [데모 앱별 비교표](#8-데모-앱별-비교표)

---

## 1. 전체 워크플로우

### 1.1 10단계 정석 순서

```
 1. 충전금 확인       GET  /credits
 2. 책 생성 (draft)   POST /books
 3. 사진 업로드       POST /books/{bookUid}/photos     (선택 -- URL 직접 전달 시 불필요)
 4. 표지 생성         POST /books/{bookUid}/cover
 5. 내지 삽입 (반복)  POST /books/{bookUid}/contents
 6. 빈내지 패딩       POST /books/{bookUid}/contents    (페이지 부족 시)
 7. 발행면 삽입       POST /books/{bookUid}/contents    (template_kind=publish)
 8. 책 확정           POST /books/{bookUid}/finalization
 9. 가격 견적         POST /orders/estimate
10. 주문 생성         POST /orders
```

### 1.2 SDK 예제의 전체 흐름 (server_pipeline.py)

```python
# 1. 충전금 확인
credit = client.credits.get_balance()
balance = credit["data"]["balance"]

# 2. 책 생성
book = client.books.create(
    book_spec_uid="SQUAREBOOK_HC",
    title="서버 파이프라인 테스트",
    creation_type="TEST",
    external_ref="PIPELINE-001",
)
book_uid = book["data"]["bookUid"]

# 3. 사진 업로드
upload = client.photos.upload(book_uid, "sample_photo.jpg")
photo_name = upload["data"]["fileName"]

# 4. 표지
client.covers.create(book_uid,
    template_uid=TPL_COVER,
    parameters={"title": "나의 일기장", "dateRange": "2026.01 - 2026.01",
                 "coverPhoto": photo_name},
)

# 5. 간지 + 내지 (반복)
client.contents.insert(book_uid, template_uid=TPL_GANJI,
    parameters={"year": "2026", "monthTitle": "1월", ...})

for entry in SAMPLE_ENTRIES:
    client.contents.insert(book_uid, template_uid=TPL_NAEJI,
        parameters={"monthNum": entry["month"], "dayNum": entry["day"], ...})
    time.sleep(0.5)

# 6. 빈내지 패딩
for i in range(padding_needed):
    client.contents.insert(book_uid, template_uid=TPL_BLANK, break_before="page")

# 7. 발행면
client.contents.insert(book_uid, template_uid=TPL_PUBLISH,
    parameters={"title": "나의 일기장", "publishDate": "2026.03.16", "author": "홍길동"})

# 8. finalize (재시도 루프 포함)
for attempt in range(5):
    try:
        fin = client.books.finalize(book_uid)
        break
    except ApiError as e:
        if "최소 페이지 미달" in str(e.details):
            for _ in range(4):
                client.contents.insert(book_uid, template_uid=TPL_BLANK, break_before="page")

# 9. 견적
estimate = client.orders.estimate([{"bookUid": book_uid, "quantity": 1}])

# 10. 주문
order = client.orders.create(
    items=[{"bookUid": book_uid, "quantity": 1}],
    shipping=SHIPPING,
    external_ref="PIPELINE-001",
)
```

### 1.3 데모 앱의 공통 흐름 (JavaScript)

데모 앱들은 모두 같은 패턴을 따른다:

```
books.create() --> covers.create() --> [간지 + 내지 반복] --> 빈내지 --> 발행면 --> (UI에서 finalize 버튼)
```

주문은 별도의 파트너 주문 데모(`partner-order-demo`)에서 처리한다.

### 1.4 각 단계의 API 요청/응답 형식

#### 책 생성

```javascript
// 요청
const createResult = await client.books.create({
    title: bookTitle,
    bookSpecUid: 'SQUAREBOOK_HC',
    creationType: 'TEST'  // 또는 'LIVE'
});
// 응답: { bookUid: "bk_xxx" }
```

#### 사진 업로드

```python
# Python SDK
upload = client.photos.upload(book_uid, "photo.jpg")
# 응답: { "data": { "fileName": "photo250105143052123.JPG", ... } }
```

```javascript
// JS SDK
const result = await client.photos.upload(bookUid, file);
// 응답: { fileName: "photo250105143052123.JPG", ... }
```

#### 견적

```javascript
// 파트너 주문 데모
const data = await client.orders.estimate({ items: [{ bookUid, quantity: 1 }] });
// 응답에서 주요 필드:
//   paidCreditAmount: 실제 차감 금액 (VAT 포함)
//   creditSufficient: 잔액 충분 여부
```

#### 주문

```javascript
const data = await client.orders.create({
    items: [{ bookUid, quantity: 1 }],
    shipping: {
        recipientName: "홍길동",
        recipientPhone: "010-1234-5678",
        postalCode: "06100",
        address1: "서울특별시 강남구 테헤란로 123",
        address2: "4층",
        memo: "부재 시 경비실"
    },
    externalRef: "ORDER-001"
});
// 응답: { orderUid, paidCreditAmount, creditBalanceAfter, ... }
```

---

## 2. contents.insert 상세

### 2.1 요청 형식

```
POST /books/{bookUid}/contents?breakBefore={value}
Content-Type: multipart/form-data
```

**폼 필드**:

| 필드 | 필수 | 설명 |
|------|------|------|
| `templateUid` | O | 내지 템플릿 UID |
| `parameters` | - | JSON 문자열 (템플릿 파라미터) |
| 동적 이미지 필드 | - | `rowPhotos` 등 파일 업로드 |

### 2.2 breakBefore 옵션

| 값 | 동작 | 용도 |
|----|------|------|
| `none` (또는 빈 문자열) | 이전 콘텐츠 바로 다음에 배치 | 연속 콘텐츠 |
| `column` | 다음 컬럼/슬롯 또는 새 페이지 | 컬럼 분리 |
| `page` | 새 페이지/사이드부터 시작 | 챕터, 간지, 발행면 |
| `pageSide` (left/right) | divider/publish에서만 사용 | 특정 사이드 지정 |

**template_kind별 breakBefore 허용**:

| template_kind | none | column | page | pageSide |
|---------------|------|--------|------|----------|
| content       | O    | O      | O    | X (에러) |
| divider       | X    | X      | O (기본) | O (left/right) |
| publish       | X    | X      | O (기본) | O (left/right) |

### 2.3 데모 앱에서의 breakBefore 사용 패턴

**중요**: 데모 앱은 SDK에 `breakBefore` 전달 시 `'none'`을 빈 문자열로 변환한다:

```javascript
// book-builder.js (일기장, 알림장, 구글포토북 모두 동일)
async function sdkPostContent(client, bookUid, templateUid, parameters, breakBefore) {
    return client.contents.insert(bookUid, templateUid, stripEmptyImages(parameters), {
        breakBefore: breakBefore === 'none' ? '' : breakBefore,
    });
}
```

**breakBefore 배정 규칙 (데모 앱 공통)**:
- 간지: `'page'` (항상 새 페이지)
- 첫 번째 내지 (간지 바로 다음): `'page'` 또는 `'none'` (타입에 따라 다름)
- 이후 내지: `'none'` (연속 배치)
- 빈내지: `'page'` (항상 새 페이지)
- 발행면: `'page'` (항상 새 페이지)

### 2.4 응답과 cursor 객체

JS SDK의 `ContentsClient.insert()`는 응답에서 `cursor` 객체를 추출하여 반환값에 병합한다:

```javascript
// sweetbook-sdk-user.js -- ContentsClient.insert()
async insert(bookUid, templateUid, parameters, options = {}) {
    const { files, breakBefore } = options;
    const fd = this._buildTemplateFormData(templateUid, parameters, files, 'rowPhotos');
    const params = {};
    if (breakBefore) params.breakBefore = breakBefore;
    const body = await this._request('POST', `/Books/${bookUid}/contents`, { formData: fd, params });
    const data = new ResponseParser(body).getData();
    if (body?.cursor && data && typeof data === 'object') {
      data.pageNum = body.cursor.pageNum;
      data.pageSide = body.cursor.pageSide;
    }
    return data;
}
```

**cursor 객체의 필드**:

| 필드 | 타입 | 설명 |
|------|------|------|
| `pageNum` | number | 현재 삽입된 콘텐츠의 마지막 페이지 번호 |
| `pageSide` | string | `"left"` 또는 `"right"` -- 마지막 콘텐츠가 놓인 사이드 |

**추가로 응답의 `data` 에 포함되는 필드**:

| 필드 | 설명 |
|------|------|
| `pageCount` | 현재 책의 총 페이지 수 |
| `result` | `"inserted"` |
| `breakBefore` | 실제 적용된 breakBefore 값 |

데모 앱은 이 `pageSide`와 `pageCount`를 적극 활용한다:
- `pageSide`: 발행면 위치 보장을 위한 빈내지 삽입 판단
- `pageCount`: finalize 가능 여부 판단 (24페이지 이상)

---

## 3. pageSide 메커니즘

### 3.1 left/right 교대 규칙

양면 인쇄에서 페이지는 left(왼쪽)와 right(오른쪽)으로 교대 배치된다:

| pageNum | pageSide | 설명 |
|---------|----------|------|
| 0       | right    | 표지 |
| 1       | right    | 첫 번째 내지 (오른쪽 시작) |
| 2       | left     | 두 번째 내지 |
| 3       | right    | 세 번째 내지 |
| ...     | ...      | left/right 교대 |

### 3.2 정방형 책 예외 (SQUAREBOOK_HC)

첫 내지(pageNum=1)는 **right**에서 시작한다. `pageSide=left` 요청 시 pageNum=2, left에 배치.

### 3.3 pageSide 배치 알고리즘 (divider/publish)

| 현재 Side | 요청 Side | 결과 페이지 | 결과 Side | 설명 |
|-----------|-----------|-------------|-----------|------|
| left      | left      | +1          | left      | 다음 페이지 왼쪽 |
| left      | right     | same        | right     | 같은 페이지 오른쪽 |
| right     | left      | +1          | left      | 다음 페이지 왼쪽 |
| right     | right     | +1          | right     | 다음 페이지 오른쪽 |

### 3.4 발행면 위치 보장 패턴

데모 앱들은 마지막 내지의 `pageSide`를 확인하여 발행면이 올바른 위치에 오도록 빈내지를 삽입한다:

```javascript
// 일기장 데모 -- app.js processEntries() 끝부분
const lastSide = lastResult?.pageSide || 'right';
if (lastSide === 'left' && tplUids.tplBlank) {
    appendLog('빈내지 삽입 (발행면 위치 조정)...', 'info');
    await sdkPostContent(client, bookUid, tplUids.tplBlank, {}, 'page');
    appendLog('빈내지 삽입 완료', 'success');
}
```

```javascript
// 알림장 데모 -- app.js processEntries() 끝부분
const lastSide = lastResult?.pageSide || 'right';
if (lastSide === 'left' && tplUids.blank) {
    appendLog('빈내지 삽입 (발행면 위치 조정)...', 'info');
    // ...빈내지 파라미터 구성 (타입에 따라 다름)...
    await sdkPostContent(client, bookUid, tplUids.blank, blankP, 'page');
    appendLog('빈내지 삽입 완료', 'success');
}
```

```javascript
// 구글포토북 데모 -- app.js createPhotoBook() 끝부분
let lastResult = result?.lastResult;
const lastSide = lastResult?.pageSide || 'right';
if (lastSide === 'left' && tplUids.tplBlank) {
    appendLog('빈내지 삽입 (발행면 위치 조정)...', 'info');
    lastResult = await sdkPostContent(client, bookUid, tplUids.tplBlank, {}, 'page');
    appendLog('빈내지 삽입 완료', 'success');
}
```

**패턴 요약**: `lastSide === 'left'`이면 빈내지 1장 삽입 -> 발행면이 left(왼쪽 페이지)에 오도록 보장.

---

## 4. 빈내지 패딩

### 4.1 SDK의 사전 계산 방식 (server_pipeline.py)

SDK 예제는 내지 삽입 **전에** 필요한 빈내지 수를 사전 계산한다:

```python
# 간지(2p) + 내지15개(15p) = 17p -> 최소24p까지 빈내지 추가 + 발행면(1p) 여유
padding_needed = 6  # 24 - 17 - 1(발행면) = 6p
for i in range(padding_needed):
    client.contents.insert(book_uid, template_uid=TPL_BLANK, break_before="page")
    time.sleep(0.5)
```

### 4.2 SDK의 finalize 재시도 루프 (server_pipeline.py)

사전 계산이 빗나갈 경우를 대비한 안전장치:

```python
# 7. 확정 (페이지 부족 시 빈내지 추가 후 재시도)
for attempt in range(5):
    try:
        fin = client.books.finalize(book_uid)
        final_pages = fin["data"].get("pageCount", "?")
        break
    except ApiError as e:
        if "최소 페이지 미달" in str(e.details):
            for _ in range(4):
                client.contents.insert(book_uid, template_uid=TPL_BLANK, break_before="page")
                time.sleep(0.5)
        else:
            raise
```

**핵심**: `"최소 페이지 미달"` 에러 감지 -> 빈내지 4장 추가 -> 재시도 (최대 5회)

### 4.3 데모 앱의 동적 방식 (pageCount 활용)

데모 앱들은 사전 계산 없이, `contents.insert` 응답의 `pageCount`를 실시간으로 확인한다:

```javascript
// 일기장/알림장 데모 -- processEntries() 마지막 단계
const publishResult = await sdkPostContent(client, bookUid, tplUids.tplPublish, publishParams, 'page');
const pageCount = publishResult?.pageCount || 0;

// finalize 버튼은 24페이지 이상일 때만 활성화
const finalizeBtn = document.getElementById('finalizeBtn');
finalizeBtn.disabled = pageCount < 24;
```

### 4.4 socialBook의 발행면 보류 패턴

구글포토북 데모는 가장 정교한 빈내지/발행면 처리를 한다:

```javascript
// socialBook-demo/app.js
const MIN_PAGES_FOR_FINALIZE = 24;
const MIN_PAGES_FOR_PUBLISH = 22;

// 발행면 삽입 전 페이지 수 확인
const prePublishPages = lastResult?.pageCount || 0;
let totalPages = prePublishPages;
let publishDeferred = false;

if (prePublishPages >= MIN_PAGES_FOR_PUBLISH) {
    // 22페이지 이상이면 발행면 바로 삽입
    const publishResult = await sdkPostContent(client, bookUid, tplUids.tplPublish, publishParams, 'page');
    totalPages = publishResult?.pageCount || 0;
} else {
    publishDeferred = true;
    appendLog(`현재 ${prePublishPages}페이지 -- 페이지 부족으로 발행면 삽입을 보류합니다.`, 'info');
}

// 빈내지 추가 버튼 + 발행면 추가 버튼 + 제작 버튼 동적 활성화
if (totalPages < MIN_PAGES_FOR_FINALIZE && tplUids.tplBlank) {
    addBlankBtn.disabled = false;
    addBlankBtn.style.display = 'inline-block';
}
if (publishDeferred && totalPages >= 22 && totalPages % 2 === 0) {
    addPublishBtn.disabled = false;
    addPublishBtn.style.display = 'inline-block';
}
```

**socialBook의 빈내지 추가 버튼 로직**:

```javascript
// addBlankBtn click handler
const result = await sdkPostContent(client, bookUid, tplBlank, {}, 'page');
const pageCount = result?.pageCount || 0;

// 발행면 보류 상태 + 짝수 페이지 + 22이상이면 발행면 추가 버튼 표시
const publishDeferred = addPublishBtn.dataset.published !== 'true';
if (publishDeferred && pageCount >= MIN_PAGES_FOR_PUBLISH && pageCount % 2 === 0) {
    addPublishBtn.disabled = false;
    addPublishBtn.style.display = 'inline-block';
}

if (pageCount >= MIN_PAGES_FOR_FINALIZE) {
    addBlankBtn.style.display = 'none';
    finalizeBtn.disabled = false;
}
```

---

## 5. 에러 처리 패턴

### 5.1 일시중지/이어서하기 (pause/resume)

모든 데모 앱은 `_paused` 플래그와 `_saved` 스냅샷으로 일시중지/이어서하기를 구현한다:

```javascript
// 전역 상태
let _paused = false;     // 일시중지 요청 플래그
let _saved = null;       // 이어서하기용 스냅샷
```

**일시중지 요청 감지** (entries 루프 내부):

```javascript
// 일기장 데모 -- processEntries()
for (let i = startIndex; i < entries.length; i++) {
    // 일시중지 체크
    if (_paused) {
        _saved = { ...ctx, startIndex: i, successCount, failCount, lastResult };
        appendLog(`일시중지 (${i}/${totalEntries})`, 'info');
        loading.classList.remove('show');
        setButtons('paused');
        return;
    }
    // ... entry 처리 ...
}
```

**에러 시 자동 스냅샷 저장** (catch 블록):

```javascript
} catch (err) {
    const detail = err.details ? ` | ${JSON.stringify(err.details)}` : '';
    appendLog(`${entry.type} 오류: ${err.message}${detail}`, 'error');
    failCount++;
    _saved = { ...ctx, startIndex: i, successCount, failCount, lastResult };
    appendLog('"이어서하기"로 재시도 가능', 'info');
    loading.classList.remove('show');
    setButtons('stopped');
    return;
}
```

**이어서하기**:

```javascript
async function resumeBook() {
    if (!_saved) return;
    _paused = false;
    loading.classList.add('show');
    setButtons('running');
    await processEntries(_saved);
}
```

### 5.2 stripEmptyImages -- 빈 이미지 파라미터 제거

모든 데모 앱은 이미지 파라미터가 빈 문자열이면 제거한다. API가 빈 이미지 URL을 에러로 처리하기 때문이다:

```javascript
// 일기장 데모 -- book-builder.js
const IMAGE_PARAM_KEYS = new Set(['coverPhoto','photo','photo1','photo2','frontPhoto','backPhoto']);

function stripEmptyImages(obj) {
    const result = {};
    for (const [k, v] of Object.entries(obj)) {
        if (IMAGE_PARAM_KEYS.has(k) && (!v || v === '')) continue;
        result[k] = v;
    }
    return result;
}
```

```javascript
// 알림장 데모 -- book-builder.js (이미지 키가 다름)
const IMAGE_PARAM_KEYS = new Set([
    'coverPhoto', 'monthCharacter', 'lineVertical',
    'parentBalloon', 'weatherIcon', 'photo',
]);
```

```javascript
// 구글포토북 데모 -- book-builder.js
const IMAGE_PARAM_KEYS = new Set(['coverPhoto', 'photo', 'frontPhoto', 'backPhoto']);
```

### 5.3 breakBefore 빈 값 변환

모든 데모 앱에서 공통:

```javascript
async function sdkPostContent(client, bookUid, templateUid, parameters, breakBefore) {
    return client.contents.insert(bookUid, templateUid, stripEmptyImages(parameters), {
        breakBefore: breakBefore === 'none' ? '' : breakBefore,
    });
}
```

**이유**: API는 `breakBefore` 쿼리 파라미터가 없으면 기본값 `none`을 적용한다. 명시적으로 `'none'`을 보내면 빈 문자열과 동일하게 동작하지만, SDK는 `breakBefore`가 falsy(빈 문자열)이면 쿼리 파라미터 자체를 생략한다:

```javascript
// sweetbook-sdk-user.js -- ContentsClient.insert()
const params = {};
if (breakBefore) params.breakBefore = breakBefore;
// breakBefore가 ''이면 params에 추가되지 않음 -> API 기본값 none 적용
```

### 5.4 Rate Limit 대응

**SDK (Python)**: `time.sleep(0.5)` 호출 간격으로 Rate Limit 방지

```python
# server_pipeline.py -- 매 내지 삽입 후 0.5초 대기
for i, entry in enumerate(SAMPLE_ENTRIES):
    client.contents.insert(book_uid, template_uid=TPL_NAEJI, parameters={...})
    time.sleep(0.5)
```

**데모 앱 (JavaScript)**: 별도 sleep 없이 순차 `await`로 자연스러운 간격 유지. 에러 발생 시 일시중지/이어서하기로 대응.

**API Rate Limit 사양**:

| 대상 | 제한 |
|------|------|
| 일반 API | 300 req/min |
| 파일 업로드 | 200 req/min |

초과 시 `429 Too Many Requests` + `Retry-After: 60` 헤더 반환.

---

## 6. 표지 생성 상세

### 6.1 API 엔드포인트

```
POST /books/{bookUid}/cover
Content-Type: multipart/form-data
```

**폼 필드**:

| 필드 | 필수 | 설명 |
|------|------|------|
| `templateUid` | O | 표지 템플릿 UID |
| `parameters` | - | JSON 문자열 (템플릿 파라미터) |
| `files` | - | $upload 플레이스홀더에 매칭되는 파일 |

### 6.2 이미지 전달 방식 (4가지)

1. **URL**: http/https URL 문자열 직접 전달
2. **서버 파일명**: Photos API로 업로드한 `fileName` 전달
3. **$upload 플레이스홀더**: `"frontPhoto": "$upload"` + files 필드에 파일 매칭
4. **파일 직접 업로드**: multipart/form-data로 전송

### 6.3 데모 앱별 표지 파라미터 차이

**일기장A**:
```javascript
coverParams = {
    coverPhoto,           // URL 또는 fileName
    title: "나의 하루 기록",
    dateRange: "26.01 - 27.03"
};
```

**일기장B**:
```javascript
coverParams = {
    frontPhoto: coverPhoto,
    backPhoto,
    dateRange: "2026.01.01 - \n2027.05.30",
    spineTitle: "2026 Diary Book"
};
```

**알림장** (A/B/C 공통 구조):
```javascript
const coverParams = {
    childName: "김아이",
    schoolName: "꽃잎 유치원",
    volumeLabel: "Vol.1",
    periodText: "2026년 1월~2026년 12월",
    coverPhoto,
};
```

**구글포토북A**:
```javascript
const params = {
    subtitle: "나의 모든 순간들",
    dateRange: "2024.06 - 2025.12",
    coverPhoto,            // 선택적 -- stripEmptyImages로 빈 값 제거
};
```

**구글포토북B/C**: 커버 데이터를 JSON에서 그대로 전달 (`coverParamsB(data)` / `coverParamsC(data)`).

### 6.4 표지 생성 호출 패턴

```javascript
// 공통 패턴 (모든 데모 앱)
const cleanCoverParams = stripEmptyImages(coverParams);
await client.covers.create(bookUid, tplUids.tplCover || tplUids.cover, cleanCoverParams);
```

Python SDK:
```python
client.covers.create(book_uid,
    template_uid=TPL_COVER,
    parameters={"title": "나의 일기장", "dateRange": "2026.01 - 2026.01",
                 "coverPhoto": photo_name},
)
```

---

## 7. finalize 상세

### 7.1 제약조건

| 판형 | pageMin | pageMax | pageIncrement |
|------|---------|---------|---------------|
| SQUAREBOOK_HC | 24 | 130 | 2 |
| PHOTOBOOK_A4_SC | 24 | 130 | 2 |
| PHOTOBOOK_A5_SC | 50 | 200 | 2 |

- 페이지 수가 `pageMin` ~ `pageMax` 범위 내여야 한다
- 페이지 수가 `pageIncrement`의 배수여야 한다 (2단위)
- draft 상태의 책만 finalize 가능

### 7.2 API 엔드포인트

```
POST /books/{bookUid}/finalization
```

**성공 응답**:
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

### 7.3 멱등성

이미 finalized된 책에 대해 재호출 시 `200 OK`를 반환한다 (에러 아님). 확정 후에는 내용 수정 불가.

### 7.4 데모 앱의 finalize 패턴

데모 앱들은 finalize를 UI 버튼으로 분리하여, 사용자가 빈내지를 수동으로 추가한 후 수행할 수 있게 한다:

```javascript
// 모든 데모 앱 공통
document.getElementById('finalizeBtn').addEventListener('click', async () => {
    const bookUid = finalizeBtn.dataset.bookUid;
    finalizeBtn.disabled = true;
    try {
        await client.books.finalize(bookUid);
        appendLog(`최종화 완료! bookUid: ${bookUid}`, 'success');
        finalizeBtn.style.display = 'none';
    } catch (error) {
        appendLog(`최종화 오류: ${error.message}`, 'error');
        finalizeBtn.disabled = false;
    }
});
```

**finalize 버튼 활성화 조건**:
```javascript
// 일기장/알림장: pageCount 기반
finalizeBtn.disabled = pageCount < 24;

// 구글포토북: 상수 사용
const MIN_PAGES_FOR_FINALIZE = 24;
finalizeBtn.disabled = totalPages < MIN_PAGES_FOR_FINALIZE;
```

### 7.5 SDK의 finalize 재시도 루프 vs 데모 앱 방식

| 항목 | SDK (server_pipeline.py) | 데모 앱 |
|------|--------------------------|---------|
| 빈내지 추가 시점 | 내지 삽입 후, finalize 전 사전 계산 | 실시간 pageCount 확인 |
| finalize 실패 대응 | `for attempt in range(5)` 자동 재시도 루프 | UI 버튼으로 수동 재시도 |
| 빈내지 추가 단위 | 4장씩 추가 (재시도당) | 1장씩 수동 추가 (socialBook) |
| 발행면 위치 | 빈내지 후 고정 삽입 | pageSide 동적 확인 |

---

## 8. 데모 앱별 비교표

### 8.1 사진 처리

| 항목 | 일기장 | 알림장 | 구글포토북 | 파트너 주문 |
|------|--------|--------|------------|-------------|
| 사진 소스 | JSON 내 URL | JSON 내 URL | Google Photos / 로컬 파일 / JSON | N/A (주문만) |
| Photos API 업로드 | X (URL 직접 전달) | X (URL 직접 전달) | O (Google/로컬 사진 업로드) | N/A |
| 이미지 크기 조회 | O (일기장B: 가로/세로 판별) | X | X | N/A |
| 이미지 전달 방식 | URL 문자열 | URL 문자열 | fileName (업로드 후) / URL (JSON) | N/A |

### 8.2 빈내지 처리

| 항목 | 일기장 | 알림장 | 구글포토북 | SDK |
|------|--------|--------|------------|-----|
| 빈내지 삽입 기준 | pageSide (발행면 위치) | pageSide (발행면 위치) | pageSide + pageCount | 사전 계산 + finalize 재시도 |
| 빈내지 파라미터 | `{}` (빈 객체) | 타입별 다름 (bookTitle, lineVertical 등) | `{}` (빈 객체) | 빈 객체 |
| 빈내지 추가 UI | 없음 (자동) | 없음 (자동) | 버튼 (수동 1장씩) | N/A |
| 빈내지 breakBefore | `'page'` | `'page'` | `'page'` | `"page"` |

### 8.3 발행면 처리

| 항목 | 일기장 | 알림장 | 구글포토북 |
|------|--------|--------|------------|
| 삽입 시점 | 모든 entries 완료 후 즉시 | 모든 entries 완료 후 즉시 | pageCount >= 22이면 즉시, 아니면 보류 |
| 보류 패턴 | X | X | O (addPublishBtn 별도) |
| breakBefore | `'page'` | `'page'` | `'page'` |
| 파라미터 | photo, title, publishDate, author, hashtags | photo, title, publishDate, author, hashtags | photo, title, publishDate, author, hashtags, publisher |

### 8.4 finalize 처리

| 항목 | 일기장 | 알림장 | 구글포토북 | SDK | 파트너 주문 |
|------|--------|--------|------------|-----|-------------|
| 방식 | UI 버튼 | UI 버튼 | UI 버튼 | 코드 내 자동 | N/A (이미 finalized) |
| 재시도 | 수동 | 수동 | 수동 | 자동 (5회 루프) | N/A |
| 활성화 조건 | pageCount >= 24 | pageCount >= 24 | pageCount >= 24 | 에러 기반 | N/A |

### 8.5 에러 복구

| 항목 | 일기장 | 알림장 | 구글포토북 | SDK |
|------|--------|--------|------------|-----|
| 일시중지 | O (_paused) | O (_paused) | O (_paused) | X |
| 이어서하기 | O (_saved 스냅샷) | O (_saved 스냅샷) | O (_saved 스냅샷 + phase 구분) | X |
| 에러 시 동작 | 스냅샷 저장 + stopped 상태 | 스냅샷 저장 + stopped 상태 | 스냅샷 저장 + stopped 상태 | 예외 발생 |
| rate limit 대응 | 없음 (순차 await) | 없음 (순차 await) | 없음 (순차 await) | time.sleep(0.5) |

### 8.6 전체 아키텍처 비교

| 항목 | 일기장 | 알림장 | 구글포토북 | 파트너 주문 |
|------|--------|--------|------------|-------------|
| SDK | sweetbook-sdk-user.js (SweetbookClient) | sweetbook-sdk-user.js | sweetbook-sdk-user.js | sweetbook-sdk-order.js (OrderClient) |
| 파일 구성 | app.js + book-builder.js + diary-config.js | app.js + book-builder.js + alrimjang-config.js | app.js + book-builder.js + photobook-config.js | app.js + sweetbook-sdk-order.js |
| 책 생성 | O | O | O | X (조회만) |
| 주문 생성 | X | X | X | O |
| 타입 수 | 2 (A/B) | 3 (A/B/C) | 3 (A/B/C) | 1 |
| 판형 | SQUAREBOOK_HC | SQUAREBOOK_HC | SQUAREBOOK_HC | 다양 (finalized 책 기반) |

---

## 부록: 주요 코드 경로

| 파일 | 역할 |
|------|------|
| `test/bookprintapi-python-sdk/examples/server_pipeline.py` | Python SDK 전체 파이프라인 예제 |
| `demos/diaryBook-demo/app.js` | 일기장 UI + 플로우 |
| `demos/diaryBook-demo/book-builder.js` | 일기장 entries 빌드 + API 호출 |
| `demos/diaryBook-demo/diary-config.js` | 일기장 템플릿/설정 |
| `demos/diaryBook-demo/sweetbook-sdk-user.js` | JS SDK (Books, Photos, Covers, Contents) |
| `demos/kidsDailyBook-demo/app.js` | 알림장 UI + 플로우 |
| `demos/kidsDailyBook-demo/book-builder.js` | 알림장 entries 빌드 + API 호출 |
| `demos/kidsDailyBook-demo/alrimjang-config.js` | 알림장 템플릿/설정 |
| `demos/socialBook-demo/app.js` | 구글포토북 UI + 플로우 |
| `demos/socialBook-demo/book-builder.js` | 구글포토북 파라미터 빌더 |
| `demos/socialBook-demo/photobook-config.js` | 구글포토북 템플릿/설정 |
| `demos/partner-order-demo/app.js` | 파트너 주문 UI (충전금, 책 목록, 견적, 주문) |
| `demos/partner-order-demo/sweetbook-sdk-order.js` | JS SDK (Orders, Credits, Books 조회) |
