# 통합 테스트 리포트

## 테스트 일시
2026-04-04 (금) — Phase 2 완료 시점 (AI 기능 미착수)

---

## 1단계: API 문서 vs 코드 대조

### 대상 파일
- `backend/app/services/bookprint.py` vs `.claude/docs/bookprint-api.md`

### 불일치 목록

| # | 파일:라인 | 문서 내용 | 코드 내용 | 심각도 |
|---|---------|---------|---------|--------|
| 1 | bookprint.py:431-432 | 템플릿 선택 시 파라미터 정의를 확인하여 적합한 템플릿 선택 필요 | `cover_templates[0]`, `content_templates[0]` — 무조건 첫 번째 템플릿 사용. 파라미터 정의 확인 없음 | **치명** |
| 2 | bookprint.py:459-463 | 내지 템플릿별 필수 파라미터가 다름 (year, month, date, diaryText, photo1 등) | `{"text": ..., "photo": ...}` 고정 파라미터명 사용. 어떤 content 템플릿도 `text`와 `photo` 파라미터를 동시에 받지 않음 | **치명** |
| 3 | bookprint.py:444-449 | 표지 템플릿의 필수 파라미터: `frontPhoto`(file), `dateRange`(text), `spineTitle`(text) | `{"title": title}` + `frontPhoto`만 전달. `dateRange`와 `spineTitle` 누락 | **치명** |
| 4 | bookprint.py:197 | 사진 업로드 시 실제 파일의 MIME type 감지 필요 | `"image/png"` 하드코딩. JPEG 파일도 PNG로 전송됨 | **중요** |
| 5 | bookprint.py:424 | 더미 이미지(placeholder)는 실제 파일이 아님 → 업로드 불가 | `placeholder_{filename}` 문자열을 fileName으로 사용 시도 | **치명** |
| 6 | bookprint.py:482-493 | 최종화 전 페이지 수 검증은 `pages_data` 기준이지만, 실제로는 Book Print에 삽입된 페이지 수가 기준 | 내지 삽입 실패 시에도 페이지 수 체크는 로컬 데이터 기준 | **경미** |

### 추가 확인 사항 (정상)

| 항목 | 결과 |
|------|------|
| URL 경로 | 모든 엔드포인트 경로 문서와 일치 |
| HTTP 메서드 | 모두 정확 |
| Content-Type (cover/contents) | multipart/form-data로 올바르게 전송 (files 파라미터 사용) |
| 인증 헤더 | `Authorization: Bearer {key}` 정확 |
| 응답 파싱 (templates) | `data.get("templates", data.get("items", []))` — 실제 응답 키 `templates`와 일치 |
| Credits API | 경로, 파라미터 모두 정확 |
| Orders API | 경로, 파라미터 모두 정확 |
| 429 Rate Limit 처리 | Retry-After 기반 재시도 구현됨 |
| 에러 코드 처리 | 400/401/402/429 등 문서와 일치 |

---

## 2단계: 실제 API 호출 테스트

### 2-A: 백엔드 내부 API (27/28 PASS)

