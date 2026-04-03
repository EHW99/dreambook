# 통합 테스트 리포트 — 라운드 4

## 테스트 일시
2026-04-04 (금) — 라운드 4 재검증

## 라운드별 점수 추이
| 라운드 | 점수 | 판정 |
|--------|------|------|
| R1 | 75 | CONDITIONAL |
| R2 | 72 | CONDITIONAL |
| R3 | 83 | CONDITIONAL |
| **R4** | **91** | **PASS** |

---

## 1단계: API 문서 vs 코드 대조

### bookprint.py vs bookprint-api.md 대조 결과

| # | 항목 | 문서 | 코드 | 일치 | 비고 |
|---|------|------|------|:----:|------|
| 1 | Base URL | `https://api-sandbox.sweetbook.com/v1` | `settings.BOOKPRINT_BASE_URL` | O | 환경변수에서 로드 |
| 2 | 인증 헤더 | `Authorization: Bearer {API_KEY}` | `Bearer {self.api_key}` | O | |
| 3 | POST /books | JSON body: title, bookSpecUid, creationType | 일치 | O | |
| 4 | POST /books/{uid}/photos | multipart/form-data, field: file | 일치 | O | MIME type 감지 로직 포함 |
| 5 | GET /templates | params: bookSpecUid, templateKind, limit | 일치 | O | |
| 6 | GET /templates/{uid} | parameters.definitions 중첩 구조 | 언래핑 처리 | O | `definitions` 키 언래핑 정상 |
| 7 | POST /books/{uid}/cover | multipart/form-data: templateUid, parameters(JSON) | 일치 | O | |
| 8 | POST /books/{uid}/contents | multipart/form-data + breakBefore query param | 일치 | O | |
| 9 | POST /books/{uid}/finalization | JSON (no body) | 일치 | O | |
| 10 | POST /orders/estimate | JSON: items[{bookUid, quantity}] | 일치 | O | |
| 11 | POST /orders | JSON: items, shipping, externalRef | 일치 | O | |
| 12 | POST /orders/{uid}/cancel | JSON: cancelReason | 일치 | O | |
| 13 | PATCH /orders/{uid}/shipping | JSON: 변경 필드만 | 일치 | O | |
| 14 | GET /credits | 경로 일치 | 일치 | O | |
| 15 | POST /credits/sandbox/charge | JSON: amount, memo | 일치 | O | |
| 16 | 429 Rate Limit 처리 | Retry-After 헤더 기반 재시도 | 최대 2회, 30초 상한 | O | |
| 17 | 응답 파싱 | `data` 키 내 실제 데이터 | `.get("data", {})` | O | |
| 18 | 템플릿 응답 키 | `data.templates` 또는 `data.items` | 양쪽 모두 처리 | O | `data.get("templates", data.get("items", []))` |

### 불일치 목록
**없음.** R3에서 지적된 `total_pages = page_count // 2` 문제가 `total_pages = page_count`로 수정 확인 완료 (generate.py:97).

### 주의: 서버 재시작 필요
R3 수정 후 서버가 재시작되지 않아 `__pycache__` 캐시로 인해 이전 바이트코드가 실행되고 있었음. 서버 재시작 + 캐시 삭제 후 수정 사항이 정상 반영됨. **배포 시 반드시 서버 재시작 필요.**

---

## 2단계: 실제 API 호출 테스트

### 2-A: 백엔드 내부 API (18/18 PASS)

| # | 엔드포인트 | 상태 | 비고 |
|---|---------|:----:|------|
| 1 | POST /api/auth/signup | PASS | 201 Created |
| 2 | POST /api/auth/login | PASS | 200 + JWT 토큰 |
| 3 | POST /api/photos | PASS | 201 (600x600 PNG) |
| 4 | GET /api/photos | PASS | 200 + 1건 |
| 5 | POST /api/vouchers/purchase | PASS | 201 (story_and_print) |
| 6 | POST /api/books | PASS | 201 |
| 7 | PATCH /api/books/:id | PASS | 200 (아이 이름, 직업, 사진 설정) |
| 8 | POST /api/books/:id/character | PASS | 201 |
| 9 | PATCH /api/books/:id/character/:cid/select | PASS | 200 |
| 10 | POST /api/books/:id/generate | PASS | 200 |
| 10a | **페이지 수 검증** | **PASS** | **24페이지 생성 확인 (R3 수정 반영)** |
| 11 | GET /api/books/:id/pages | PASS | 200 |
| 11a | **DB 저장 검증** | **PASS** | **24페이지 DB 저장 확인** |
| 12 | PATCH /api/books/:id/pages/:pid | PASS | 200 (텍스트 수정) |
| 13 | POST /api/books/:id/estimate | PASS | 200 (견적 조회) |
| 14 | **POST /api/books/:id/order** | **PASS** | **200 -- order_uid=or_3CNddMrdu0eg (BookPrint 실제 주문 성공!)** |
| 15 | GET /api/orders | PASS | 200 + 1건 |
| 15a | 주문 존재 확인 | PASS | Count=1 |

