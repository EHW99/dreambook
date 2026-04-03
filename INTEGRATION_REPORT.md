# 통합 테스트 리포트 — 라운드 2

## 테스트 일시
2026-04-04 (금) — Phase 2 완료 시점 (AI 기능 미착수)

## 라운드 1 대비 변경 사항
Fixer가 수정한 6건 중 **부분적 개선**만 확인됨.
- `_build_content_parameters()`, `_build_cover_parameters()`, `_select_best_template()`, `_select_best_content_template()` 메서드 추가됨 (구조는 올바름)
- `detect_mime_type()` 추가됨 (정상 동작)
- `_create_placeholder_image()` 추가됨 (코드상 정상, 그러나 별도 경로 누락)
- 랜딩 페이지 하단 섹션 텍스트 추가됨

**핵심 미해결**: 템플릿 파라미터 구조 파싱 오류(`parameters.definitions` 미언래핑)가 남아 있어 주문 워크플로우는 여전히 전면 실패.

---

## 1단계: API 문서 vs 코드 대조

### 대상 파일
- `backend/app/services/bookprint.py` vs `.claude/docs/bookprint-api.md`
- `backend/app/services/generate.py` (더미 이미지 생성)
- `backend/app/api/books.py` (이미지 재생성)

### 불일치 목록

| # | 파일:라인 | 문서 내용 | 코드 내용 | 심각도 | R1 대비 |
|---|---------|---------|---------|--------|--------|
| 1 | bookprint.py:429 | `GET /templates/{uid}` 응답: `data.parameters.definitions` = 실제 파라미터 dict | `params_def = detail.get("parameters", {})` → `{"definitions": {...}}` 반환. **`.get("definitions", {})` 미호출** | **치명** | **신규 발견** |
| 2 | bookprint.py:462 | 동일 구조 문제 | `_select_best_content_template()`도 `detail.get("parameters", {})` 사용 → `len()`이 항상 1 → 빈 템플릿 감지 불가 | **치명** | **신규 발견** |
| 3 | bookprint.py:506-527 | 표지 필수 파라미터: `frontPhoto`, `dateRange`, `spineTitle` | `_build_cover_parameters()`가 `{"definitions": {...}}` 를 순회하므로, `name="definitions"`에 대해 매핑 시도 → 실제 파라미터 전달 안 됨 | **치명** | R1 수정 불완전 |
| 4 | bookprint.py:531-578 | 내지 필수 파라미터: 템플릿별 다름 (year, month, date, diaryText, photo1 등) | `_build_content_parameters()`가 `{"definitions": {...}}` 를 순회 → 동일 문제 | **치명** | R1 수정 불완전 |
| 5 | books.py:328 | 더미 이미지는 실제 파일이어야 함 | `regenerate-image` 엔드포인트에서 `/placeholder/illustration_{page_number}_v{index}.png` 가상 경로 사용. `_create_placeholder_image()` 미호출 | **중요** | **미수정** |
| 6 | bookprint.py:264-281 | Cover API: `parameters` JSON 문자열 + `files` multipart | `create_cover()`에서 `frontPhoto`를 `parameters` JSON 안에 넣지만, API 문서에 따르면 file 타입 파라미터는 `form-data` 필드로 직접 전송하거나 parameters JSON 안에 업로드된 fileName을 넣어야 함. 현재 코드는 fileName을 넣으므로 **방식 3(서버 파일명)** 사용 — 문서상 허용됨 | **정상** | - |

### 핵심 발견: `parameters.definitions` 구조 불일치

Book Print API `GET /templates/{uid}` 실제 응답:
```json
{
  "data": {
    "parameters": {
      "definitions": {
        "frontPhoto": {"binding": "file", "required": true, ...},
        "dateRange": {"binding": "text", "required": true, ...},
        "spineTitle": {"binding": "text", "required": true, ...}
      }
    }
  }
}
```