| # | 엔드포인트 | 상태 | 비고 |
|---|---------|------|------|
| 1 | POST /api/auth/signup | **PASS** | 201 Created |
| 2 | POST /api/auth/login | **PASS** | 토큰 정상 발급 |
| 3 | GET /api/auth/me | **PASS** | 사용자 정보 반환 |
| 4 | POST /api/photos | **PASS** | 600x600 PNG 업로드 성공 |
| 5 | GET /api/photos | **PASS** | 목록 정상 |
| 6 | POST /api/vouchers/purchase | **PASS** | 이용권 생성 |
| 7 | POST /api/books | **PASS** | 동화책 생성 + 이용권 연결 |
| 8a | PATCH /api/books/:id (아이 정보) | **PASS** | step 1 |
| 8b | PATCH /api/books/:id (직업) | **PASS** | step 2 |
| 8c | PATCH /api/books/:id (스타일) | **PASS** | step 3 |
| 8d | PATCH /api/books/:id (그림체) | **PASS** | step 4 |
| 9 | POST /api/books/:id/character | **PASS** | 더미 캐릭터 생성 |
| 10 | PATCH /api/books/:id/character/:charId/select | **PASS** | 캐릭터 선택 |
| 11 | PATCH /api/books/:id (step 5) | **PASS** | 캐릭터 확정 후 단계 이동 |
| 12a | PATCH /api/books/:id (옵션) | **PASS** | step 6 |
| 12b | PATCH /api/books/:id (줄거리) | **PASS** | step 7 |
| 13 | POST /api/books/:id/generate | **PASS** | 12페이지 더미 스토리 생성, 상태 editing 전환 |
| 14 | GET /api/books/:id/pages | **PASS** | 12페이지 조회 |
| 15 | PATCH /api/books/:id/pages/:pageId | **PASS** | 텍스트 수정 |
| 16 | POST /api/books/:id/estimate | **PASS** | 로컬 견적 계산 (23,800원) |
| 17 | POST /api/books/:id/order | **FAIL** | 502 — Book Print API 표지 템플릿 필수 파라미터 `frontPhoto` 누락 (더미 이미지 경로가 실제 파일이 아님) |
| 18 | GET /api/orders | **PASS** | 빈 목록 |
| 19 | GET /api/books/:id/audio-data | **PASS** | 페이지별 텍스트+이미지 |
| 20 | GET /api/vouchers | **PASS** | 이용권 목록 |
| 21 | GET /api/books | **PASS** | 동화책 목록 |
| 22 | GET /api/books/:id | **PASS** | 상세 조회 |
| 23 | GET /api/books/:id/characters | **PASS** | 캐릭터 갤러리 |
| 24 | PATCH /api/users/password | **PASS** | 비밀번호 변경 |

**주문 실패 원인 분석:**
- `execute_order_workflow`가 Book Print API를 호출할 때, 더미 이미지 경로(`/placeholder/...`)는 실제 파일이 아니므로 업로드 실패
- 업로드 실패 시 `placeholder_{filename}`을 fileName으로 사용하지만, 이것은 Book Print API에 존재하지 않는 파일
- 표지 템플릿의 필수 파라미터 `frontPhoto`에 해당 placeholder를 전달하면 Book Print API가 Validation Error 반환
- **근본 원인**: Phase 2의 더미 이미지가 실제 파일 시스템에 존재하지 않아 Book Print API 워크플로우가 전면 실패

### 2-B: Book Print API 직접 호출 테스트

| # | 엔드포인트 | 상태 | 비고 |
|---|---------|------|------|
| 1 | GET /credits | **PASS** | 잔액 조회 성공 |
| 2 | POST /credits/sandbox/charge | **PASS** | 100만원 충전 성공 |
| 3 | POST /books | **PASS** | bookUid 획득 |
| 4 | POST /books/{bookUid}/photos | **PASS** | 실제 PNG 업로드 성공 |
| 5 | GET /templates (cover) | **PASS** | 8개 cover 템플릿 조회. 응답 키: `templates` |
| 6 | GET /templates (content) | **PASS** | 10+ content 템플릿 조회 |
| 7 | GET /templates/{templateUid} | **PASS** | 파라미터 정의 확인 완료 |
| 8 | POST /books/{bookUid}/cover | **PASS** | multipart/form-data + 필수 파라미터 전달 시 성공 |
| 9 | POST /books/{bookUid}/contents | **FAIL** | 415 (httpx data= 사용 시) / 400 (파라미터 불일치) — 템플릿 필수 파라미터 불일치 |
| 10 | POST /books/{bookUid}/finalization | **FAIL** | 내지가 없어 "epages 데이터가 없음" 에러 |
| 11 | POST /orders/estimate | **FAIL** | 책이 FINALIZED 상태 아님 |
| 12 | POST /orders | **FAIL** | 동일 |

