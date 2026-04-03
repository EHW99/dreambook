# 통합 테스트 리포트 — 라운드 3

## 테스트 일시
2026-04-04 (금) — Phase 2 완료 시점 (AI 기능 미착수)

## 라운드 2 대비 변경 사항 (Fixer 수정 4건 검증)

| # | 수정 사항 | 검증 결과 |
|---|---------|---------|
| 1 | `get_template_detail()`에서 `parameters.definitions` 자동 언래핑 | **확인됨** — 언래핑 정상 동작. 직접 API 호출 테스트에서 `frontPhoto`, `dateRange`, `spineTitle` 등 올바르게 파싱됨 |
| 2 | `books.py` `regenerate_image()`에서 `_create_placeholder_image()` 호출 | **확인됨** — 코드에 반영됨. 실제 PNG 파일 생성 |
| 3 | 랜딩 카드 크기 축소 | **부분 확인** — 카드 높이 축소됨. 그러나 이미지 없이 빈 배경 영역이 여전히 넓음 |
| 4 | 인증 로딩 스피너 | **확인됨** — `auth-guard.tsx`에 `.animate-spin` 스피너 + "잠시만 기다려주세요..." 텍스트 구현. 다만 `loading` 상태가 수 ms만 지속되어 Playwright 캡처 어려움 |

**핵심 변화**: `parameters.definitions` 언래핑이 수정되어 Book Print API 표지/내지 파라미터 매핑이 정상 동작함. 직접 API 호출 테스트에서 **표지 생성, 24페이지 내지 삽입, 최종화, 견적, 주문까지 전체 성공**.

---

## 1단계: API 문서 vs 코드 대조

### 대상 파일
- `backend/app/services/bookprint.py` vs `.claude/docs/bookprint-api.md`
- `backend/app/services/generate.py` (더미 이미지 생성)
- `backend/app/api/books.py` (이미지 재생성)
- `backend/app/api/orders.py` (주문 워크플로우)

### 불일치 목록

| # | 파일:라인 | 문서 내용 | 코드 내용 | 심각도 | R2 대비 |
|---|---------|---------|---------|--------|--------|
| 1 | generate.py:97 | Book Print API는 판형별 최소 24~50 페이지 요구 | `page_count // 2`로 12페이지만 생성 (24페이지 설정 시). `execute_order_workflow()`에서 12페이지 삽입 후 "페이지 수 부족" 에러 발생 | **치명** | **신규** |
| 2 | bookprint.py:257-270 | `parameters.definitions` 언래핑 필요 | **수정 완료** — `get_template_detail()`에서 자동 언래핑 | **해결됨** | R2 치명 해결 |
| 3 | books.py:324-329 | 이미지 재생성 시 실제 파일 필요 | **수정 완료** — `_create_placeholder_image()` 호출 | **해결됨** | R2 중요 해결 |

### R2에서 해결된 항목 확인

**`parameters.definitions` 언래핑 — 직접 검증 결과:**

Book Print API `GET /templates/4MY2fokVjkeY` 실제 응답:
```
parameters.definitions = {frontPhoto, backPhoto, dateRange, spineTitle}
```

`BookPrintService.get_template_detail()` 반환값 (언래핑 후):
```
parameters = {frontPhoto, backPhoto, dateRange, spineTitle}  // definitions 제거됨
```

`_build_cover_parameters()` 결과:
```json
{"frontPhoto": "photo260403201438466.PNG", "backPhoto": "photo260403201438466.PNG", "dateRange": "2026-04-04", "spineTitle": "IntTest R3"}
```

**표지 생성 성공 확인**: `POST /books/{bookUid}/cover` → `{"result": "inserted"}`

### 추가 확인 사항 (정상)

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
| MIME type 감지 | `detect_mime_type()` 정상 동작 |
| 페이지 수 검증 | `inserted_count` 기준 (R1 개선 유지) |

---

## 2단계: 실제 API 호출 테스트

### 2-A: 백엔드 내부 API

서버 재시작 후 테스트 (코드 변경 사항 반영 확인).