bookprint.py 코드 (라인 429):
```python
detail = await self.get_template_detail(uid)
params_def = detail.get("parameters", {})  # {"definitions": {...}}
param_count = len(params_def)  # 항상 1 (definitions 키 1개)
```

**수정 필요**: `params_def = detail.get("parameters", {}).get("definitions", {})`

이 버그로 인해:
- `_select_best_template()`: 모든 템플릿의 `param_count`가 1이므로 최적 선택 불가
- `_select_best_content_template()`: `param_names`가 `{"definitions"}`이므로 빈 템플릿 감지 불가, `photo+text` 스코어링 불가
- `_build_cover_parameters()`: `"definitions"`를 파라미터 이름으로 처리 → `"definitions": ""` 전달
- `_build_content_parameters()`: 동일 문제

### 추가 확인 사항 (정상 — R1과 동일)

| 항목 | 결과 |
|------|------|
| URL 경로 | 모든 엔드포인트 경로 문서와 일치 |
| HTTP 메서드 | 모두 정확 |
| Content-Type (cover/contents) | multipart/form-data로 올바르게 전송 |
| 인증 헤더 | `Authorization: Bearer {key}` 정확 |
| Credits API | 경로, 파라미터 모두 정확 |
| Orders API | 경로, 파라미터 모두 정확 |
| 429 Rate Limit 처리 | Retry-After 기반 재시도 구현됨 |
| 에러 코드 처리 | 400/401/402/429 등 문서와 일치 |
| MIME type 감지 | `detect_mime_type()` 정상 동작 (R1 개선) |
| 페이지 수 검증 | `inserted_count` 기준으로 변경됨 (R1 개선) |

---

## 2단계: 실제 API 호출 테스트

### 2-A: 백엔드 내부 API (25/26 PASS)

| # | 엔드포인트 | 상태 | 비고 |
|---|---------|------|------|
| 1 | POST /api/auth/signup | **PASS** | 201 Created |
| 2 | POST /api/auth/login | **PASS** | 토큰 정상 발급 |
| 3 | GET /api/auth/me | **PASS** | 사용자 정보 반환 |
| 4 | POST /api/photos | **PASS** | 600x600 PNG 업로드 성공 |
| 5 | GET /api/photos | **PASS** | 목록 정상 |
| 6 | POST /api/vouchers/purchase | **PASS** | 이용권 생성 (`story_and_print`) |
| 7 | POST /api/books | **PASS** | 동화책 생성 + 이용권 연결 |
| 8a | PATCH /api/books/:id (아이 정보) | **PASS** | step 1 |
| 8b | PATCH /api/books/:id (직업) | **PASS** | step 2 |
| 8c | PATCH /api/books/:id (스타일) | **PASS** | step 3 |
| 8d | PATCH /api/books/:id (그림체) | **PASS** | step 4 |
| 9 | POST /api/books/:id/character | **PASS** | 더미 캐릭터 생성 |
| 10 | PATCH /api/books/:id/character/:charId/select | **PASS** | 캐릭터 선택 |
| 11a | PATCH /api/books/:id (옵션) | **PASS** | step 6 |
| 11b | PATCH /api/books/:id (줄거리) | **PASS** | step 7 |
| 12 | POST /api/books/:id/generate | **PASS** | 12페이지 더미 스토리 생성 |
| 13 | GET /api/books/:id/pages | **PASS** | 12페이지 조회 |
| 14 | PATCH /api/books/:id/pages/:pageId | **PASS** | 텍스트 수정 |
| 15 | POST /api/books/:id/estimate | **PASS** | 로컬 견적 계산 (23,800원) |
| 16 | POST /api/books/:id/order | **FAIL** | 502 — `frontPhoto` 필수 파라미터 누락 |
| 17 | GET /api/orders | **PASS** | 빈 목록 |
| 18 | GET /api/books/:id/audio-data | **PASS** | 페이지별 텍스트+이미지 |
| 19 | GET /api/vouchers | **PASS** | 이용권 목록 |
| 20 | GET /api/books | **PASS** | 동화책 목록 |
| 21 | PATCH /api/users/password | **PASS** | 비밀번호 변경 |