**핵심 발견:**
- Cover/Contents API는 반드시 `multipart/form-data`로 전송해야 함 (httpx `files=` 파라미터) — `bookprint.py`는 이미 올바르게 구현
- **모든 content 템플릿의 필수 파라미터가 `text`/`photo`가 아닌 `year`, `month`, `date`, `diaryText`, `photo1` 등 템플릿별 고유 파라미터** — `bookprint.py`의 `execute_order_workflow`가 사용하는 `{"text": ..., "photo": ...}` 파라미터와 완전 불일치
- Cover 템플릿도 `frontPhoto`(필수), `dateRange`(필수), `spineTitle`(필수) 등 추가 필수 파라미터 존재

---

## 3단계: E2E 브라우저 테스트

### 시나리오별 결과

| 시나리오 | 결과 | 세부 |
|---------|------|------|
| S1: 비로그인 접근 | **PASS** (4/4) | 랜딩 표시, CTA→로그인 리다이렉트, 마이페이지→로그인 리다이렉트 |
| S2: 회원가입→로그인→로그아웃 | **PASS** (6/6) | 가입→로그인→헤더 버튼 표시→로그아웃 모두 정상 |
| S3: 마이페이지 | **PASS** (5/5) | 4개 탭(회원정보/사진/책장/주문) 모두 접근 가능, 빈 상태 UI 표시 |
| S4: 동화책 만들기 위자드 | **PARTIAL** (2/4) | 이용권 구매 성공, 위자드 1단계 진입 확인. 그러나 URL 체크 타이밍 문제로 테스트 스크립트가 FAIL 기록 (실제로는 create 페이지 정상 진입) |
| S5: 내 책장 + 주문 관리 | **PASS** (1/1) | 마이페이지 접근 확인 (빈 상태) |
| S6: 에러/엣지 케이스 | **PASS** (1/1) | 404 페이지 정상 표시 ("길을 잃었나봐요" + 홈으로 버튼) |
| 반응형 | **PASS** (4/4) | 모바일(375px)/태블릿(768px)/데스크톱(1280px) 모두 렌더링 정상 |

### 스크린샷 기반 UI/UX 평가

**데스크톱 (1280px):**
- 랜딩 페이지: 히어로 섹션 표시, CTA 버튼 명확, 하단 섹션은 콘텐츠 비어 있음 (샘플 동화책 미리보기/스타일 갤러리 영역)
- 회원가입/로그인: 깔끔한 폼 카드, 파스텔 톤 일관
- 마이페이지: 탭 구성 명확, 빈 상태 UI에 일러스트 아이콘+안내 문구+CTA 버튼 제공
- 404 페이지: 따뜻한 일러스트(책 아이콘)+원형 배경+파스텔 도트 장식, "길을 잃었나봐요" 문구
- 위자드: 9단계 진행바 명확, 정보 입력 폼 구성 양호

**모바일 (375px):**
- 랜딩 페이지: 반응형 정상 적용, 텍스트 가독성 유지, 햄버거 메뉴 표시
- 전반적으로 모바일 레이아웃 양호

**태블릿 (768px):**
- 중간 크기 정상 표시, 레이아웃 적절히 조정됨

### 콘솔 에러
- 1건: `Failed to load resource: the server responded with a status of 404 (Not Found)` — 리소스 로딩 실패 (경미)

---

## 채점

### 1. API 연동 정확성 (25점) → **12점**

- Credits API: 정확 (+)
- Books API (생성): 정확 (+)
- Photos API (업로드): 정확이지만 MIME type 하드코딩 (-)
- Templates API (조회): 파싱 정확, 그러나 **템플릿 선택 로직 없음** — 첫 번째 템플릿 무조건 사용 (--)
- Cover API: multipart 전송 정확, 그러나 **필수 파라미터 누락** (frontPhoto 외 dateRange, spineTitle) (--)
- Contents API: multipart 전송 정확, 그러나 **파라미터명 완전 불일치** — 어떤 템플릿과도 매칭 불가 (---)
- Finalization/Orders: 위 단계 실패로 실제 동작 불가 (--)
- **결론**: 개별 API 호출 메커니즘은 올바르나, 워크플로우 전체가 템플릿 파라미터 불일치로 실패. 주문 불가.

### 2. 프론트엔드 ↔ 백엔드 연동 (25점) → **22점**

