# 셀프체크 — 태스크 8: 동화책 만들기 위자드 — 옵션 + 줄거리 + 생성 (R2)

## 테스트 결과
- 전체 테스트 수: 139개 (기존 111개 + 태스크 8 신규 28개)
- 통과: 139개
- 실패: 0개
- 프론트엔드 빌드: 성공

## R2 피드백 반영 내역

### 1. 판형별 페이지 수 범위 분리 (백엔드 + 프론트엔드)
- [x] 백엔드: `BOOK_SPEC_PAGE_RANGES` 딕셔너리 추가 (SQUAREBOOK_HC: 24~130, PHOTOBOOK_A4_SC: 24~130, PHOTOBOOK_A5_SC: 50~200)
- [x] 백엔드: `@model_validator(mode="after")`로 page_count + book_spec_uid 교차 검증
- [x] 프론트엔드: BOOK_SPECS에 minPages/maxPages 필드 추가
- [x] 프론트엔드: 슬라이더 min/max를 판형에 따라 동적 변경
- [x] 프론트엔드: 판형 변경 시 pageCount가 새 범위 밖이면 자동 보정
- [x] 프론트엔드: validateOptions에서 판형별 범위 검증

### 2. plot_input 길이 제한
- [x] 백엔드: `@field_validator("plot_input")` 추가 — 최대 1000자, 초과 시 에러 반환

### 3. generate 재호출 방어
- [x] 백엔드: `book.status not in ("draft", "character_confirmed")` 체크 추가
- [x] 이미 editing/completed 상태인 책에 generate 호출 시 422 반환

### 4. 테스트 케이스 추가 (11개 신규, 총 28개)
- [x] test_page_count_exceeds_130_rejected — SQUAREBOOK_HC 130 초과 거부
- [x] test_a5_below_50_rejected — PHOTOBOOK_A5_SC 24p 거부
- [x] test_a5_50_accepted — PHOTOBOOK_A5_SC 50p 허용
- [x] test_a5_200_accepted — PHOTOBOOK_A5_SC 200p 허용
- [x] test_a5_above_200_rejected — PHOTOBOOK_A5_SC 202p 거부
- [x] test_squarebook_130_accepted — SQUAREBOOK_HC 130p 허용
- [x] test_plot_input_over_1000_rejected — 1001자 거부
- [x] test_plot_input_exactly_1000_accepted — 1000자 허용
- [x] test_generate_twice_rejected — editing 상태 재호출 거부
- [x] test_generate_completed_rejected — completed 상태 재호출 거부
- [x] test_page_types_title_content_ending — page_type 구성 검증

## SPEC 기능 체크

### 옵션 선택 (Step 6)
- [x] 페이지 수 선택 (판형별 동적 범위, 2p 단위 증가, 슬라이더 + 버튼)
- [x] 판형 선택 (SQUAREBOOK_HC 기본, PHOTOBOOK_A4_SC, PHOTOBOOK_A5_SC)
- [x] 예상 가격 실시간 표시 (판형 + 페이지 수 기반 계산)
- [x] 유효성 검증 (판형별 page_count 범위, 짝수 / book_spec_uid: 3종만 허용)

### 줄거리 작성 (Step 7)
- [x] 스토리 테마 선택 UI (직업별 테마 카드 3개 + "직접 쓸래요")
- [x] "직접 쓸래요"만 활성화, 나머지는 "준비 중" 배지
- [x] "준비 중" 카드 클릭 시 토스트 "곧 제공될 예정입니다"
- [x] "직접 쓸래요" 선택 시 textarea (최대 1000자, 글자 수 표시)

### 생성 중 (Step 8)
- [x] 더미 스토리 + 더미 이미지로 즉시 페이지 데이터 생성
- [x] 원형 진행률 UI (SVG 기반 + 애니메이션)
- [x] 생성 중 상태에서 뒤로가기 차단 (popstate + 버튼 숨김)
- [x] 생성 완료 시 자동으로 편집 화면(`/create/edit?book_id=...`)으로 이동

### 백엔드
- [x] `PATCH /api/books/:id` — page_count, book_spec_uid, plot_input 저장 + 판형별 범위 검증 + plot_input 1000자 제한
- [x] `POST /api/books/:id/generate` — 더미 스토리+이미지 생성 + 재호출 방어
- [x] `GET /api/books/:id/pages` — 페이지 목록 조회

### 디자인/반응형
- [x] 파스텔 톤 색상 팔레트 적용
- [x] Framer Motion 애니메이션 (페이지 전환, 카드 호버, 진행률)
- [x] 반응형 레이아웃 (max-w, grid, padding)
- [x] 둥근 모서리 (rounded-2xl, rounded-xl)

## 특이사항
- Phase 2이므로 AI 호출 없이 더미 데이터 사용 (templates 기반 텍스트 치환)
- 편집 페이지(`/create/edit`)는 기본 레이아웃만 구현 (태스크 9 범위)
- Lottie 애니메이션 대신 SVG 기반 원형 프로그레스 구현 (외부 라이브러리 의존성 최소화)