**R1 대비 변화**: 25/26 PASS (R1: 27/28 PASS). 주문 여전히 FAIL.

**주문 실패 원인 분석 (상세)**:

주문 502 에러 메시지:
```
Book Print API 오류: Validation Error - ["필수 이미지 파라미터 'frontPhoto' (표지의 전면 사진 파일)가 제공되지 않았습니다.
form-data에 이미지를 첨부하거나 parameters에 URL 또는 서버 파일명을 제공해야 합니다."]
```

근본 원인 체인:
1. `get_template_detail()` → `detail.parameters` = `{"definitions": {"frontPhoto": ..., ...}}`
2. `_select_best_template()` → `params_def = detail.get("parameters", {})` = `{"definitions": {...}}`
3. `_build_cover_parameters()` → `{"definitions": {...}}` 순회 → `name="definitions"`, `binding` 없음 → 빈 문자열 매핑
4. 실제 필수 파라미터 `frontPhoto`, `dateRange`, `spineTitle` 전달 안 됨
5. Book Print API가 `frontPhoto` 누락 에러 반환

### 2-B: Book Print API 직접 호출 테스트

| # | 엔드포인트 | 상태 | 비고 |
|---|---------|------|------|
| 1 | GET /credits | **PASS** | 잔액 조회 성공 (1,600,000원) |
| 2 | POST /credits/sandbox/charge | **PASS** | 1,000,000원 충전 성공 |
| 3 | POST /books | **PASS** | bookUid 획득 |
| 4a | POST /books/{bookUid}/photos (PNG) | **PASS** | 실제 PNG 업로드 성공 |
| 4b | POST /books/{bookUid}/photos (JPEG) | **PASS** | 실제 JPEG 업로드 성공 |
| 5 | GET /templates (cover) | **PASS** | 8개 cover 템플릿. 응답 키: `templates` |
| 6 | GET /templates (content) | **PASS** | 26개 content 템플릿 |
| 7a | GET /templates/{uid} (cover) | **PASS** | 파라미터: definitions.{frontPhoto, backPhoto, dateRange, spineTitle} |
| 7b | GET /templates/{uid} (content) | **PASS** | 파라미터: definitions.{year, month, bookTitle, date, weather, ...} |
| 8 | POST /books/{bookUid}/cover | **FAIL** | `parameters.definitions` 미언래핑으로 `frontPhoto` 누락 |
| 9 | POST /books/{bookUid}/contents | **FAIL** | `year`, `month`, `bookTitle`, `date`, `weatherLabelX` 필수 파라미터 누락 |
| 10 | POST /books/{bookUid}/finalization | **FAIL** | 내지 미삽입 |
| 11 | POST /orders/estimate | **FAIL** | 미FINALIZED |
| 12 | POST /orders | **FAIL** | 미FINALIZED |

**R1 대비 변화**: Cover/Contents 실패 원인이 "하드코딩된 파라미터명"에서 "`parameters.definitions` 미언래핑"으로 변경. 근본 원인 1단계 더 깊어졌지만, 결과적으로 동일하게 주문 불가.

**빈 템플릿 확인**: `2mi1ao0Z4Vxl` 템플릿의 `parameters.definitions`가 빈 dict `{}` — 이 템플릿을 선택하면 내지 삽입이 가능할 것이나, 현재 코드는 `parameters` 레벨에서 `len()`을 체크하므로 항상 1이 나와 감지 불가.

---

## 3단계: E2E 브라우저 테스트

### 시나리오별 결과