- 인증 흐름 (signup/login/logout/refresh): 완벽 동작
- 사진 업로드/조회/삭제: 정상
- 이용권 구매/조회: 정상
- 동화책 CRUD + 단계별 저장: 정상
- 캐릭터 생성/선택: 정상
- 스토리 생성(더미): 정상
- 페이지 조회/편집: 정상
- 견적 조회: 정상 (로컬 계산 폴백)
- **주문 생성: FAIL** — Book Print API 연동 실패
- 주문 목록/상세: 정상 (빈 데이터)
- 오디오북 데이터: 정상
- **감점 이유**: 주문 생성 실패 (-3점)

### 3. E2E 사용자 플로우 (20점) → **16점**

- 비로그인 접근 제어: 완벽
- 회원가입 → 로그인 → 로그아웃: 완벽
- 마이페이지 탭 전환: 완벽
- 빈 상태 UI: 완벽
- 위자드 진입: 정상
- 404 페이지: 완벽
- 반응형: 정상
- **감점**: 위자드 전체 플로우 (정보 입력~주문)를 브라우저에서 끝까지 완주하지 못함 — 주문 단계에서 502 에러 예상 (-4점)

### 4. UI/UX 품질 (30점) → **25점**

| 항목 | 배점 | 점수 | 비고 |
|------|------|------|------|
| 색상/테마 일관성 | 6 | **5** | 파스텔 톤 팔레트 전체 적용, 배경 #FFF8F0 일관. 랜딩 페이지 하단 섹션 비어 있어 -1 |
| 타이포그래피 | 4 | **4** | 폰트 통일, 크기/굵기 위계 적절 |
| 레이아웃/간격 | 5 | **4** | 전반적으로 양호. 랜딩 페이지 하단 빈 공간 과다 -1 |
| 반응형 | 5 | **4** | 모바일/태블릿/데스크톱 모두 동작. 모바일 햄버거 메뉴 존재 확인. 콘텐츠 영역 빈 곳 있어 -1 |
| 애니메이션/전환 | 4 | **3** | Framer Motion 적용 확인 (FadeInSection). 페이지 전환 부드러움. 로딩 애니메이션 미확인 -1 |
| 상태 UI | 3 | **3** | 로딩/에러/빈 상태 모두 디자인과 일관. 빈 상태 아이콘+문구+CTA 완비 |
| 접근성/사용성 | 3 | **2** | 버튼 크기 적절, 에러 안내 존재. 랜딩 페이지의 빈 콘텐츠 섹션이 사용자 경험 저하 -1 |

---

### 총점

| 항목 | 배점 | 점수 |
|------|------|------|
| API 연동 정확성 | 25 | **12** |
| 프론트↔백엔드 연동 | 25 | **22** |
| E2E 사용자 플로우 | 20 | **16** |
| UI/UX 품질 | 30 | **25** |
| **합계** | **100** | **75** |

### 판정: **CONDITIONAL**

75점 — 90점 미만이므로 Fixer 수정 후 재검증 필요.
API 연동 12점 > 10점이므로 AUTO-FAIL은 아님.

---

## 종합 문제 목록 (Fixer에게 전달)

### 치명 (주문 불가) — 3건

**1. [치명] 내지 템플릿 파라미터 불일치 — 주문 워크플로우 전면 실패**
- **파일**: `backend/app/services/bookprint.py:459-463`
- **원인**: `execute_order_workflow`에서 내지 삽입 시 `{"text": ..., "photo": ...}` 파라미터를 사용하지만, Book Print API의 모든 content 템플릿은 `text`/`photo` 파라미터를 받지 않음. 실제 필수 파라미터는 `year`, `month`, `date`, `diaryText`, `photo1` 등 템플릿별로 다름.
- **수정 방향**: 
  - (A) 동화책 전용 content 템플릿을 찾거나, 최소 파라미터 템플릿(`2mi1ao0Z4Vxl` — 빈 템플릿, 필수 파라미터 없음)을 사용하거나
  - (B) 템플릿 상세 조회(`GET /templates/{uid}`)로 파라미터 정의를 확인한 후, 가장 적합한 템플릿을 선택하고 필수 파라미터를 동적으로 매핑
  - (C) 사진+텍스트만 있는 단순 템플릿(`79LHkH32MLH1` — photo(file) + dayLabel(text))을 선택하여 파라미터 매핑