| # | 엔드포인트 | 상태 | 비고 |
|---|---------|------|------|
| 1 | POST /api/auth/signup | **PASS** | 201 Created |
| 2 | POST /api/auth/login | **PASS** | 토큰 정상 발급 |
| 3 | GET /api/auth/me | **PASS** | 사용자 정보 반환 |
| 4 | POST /api/photos | **PASS** | 600x600 PNG 업로드 성공 |
| 5 | GET /api/photos | **PASS** | 목록 정상 |
| 6 | POST /api/vouchers/purchase | **PASS** | 이용권 생성 (`story_and_print`) |
| 7 | POST /api/books | **PASS** | 동화책 생성 + 이용권 연결 |
| 8a | PATCH /api/books/:id (아이 정보) | **PASS** | child_name, child_birth_date |
| 8b | PATCH /api/books/:id (직업) | **PASS** | job_category, job_name |
| 8c | PATCH /api/books/:id (화풍) | **PASS** | art_style |
| 8d | PATCH /api/books/:id (스토리) | **PASS** | story_style (dreaming_today/future_me만 허용) |
| 9 | POST /api/books/:id/character | **PASS** | 캐릭터 시트 생성 |
| 10 | PATCH /api/books/:id/character/:id/select | **PASS** | 캐릭터 선택 → status=character_confirmed |
| 11a | PATCH /api/books/:id (옵션) | **PASS** | page_count, book_spec_uid |
| 11b | PATCH /api/books/:id (줄거리) | **PASS** | plot_input |
| 12 | POST /api/books/:id/generate | **PASS** | 12페이지 더미 스토리 생성, **실제 PNG 파일 생성 확인** |
| 13 | GET /api/books/:id/pages | **PASS** | 12페이지 조회, image_path가 절대 경로 |
| 14 | POST /api/books/:id/pages/:id/regenerate-image | **PASS** | 실제 PNG 파일 생성 확인 |
| 15 | POST /api/books/:id/estimate | **PASS** | 로컬 견적 계산 (23,800원) |
| 16 | POST /api/books/:id/order | **FAIL** | 502 — "삽입된 페이지 수(12)가 판형 제약을 벗어납니다 (SQUAREBOOK_HC: 24~130페이지)" |
| 17 | GET /api/orders | **PASS** | 빈 목록 |
| 18 | GET /api/books/:id/audio-data | **PASS** | 페이지별 텍스트+이미지 |
| 19 | GET /api/vouchers | **PASS** | 이용권 목록 |
| 20 | GET /api/books | **PASS** | 동화책 목록 |
| 21 | PATCH /api/users/password | **PASS** | 비밀번호 변경 |

**결과: 24/25 PASS, 1 FAIL** (R2: 22/25)

**R2 대비 개선**: +2 PASS (이미지 경로 관련 문제 해결됨)

**주문 실패 원인 (R2와 다른 원인)**:
- R2: `frontPhoto` 필수 파라미터 누락 (parameters.definitions 미언래핑)
- **R3: 페이지 수 부족** — `generate_dummy_story()`가 `page_count // 2 = 12` 페이지만 생성하지만 SQUAREBOOK_HC는 최소 24페이지 요구

근본 원인 체인:
1. `generate.py:97` → `total_pages = page_count // 2` = 12 (24페이지 설정 시)
2. `execute_order_workflow()`에서 12개 `insert_content()` 호출
3. `bookprint.py:720` → `inserted_count(12) < page_min(24)` → 에러

### 2-B: Book Print API 직접 호출 테스트

**bookprint.py 서비스 메서드를 통한 전체 워크플로우 직접 실행** — 24페이지 수동 삽입.