**핵심 검증 결과**: R3 수정(`total_pages = page_count`)이 정상 반영되어 24페이지가 생성되고, SQUAREBOOK_HC 최소 페이지 수(24) 요구사항을 충족하여 BookPrint API 주문까지 성공. 이전 라운드의 502 에러 완전 해소.

### 2-B: Book Print API 직접 호출

| # | 엔드포인트 | 상태 | 비고 |
|---|---------|:----:|------|
| 1 | GET /credits | PASS | 잔액 3,593,180원 |
| 2 | POST /credits/sandbox/charge | PASS | 충전 성공 |
| 3 | POST /books | PASS | bookUid 생성 |
| 4 | POST /books/{uid}/photos | PASS | 사진 업로드 성공 |
| 5 | GET /templates (cover) | PASS | 표지 템플릿 조회 |
| 6 | GET /templates (content) | PASS | 내지 템플릿 조회 |
| 7 | GET /templates/{uid} | PASS | 상세 조회 + 파라미터 정의 |
| 8 | POST /books/{uid}/cover | INFO | 빈 파라미터로 호출 시 400 (frontPhoto 필수) -- 코드는 `_build_cover_parameters()`로 정상 매핑 |
| 9 | POST /books/{uid}/contents | INFO | 빈 파라미터로 호출 시 400 (year 필수) -- 코드는 `_build_content_parameters()`로 정상 매핑 |
| 10-12 | finalization/estimate/order | N/A | 8-9 실패로 미도달 (직접 호출 한정) |

**참고**: 직접 호출에서 빈 파라미터로 인한 400 에러는 **예상된 동작**. bookprint.py의 파라미터 빌더가 템플릿 정의에 맞게 자동 매핑하며, **내부 API 경유 테스트(2-A 스텝 14)에서 전체 워크플로우가 성공**했으므로 문제 없음.

---

## 3단계: E2E 브라우저 테스트

### 시나리오별 결과 (12/13 PASS)

| 시나리오 | 테스트 | 결과 | 비고 |
|---------|--------|:----:|------|
| S1: 비로그인 | 랜딩 페이지 렌더링 | PASS | 히어로 섹션 + CTA 정상 |
| S1: 비로그인 | CTA 버튼 존재 | PASS | "동화책 만들기" 버튼 확인 |
| S1: 비로그인 | CTA->로그인 리다이렉트 | PASS | /login으로 이동 |
| S1: 비로그인 | 마이페이지->로그인 리다이렉트 | PASS | 비로그인 접근 차단 |
| S2: 회원가입 | 폼 제출 | PASS | -> /login 이동 |
| S2: 로그인 | 로그인 성공 | PASS | JWT + 홈 이동 |
| S2: 로그인 | 헤더 마이페이지 버튼 | PASS | 로그인 후 표시 |
| S2: 로그인 | 헤더 로그아웃 버튼 | PASS | 로그인 후 표시 |
| S2: 로그아웃 | 로그아웃 후 로그인 버튼 | PASS | 정상 전환 |
| S3: 마이페이지 | 페이지 접근 | PASS | /mypage 정상 |
| S3: 마이페이지 | 탭 UI | PASS | 회원 정보/아이 사진/내 책장/주문 내역 |
| S4: 만들기 | 페이지 접근 | PASS* | /create -> /vouchers (이용권 미보유 시 정상) |
| S6: 에러 | 404 페이지 | PASS | 커스텀 디자인 (책 아이콘 + 홈 링크) |

*S4는 이용권이 없으면 /vouchers로 리다이렉트되는 것이 정상 설계.

### 반응형 검증 (스크린샷 기반)

| 뷰포트 | 랜딩 | 로그인 | 회원가입 | 404 | 결과 |
|--------|:----:|:-----:|:------:|:---:|:----:|
| 모바일 (375px) | O | O | O | O | PASS |
| 태블릿 (768px) | O | - | - | - | PASS |
| 데스크톱 (1280px) | O | O | O | O | PASS |

### 스크린샷 저장 위치
`test/screenshots/` 디렉토리에 13개 캡처 저장 완료.

---

## 채점