**2. [치명] 표지 템플릿 필수 파라미터 누락**
- **파일**: `backend/app/services/bookprint.py:444-449`
- **원인**: 표지 생성 시 `{"title": title}` + `frontPhoto`만 전달하지만, 선택된 cover 템플릿(`4MY2fokVjkeY`)은 `frontPhoto`(file/필수), `dateRange`(text/필수), `spineTitle`(text/필수) 모두 필요
- **수정 방향**: 
  - 표지 템플릿의 파라미터 정의를 조회하여 필수 파라미터를 모두 채움
  - `dateRange`에 생성일, `spineTitle`에 책 제목 매핑

**3. [치명] 더미 이미지 경로가 실제 파일이 아님 — 사진 업로드 실패**
- **파일**: `backend/app/services/bookprint.py:416-425`, `backend/app/services/generate.py` (더미 이미지 생성 부분)
- **원인**: Phase 2 더미 이미지 경로(`/placeholder/illustration_*.png`)는 파일 시스템에 존재하지 않음. `os.path.exists()` 체크에서 False → 업로드 건너뜀 → placeholder 문자열을 fileName으로 사용 → Book Print API에서 해당 파일 찾을 수 없어 에러
- **수정 방향**: 
  - 더미 이미지 생성 시 실제 파일을 생성하여 `uploads/` 디렉토리에 저장
  - 또는 주문 워크플로우에서 이미지가 없는 경우 기본 placeholder 이미지를 동적 생성하여 업로드

### 중요 (기능 불완전) — 2건

**4. [중요] 템플릿 선택 로직 부재 — 첫 번째 템플릿 무조건 사용**
- **파일**: `backend/app/services/bookprint.py:431-432`
- **원인**: `cover_templates[0]`, `content_templates[0]`로 무조건 첫 번째 템플릿 선택. 해당 템플릿이 동화책 서비스에 적합하지 않을 수 있음 (현재 첫 번째 cover 템플릿은 diary 스타일)
- **수정 방향**: 
  - 템플릿 상세를 조회하여 파라미터가 가장 단순한(또는 가장 적합한) 템플릿 선택
  - 또는 적합한 템플릿 UID를 하드코딩

**5. [중요] 사진 업로드 MIME type 하드코딩**
- **파일**: `backend/app/services/bookprint.py:197`
- **원인**: `content_type: str = "image/png"` 하드코딩. JPEG 이미지도 `image/png`로 전송됨
- **수정 방향**: 파일 확장자 또는 magic bytes 기반으로 실제 MIME type 감지

### 경미 (UX 개선) — 3건

**6. [경미] 랜딩 페이지 하단 섹션 콘텐츠 비어 있음**
- **위치**: 프론트엔드 랜딩 페이지 (`frontend/src/app/page.tsx`)
- **현상**: "샘플 동화책 미리보기" 및 "스타일 갤러리" 섹션 영역은 있지만 실제 콘텐츠(이미지)가 없어 빈 공간이 넓게 표시됨
- **수정 방향**: 더미 이미지라도 배치하거나, Phase 2에서는 해당 섹션을 숨김 처리

**7. [경미] 콘솔 에러 1건 — 리소스 404**
- **현상**: 브라우저 콘솔에서 `Failed to load resource: 404` 에러 1건 발생
- **수정 방향**: 누락된 리소스(이미지/폰트 등) 확인 및 수정

**8. [경미] 페이지 수 사전 검증 위치**
- **파일**: `backend/app/services/bookprint.py:482-493`
- **현상**: 최종화 전 페이지 수 검증이 내지 삽입 후에 수행되지만, Book Print API에 실제로 삽입된 페이지 수와 로컬 `pages_data` 수가 다를 수 있음
- **수정 방향**: 최종화 API 호출 후 에러 응답으로 판단하거나, 내지 삽입 성공 수를 카운트