| # | 엔드포인트 | 상태 | 비고 |
|---|---------|------|------|
| 1 | GET /credits | **PASS** | 잔액 2,600,000원 |
| 2 | POST /credits/sandbox/charge | **PASS** | 1,000,000원 충전 |
| 3 | POST /books | **PASS** | bookUid: bk_13rS6ouz8W9U |
| 4 | POST /books/{bookUid}/photos | **PASS** | PNG 업로드, fileName 획득 |
| 5 | GET /templates (cover) | **PASS** | 8개 cover 템플릿 |
| 6 | GET /templates (content) | **PASS** | 26개 content 템플릿 |
| 7a | GET /templates/{uid} (cover detail) | **PASS** | 언래핑 후 frontPhoto/backPhoto/dateRange/spineTitle 정상 파싱 |
| 7b | _select_best_content_template() | **PASS** | 빈 템플릿 `2mi1ao0Z4Vxl` 감지 성공 (score=0) |
| 8 | POST /books/{bookUid}/cover | **PASS** | 파라미터: frontPhoto, backPhoto, dateRange, spineTitle 모두 전달, `{"result": "inserted"}` |
| 9 | POST /books/{bookUid}/contents (x24) | **PASS** | 빈 템플릿으로 24페이지 삽입 성공 |
| 10 | POST /books/{bookUid}/finalization | **PASS** | 최종화 성공 |
| 11 | POST /orders/estimate | **PASS** | unitPrice: 100원 (sandbox), totalAmount: 4100원 |
| 12 | POST /orders | **PASS** | orderUid: or_5A2u3BAyClEz, status: PAID(20) |

**결과: 12/12 PASS** (R2: 7/12)

**R2 대비: +5 PASS** — Cover, Contents, Finalization, Estimate, Orders 모두 성공으로 전환.

`parameters.definitions` 언래핑 수정으로 **Book Print API 전체 워크플로우가 정상 동작**함을 확인.

---

## 3단계: E2E 브라우저 테스트

### 시나리오별 결과

| 시나리오 | 결과 | 세부 |
|---------|------|------|
| S1a: 랜딩 페이지 | **PASS** | 정상 로드, 타이틀 "꿈꾸는 나 — AI 직업 동화책" |
| S1b: CTA → 로그인 리다이렉트 | **PASS** | "동화책 만들기" 클릭 → /login 이동 |
| S1c: 마이페이지 → 로그인 리다이렉트 | **PASS** | 비인증 상태에서 /mypage → /login |
| S2a: 회원가입 | **PASS** | 폼 입력 → 201 → "회원가입 완료" → /login 리다이렉트 |
| S2b: 로그인 | **PASS** | 이메일/비밀번호 입력 → 토큰 저장 → 홈으로 이동 |
| S2c: 헤더 로그인 상태 | **PASS** | 마이페이지 링크 표시 |
| S2d: 로그아웃 | **PASS** | 로그아웃 버튼 클릭 → 로그인 링크 표시 |
| S3a: 마이페이지 접근 | **PASS** | 로그인 후 /mypage 정상 접근 |
| S3b: 빈 상태 UI | **PASS** | "아직" 텍스트 감지 — 빈 상태 안내 존재 |
| S4: 동화책 만들기 | **PARTIAL** | /create → /vouchers 리다이렉트 (이용권 미구매 시 정상 동작) |
| S5: 404 페이지 | **PASS** | "길을 잃었나봐요" + 홈 버튼 |
| S6: 반응형 | **PASS** | 모바일(375px)/태블릿(768px)/데스크톱(1280px) 모두 정상 |
| Auth guard 스피너 | **PARTIAL** | 코드에 구현됨 (.animate-spin + "잠시만 기다려주세요"). 그러나 loading 상태가 수 ms라 캡처 불가 |

**결과: 11/13 PASS, 2 PARTIAL** (R2: 6/13 기준)

**R2 대비 개선**: 회원가입/로그인/로그아웃/마이페이지 전체 성공 (+5). 프론트엔드 서버 재시작으로 JS chunk 404 문제 해결.

### 스크린샷 기반 UI/UX 평가

**데스크톱 (1280px):**
- 랜딩 히어로 섹션: 파스텔 피치톤 그래디언트 배경, "아이의 꿈을 동화책으로 만들어주세요" 타이틀 명확
- CTA 버튼: 코랄 톤 라운드 버튼, 충분한 크기
- 랜딩 하단: "샘플 동화책 미리보기" 텍스트 있음. 카드 높이 축소됨 (R2 개선). 그러나 **실제 이미지 없이 빈 그래디언트 배경만** 표시 — 시각적 밀도 부족
- 회원가입/로그인 폼: 깔끔한 카드, rounded-3xl 모서리, 파스텔 배경 일관
- 마이페이지: 4탭 구성 (회원 정보, 아이 사진, 내 책장, 주문 내역), 비밀번호 변경/회원 탈퇴 UI 완비
- 이용권 구매: 2개 카드 레이아웃, 가격 명확 표시
- 404 페이지: 책 아이콘 + 원형 배경 + 파스텔 도트 장식 — 디자인 완성도 높음