### 1. API 연동 정확성 (25점)

**점수: 23/25** (R3: 20 -> R4: 23, +3)

- BookPrint API 문서와 코드 100% 일치 확인 (18개 항목 모두 일치)
- 전체 주문 워크플로우 성공: 책 생성 -> 사진 업로드 -> 표지 -> 내지(24p) -> 최종화 -> 견적 -> 주문 (order_uid 발급)
- 429 Rate Limit, 402 충전금 부족 등 에러 처리 로직 정상
- **감점(-2)**: Idempotency-Key 헤더 미전송 (문서 권장사항이나 필수는 아님)

### 2. 프론트 <-> 백엔드 연동 (25점)

**점수: 24/25** (R3: 22 -> R4: 24, +2)

- 회원가입/로그인/로그아웃 전체 플로우 정상
- JWT 인증 + 보호된 라우트 정상 (마이페이지 비로그인 -> 로그인 리다이렉트)
- 사진 업로드, 이용권 구매, 동화책 생성, 캐릭터, 생성, 편집, 견적, 주문 전체 API 연동 성공
- 주문 생성 시 BookPrint 외부 API 호출까지 end-to-end 성공
- **감점(-1)**: 이용권 구매 후 자동 플로우 이동이 다소 간접적

### 3. E2E 사용자 플로우 (20점)

**점수: 18/20** (R3: 16 -> R4: 18, +2)

- 비로그인 접근 제어 정상
- 회원가입 -> 로그인 -> 로그아웃 전체 사이클 정상
- 마이페이지 4개 탭 정상 접근
- 404 커스텀 페이지 정상 동작
- **감점(-2)**: 동화책 만들기 전체 플로우를 브라우저에서 끝까지 수행하는 E2E 자동화 미완 (API 레벨에서는 전체 성공 확인)

### 4. UI/UX 품질 (30점)

**점수: 26/30** (R3: 25 -> R4: 26, +1)

| 세부 항목 | 배점 | 점수 | 평가 |
|----------|:----:|:----:|------|
| 색상/테마 일관성 | 6 | 6 | 파스텔 피치/핑크 톤 전체 일관 적용 |
| 타이포그래피 | 4 | 4 | display 폰트 + 본문 위계 적절 |
| 레이아웃/간격 | 5 | 4 | 양호. 랜딩 하단 샘플 영역 빈 느낌 잔존(-1) |
| 반응형 | 5 | 4 | 3개 뷰포트 정상. 모바일 랜딩 빈 영역 과다(-1) |
| 애니메이션/전환 | 4 | 3 | framer-motion 적용 확인. 헤드리스 제한(-1) |
| 상태 UI | 3 | 3 | 로딩/에러/빈 상태 디자인 적용 |
| 접근성/사용성 | 3 | 2 | 포커스 시각 피드백 약함(-1) |

---

## 최종 채점 요약

| 항목 | 배점 | R3 점수 | R4 점수 | 변화 |
|------|:----:|:------:|:------:|:----:|
| API 연동 정확성 | 25 | 20 | 23 | +3 |
| 프론트-백 연동 | 25 | 22 | 24 | +2 |
| E2E 사용자 플로우 | 20 | 16 | 18 | +2 |
| UI/UX 품질 | 30 | 25 | 26 | +1 |
| **합계** | **100** | **83** | **91** | **+8** |

### 판정: PASS (91/100)

90점 이상 달성. Phase 3 진행 가능.

---

## R3 -> R4 핵심 개선 확인

### 치명 문제 해소
1. **generate.py 24페이지 생성**: `total_pages = page_count // 2` -> `total_pages = page_count` 수정 확인. 실제 API 호출에서 24페이지 생성 + DB 저장 확인.
2. **주문 워크플로우 성공**: POST /api/books/:id/order가 BookPrint API 전체 워크플로우를 성공 완료하여 order_uid(`or_3CNddMrdu0eg`) 발급. R3의 502 에러 완전 해소.

---

## 잔여 개선 사항 (경미 -- 차기 개선 권장)

### 경미 (UX 개선)
1. **랜딩 페이지 샘플 미리보기 영역**: 실제 이미지 없이 그래디언트 배경만 표시. Phase 3에서 AI 생성 이미지로 대체 예정.
2. **입력 필드 포커스 피드백**: border 색상 변화 강화 권장.
3. **Idempotency-Key 헤더**: BookPrint API POST 요청에 UUID 기반 중복 방지 헤더 추가 권장.
4. **서버 재시작 주의**: uvicorn --reload 미사용 시 코드 변경 후 반드시 수동 재시작 필요.