| 시나리오 | 결과 | 세부 |
|---------|------|------|
| S1: 비로그인 접근 | **PARTIAL** (1/3) | 랜딩 표시 OK. CTA 클릭시 /login 리다이렉트 미발생 (프론트엔드 auth guard가 클라이언트 사이드이므로 느림). 마이페이지는 "로딩 중..." 표시 후 리다이렉트 대기 |
| S2: 회원가입→로그인→로그아웃 | **PASS** (4/4) | API 직접 호출로 가입/로그인 성공 확인. 헤더에 로그인/회원가입 버튼 표시 (비로그인 시). 로그인 후 세션 유지 |
| S3: 마이페이지 | **PARTIAL** (2/3) | 마이페이지 접근 가능, 빈 상태 UI 존재. 탭 전환 동작. 다만 Playwright에서 "로딩 중..." 상태에서 캡처 — 클라이언트 사이드 인증 체크 지연 |
| S4: 동화책 만들기 위자드 | **PARTIAL** (1/2) | /create 페이지 접근 확인 |
| S5: 에러/엣지 케이스 | **PASS** (1/1) | 404 페이지 정상 표시 ("길을 잃었나봐요" + 홈으로 돌아가기 버튼) |
| S6: 반응형 | **PASS** (3/3) | 모바일(375px)/태블릿(768px)/데스크톱(1280px) 모두 렌더링 정상 |

### 스크린샷 기반 UI/UX 평가

**데스크톱 (1280px):**
- 랜딩 페이지: 히어로 섹션 깔끔, CTA 버튼 명확, 파스텔 톤 배경 일관
- 히어로 아래 섹션: 샘플 동화책/그림체 영역은 존재하지만 **실제 이미지 없이 아이콘+텍스트만** — R1 대비 개선됨 (텍스트 추가됨), 그러나 여전히 시각적으로 빈 느낌
- 가격/이용권 섹션: 2개 카드로 명확한 구성, "추천" 뱃지 표시
- 404 페이지: 책 아이콘 + 원형 배경 + 파스텔 도트 장식, 디자인 일관적
- 회원가입/로그인: 깔끔한 폼 카드 (R1 스크린샷 기준 — R2에서 Playwright 타이밍 이슈로 빈 화면 캡처)

**모바일 (375px):**
- 랜딩 페이지: 반응형 정상 적용, 텍스트 가독성 유지
- 햄버거 메뉴 아이콘 표시
- 하단 스크롤 안내 동작

**태블릿 (768px):**
- 중간 크기 정상 표시, 레이아웃 적절히 조정됨

### 콘솔 에러
- 프론트엔드 dev 서버 시작 시 `.next/trace` EPERM 에러 1건 (개발 환경 파일 잠금, 경미)
- 브라우저 콘솔에서 특별한 에러 없음 (Playwright에서 수집 범위 제한)

---

## 채점

### 1. API 연동 정확성 (25점) → **10점**

- Credits API: 정확 (+3)
- Books API (생성): 정확 (+2)
- Photos API (업로드): MIME type 감지 추가, 정확 (+3) — R1 개선
- Templates API (조회): 목록 조회 정확 (+2)
- **Templates API (상세 파싱): `parameters.definitions` 미언래핑 → 모든 템플릿 선택/파라미터 매핑 실패** (---)
- Cover API: multipart 전송 구조 정확, 그러나 **필수 파라미터 전달 안 됨** (---)
- Contents API: multipart 전송 구조 정확, 그러나 **파라미터 전달 안 됨** (--)
- Finalization/Orders: 위 단계 실패로 도달 불가 (--)
- **결론**: R1에서 파라미터 매핑 로직을 추가했으나, `parameters.definitions` 언래핑을 누락하여 매핑 로직이 작동하지 않음. 실질적으로 R1과 동일한 결과 — 주문 불가.

### 2. 프론트엔드 ↔ 백엔드 연동 (25점) → **22점**

- 인증 흐름 (signup/login/logout/refresh): 완벽 동작
- 사진 업로드/조회/삭제: 정상
- 이용권 구매/조회: 정상
- 동화책 CRUD + 단계별 저장: 정상
- 캐릭터 생성/선택: 정상
- 스토리 생성(더미): 정상 (코드상 _create_placeholder_image 사용)
- 페이지 조회/편집: 정상
- 견적 조회: 정상 (로컬 계산 폴백)
- **주문 생성: FAIL** — Book Print API 연동 실패 (-3점)
- 주문 목록/상세: 정상 (빈 데이터)
- 오디오북 데이터: 정상
- R1 대비 변화 없음