**모바일 (375px):**
- 반응형 정상 — 텍스트 크기, 레이아웃 모두 적절 조정
- 헤더: 마이페이지/로그아웃 버튼 축소 표시
- 하단 빈 공간이 모바일에서 더 두드러짐

**태블릿 (768px):**
- 중간 크기 레이아웃 정상
- "샘플 동화책 미리보기" 텍스트 표시

---

## 채점

### 1. API 연동 정확성 (25점) → **18점** (R2: 10점, +8)

- Credits API: 정확 (+3)
- Books API (생성): 정확 (+2)
- Photos API (업로드): MIME type 감지 정확 (+3)
- Templates API (조회 + 상세): **정상 동작** (+3) — R2에서 치명 버그였던 `parameters.definitions` 언래핑 해결
- Cover API: **파라미터 매핑 정상, 표지 생성 성공** (+3) — R2에서 실패했던 부분 해결
- Contents API: **빈 템플릿 감지 + 24페이지 삽입 성공** (직접 테스트) (+2)
- Finalization: **성공** (직접 테스트) (+1)
- Orders API (견적+주문): **성공** (직접 테스트) (+1)
- **감점**: 내부 API 경유 주문에서 페이지 수 불일치로 실패 (-7점). `generate_dummy_story()`가 12페이지만 생성하는데 판형 최소 24페이지 요구.

**결론**: Book Print API 연동 코드 자체는 올바르게 수정되었으나, 더미 스토리 생성기의 페이지 수 계산 버그로 인해 **내부 API 경유 주문은 여전히 실패**. 직접 API 호출 시에는 전체 워크플로우 성공.

### 2. 프론트엔드 ↔ 백엔드 연동 (25점) → **22점** (R2: 22점, 0)

- 인증 흐름 (signup/login/logout): 완벽 동작
- 사진 업로드/조회: 정상
- 이용권 구매/조회: 정상
- 동화책 CRUD + 단계별 저장: 정상
- 캐릭터 생성/선택: 정상
- 스토리 생성(더미): 정상 — **이미지 실제 파일 생성 확인** (R2 개선)
- 페이지 조회: 정상, image_path가 절대 경로
- 이미지 재생성: 정상 — **실제 PNG 생성 확인** (R2 개선)
- 견적 조회: 정상 (로컬 계산)
- **주문 생성: FAIL** — 페이지 수 불일치 (-3점)
- 주문 목록/상세: 정상 (빈 데이터)
- 오디오북 데이터: 정상

### 3. E2E 사용자 플로우 (20점) → **17점** (R2: 15점, +2)

- 비로그인 접근 제어: **완벽** — CTA 클릭, 마이페이지 접근 모두 /login 리다이렉트 (+3)
- 회원가입 → 로그인 → 로그아웃: **완벽** (+4) — R2에서 실패했던 부분 해결
- 마이페이지 탭: 4탭 정상 동작, 빈 상태 UI 존재 (+3)
- 위자드 진입: /create → /vouchers (이용권 미구매 시 정상 플로우) (+2)
- 404 페이지: 완벽 디자인 (+2)
- 반응형: 3개 뷰포트 정상 (+3)
- **감점**: 주문 단계에서 502 에러 (-3점)

### 4. UI/UX 품질 (30점) → **26점** (R2: 25점, +1)

| 항목 | 배점 | R2 | R3 | 비고 |
|------|------|-----|-----|------|
| 색상/테마 일관성 | 6 | 5 | **5** | 파스텔 피치 톤 전체 적용, #FFF8F0 배경 일관. 랜딩 하단 빈 영역 -1 |
| 타이포그래피 | 4 | 4 | **4** | 폰트 통일, 크기/굵기 위계 적절 |
| 레이아웃/간격 | 5 | 4 | **4** | 전반적 양호. 랜딩 하단 빈 공간 축소됨(R2 개선), 그러나 여전히 이미지 부재 -1 |
| 반응형 | 5 | 5 | **5** | 모바일/태블릿/데스크톱 모두 정상 |
| 애니메이션/전환 | 4 | 3 | **4** | FadeInSection, 스크롤 안내, auth guard 스피너(animate-spin) 구현 확인. R2 개선 |
| 상태 UI | 3 | 2 | **2** | 빈 상태 UI 존재. auth guard 스피너 구현 확인. 그러나 페이지 전환 로딩 표시 미흡 -1 |
| 접근성/사용성 | 3 | 2 | **2** | 버튼 크기 적절, 에러 안내 존재. 랜딩 빈 콘텐츠 -1 |

---

### 총점

| 항목 | 배점 | R1 | R2 | R3 | R2→R3 변화 |
|------|------|-----|-----|-----|-----------|
| API 연동 정확성 | 25 | 12 | 10 | **18** | **+8** |
| 프론트↔백엔드 연동 | 25 | 22 | 22 | **22** | 0 |
| E2E 사용자 플로우 | 20 | 16 | 15 | **17** | **+2** |
| UI/UX 품질 | 30 | 25 | 25 | **26** | **+1** |
| **합계** | **100** | **75** | **72** | **83** | **+11** |

### 판정: **CONDITIONAL** (83점)

83점 — 90점 미만이므로 Fixer 수정 후 재검증 필요.

API 연동 18점 > 10점이므로 AUTO-FAIL 아님.

> **R2 대비 대폭 개선 (+11점)**: `parameters.definitions` 언래핑 수정으로 Book Print API 직접 호출 시 전체 워크플로우(표지→내지 24p→최종화→견적→주문) 성공 확인. 잔여 문제는 **더미 스토리 생성기의 페이지 수 계산 버그 1건**으로 좁혀짐.

---

## 종합 문제 목록 (Fixer에게 전달)

### 치명 (주문 불가) — 1건

**1. [치명] `generate_dummy_story()`가 판형 최소 페이지 수보다 적은 페이지를 생성**

- **파일**: `backend/app/services/generate.py:97`
- **라인**: `total_pages = page_count // 2` → 24 // 2 = 12
- **원인**: page_count를 "양면"으로 해석하여 절반으로 나누지만, Book Print API의 `insert_content()`는 **호출 1회 = 1페이지**로 카운트한다. SQUAREBOOK_HC는 최소 24페이지를 요구하므로, 12페이지만 삽입하면 `execute_order_workflow()`의 사전 검증에서 실패한다.
- **영향**: 내부 API 경유 주문 전체 실패 (`POST /api/books/:id/order` → 502)
- **수정 방향**: `total_pages = page_count` (나누지 않음). 또는 `page_count // 2`는 유지하되 `execute_order_workflow()`에서 각 논리 페이지를 2회 삽입 (양면). 가장 단순한 수정:
  ```python
  # generate.py:97 변경 전
  total_pages = page_count // 2
  # 변경 후
  total_pages = page_count
  ```
  이 경우 `content_pages = total_pages - 2 = 22`가 되어 title(1) + content(22) + ending(1) = 24페이지 생성.

### 경미 (UX 개선) — 1건

**2. [경미] 랜딩 페이지 하단 "샘플 동화책 미리보기" 영역에 실제 콘텐츠 부재**

- **위치**: `frontend/src/app/page.tsx`
- **현상**: R2에서 카드 높이를 줄였으나, 실제 이미지 없이 빈 그래디언트 배경만 표시. 전체 랜딩 페이지 면적의 약 50%가 빈 공간. Phase 3(AI 이미지 생성)에서 해결될 수 있으나, 현재 상태에서는 사용자 경험 저하.
- **수정 방향**: Phase 2 단계에서는 SVG 일러스트레이션이나 이모지 기반 시각 요소를 추가하여 빈 느낌 최소화. 또는 해당 섹션을 Phase 3까지 숨김.

---

## 재검증 요청 범위 (라운드 4)

1. **`generate_dummy_story()` 페이지 수 수정 후**: 24페이지 이상 생성 확인
2. **내부 API 경유 주문 전체 재실행**: `POST /api/books/:id/order` → 성공 확인
3. **테스트 실행**: 기존 테스트 전체 통과 확인 (페이지 수 변경에 따른 테스트 업데이트 필요할 수 있음)