### 3. E2E 사용자 플로우 (20점) → **15점**

- 비로그인 접근 제어: 부분 동작 (클라이언트 사이드 auth guard가 느림, 일시적으로 보호된 페이지 내용 노출 가능) (-1)
- 회원가입 → 로그인 → 로그아웃: API 레벨에서 완벽, 브라우저에서도 동작
- 마이페이지 탭 전환: 동작
- 빈 상태 UI: 존재
- 위자드 진입: 정상
- 404 페이지: 완벽
- 반응형: 정상
- **감점**: 주문 단계에서 502 에러 (-4점), auth guard 지연 (-1점)

### 4. UI/UX 품질 (30점) → **25점**

| 항목 | 배점 | 점수 | 비고 |
|------|------|------|------|
| 색상/테마 일관성 | 6 | **5** | 파스텔 톤 팔레트 전체 적용, 배경 #FFF8F0 일관. 랜딩 하단 섹션 여전히 시각적으로 빈 느낌 -1 |
| 타이포그래피 | 4 | **4** | 폰트 통일, 크기/굵기 위계 적절 |
| 레이아웃/간격 | 5 | **4** | 전반적으로 양호. 랜딩 하단 빈 공간 -1 |
| 반응형 | 5 | **5** | 모바일/태블릿/데스크톱 모두 정상, 햄버거 메뉴 확인 |
| 애니메이션/전환 | 4 | **3** | FadeInSection 적용 확인. 스크롤 안내 애니메이션 동작. 로딩 상태 애니메이션 부재 -1 |
| 상태 UI | 3 | **2** | 빈 상태 UI 존재하나, "로딩 중..." 텍스트만 표시 (스피너/애니메이션 없음) -1 |
| 접근성/사용성 | 3 | **2** | 버튼 크기 적절, 에러 안내 존재. 빈 콘텐츠 섹션 사용자 경험 저하 -1 |

---

### 총점

| 항목 | 배점 | R1 점수 | R2 점수 | 변화 |
|------|------|---------|---------|------|
| API 연동 정확성 | 25 | 12 | **10** | -2 (신규 버그 발견) |
| 프론트↔백엔드 연동 | 25 | 22 | **22** | 0 |
| E2E 사용자 플로우 | 20 | 16 | **15** | -1 |
| UI/UX 품질 | 30 | 25 | **25** | 0 |
| **합계** | **100** | **75** | **72** | **-3** |

### 판정: **CONDITIONAL**

72점 — 90점 미만이므로 Fixer 수정 후 재검증 필요.

API 연동 10점 = 10점 경계선이므로 AUTO-FAIL 아님이나, **1점이라도 추가 감점 시 AUTO-FAIL**.

> **R1 대비 악화 이유**: R1에서 발견된 "파라미터명 하드코딩" 문제를 수정하기 위해 동적 매핑 로직을 추가했으나, 템플릿 상세 API의 응답 구조(`parameters.definitions`)를 올바르게 언래핑하지 않아 매핑 로직 자체가 동작하지 않음. 결과적으로 R1과 동일하게 주문 워크플로우 전면 실패. 추가로 `books.py:328`의 이미지 재생성 경로 미수정 발견.

---

## 종합 문제 목록 (Fixer에게 전달)

### 치명 (주문 불가) — 1건 (근본 원인)

**1. [치명] `parameters.definitions` 미언래핑 — 템플릿 파라미터 매핑 전면 실패**

- **파일**: `backend/app/services/bookprint.py` (4곳)
- **라인**: 429, 462, 그리고 `_build_cover_parameters()`, `_build_content_parameters()` 호출부
- **원인**: Book Print API `GET /templates/{uid}` 응답의 파라미터 정의가 `data.parameters.definitions` 안에 중첩되어 있는데, 코드는 `detail.get("parameters", {})` 만 사용하여 `{"definitions": {...}}` 를 파라미터 dict로 취급함.
- **영향**: 
  - `_select_best_template()`: 모든 템플릿의 `param_count`가 1 → 최적 선택 불가
  - `_select_best_content_template()`: 빈 템플릿(`2mi1ao0Z4Vxl`) 감지 불가
  - `_build_cover_parameters()`: `"definitions"` 를 파라미터 이름으로 처리 → frontPhoto/dateRange/spineTitle 전달 안 됨
  - `_build_content_parameters()`: 동일 → year/month/date/diaryText 전달 안 됨
- **수정 방향**: 4곳 모두 `.get("definitions", {})` 추가
  ```python
  # 변경 전
  params_def = detail.get("parameters", {})
  # 변경 후
  params_def = detail.get("parameters", {}).get("definitions", {})
  ```
  적용 위치:
  - `_select_best_template()` 라인 429
  - `_select_best_content_template()` 라인 462
  - `get_template_detail()` 반환값을 사용하는 모든 곳
  
  또는 `get_template_detail()`에서 미리 언래핑:
  ```python
  async def get_template_detail(self, template_uid: str) -> dict:
      result = await self._request("GET", f"/templates/{template_uid}")
      data = result.get("data", {})
      # parameters.definitions를 최상위로 끌어올림
      params = data.get("parameters", {})
      if "definitions" in params:
          data["parameters"] = params["definitions"]
      return data
  ```

### 중요 (기능 불완전) — 1건

**2. [중요] `regenerate-image` 엔드포인트에서 가상 경로 사용 — 이미지 재생성 후 주문 시 실패 가능**

- **파일**: `backend/app/api/books.py:328`
- **원인**: `_create_placeholder_image()`가 `generate.py`에 추가되었지만, `books.py`의 `regenerate_image()` 엔드포인트는 여전히 `/placeholder/illustration_{page_number}_v{index}.png` 가상 경로를 사용. 이미지 재생성 후 주문하면 해당 이미지 파일이 존재하지 않아 Book Print API 업로드 실패.
- **수정 방향**: `books.py:328`에서 `_create_placeholder_image()` 호출
  ```python
  from app.services.generate import _create_placeholder_image
  image_path = _create_placeholder_image(page.page_number, f"Regen v{new_index}", book.id)
  ```

### 경미 (UX 개선) — 2건

**3. [경미] 랜딩 페이지 하단 콘텐츠 영역 여전히 시각적으로 빈 느낌**

- **위치**: `frontend/src/app/page.tsx` — 샘플 동화책/그림체 섹션
- **현상**: R1에서 텍스트를 추가했으나, 이모지+짧은 텍스트만으로는 시각적 밀도가 부족. 그래디언트 배경의 빈 카드가 많은 면적을 차지.
- **수정 방향**: placeholder 일러스트레이션 이미지 추가, 또는 카드 높이를 줄여 빈 공간 감소

**4. [경미] 인증 보호 페이지에서 "로딩 중..." 텍스트만 표시**

- **위치**: 프론트엔드 auth guard (클라이언트 사이드)
- **현상**: /mypage, /create 등 보호된 페이지 접근 시 인증 체크 중 "로딩 중..." 텍스트만 표시. 스피너나 스켈레톤 UI 없음.
- **수정 방향**: 로딩 스피너 또는 스켈레톤 UI 추가

---

## 재검증 요청 범위 (라운드 3)

1. **`parameters.definitions` 언래핑 수정 후**: `bookprint.py`의 4곳 수정 확인
2. **전체 주문 워크플로우 재실행**: 충전금 확인 → 책 생성 → 사진 업로드 → 템플릿 선택 → 표지 → 내지 24p → 최종화 → 견적 → 주문
3. **`books.py:328` 수정 확인**: 이미지 재생성 후 실제 파일 존재 여부
4. **테스트 실행**: 기존 259개 + 신규 테스트 전체 통과 확인
